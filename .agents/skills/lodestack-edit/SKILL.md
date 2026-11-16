---
name: "lodestack-edit"
description: "The LodeStack Edit contract - the code-editing cycle for every code change, review or refactor. REASON, LOCATE, ANALYZE (agent marks ACCEPT/REJECT per element, table to developer), EDIT via tree-sitter-edit with text-diff fallback, VERIFY gate (LINT, TYPECHECK, SECURITY, FORMAT, TEST, LODE, RECHECK) with an inner EDIT-VERIFY loop, the 3-attempt break rule and the wildcard mechanism on repeat breaks. Load for ALL code work in any project."
version: "1.0.12"
author: "Damian Zaręba"
license: "MIT"
constitution: "a7033902800284dbfb8857af74558765243fb85b"
tags:
  - lodestack
  - edit
  - code-review
  - edit-discipline
  - tree-sitter
---

# Skill: lodestack-edit

## Purpose
The LodeStack Edit contract: the step-by-step protocol for every code
change. This is where the stack's cognitive ownership is exercised on
code - the agent does the work, the developer keeps the judgment.

- No shortcuts in code manipulation, reasoning and decisions.
- Research before solutions is mandatory; the operational ordering
  lives in [Reference.md](Reference.md).

Sibling contracts: **lodestack-memory** owns `lode/` and the ADRs a
REASON cites; **lodestack-code-standards** /
**lodestack-test-standards** own the quality rules VERIFY enforces.
Link, do not restate.

## The cycle

Five stages, in order. A stage starts only after the previous one
produced its artifact.

### 1. REASON
Why this change exists - acceptance evidence: a failing test, a
reproducible case, an ADR citation, a plan checkbox. One reason per
change. No evidence, no change.

### 2. LOCATE
Find the edit sites by searching the codebase - never from memory.
A bounded list of files/symbols. A long list means the task is too
big: split it and say so. The same bound holds for the diff: if the
developer cannot review the full diff in reasonable time, it is too
big - split it.

### 3. ANALYZE
List every dependent of the edit sites: callers, bindings,
signals/events, UI wiring, config, build files, resources, docs,
packaging. The agent marks each element **ACCEPT** or **REJECT** with
a short reason - first is agent. Present the status as a table; the
developer reviews it. No silent members.

### 4. EDIT
Only the sites and the ACCEPTed elements. Minimal viable diff, in
cycles; remove removed code completely; match the file's style.

Primary mechanism: **AST via `tree-sitter-edit`** - usage patterns in
[tse-recipes.md](tse-recipes.md). Why primary: every edit is
re-parsed before it is written (unparseable output is refused,
exit 1, nothing written), writes are atomic, and batch results are
canonical - the reviewable diff is structurally sound. Minimal loop:

```sh
tree-sitter-edit dump --depth 2 <file>                    # shape first
tree-sitter-edit edit --query '(...)' --capture n \
  --text <payload> --dry-run --format diff <file>          # review the hunk
tree-sitter-edit edit --query '(...)' --capture n \
  --text <payload> --in-place <file>                      # apply, re-parsed
```

Fall back to text-diff editing when: the binary is missing, the
file's grammar is unsupported, or the edit cannot be expressed as
a query - a query compile error is first an EDIT-loop iteration
(dump the file's node types, fix the query), fallback only when
the grammar has no node type for the target. An edit mechanism
not used is recorded, never silently swapped: binary missing is
recorded and earns the one-command install offer; the other
triggers are recorded with a one-line reason in the report. A
failed VERIFY is not a fallback - it is an inner-loop iteration.

### 5. VERIFY
The gate, as checkboxes. Points a-d run specialized tools for the
language in use. A missing tool is `N/A`-recorded AND the agent
offers to set it up - a gate that cannot run is recorded, never
silently absent.

- a. **LINT**
- b. **TYPECHECK**
- c. **SECURITY** - defensive strategies in the code, plus scanning
  with specialized tools
- d. **FORMAT**
- e. **TEST** - the executable specification, derived from the ADR
- f. **LODE** - the change checked against `lode/` itself. Touched
  model files - `lode/adr/ADR-*.md`, `lode/plan/PLAN-*.md`,
  `lode/architecture/*.md` - must carry a mermaid diagram: run
  `lodectl check` when it is on PATH; else `grep -L mermaid` on the
  touched model files must list none of them. If `lode/` is absent,
  record `N/A` and offer setup (AGENTS contract)
- g. **RECHECK** - the ANALYZE table re-run against the actual diff:
  every entry edited as declared, or flipped to EXEMPT/REJECT with a
  reason stated. Re-read the changed files: the reported diff must
  be what actually landed, not merely what compiles.

When VERIFY does not pass, run the smaller EDIT-VERIFY loop inside
the stage. Edits stay minimal-viable: they must satisfy REASON and
VERIFY, nothing more.

### Break rule
If REASON and VERIFY cannot both be satisfied within 3 attempts,
break the cycle and surface to the developer as a table: found
problems, a description of each, proposed solutions - one complete
paragraph of reasoning per pain point. The developer picks.

### Wildcard mechanism
The sanctioned escape from circling - creative thinking, bounded.

- **Trigger**: the same solution proposed twice without progress,
  the break rule firing twice on the same reason, research
  returning nothing new, or the developer declaring unexplored
  territory.
- **Action**: the next proposal set carries exactly one marked
  wildcard option, reasoned seriously like any other. The mark
  names the kind: `wildcard:contrarian` (the least-obvious path,
  against the working assumption), `wildcard:analogy` (a solved
  problem from an unconnected domain - state the structural
  mapping "X here is Y there, because..." explicitly),
  `wildcard:indirect` (change the frame so the problem dissolves).
  A wildcard may be a hint, not a full solution; a hint that
  survives first contact becomes a spike in `lode/tmp/`.
- **Bound**: one wildcard per decision; a repeated trigger on the
  same decision rotates the kind (contrarian, then analogy, then
  indirect); the developer still picks.

The gate is the marked option's presence; its honesty is the
developer's to judge.

## Reports

After VERIFY passes, present in tabular form:

1. Summary of what was done
2. Findings made along the work
3. Potential issues
4. Edit mechanism per file: `tree-sitter-edit`, or text-diff with
   the trigger recorded

Present the VERIFY result itself as a list - one check per line,
with its status - not as inline prose.

Then propose a commit message and offer to commit after the manual
developer check. The summary table doubles as the commit body.

## Aliases (v1 -> v2)
INTENT = REASON, IMPACT = ANALYZE, PROPAGATE absorbed into VERIFY
(commit, report and re-check duties carried). Old AGENTS.md copies
still decode.

## Sources
Constitution: `constitution/LodeStack.md` at `a7033902`.
Context: [Reference.md](Reference.md). Tool recipes:
[tse-recipes.md](tse-recipes.md) - pinned by SHA header.
