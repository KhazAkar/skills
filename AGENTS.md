# AGENTS.md — agent contract for the skills repo

This file binds every AI coding agent (Vibe, Devin, Claude Code, Copilot
or any other) that works in this repository. This repo is the canonical
home of the contract itself: the code-edit skill in
`.agents/skills/code-edit/`.

Read first:
- `.agents/skills/code-edit/SKILL.md` — the contract, full text.
- `.agents/skills/lode-programming/SKILL.md` — the lode backbone. It
  governs projects with a `lode/` folder; this repo has none.

## The edit contract (v1.2 — every point non-negotiable)

Every change runs five stages, in order. A stage starts only after the
previous stage produced its artifact. Artifacts go in the commit body.

1. **INTENT.** Acceptance evidence before any edit: a named outcome
   (skill loads, section added, version bumped). One intent per change.
2. **LOCATE.** List the edit sites by searching the repo, never from
   memory. Bounded list of files. A long list means the task is too
   big: split it and say so.
3. **IMPACT.** List every dependent of the edit sites: the skill's
   SKILL.md, README.md, metadata.json, `reference/` and `templates/`
   files, cross-references in other skills, this AGENTS.md. Mark each
   entry EDIT or EXEMPT with a reason. No silent members.
4. **EDIT.** Only the edit sites and EDIT members. Minimal diff. Match
   the file's style. Research is part of the edit: verify against, in
   order — 1. this repo (how the existing skills do it); 2. the skill
   format (SKILL.md = YAML frontmatter: name, description <= 1024
   characters, quoted when it contains a colon, version, author,
   license, tags; metadata.json id and version fields); 3. CLI help
   and man pages when tooling is involved. Model memory is not a
   source. Reuse first: copy the pattern of an existing skill. No
   drive-by edits to other skills; adjacent problems go to the
   backlog, not into the diff.
5. **PROPAGATE.** Re-check every impact entry: edited as declared, or
   EXEMPT with a reason. This repo has no CI; the gates are: re-fetch
   the changed files and verify the content, and check the version
   triple is in sync. Record the numbers in the commit body.

## Hard rules

- One skill per folder under `.agents/skills/<name>/`: SKILL.md,
  README.md, metadata.json; optional `reference/` and `templates/`.
- Version triple-sync: SKILL.md `version:`, metadata.json
  `version`/`latestVersion`/`updatedAt`, README.md `## Version` bump
  together in the bump commit. Never skip a file: the 2026-11-03 1.3.0
  bump skipped two and created ledger drift.
- Commits: conventional title with the skill as scope; a change
  commit, then a version-bump commit (repo history: 34bce29d then
  50549fa7; 349d9a2d then 1a284393).
- No `lode/` here: docs-only repo. Decisions live in commit bodies;
  the skills themselves are the memory.
- `_shared/` holds firmware topic references only. Link, never copy.
- Commits end with an appropriate trailer for the agent that did the
  work, not Co-Authored-By:
  `Assisted-By: [agent name] <email>` (example:
  `Assisted-By: Mistral Vibe <vibe@mistral.ai>`)
