---
name: "lode-programming"
description: "Use this skill for programming tasks to maintain durable project memory using Lode Coding methodology. Load when starting projects, explaining code, making architectural decisions, or when you want to preserve knowledge across sessions."
version: "1.2.1"
author: "Damian Zaręba"
license: "MIT"
tags:
  - programming
  - documentation
  - lode
  - project-memory
  - knowledge-management
---

# Skill: lode-programming

## Purpose
Implement **Lode Coding**: durable project memory in `lode/` folder.
AI maintains the lode as a byproduct of your work.

**Core Principles**:
- **You own decisions. AI owns memory.**
- **Lode is a byproduct, not a documentation job.** It grows from planning, correcting and reviewing with the agent — never written upfront as an inventory.
- **Code is the source of truth.** If the lode contradicts the code, summarize the gap and ask before fixing the lode.
- **Summarize, don't dump.** Relay lode contents in your own words; quote a file verbatim only when asked for it by path.
- **YAGNI**: Do not build features, abstractions, or config knobs that are not needed now.
- **Maximize human maintainability**: Clear naming, small files/functions, obvious structure over cleverness. A human must be able to pick up the code without the AI.

## When to Load
- Starting any programming project
- Making architectural decisions
- Onboarding to existing codebase
- When you notice repeated explanations

## Mandatory Structure
```
lode/
├── summary.md          # Project purpose & architecture
├── terminology.md      # Domain terms & acronyms
├── practices.md        # Coding standards & patterns
├── lode-map.md         # Index of all lode files
├── decisions/          # Architecture Decision Records
│   └── [number]-[name].md
├── plans/              # Roadmaps and TODOs (create when needed)
└── tmp/                # Git-ignored session scraps and handovers
```
If `lode/` does not exist, ask the user before creating it. Add `lode/tmp/` to
`.gitignore`.

Pre-filled templates for every standard lode file live in `templates/` — copy
the matching one instead of writing from a blank page (`templates/summary.md`
→ `lode/summary.md`, `templates/terminology.md` → `lode/terminology.md`,
`templates/decisions/adr-template.md` → new ADRs).

## Session Start
1. Read `lode-map.md`, `terminology.md`, `summary.md`.
2. Check `lode-map.md` *before* exploring the codebase — it is the index.
3. Briefly show domain knowledge before attending to the first request.

## Cadence
A **cycle** is one user request or feature: discussion → decision →
implementation → acceptance. Main lode files are written at two moments:

1. **When a decision is taken** — create the ADR before the code it justifies.
   Iterating on that ADR while the cycle is in flight is normal (the
   architecture part of AMDD).
2. **At acceptance** ("looks good", "ship it", the request is done) —
   immediately update every affected lode file so it reflects the current
   state, before moving to the next request.

Not per step, not per commit. Outside the cadence:

- `lode/tmp/` and anything the user explicitly asks for (a handover, "write
  this down now") — written when requested.
- Operational records a specialized skill must capture as they happen (a
  hardware inventory, a dump checksum) — jotted immediately, tidied at
  acceptance.

Specialized skills (e.g. firmware) add their own file names but follow this
cadence; they do not define their own.

## Workflow
1. **Before coding**: Check `lode-map.md` for relevant files
2. **During design**: Chat first, code second; implement only after a clear decision
3. **After decisions**: Immediately create/update ADR
4. **At acceptance**: Update lode to reflect current state
5. **After big changes**: Check the lode structure still mirrors the codebase; refactor it if not

## What Goes Where
- Needed in a future session → main lode file (permanent learning)
- "How I solved today's problem" → chat, or `lode/tmp/` if it must survive the session
- Changelog-style notes → `lode/tmp/`, never a main lode file
- **Handover** (on request): write `lode/tmp/handover-<date>.md` with task state,
  decisions, approaches tried, blockers, next steps

## ADR Template
```markdown
# [Number]: [Decision Title]

**Status**: ✅ Accepted | ❌ Superseded by [ADR-XXX] | 🚧 Proposed

**Context**: [The problem/forces at play]

**Decision**: [What we decided]

**Consequences**:
- ✅ [Positive impact]
- ❌ [Negative tradeoff]

**Alternatives Considered**:
- [Option A]: Why rejected
- [Option B]: Why rejected
```

## Subsystems (Optional)
For complex projects, create domain folders:
```
lode/
├── auth/
│   ├── summary.md
│   └── decisions/
└── api/
    ├── summary.md
    └── patterns.md
```

## Best Practices
- **One topic per file**
- **<250 lines per file** (split if larger)
- **Link to code**: `Implementation: src/auth/service.go:42`
- **Link between files**: `[ADR-001](../decisions/adr-001.md)`
- **Current state only** (not changelog)
- **Concrete examples** > abstract descriptions
- **Diagrams are Mermaid only**

## AMDD Inspiration
Agile Model Driven Development (AMDD) is a lightweight approach to software modeling. It emphasizes creating models that are *just barely good enough*, *just in time*. In our workflow, this means capturing decisions and patterns as they emerge during development, not in advance. red/green/blue (refactor) and **YAGNI** (You Aren't Gonna Need It) are key parts of this approach.

## Commands (Natural Language)
- *"What does the lode say about [topic]?"* → Search lode files
- *"Create ADR for [decision]"* → Use ADR template
- *"Update lode-map"* → Regenerate index
- *"Review lode"* → Check for outdated info
- *"Handover"* → Write `lode/tmp/handover-<date>.md`

## Philosophy
The lode is your external cognitive partner. It remembers so you can focus on creating.
