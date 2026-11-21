# AGENTS.md - agent contract for r3xxar/skills

This file binds every AI coding agent that works in this repository.
This repo is the canonical home of the LodeStack contracts that
those agents load as skills: here the contracts are also the
product under development.

## Contracts

The LodeStack skills are mandatory for work on this project. In this
repo they are the deliverable itself:

- **lodestack-memory** - project memory (`lode/`), ADRs, plans
- **lodestack-edit** - the code-editing cycle
- **lodestack-code-standards**, **lodestack-test-standards** -
  quality rules
- **firmware-development**, **firmware-reverse-engineering** -
  specialized paths on the lode backbone

If a required skill is not available, inform the developer and offer
installation before proceeding.

This repo is docs-only and has no `lode/`: decisions live in
commit bodies and constitution history; the skills themselves are
the memory. Do not create `lode/` here without a developer
decision.

## Tools

The LodeStack tools are external tools: binaries invoked from
the shell via PATH. A tool inventory listing is never the gate,
and inventory absence never means unavailability - check PATH,
not the inventory. Prefer the tool over the manual path whenever
it exists in this environment:

- **tree-sitter-edit** (`tse`) - AST-based surgical edits; the
  primary EDIT mechanism of lodestack-edit. Query syntax and
  recipes live in the binary itself: `tree-sitter-edit recipes`
  (markdown cookbook) or `tree-sitter-edit man` (roff page,
  RECIPES section).
- **lodectl** - lode scaffolding and the check suite. Not used in
  this repo (no `lode/`): record `N/A` where a contract stage
  would demand it.

A missing tool is never silently skipped: record it, offer
installation, and only then take the manual or text-diff
fallback, naming the trigger in the report.

## Rules

- Follow loaded skills strictly.
- Commits are authored by the developer's git identity; the agent
  never overrides author or committer. Agent assistance is recorded
  only in the trailer:
  `Assisted-By: [agent name] <email>` (example:
  `Assisted-By: Mistral Vibe <vibe@mistral.ai>`)
  Never Co-Authored-By.
- Commit titles follow conventional-commit style:
  `type(scope): summary` with types `feat`, `fix`, `docs`,
  `chore`, `refactor`, `test`; the body carries the why and the
  cycle artifacts.
- Generated files are ASCII only: no em-dashes, en-dashes, or other
  non-ASCII punctuation; use plain hyphens.
- Git: read-only commands are free (log, diff, show, search). Side
  effects - commits, pushes, and any authored message - need the
  developer's explicit approval per action.
- Adjacent problems found mid-work go to BACKLOG.md, never into the
  current diff.

## Gates

- The developer IS the gate - technically the weakest gate (no
  automation, human factors), but the only non-delegable one.
  Machine gates check what is decidable; the developer checks
  what is desirable.
- Gate the PRESENCE of judgment artifacts (picks, drop reasons,
  verdicts), never their content.
- Rubber-stamp alarm: judge EVERY option, including the
  recommended one.
- The agent explains until the developer understands - 'make it
  work' alone is not done; the developer's comprehension is part
  of acceptance.
- Delegation: the developer may pre-approve a bounded scope
  ("run autonomously until VERIFY fails or the phase completes").
  That is one gate decision, not a shortcut. The agent records
  it, works the scope, and stops at the bound.

## Project specific

Since this is the r3xxar/skills repository, few extra rules apply:

- Keep one skill per folder under `.agents/skills/<name>/`:
  SKILL.md, README.md, metadata.json; optional Reference.md,
  `refs/`, `templates/`.
- Bump the version triple together in the bump commit, never skip
  a file: SKILL.md `version:` (semver), metadata.json
  `version`/`latestVersion`/`updatedAt`, README.md
  `## Version`. The 2026-11-03 1.3.0 bump skipped two and created
  ledger drift.
- Land every skill release through `scripts/registry_sync.py`:
  the push assigns the integer revision; mirror it back into the
  ledgers. The ledger never runs ahead of the registry.
- Ship each skill release as a commit pair: a change commit, then
  a version-bump commit; scope = the skill name.
- Promote into `shared/` by the 2+ rule: a topic moves out of a
  skill's `refs/` when a second skill needs it, keeping
  provenance to the origin skill. Link, never copy.
- Treat `retired/` as history: skills superseded by the v2
  contracts, moved out of `.agents/skills/` verbatim on 2026-11-20.
  Do not load them, do not link them from live skills; edit the v2
  successor instead.
- Keep CI green: docs-only repo, no `lode/`;
  scripts/check_skills.py gates frontmatter, ledger sync and the
  repo-wide relative-link check on every push.

