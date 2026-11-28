---
name: "lodestack-memory"
description: "Durable project memory - the LodeStack Memory contract. lode/ structure (lode-map, summary, terminology, practices, quirks-and-gotchas, adr/, tasks/, plan/, architecture/, tmp/), the ADR spec (octet slots, status machine, sibling Verification section, TASKLIST bound), Plan and backlog formats and exploration lane. Load when starting projects, making architecture decisions, onboarding a codebase, or whenever a repo has lode/. Ships AGENTS.template.md."
version: "2.0.1"
author: "Damian Zaręba"
license: "MIT"
constitution: "753997cbaf01e79114bc2c58f687225cfc52ff7c"
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
   inform and offer setup - `lodectl init` is the one-command answer.
   In repositories with `lode/`, lodectl (external tool) is
   mandatory equipment: run `lodectl check` and deal with every
   finding - fixed, refuted on record, or a named tool-limit
   follow-up; install it, with developer approval, when the
   binary is missing. The developer gates the dispositions at
   review.

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
|-- adr/                 # ADR-<YYYY-MM-DD>-<seq>.md files
|-- tasks/               # TASKLIST-ADR-<YYYY-MM-DD>-<seq>.md files
|-- plan/                # PLAN-*.md and BL-*.md
|-- architecture/        # system.md + <module>.md
\-- tmp/                 # scratch; folders per ADR/Plan; git-ignored
```

`practices.md` has four sections: necessary and opt-in tooling;
first setup; running; testing.
Practices that bind the agent carry a short order twin in the
repo AGENTS.md (`## Project specific`); explanations, procedures
and options stay here (SKILL.md to Reference.md pattern: orders
bind, the practice entry carries the why). Only binding
practices get a twin; a practice changes only together with its
order twin, in one commit.

Rules for every file: one topic per file; under 250 lines; link to
code by path plus symbol name (`path/file.ext` + `symbol` - never a
line number: lines rot, symbols are the stable anchor); link between
files; current state only
(changelog goes to `tmp/`); all diagrams valid mermaid; every
`architecture/` file carries one.

If `lode/` does not exist, ask before creating it. Add `lode/tmp/`
to `.gitignore`.

## Cadence
One cycle = one development cycle (ADR -> Test -> Code). The lode is
written at two moments:

1. **Decision** - the ADR exists before the code it justifies.
   ADR-first is the rule, not the exception.
2. **Acceptance** - when the developer accepts the work, update every
   affected lode file before the next request, and the AGENTS.md
   order twin of any changed practice (same commit).

Not per step, not per commit.

## Exploration lane
Work may live in `lode/tmp/<topic>/` with no ADR and no gates. It
graduates to a Proposed ADR when it becomes real. This protects
research-grade and spike work from ceremony it is not ready for.

## ADR
An ADR is a permanent model of one decision - the input for the
executable specification (the test). Write it as a specification:
applying its logic verbatim produces the test.

### Octet slots
An ADR has eight slots: a Status field followed by seven H2
sections. The document title carries the decision name; the slots
below follow in this exact order.
1. **Status** - Proposed / Accepted / Superseded.
2. **What** - feature or fix, including the actor pain or context
   that motivates it. The old Who slot folds here.
3. **When** - Now / Backlog.
4. **Model** - the mermaid model, directly before Specification.
5. **Specification** - the whole description of the feature, written
   as an executable specification. Touched areas belong here; the
   old Where slot folds here.
6. **Verification** - a sibling H2 section directly after
   Specification: testable assertions (given X, when Y, then Z).
   The ADR->test derivation must be mechanical.
7. **Pick** - technologies to use. The agent proposes a researched
   list with reasoning; the developer picks and owns the reason.
   When the wildcard trigger fires, the proposal list carries
   exactly one marked least-obvious option, reasoned like any
   other (mechanism: lodestack-edit).
8. **Drop** - the rest of the proposed list. The developer owns the
   rejection reason for each, even when the agent writes it down.

Do not use Who or Where headings in new ADRs. Their content is not
lost: Who/context belongs in What, and Where/touched areas belongs
in Specification.

### What-if analysis
For decisions under deep uncertainty: explore 4 to 6 branches
(best, likely, worst, wildcard, contrarian, second-order). Per
branch: what must be true, what it costs and buys, the early
signal that it is happening. The branch table is the artifact;
it lives in the ADR or `lode/tmp/`.

### Rules
- Do not edit an Accepted ADR. Exceptions: a technology version bump
  updates the version line, and a repository-wide contract migration
  may move existing content into new slots without rewriting the
  decision substance.
- A Proposed ADR may iterate model and description; the topic stays.
- Every ADR carries a valid mermaid diagram (presence and syntax,
  gated by `lodectl check`) - it is the model the
  Verification section and the test derive from. The diagram
  lives in its own `## Model` section directly before the
  Specification, never embedded mid-prose.
- Superseding is the default way to change a decision. Never mutate
  history.
- Link the relevant technology documentation at the version in use.
- Name: `ADR-<YYYY-MM-DD>-<seq>.md`; `<seq>` is a zero-padded number
  per day (`ADR-2026-11-15-001.md`).
- Work steps live in `lode/tasks/TASKLIST-ADR-<YYYY-MM-DD>-<seq>.md`.
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

## Language
- English: ASD-STE100 Simplified Technical English - one word one
  meaning, short sentences, active voice, present tense, no idioms.
- Other languages: STE-100 in spirit.
- Applies to lode files, ADRs, summaries and commit messages.

## Commands (natural language)
- "Set up lode/" -> run `lodectl init`
  (gitlab.com/r3xxar/lodectl); if the binary is missing, install it
  (`go install gitlab.com/r3xxar/lodectl@latest`) with developer
  approval - the Structure section above is the fallback only
  until the install lands
- "What is open in the backlog?" -> run `lodectl backlog`
  (gitlab.com/r3xxar/lodectl); install first when missing, as above
- "Create ADR for X" -> the ADR spec above
- "Check lode" -> run `lodectl check`
  (gitlab.com/r3xxar/lodectl) - it gates the lode structure and
  hygiene suite, incl. mermaid-missing and mermaid-syntax-error among
  the other checks. Mandatory in repos with `lode/`: deal with
  every finding in the same cycle, regardless of ADR status -
  fixed, refuted on record, or a named tool-limit follow-up; a
  missing binary means install first, and a finding is never
  silenced (the LODE gate in lodestack-edit VERIFY.f)
- "How do I use lodectl?" -> `lodectl help` or
  `lodectl <command> --help`; full reference page: `lodectl man`
  (search it: `lodectl man | grep <topic>`); finding explanations:
  `lodectl recipes`
- "Run OSMM assessment" -> dated pass table into `lode/osmm.md`
- "Handover" -> write `lode/tmp/handover-<date>.md`

## Sources
Constitution: `constitution/LodeStack.md` at `753997cb`.
Context and mappings: [Reference.md](Reference.md).
