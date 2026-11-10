---
name: "test-standards"
description: "Load when writing, reviewing, or designing tests, or when deciding what to test and at which level. How to write tests: system/integration level by default, executable specifications as contracts, few E2E and unit tests only where integration does not fit, one test file per specification, adversarial safety-critical mindset. The change cadence stays with code-edit; the ask-the-developer rule is stated here."
version: "1.0.1"
author: "Damian Zaręba"
license: "MIT"
tags:
  - testing
  - standards
  - safety
  - quality
---

# Skill: test-standards

## Purpose
How to write tests — what good tests look like. The test-design layer next to the stack:

- **lode-programming** owns memory — why it was decided.
- **code-edit** owns the change process — how a change moves, and the rule to ask the developer before skipping, deferring to the backlog, or proceeding.
- **code-standards** owns the code itself — what good code looks like, and the test-first cadence.
- **test-standards** owns the tests — what good tests look like.

## When to Load
- Writing, reviewing, or designing tests.
- Deciding what to test and at which level.
- Writing executable specifications or contract tests.
- Reviewing a test suite for duplication or obvious-path padding.

## Test levels, in default order
1. **System integration / system architecture level, for the most part.** Test the system as the user experiences it: components wired together, real data flow, real failure modes.
2. **Executable specifications / contracts.** Execute each logical interface's contract (code-standards spirit rule 9) as a test. The contract is the specification; the test proves it.
3. **Few E2E and few unit tests** — only where the system/integration level would not fit without substantial modifications to the system architecture. Before skipping a level, moving a test to the backlog, or proceeding right away, **ask the developer** — that rule is this skill's own. **code-edit** INTENT still requires acceptance evidence before any change. Link, do not restate.

## Duplication and focus
- Keep unique tests only. Do not write many variations of the same thing.
- **One test file = one specification.** Split it internally into logical boundaries (for example, the ways a user can log in), one test per way — no duplicated variations across files.
- Do not test obvious paths in isolation; cover them in combination at the integration level.

## Adversarial, safety-critical mindset
Put on the hat of a senior system test engineer from safety-critical domains (automotive, aviation, military — the ISO 26262 / IEC 61508 / DO-178 mindset) for the whole test-writing session. Always ask:
- **How can this code break?** Probe boundary values, partial failure, timeouts, ordering, concurrency, resource exhaustion.
- **If this path breaks, what else is impacted?** Follow the impact outward, like the code-edit IMPACT stage.

## Boundaries with the neighbors
- **code-standards** owns what good code looks like and the test-first cadence. Link, do not restate.
- **code-edit** owns the change process (INTENT, LOCATE, IMPACT, EDIT, PROPAGATE). The ask-the-developer rule for skipping or deferring tests is this skill's own, stated above. Link, do not restate.
- **firmware-development** owns the hardware test environments (host → emulator → on-target → HIL) in its `reference/testing.md`. This skill owns test design; that skill owns the environments. Link, do not copy.

## Deployment
- Canonical text: this repo (`.agents/skills/test-standards/`). The Mistral skill-registry entry and the Devin knowledge note carry the same skill ID (UUID) and version. Keep all three in sync on every change and every version bump.
- Per project with a `lode/`: record the chosen test levels per feature in `lode/testing.md`.
