tree-sitter-edit: defb3d95521ef85f3781bb878914091ccfcba9a4

Core subset of docs/agent-recipes.md at the pinned commit (refreshed from defb3d9 on master). Refresh trigger: re-check upstream when the tool's recipes change. Dropped recipe sections are covered by `tree-sitter-edit --help` or the notes at the end.

# Agent recipes (core)

Ready-to-use snippets for driving `tree-sitter-edit` from an agent.
Every command assumes the binary is on `PATH` (or use
`alias tse=tree-sitter-edit`).

Guarantees you can rely on in scripts:

- Every edit is re-parsed before it is written. If the result does
  not parse, nothing is written and the exit code is 1.
- `--in-place` and `-o` write atomically (temp file + rename) and
  preserve the original file mode.
- Exit codes: `0` success, `1` edit/parse/IO failure, `2` usage
  error (bad flags, bad query, conflicting flags). stderr carries
  the message; stdout carries only results.
- Batch results are canonical: the JSON `replacements` list is
  sorted by byte offset; `--query`/`--text` order does not change
  the output source or the report.

## Discover node shapes first: dump, then query

Token-budget pattern: dump shallow to learn the shape, then drill by
position.

```sh
# 1. shallow look at the shape (no default cap; bound it yourself)
tree-sitter-edit dump --depth 2 src/config.cpp

# 2. drill to a position (grep says line 12 -> row 11, 0-based) and see the
#    ancestry path -- "why did my edit hit the wrong node" lives here
tree-sitter-edit dump --at-row-col 11:5 src/config.cpp

# 3. full tree as JSON with byte ranges per node (same field names as
#    query --format json), anonymous nodes only when you need them
tree-sitter-edit dump --format json --anonymous src/config.cpp

# 4. mark query matches in the tree; the marked set equals query's match set
tree-sitter-edit dump --query '((function_definition) @fn)' src/config.cpp
```

`dump` exits 0 even on files with syntax errors (`ERROR` nodes are
visible, `"has_errors": true` in JSON) — it inspects, it does not
gate; the gate is `check` below. Node
type names differ per grammar; `dump` is how you see them before
writing a query.

`dump --node-types <file>` lists the grammar's node types without the
tree (one per line; json `node_types` array). Use it when a query fails
with `unknown node type` - the exit-1 error hints at this command
(ADR-2026-11-15-008).

## Node boundary trivia (per grammar)

A payload replaces the node's exact bytes; trivia around the node
survives. Two cases bit us in the ags session -- check the node's
exact range first (`query --format json`, or `dump --at-row-col
R:C`):

- Rust: `field_declaration` and `shorthand_field_initializer`
  EXCLUDE the trailing comma. The payload must not repeat it:
  `health: u32,\n    ticks: u32,` produces a double comma and the
  re-parse gate rejects the edit (exit 1).
- Go: `expression_case` INCLUDES its trailing newline. A payload
  without one glues the next `case` onto the same line. tree-sitter
  accepts that glue (the re-parse gate is grammar-level, not
  compiler-level -- pinned in `internal/cli/hostile_test.go`), so
  `go build` remains the real check.

- Markdown: the `atx_heading` node starts AFTER the `## ` marker, so
  `--op insert-before` on the heading node lands mid-heading (`## ## Tools`).
  Anchor on the marker node instead:
  `(atx_heading (atx_h2_marker) @m heading_content: (inline) @c (#eq? @c "Rules"))`
  with `--capture m`.

## Find a definition by name

```sh
# Go function
tree-sitter-edit query \
  --query '((function_declaration name: (identifier) @name) (#eq? @name "handleSensorReading"))' \
  --capture name --format json main.go

# C++ method defined out of line (Config::clear) - declarator is a qualified_identifier
tree-sitter-edit query \
  --query '((function_definition declarator: (function_declarator declarator: (qualified_identifier name: (identifier) @name))) (#eq? @name "clear"))' \
  --capture name --format json src/config.cpp

# C++ method defined inline in the class - declarator is a field_identifier
tree-sitter-edit query \
  --query '((function_definition declarator: (function_declarator declarator: (field_identifier) @name)) (#eq? @name "clear"))' \
  --capture name --format json src/config.cpp
```

In the Go grammar plain functions are `function_declaration` but
methods are `method_declaration`; in C++ both are
`function_definition` and differ by declarator shape. `query`
discovers the node types of your target; `--format json` gives byte
offsets and row:col per match, `--capture` prints one capture when a
query has several.

## Rename a symbol, definition plus all references

```sh
tree-sitter-edit rename \
  --query '(function_declaration name: (identifier) @name)' \
  --capture name --occurrence 0 --text newName \
  --dry-run --format diff main.go   # review first
tree-sitter-edit rename \
  --query '(function_declaration name: (identifier) @name)' \
  --capture name --occurrence 0 --text newName \
  --in-place main.go
```

`rename` uses vendored locals queries (go, python, rust, typescript,
cpp) and renames the definition and every reference in its scope,
handling shadowing. Single-node replacement (no reference handling)
is `edit` with `--text`.

## List a symbol's references, or jump to its definition

```sh
# every site rename would touch - kind-tagged, byte-sorted
tree-sitter-edit references --at-row-col 4:6 --format json main.go

# the one definition for the symbol under a position
tree-sitter-edit definition --at-byte 115 --format json main.go
```

Both take the same addressing as `rename` (`--query`/`--capture`/
`--occurrence`, or a position). The JSON is LSP-shaped: `file`,
`kind` (`definition`|`reference`), `text`, plus row:col and byte
range fields. A position that is not a symbol returns
`"locations": []`, exit 0.

## Edit one node: review the diff, then apply

```sh
tree-sitter-edit edit \
  --query '((function_declaration name: (identifier) @name) (#eq? @name "hello"))' \
  --capture name --text greet \
  --dry-run --format diff main.go    # prints one unified hunk, writes nothing

tree-sitter-edit edit \
  --query '((function_declaration name: (identifier) @name) (#eq? @name "hello"))' \
  --capture name --text greet \
  --in-place main.go
```

Use `--occurrence N` (0-based) when the query matches several nodes.

## Batch: several edits in one invocation, one write

```sh
# one --text per --query, paired by position; texts from one kind only
tree-sitter-edit edit \
  --query '((function_declaration name: (identifier) @n) @fn (#eq? @n "alpha"))' --text-file alpha.txt \
  --query '((function_declaration name: (identifier) @n) @fn (#eq? @n "beta"))'  --text-file beta.txt \
  --capture fn \
  --dry-run --format diff main.go    # review all hunks first, then --in-place
```

All targets resolve against the original parse (order-independent);
overlapping ranges are exit 2; one re-parse, one atomic write; a
query matching nothing fails the batch (exit 1) before anything
writes. `--all`/`--occurrence`/`--at-*` are rejected in batch;
`--capture` and `--query-file` repeat per `--query` entry, paired
positionally (query-file dodges shell quoting). Mixed operations
per entry via `--op` (`replace`, `insert-before`, `insert-after`,
`delete`); a single `--op` value broadcasts to all entries:

```sh
tree-sitter-edit edit \
  --query '(import_declaration) @i' --capture i \
  --op insert-after --text $'\nimport "os"' \
  --query '(call_expression) @c' --capture c \
  --op insert-before --text $'fmt.Println("x")\n\t' \
  --dry-run --format diff main.go
```

Insert payloads write at the node's boundary byte and carry their
own newlines/indentation; an insert that breaks syntax is exit 1,
two inserts on the same byte are exit 2.

## Delete a node

```sh
tree-sitter-edit edit \
  --query '(expression_statement) @stmt' --capture stmt \
  --op delete --in-place main.go
```

`--op delete` removes the node's exact bytes only. Surrounding blank
lines and list separators (commas) survive; if that leaves
unparseable code, the re-parse check rejects the edit with exit 1.

## Address a node by position (from grep, an editor, or an LSP)

```sh
grep -n "func hello" main.go        # 4:func hello() {   (grep lines are 1-based)
tree-sitter-edit edit --at-row-col 3:5 --text greet main.go   # tool rows are 0-based
tree-sitter-edit edit --at-byte 1234 --text greet main.go
```

`--at-row-col` is strict: `4:5:2` or `4:5x` are rejected with exit 2.

## Scan a file for parse errors (check)

```sh
tree-sitter-edit check src/big.cpp
# exit 0 = clean, 1 = parse errors found (listed), 3 = file couldn't
# be checked; multiple files report each in argument order

tree-sitter-edit check --format json src/big.cpp | jq '.files[0].errors'
# [{"type":"missing","text":"}","start_byte":...,"start_row":4,"start_col":0,...}]
```

`check` reports each ERROR and MISSING node with its range; MISSING
means the grammar expected a token that is absent (unclosed `}`, `)`,
empty expression) - the `text` field names the missing symbol. Gate a
pipeline on the exit code; inspect locations from the report.

## Edit many files: --glob

```sh
# same operation on every match; one combined report
tree-sitter-edit edit --all \
  --query '(identifier) @n (#eq? @n "oldName")' --capture n \
  --text newName --glob 'src/**/*.go' --in-place

# dry-run the whole set first: per-file status + replacements, no writes
tree-sitter-edit rename \
  --query '(function_declaration name: (identifier) @name)' \
  --text greet --glob 'src/**/*.go' --dry-run --format json
```

The file set is every pattern's matches, deduplicated and sorted.
Semantics stay per-file: a file that fails reports
`"status":"error"` and the rest still apply (exit 1 says some
failed; the JSON says which); no cross-file analysis, no
whole-batch rollback. Position flags and `--format diff` are
rejected under `--glob`; use a query to address.

## Odds and ends

- `--text-file FILE` reads a payload verbatim (trailing newline
  kept); `-` reads stdin, but not when the input file is also `-`.
  Mutually exclusive with `--text` and `--op delete`.
- `--all` replaces every match of a single-query edit.
- `-` as the file reads stdin and requires `--lang` (no extension to
  detect).
- QML is supported via a vendored qmljs grammar; same commands, but
  node shapes differ (`ui_binding`, `ui_property`).
- For file sets a glob cannot express (changed files only,
  grep-filtered), a shell loop over `grep -rl` still composes.
- Flags come before the file argument (Go `flag` convention).
