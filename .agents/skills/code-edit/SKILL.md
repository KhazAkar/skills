---
name: "code-edit"
description: "Default mode for ALL code work — load this skill for every code change, code review, or coding task, in any project. The universal surgical edit contract: five non-negotiable stages (INTENT, LOCATE, IMPACT, EDIT, PROPAGATE) with checkable artifacts, research-first (codebase, then official docs, then CLI help/man), reuse-first, per-change metrics in commit bodies."
version: "1.0.3"
author: "Damian Zaręba"
license: "GPL-3.0-or-later"
tags:
  - programming
  - code-review
  - edit-discipline
  - yagni
---

# Code Edit (Surgical Edit Contract)

The default way of working for code changes. Every code change runs five
stages, in order. A stage starts only after the previous stage produced
its artifact. Artifacts go in the change description (commit body, MR
description, or session note). Every point is non-negotiable.

1. **INTENT.** Acceptance evidence before any code: a failing test, a
   reproducible case, a ticket acceptance line, or a plan checkbox. One
   intent per change. No evidence, no change.
2. **LOCATE.** Find edit sites by searching the codebase (search,
   indexes, tags, call graphs), never from memory. Bounded list of
   file/class/function. A long list means the task is too big: split it
   and say so. Read only what the list requires.
3. **IMPACT.** List every dependent, both directions: callers, bindings,
   signals/events, UI wiring, config, build files, resources, docs,
   translations, packaging. Mark each entry EDIT or EXEMPT with a
   reason. No silent members. The human reviews this list first, the
   diff second.
4. **EDIT.** Only the edit sites and EDIT members. Minimal diff; remove
   removed code completely; match file style. Research is part of the
   edit: verify every library call, API field, flag, config key, CLI
   command, or file format against the real sources, in order —
   1. the codebase itself (how the same thing is already done there);
   2. official documentation of the library/framework/app;
   3. CLI help (`--help`, `-h`) and man pages.
   Model memory is not a source. If sources disagree or cannot confirm,
   the change waits; record the gap. Reuse first: existing code in this
   repo, then stdlib/platform/framework; state what was reused and why
   new code was needed. No drive-by refactors, no abstraction with a
   single caller, no new dependency without asking; adjacent problems go
   to the backlog, not into the diff.
5. **PROPAGATE.** Re-check every impact entry: edited as declared, or
   EXEMPT with a reason. Run the project's gates (lint, build, tests)
   and keep them green. State the satisfied acceptance line. Record the
   numbers: lines +/−, files touched, edit sites, EDIT/EXEMPT counts,
   reuse decisions, research sources consulted (doc pages, man sections,
   CLI commands).

## Deployment

- Repo with an AGENTS.md / CLAUDE.md carrying the contract: follow that
  copy; it may name stack-specific sources.
- Repo without one: follow this contract anyway — it is the default —
  and propose adopting it (an AGENTS.md / CLAUDE.md at the repo root)
   before the first substantial change.
- Repo with a `lode/` folder: also follow the lode-programming skill
  cadence — create the ADR before the code it justifies, update the
  lode at acceptance. Commit-body artifacts record the change; ADRs
  record the decision. Both, not either.
- When an AI agent assisted, commits end with a trailer stating the
  agent's official identity and a real contact address of the agent or
  its vendor, not Co-Authored-By:
  `Assisted-By: [agent name] <email>` (example:
  `Assisted-By: Mistral Vibe <vibe@mistral.ai>`)

## Self-check before declaring done

Intent stated? Bounded edit sites? Every dependent marked EDIT or
EXEMPT? Docs/CLI/man actually consulted for anything uncertain? Reuse
checked? Gates green? Numbers recorded? Any "no" means it is not done.
