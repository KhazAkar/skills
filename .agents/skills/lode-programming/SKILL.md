---
name: "lode-programming"
description: "Use this skill for programming tasks to maintain durable project memory using Lode Coding methodology. Load when starting projects, explaining code, making architectural decisions, or when you want to preserve knowledge across sessions."
version: "1.1"
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
└── decisions/          # Architecture Decision Records
    └── [number]-[name].md
```

## Workflow
1. **Before coding**: Check `lode-map.md` for relevant files
2. **During design**: Chat first, code second
3. **After decisions**: Immediately create/update ADR
4. **After changes**: Update lode to reflect current state

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
- **Link between files**: `[ADR-001](templates/decisions/adr-template.md)`
- **Current state only** (not changelog)
- **Concrete examples** > abstract descriptions

## AMDD Inspiration
Agile Model Driven Development (AMDD) is a lightweight approach to software modeling. It emphasizes creating models that are *just barely good enough*, *just in time*. In our workflow, this means capturing decisions and patterns as they emerge during development, not in advance. red/green/blue (refactor) and **YAGNI** (You Aren't Gonna Need It) are key parts of this approach.

## Commands (Natural Language)
- *"What does the lode say about [topic]?"* → Search lode files
- *"Create ADR for [decision]"* → Use ADR template
- *"Update lode-map"* → Regenerate index
- *"Review lode"* → Check for outdated info

## Philosophy
The lode is your external cognitive partner. It remembers so you can focus on creating.
