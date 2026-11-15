tree-sitter-edit: 0c1cd42c8fab2452cb871b5d5147a4c9406288f0

Core subset of docs/agent-recipes.md at the pinned commit. Refresh
trigger: re-check upstream when the tool's recipes change. Dropped
recipe sections are covered by `tree-sitter-edit --help` or the
notes at the end.

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
gate; the gate is the `(ERROR)/(MISSING)` query scan below. Node
type names differ per grammar; `dump` is how you see them before
writing a query.

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
# one --text per --query, paired by position
tree-sitter-edit edit \
  --query '((function_declaration name: (identifier) @n) @fn (#eq? @n "alpha"))' --text-file alpha.txt \
  --query '((function_declaration name: (identifier) @n) @fn (#eq? @n "beta"))'  --text-file beta.txt \
  --capture fn \
  --dry-run --format diff main.go    # review all hunks first
tree-sitter-edit edit \
  --query '((function_declaration name: (identifier) @n) @fn (#eq? @n "alpha"))' --text-file alpha.txt \
  --query '((function_declaration name: (identifier) @n) @fn (#eq? @n "beta"))'  --text-file beta.txt \
  --capture fn --in-place main.go
```

All targets resolve against the original parse (order-independent);
overlapping ranges are exit 2; one re-parse, one atomic write; a
query matching nothing fails the batch (exit 1) before anything
writes. `--all`/`--occurrence`/`--at-*` are rejected in batch;
`--capture` and `--query-file` repeat per `--query` entry, paired
positionally (query-file dodges shell quoting).

## Delete a node

```sh
tree-sitter-edit edit \
  --query '(expression_statement) @stmt' --capture stmt \
  --delete --in-place main.go
```

`--delete` removes the node's exact bytes only. Surrounding blank
lines and list separators (commas) survive; if that leaves
unparseable code, the re-parse check rejects the edit with exit 1.

## Address a node by position (from grep, an editor, or an LSP)

```sh
grep -n "func hello" main.go        # 4:func hello() {   (grep lines are 1-based)
tree-sitter-edit edit --at-row-col 3:5 --text greet main.go   # tool rows are 0-based
tree-sitter-edit edit --at-byte 1234 --text greet main.go
```

`--at-row-col` is strict: `4:5:2` or `4:5x` are rejected with exit 2.

## Scan a file for parse errors

```sh
tree-sitter-edit query \
  --query '(ERROR) @err (MISSING) @miss' \
  --capture err --capture miss --format json src/big.cpp
# empty output + exit 0 means the file parses cleanly
```

## Odds and ends

- `--text-file FILE` reads a payload verbatim (trailing newline
  kept); `-` reads stdin, but not when the input file is also `-`.
  Mutually exclusive with `--text` and `--delete`.
- `--all` replaces every match of a single-query edit.
- `-` as the file reads stdin and requires `--lang` (no extension to
  detect).
- One file per invocation; loop over `grep -rl` for multi-file work.
- QML is supported via a vendored qmljs grammar; same commands, but
  node shapes differ (`ui_binding`, `ui_property`).
- Flags come before the file argument (Go `flag` convention).
