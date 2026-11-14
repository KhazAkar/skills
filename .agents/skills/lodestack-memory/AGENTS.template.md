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

## Rules

- Follow loaded skills strictly.
- Commits are authored by the developer's git identity; the agent
  never overrides author or committer. Agent assistance is recorded
  only in the trailer below.
- Commits end with exactly one trailer:
  `Assisted-By: <name-of-agent> <email@ofagent.xyz>`
  Never Co-Authored-By.
- Generated files are ASCII only: no em-dashes, en-dashes, or other
  non-ASCII punctuation; use plain hyphens.

## Gates

- The developer IS the gate - technically the weakest gate (no
  automation, human factors), but the only non-delegable one.
  Machine gates check what is decidable; the developer checks what
  is desirable.
- Gate the PRESENCE of judgment artifacts (picks, drop reasons,
  verdicts), never their content.
- Rubber-stamp alarm: judge EVERY option, including the recommended
  one.
- **Delegation**: the developer may pre-approve a bounded scope
  ("run autonomously until VERIFY fails or the phase completes").
  That is one gate decision, not a shortcut. The agent records it,
  works the scope, and stops at the bound.

<!--
Lode-stone marker - delete this comment if unused, fill and keep
as a plain line if the project memory lives in a shared hub:

Lode-stone transformed this project memory and now it lives here: <link_to_repository>, linked as submodule named 'lode' with project memory entry point living here: lode/projects/<name>/lode-map.md. For shared knowledge entry point, use lode/stone-map.md.
-->
