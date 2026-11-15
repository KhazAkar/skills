---
name: "lodestack-memory"
description: "Durable project memory - the LodeStack Memory contract. lode/ structure (lode-map, summary, terminology, practices, quirks-and-gotchas, adr/, plan/, architecture/, tmp/), the ADR spec (6xW, status machine, Verification block, TASKLIST bound), Plan and backlog formats, exploration lane, lode-stone shared-hub option. Load when starting projects, making architecture decisions, onboarding a codebase, or whenever a repo has lode/. Ships AGENTS.template.md."
version: "1.0.5"
author: "Damian Zaręba"
license: "MIT"
constitution: "573391b421fd31c4d4be1f0f0e540d51bc1a08fb"
tags:
  - lodestack
  - memory
  - lode
  - adr
  - project-memory
  - knowledge-management
---

# Skill: lodestack-memory

## Purpose
Durable project memory in `lode/` - the Memory contract of the
LodeStack. The lode is external memory for the developer and agents.

- **You own decisions. The agent owns memory.**
- **Lode is a byproduct of work, not a documentation job.**
- **Source of truth is layered.** Code alone is the implementation
  truth; ADR + Test + Code is the system/integration package truth;
  plus Plan is the feature-level truth. If the lode contradicts the
  code, summarize the gap and ask before fixing the lode.
- **Concise and precise.** Do not info-dump on the developer.
- **Research before solutions is mandatory.** Shortcuts in code
  manipulation, reasoning and decisions are forbidden.

Sibling contracts (load on demand; link, do not restate):
**lodestack-edit** for code changes, **lodestack-code-standards** and
**lodestack-test-standards** for quality rules. The repo-level
enforcement file ships here as
[AGENTS.template.md](AGENTS.template.md).

## When to load
- Starting a project or onboarding a codebase
- Making an architectural decision; writing or running an ADR or Plan
- First request of a session in a repo that has `lode/`

## Session start
1. Read `lode/lode-map.md`, `lode/summary.md`, `lode/terminology.md`
   before exploring the codebase. The lode-map is the index.
2. Show domain knowledge briefly before the first request.
3. If a project has no `lode/`, work normally; when it would benefit,
   inform and offer setup - `lodectl init` is the one-command answer
   when it is on PATH. The developer gates.

## Structure
```
lode/
|-- lode-map.md          # index: ADR + Plan + architecture links
|-- summary.md           # technical project description, NOT a README
|-- terminology.md       # names and verbs, ELI5-level definitions
|-- practices.md         # project actions and tooling
|-- osmm.md              # latest dated OSMM pass table
|-- quirks-and-gotchas/  # unexpected/live behaviour findings
|   |-- README.md            # main file
|   \-- <component>.md       # optional, for complex systems
|-- adr/                 # ADR-<YYYY-MM-DD>-<seq>.md + TASKLIST files
|-- plan/                # PLAN-*.md and BL-*.md
|-- architecture/        # system.md + <module>.md
\-- tmp/                 # scratch; folders per ADR/Plan; git-ignored
```

`practices.md` has four sections: necessary and opt-in tooling;
first setup; running; testing.

Rules for every file: one topic per file; under 250 lines; link to
code (`path/file.ext:line`); link between files; current state only
(changelog goes to `tmp/`); all diagrams mermaid; every
`architecture/` file carries one.

If `lode/` does not exist, ask before creating it. Add `lode/tmp/`
to `.gitignore`.

## Cadence
One cycle = one development cycle (ADR -> Test -> Code). The lode is
written at two moments:

1. **Decision** - the ADR exists before the code it justifies.
   ADR-first is the rule, not the exception.
2. **Acceptance** - when the developer accepts the work, update every
   affected lode file before the next request.

Not per step, not per commit.

## Exploration lane
Work may live in `lode/tmp/<topic>/` with no ADR and no gates. It
graduates to a Proposed ADR when it becomes real. This protects
research-grade and spike work from ceremony it is not ready for.

## ADR
An ADR is a permanent model of one decision - the input for the
executable specification (the test). Write it as a specification:
applying its logic verbatim produces the test.

### 6xW fields
1. **Status** - Proposed / Accepted / Superseded.
2. **What** - feature or fix.
3. **When** - Now / Backlog.
4. **Specification** - the whole description of the feature, written
   as an executable specification and ending with a **Verification**
   block: testable assertions (given X, when Y, then Z). The ADR->test
   derivation must be mechanical.
5. **Pick** - technologies to use. The agent proposes a researched
   list with reasoning; the developer picks and owns the reason.
6. **Drop** - the rest of the proposed list. The developer owns the
   rejection reason for each, even when the agent writes it down.

### Rules
- Do not edit an Accepted ADR. One exception: a technology version
  bump updates the version line.
- A Proposed ADR may iterate model and description; the topic stays.
- Every ADR carries a mermaid diagram - it is the model the
  Verification block and the test derive from.
- Superseding is the default way to change a decision. Never mutate
  history.
- Link the relevant technology documentation at the version in use.
- Name: `ADR-<YYYY-MM-DD>-<seq>.md`; `<seq>` is a zero-padded number
  per day (`ADR-2026-11-15-001.md`).
- Work steps live in `lode/adr/TASKLIST-ADR-<YYYY-MM-DD>-<seq>.md`.
- A TASKLIST growing past ~10 steps means the ADR is too big: split
  it into multiple ADRs and say so.

## Plan
- `PLAN-<YYYY-MM-DD>-<seq>.md` for plans; `BL-<YYYY-MM-DD>-<seq>.md`
  for feature-sized backlog items.
- Contents: a phase to-do list with a one-line title per phase; a
  high-level description of what each phase builds; a high-level
  mermaid model of elements, connections and dependencies between
  phases.
- An executing Plan can create one or several ADRs.

## OSMM assessment
Continuous, riding existing checkpoints (ADR acceptance, release
bumps, lode sync). The agent runs the pass against
[../shared/osmm-checklist.md](../shared/osmm-checklist.md), presents
it as a table; the developer judges content. The latest dated pass
table lives at `lode/osmm.md` - its presence is the checkable
artifact.

## Handover (on request)
Write `lode/tmp/handover-<date>.md`: task state, decisions,
approaches tried, blockers, next steps.

## Lode-stone (optional)
Transforms `lode/` into a shared multi-project knowledge hub mounted
as a submodule. See [refs/lode-stone.md](refs/lode-stone.md) for the
layout and the migration runbook.

## Language
- English: ASD-STE100 Simplified Technical English - one word one
  meaning, short sentences, active voice, present tense, no idioms.
- Other languages: STE-100 in spirit.
- Applies to lode files, ADRs, summaries and commit messages.

## Commands (natural language)
- "Set up lode/" -> run `lodectl init`
  (gitlab.com/r3xxar/lodectl) when it is on PATH; else the Structure
  section above
- "What is open in the backlog?" -> run `bltool`
  (gitlab.com/r3xxar/bltool) when it is on PATH; else search
  `lode/plan/` and the marker list by hand
- "What does the lode say about X?" -> search lode files
- "Create ADR for X" -> the ADR spec above
- "Update lode-map" -> regenerate the index
- "Review lode" -> check for outdated entries
- "Check lode" -> run `lodectl check`
  (gitlab.com/r3xxar/lodectl) when it is on PATH; else the
  model-file check in lodestack-edit VERIFY.f
- "Run OSMM assessment" -> dated pass table into `lode/osmm.md`
- "Handover" -> write `lode/tmp/handover-<date>.md`
- "Migrate this project to lode-stone" -> `refs/lode-stone.md`

## Sources
Constitution: `constitution/LodeStack.md` at `573391b`.
Context and mappings: [Reference.md](Reference.md).
