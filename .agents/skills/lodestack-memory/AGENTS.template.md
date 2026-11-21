# AGENTS.md - agent contract for <project>

This file binds every AI coding agent that works in this repository.

## Contracts

The LodeStack skills are mandatory for work on this project:

- **lodestack-memory** - project memory (`lode/`), ADRs, plans
- **lodestack-edit** - the code-editing cycle
- **lodestack-code-standards**, **lodestack-test-standards** -
  quality rules

If a required skill is not available, inform the developer and offer
installation before proceeding.

Project memory entry point: `lode/lode-map.md`.

## Tools

The LodeStack tools are external tools: binaries invoked from
the shell via PATH. A tool inventory listing (any manifest of
sanctioned runtime tools) is never the gate, and inventory
absence never means the tool is unavailable - check PATH, not
the inventory. Prefer the tool over the manual path whenever it
exists in this environment:

- **tree-sitter-edit** (`tse`) - AST-based surgical edits; the
  primary EDIT mechanism of lodestack-edit. Query syntax and recipes
  live in the binary itself: `tree-sitter-edit recipes` (markdown
  cookbook) or `tree-sitter-edit man` (roff page, RECIPES section).
- **lodectl** - scaffolds the `lode/` structure, runs the check
  suite (including mermaid presence and syntax validation), and
  reports the open backlog (`lodectl backlog`). Usage:
  `lodectl help`, `lodectl <command> --help`, or `lodectl man`
  (search it: `lodectl man | grep <topic>`).

In a repo with `lode/`, lodectl is mandatory equipment, not
optional: run `lodectl check` and deal with every finding before
the gated work ends - fixed in `lode/`, refuted on record with a
one-line reason, or adjudged a tool limit that goes upstream;
findings are never silenced, never ignored, and the developer
gates the dispositions at review. When the binary is missing,
install it with developer approval instead of recording `N/A`.
`N/A` applies only to repositories without `lode/`. Fixes touch
lode hygiene; Accepted ADR substance still changes by
superseding.

A missing tool is never silently skipped: record it, offer
installation, and only then take the manual or text-diff
fallback, naming the trigger in the report.

## Rules

- Follow loaded skills strictly.
- Model files - every ADR, Plan and `lode/architecture/` file -
  carry a valid mermaid diagram. VERIFY/LODE rejects a model file
  without one (mermaid-presence) or with an invalid one
  (mermaid-syntax). An ADR presents its diagram in a dedicated
  `## Model` section directly before the Specification.
- Commits are authored by the developer's git identity; the agent
  never overrides author or committer. Agent assistance is recorded
  only in the trailer below.
- Commits end with exactly one trailer stating the agent's official
  identity and a real contact address of the agent or its vendor:
  `Assisted-By: [agent name] <email>` (example:
  `Assisted-By: Mistral Vibe <vibe@mistral.ai>`)
  Never Co-Authored-By.
- Commit titles follow conventional-commit style:
  `type(scope): summary` with types `feat`, `fix`, `docs`,
  `chore`, `refactor`, `test`; the body carries the why.
- Generated files are ASCII only: no em-dashes, en-dashes, or other
  non-ASCII punctuation; use plain hyphens.
- Git: read-only commands are free (log, diff, show, search). Side
  effects - commits, pushes, PRs, issues, and any authored message -
  need the developer's explicit approval per action.

## Gates

- The developer IS the gate - technically the weakest gate (no
  automation, human factors), but the only non-delegable one.
  Machine gates check what is decidable; the developer checks what
  is desirable.
- Gate the PRESENCE of judgment artifacts (picks, drop reasons,
  verdicts), never their content.
- Rubber-stamp alarm: judge EVERY option, including the recommended
  one.
- The agent explains until the developer understands - 'make it
  work' alone is not done; the developer's comprehension is part of
  acceptance.
- **Delegation**: the developer may pre-approve a bounded scope
  ("run autonomously until VERIFY fails or the phase completes").
  That is one gate decision, not a shortcut. The agent records it,
  works the scope, and stops at the bound.

## Project specific

Project-bound rules that apply in this repository beyond the
universal contracts. Written as enforceable orders in imperative
voice: one rule per bullet, each checkable by the developer. A link
is not a rule: when following a file is mandatory, state the duty
as an enforceable clause, for example: "Before performing any
action, read `lode/practices.md` in full and follow it to the
letter." Commands, workflows and tooling stay in
`lode/practices.md` (Memory contract); reach them from here only
through such clauses, never as bare links.
Practice twins: each order here is the short, unambiguous twin of
one entry in `lode/practices.md` - the same pairing as SKILL.md
to Reference.md. Orders bind; the practice entry carries the
explanation and the procedure. Only practices that bind the agent
get a twin; informational ones live in `lode/practices.md`
alone. End each twin with its provenance, for example: (full:
Running, <practice>, lode/practices.md). A practice changes only
together with its order twin, in one commit; when the two
disagree, the agent reports the gap and asks before fixing
either. An empty section is valid.

Since this is `<project>` repository, few extra rules apply:
