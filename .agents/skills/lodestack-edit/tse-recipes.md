tree-sitter-edit: 0c1cd42c8fab2452cb871b5d5147a4c9406288f0

Copied verbatim from docs/agent-recipes.md at the pinned commit.
Refresh trigger: re-copy when the tool's recipes change upstream.

# Agent recipes

Ready-to-use snippets for driving `tree-sitter-edit` from an agent. Every
command assumes the binary is on `PATH` (or use `alias tse=tree-sitter-edit`).

Guarantees you can rely on in scripts:

- Every edit is re-parsed before it is written. If the result does not parse,
  nothing is written and the exit code is 1.
- `--in-place` and `-o` write atomically (temp file + rename) and preserve the
  original file mode.
- Exit codes: `0` success, `1` edit/parse/IO failure, `2` usage error (bad
  flags, bad query, conflicting flags). stderr carries the message; stdout
  carries only results.
- Batch results are canonical: the JSON `replacements` list is sorted by byte
  offset, and the order you pass `--query`/`--text` pairs in does not change
  the output source or the report.

## Discover node shapes first: dump, then query

Token-budget pattern: dump shallow to learn the shape, then drill by position.

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

`dump` exits 0 even on files with syntax errors (`ERROR` nodes are visible,
`"has_errors": true` in JSON) — it inspects, it does not gate; the gate is
the `(ERROR)/(MISSING)` query scan below. Node type names differ per
grammar; `dump` is how you see them before writing a query.

## Node boundary trivia (per grammar)

A payload replaces the node's exact bytes; trivia around the node survives.
Two cases bit us in the ags session -- check the node's exact range first
(`query --format json`, or `dump --at-row-col R:C`):

- Rust: `field_declaration` and `shorthand_field_initializer` EXCLUDE the
  trailing comma. The payload must not repeat it: `health: u32,\n    ticks: u32,`
  produces a double comma and the re-parse gate rejects the edit (exit 1).
- Go: `expression_case` INCLUDES its trailing newline. A payload without one
  glues the next `case` onto the same line. tree-sitter accepts that glue
  (the re-parse gate is grammar-level, not compiler-level -- pinned in
  `internal/cli/hostile_test.go`), so `go build` remains the real check.

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

Note: in the Go grammar plain functions are `function_declaration` but methods
are `method_declaration`; in C++ both are `function_definition` and differ by
declarator shape. Run `query` first to discover the node types of your target.

`--format json` gives byte offsets and row:col for each match. Use
`--capture name` to print only that capture when a query has several.

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

`rename` uses vendored locals queries (go, python, rust, typescript, cpp) and
renames the definition and every reference in its scope, handling shadowing.
Single-node replacement (no reference handling) is `edit` with `--text`.

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

## Replace a node with multi-line text from a file or a pipe

```sh
# new body in a file; bytes are used verbatim (trailing newline kept)
tree-sitter-edit edit \
  --query '((function_definition declarator: (function_declarator declarator: (qualified_identifier name: (identifier) @name)) body: (compound_statement) @body) (#eq? @name "clear"))' \
  --capture body --text-file /tmp/new_body.cpp \
  --in-place src/config.cpp

# or straight from stdin - no shell quoting hazards
tree-sitter-edit edit --query '...' --capture body --text-file - src/config.cpp < /tmp/new_body.cpp
```

`--text-file` is mutually exclusive with `--text` and `--delete`. `-` reads
stdin, but not when the input file is also `-`.

## Batch: several edits in one invocation, one write

```sh
# one --text per --query, paired by position; texts from one kind only
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

Semantics: all targets resolve against the original parse (order-independent);
overlapping ranges are exit 2; one re-parse, one atomic write; a query that
matches nothing fails the whole batch (exit 1) before anything is written.
`--all`, `--occurrence`, `--at-byte`, `--at-row-col` are rejected in batch mode.
`--capture` is repeatable in batch mode: one per `--query`, paired
positionally (ADR-011). Entries without a capture fall back to the first
capture of the match. Same for `--query-file`: repeatable, one per entry,
mutually exclusive with `--query` (ADR-013) — predicates with embedded
quotes never see a shell:

```sh
tree-sitter-edit edit \
  --query-file alpha.scm --query-file beta.scm \
  --capture fn --capture name \
  --text-file alpha.txt --text-file beta.txt \
  --in-place main.go
```

```sh
# quick batch with inline --text pairs: rename two declarations, no call sites
tree-sitter-edit edit \
  --query '((function_declaration name: (identifier) @n) (#eq? @n "alpha"))' --text a2 \
  --query '((function_declaration name: (identifier) @n) (#eq? @n "beta"))'  --text b2 \
  --capture n \
  --dry-run --format diff main.go   # all hunks in one diff

# batch delete: remove two neighboring functions; their touching ranges merge
# into a single diff hunk
tree-sitter-edit edit \
  --query '((function_declaration name: (identifier) @n) @fn (#eq? @n "alpha"))' \
  --query '((function_declaration name: (identifier) @n) @fn (#eq? @n "beta"))' \
  --capture fn --delete --in-place main.go

# machine-readable report: replacements sorted by start_byte, entry order
# does not matter
tree-sitter-edit edit \
  --query '...' --text '...' \
  --query '...' --text '...' \
  --dry-run --format json main.go
# {"file":"main.go","count":2,"replacements":[{"start_byte":19,...},{"start_byte":50,...}]}
```

## Replace in every match

```sh
tree-sitter-edit edit \
  --query '(identifier) @id' --capture id \
  --text newName --all \
  main.go        # prints "replaced N node(s)" on stderr
```

## Delete a node

```sh
tree-sitter-edit edit \
  --query '(expression_statement) @stmt' --capture stmt \
  --delete --in-place main.go
```

`--delete` removes the node's exact bytes only. Surrounding blank lines and
list separators (commas) survive; if that leaves unparseable code, the
re-parse check rejects the edit with exit 1.

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

## Pipe mode (stdin to stdout)

```sh
cat main.go | tree-sitter-edit edit --lang go \
  --query '(function_declaration name: (identifier) @name)' \
  --capture name --text greet -
```

`-` as the file reads stdin and requires `--lang` (no extension to detect).

## Get a machine-readable change report

```sh
tree-sitter-edit edit --query '...' --text '...' --dry-run --format json main.go
# {"file":"main.go","count":1,"replacements":[{"start_byte":19,"end_byte":24,"old_text":"hello","new_text":"greet"}]}
```

## Edit many files (the tool is single-file; loop yourself)

```sh
for f in $(grep -rl 'oldName' --include='*.go' src/); do
  tree-sitter-edit rename --query '(identifier) @id' --capture id \
    --text newName --occurrence 0 --in-place "$f" || exit 1
done
```

Scope is one file per invocation. For a project-wide, scope-aware rename,
loop `rename` per file; there is no cross-file analysis.

## Clear a node's content without deleting the node

```sh
tree-sitter-edit edit --query '(interpreted_string_literal) @s' --capture s \
  --text '' main.go
```

## QML (`.qml` files)

QML is supported via a vendored qmljs grammar blob (ADR-010); `rename` is
scope-aware there too. Node shapes differ from JS: bindings are `ui_binding`,
properties are `ui_property`, and `Component.onCompleted` uses a
`nested_identifier` name.

```sh
# list binding and property names with positions
tree-sitter-edit query \
  --query '[(ui_binding name: (identifier) @name) (ui_property (identifier) @name)]' \
  --capture name --format json qml/pages/UserView.qml

# change a property's string value
tree-sitter-edit edit \
  --query '((ui_property (identifier) @n (expression_statement (string) @s)) (#eq? @n "title"))' \
  --capture s --text '"hi"' \
  --dry-run --format diff qml/pages/UserView.qml

# rename a JS function inside QML, definition + call sites
tree-sitter-edit rename \
  --query '((function_declaration name: (identifier) @n) (#eq? @n "greet"))' \
  --capture n --text salute \
  --in-place qml/pages/UserView.qml
```

## Tips

- Node type names differ per grammar (see the find-by-name recipes above). Run
  `query` first to discover the shape; use the `(ERROR)`/`(MISSING)` scan to
  check a file parses before editing.
- `--dry-run --format diff` is the review step: it prints the exact hunks that
  `--in-place` would write, and writes nothing.
- Flags must come before the file argument (Go `flag` convention).
