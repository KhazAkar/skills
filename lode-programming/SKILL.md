# Skill: lode-programming

# Skill: lode-programming

## Purpose
Implement **Lode Coding**: durable project memory in `lode/` folder.
AI maintains the lode as a byproduct of your work.

**Core Principle**: You own decisions. AI owns memory.

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
- **Link between files**: `[ADR-001](../decisions/adr-001.md)`
- **Current state only** (not changelog)
- **Concrete examples** > abstract descriptions

## AMDD Inspiration
Agile Model Driven Development (AMDD) is a lightweight approach to software modeling. It emphasizes creating models that are *just barely good enough*, *just in time*. In our workflow, this means capturing decisions and patterns as they emerge during development, not in advance. TDD (Test-Driven Development) is a key part of this approach.

## Commands (Natural Language)
- *"What does the lode say about [topic]?"* → Search lode files
- *"Create ADR for [decision]"* → Use ADR template
- *"Update lode-map"* → Regenerate index
- *"Review lode"* → Check for outdated info

## Philosophy
The lode is your external cognitive partner. It remembers so you can focus on creating.

Base directory for this skill: /home/user/skills/lode-programming
Relative paths in this skill are relative to this base directory.
This skill's root SKILL.md file is already loaded in this block; do not read it again.
Use read_file only for needed support files under this base directory.
Note: this is the skill content.