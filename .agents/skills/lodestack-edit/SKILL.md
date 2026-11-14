---
name: "lodestack-edit"
description: "The LodeStack Edit contract - the code-editing cycle for every code change, review or refactor. REASON, LOCATE, ANALYZE (agent marks ACCEPT/REJECT per element, table to developer), EDIT via tree-sitter-edit with text-diff fallback, VERIFY gate (LINT, TYPECHECK, SECURITY, FORMAT, TEST, LODE) with an inner EDIT-VERIFY loop and the 3-attempt break rule. Load for ALL code work in any project."
version: "1.0.2"
author: "Damian Zaręba"
license: "MIT"
constitution: "573391b421fd31c4d4be1f0f0e540d51bc1a08fb"
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
big: split it and say so.

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
[tse-recipes.md](tse-recipes.md). Fall back to text-diff editing
when: the binary is missing, the file's grammar is unsupported, or
the edit cannot be expressed as a query. A failed VERIFY is not a
fallback - it is an inner-loop iteration.

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
- f. **LODE** - the change checked against `lode/` itself; if `lode/`
  is absent, record `N/A` and offer setup (AGENTS contract)

When VERIFY does not pass, run the smaller EDIT-VERIFY loop inside
the stage. Edits stay minimal-viable: they must satisfy REASON and
VERIFY, nothing more.

### Break rule
If REASON and VERIFY cannot both be satisfied within 3 attempts,
break the cycle and surface to the developer as a table: found
problems, a description of each, proposed solutions - one complete
paragraph of reasoning per pain point. The developer picks.

## Reports

After VERIFY passes, present in tabular form:

1. Summary of what was done
2. Findings made along the work
3. Potential issues

Present the VERIFY result itself as a list - one check per line,
with its status - not as inline prose.

Then propose a commit message and offer to commit after the manual
developer check. The summary table doubles as the commit body.

## Aliases (v1 -> v2)
INTENT = REASON, IMPACT = ANALYZE, PROPAGATE absorbed into VERIFY
(commit and report duties carried). Old AGENTS.md copies still
decode.

## Sources
Constitution: `constitution/LodeStack.md` at `573391b`.
Context: [Reference.md](Reference.md). Tool recipes:
[tse-recipes.md](tse-recipes.md) - pinned by SHA header.
