---
name: "lodestack-test-standards"
description: "The LodeStack Test Standards contract - tests are executable specifications, not afterthoughts. System/integration level by default, sparse unit and E2E tests, one test file per specification, one test per rule for standard-derived tests, adversarial safety-critical mindset (boundaries, partial failure, timeouts, ordering, concurrency, exhaustion, external impact). Derived from ADR Verification blocks per AMDD. Load when writing, reviewing or designing tests, or deciding what to test at which level."
version: "1.0.1"
author: "Damian Zaręba"
license: "MIT"
constitution: "74386bb298143f6a43909b2e3c594658d6c3ec0b"
tags:
  - lodestack
  - test-standards
  - executable-specification
  - safety-critical
  - amdd
---

# Skill: lodestack-test-standards

## Purpose
The LodeStack Test Standards contract: what good tests are and where
they live in the cycle. Tests are the executable half of cognitive
ownership - the developer's judgment, made runnable. The ADR carries
intent; the test makes it checkable; the code satisfies both.

Sibling contracts: **lodestack-memory** owns the ADR whose
Verification block a test derives from; **lodestack-edit** runs
VERIFY's TEST box; **lodestack-code-standards** owns the rules that
`gate: test` points at. Link, do not restate.

## The derivation

- **A test is an executable specification.** Each derives from the
  ADR's Verification block - Given/When/Then applied verbatim. If a
  test cannot trace to a specification, it is either an ADR gap or
  test noise; find out which before writing it.
- **Standard-derived tests: one test = one rule.** A `gate: test`
  rule from code-standards gets exactly one targeted test per
  application point - bounded-loop breach, assertion on bad input.
  No shotgun parametrization that hides which rule failed.
- **Tests change with the code they specify.** Same Edit cycle, same
  commit - a specification update is part of the change, not a
  follow-up task.

## Levels

- **System/integration level by default.** Tests exercise the
  contract across real boundaries - the code plus its actual
  collaborators. This is where specifications live.
- **Unit tests are sporadic** - where integration does not fit:
  isolated algorithms, parsers, pure transforms, hard-to-trigger
  paths. Ask the developer before adding or skipping a level.
- **E2E tests are rare** - only where the contract itself spans a
  deployed system. Most "E2E" wishes are integration tests.
- Record adopted levels in `lode/practices.md`; skipping or
  deferring a level is an ask-the-developer decision, not a default.

## Writing rules

- **One test file per specification.** The file mirrors the ADR or
  contract it executes; split when the specification splits.
- **Test the contract, not the implementation.** No test asserts
  internals that a refactor may legally change.
- **No duplicated variations.** A table of near-identical cases is
  one parameterized test or noise - pick deliberately.
- **Don't test the obvious.** Obvious paths proven by construction
  (the happy path every caller already exercises) earn no test;
  the adversarial cases below do.
- **Names state the rule.** `test_bounded_loop_rejects_overflow`
  beats `test_loop_3` - a failure names the broken specification.

## Adversarial mindset (safety-critical default)

Ask of every contract: how can this break, and what does the
failure do to everything else? Cover the categories that fit:

- **Boundaries** - empty/full, min/max, one-past-the-limit
- **Partial failure** - half-completed operations, mid-state aborts
- **Timeouts** - the slow collaborator, the never-answering peer
- **Ordering** - out-of-order delivery, replay, staleness
- **Concurrency** - races, interleavings, contention on shared state
- **Exhaustion** - memory, fds, queue depth, counter wraparound
- **External impact** - what a failure writes, sends or leaves
  behind outside the component

A test suite that only proves the happy path proves the code ran
once, not that it holds.

## Sources
Constitution: `constitution/LodeStack.md` at `74386bb`.
Context: [Reference.md](Reference.md). v1 `test-standards` ported
per the per-rule review; additions: one-test-per-rule, ADR
Verification-block derivation.
