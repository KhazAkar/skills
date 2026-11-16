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

The LodeStack tools mechanize the contracts above. Prefer the
tool over the manual path whenever it exists in this environment:

- **tree-sitter-edit** (`tse`) - AST-based surgical edits; the
  primary EDIT mechanism of lodestack-edit. Query syntax lives in
  that skill's tse-recipes.md.
- **lodectl** - scaffolds and checks the `lode/` structure,
  reports the open backlog (`lodectl backlog`).

A missing tool is never silently skipped: record it, offer
installation, and only then take the manual or text-diff
fallback, naming the trigger in the report.

## Rules

- Follow loaded skills strictly.
- Model files - every ADR, Plan and `lode/architecture/` file -
  carry a mermaid diagram. VERIFY/LODE rejects a model file
  without one. An ADR presents its diagram in a dedicated
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
