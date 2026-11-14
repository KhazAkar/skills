---
name: "lodestack-code-standards"
description: "The LodeStack Code Standards contract - one universal rule set distilled from MISRA C:2025, MISRA C++:2023, NASA JPL Power of Ten, TigerStyle, Zen of Python, YAGNI and Grug-brain, annotated by gate (test / analyzer / review) so hard rules become executable checks. Junior-maintainable code is the first principle. Per-language additions and deviations (ADR receipts) live in Reference.md. Load when writing or reviewing code, adopting a linter or analyzer, or authoring lode/practices.md."
version: "1.0.2"
author: "Damian Zaręba"
license: "MIT"
constitution: "573391b421fd31c4d4be1f0f0e540d51bc1a08fb"
tags:
  - lodestack
  - code-standards
  - misra
  - tigerstyle
  - safety-critical
---

# Skill: lodestack-code-standards

## Purpose
The LodeStack Code Standards contract: what good code looks like,
distilled to one universal set. Cognitive ownership expressed as
code quality - **code a human of junior level can maintain without
AI assistance**. Maintainable, not merely readable: a junior can
change it safely because units are small, limits are explicit,
assertions catch misuse, and the guardrails are in the code itself.

Sibling contracts: **lodestack-memory** owns the ADRs deviations
record; **lodestack-edit** runs the VERIFY gates these rules feed;
**lodestack-test-standards** owns how the `test`-gated rules get
verified. Link, do not restate.

## First principle
Verbatim from the constitution:

> Code with quality equal to being maintainable by a human, of
> junior level skill level, without AI assistance.

Values in order: safety (correctness, bounded behavior), performance
(including the developer's performance), experience (clarity,
maintainability).

## The universal rules

Every rule carries a gate annotation - how it becomes a check.
`test` = a targeted test executes it; `analyzer` = a linter,
typechecker or static analyzer enforces it; `review` = a judgment
artifact (ADR field, ANALYZE verdict, review note) is the check -
presence gated, content human.

### Boundaries and failures
- **Bounded behavior** - every loop, queue, retry, timeout,
  concurrency pool and handler has an explicit limit. Breach
  asserts and returns an error, never hangs. `gate: test`
- **Check every return value** - a deliberately ignored result is
  marked `(void)` / `_ =` / equivalent. `gate: analyzer`
- **Assert at boundaries** - function and module edges assert
  pre/post-conditions; assertions are side-effect-free and cover
  the negative space too. Fail loud at development time.
  `gate: review` (presence) + `test`
- **Initialize before use** - no read of an uninitialized value;
  no dead or unreachable code. `gate: analyzer`
- **No implicit type surprises** - no narrowing, signed/unsigned or
  essential-type conversion without an explicit cast and a reason.
  `gate: analyzer`

### Shape and size
- **Small units** - functions around ~60 lines or less; smallest
  possible scope; declare near use. `gate: analyzer`
- **One word, one meaning** - clear nouns and verbs; no
  abbreviations that a junior must guess; most-significant word
  first in names; no shadowing or identifier reuse.
  `gate: review`
- **Boring over clever** - the obvious construct wins over the
  elegant one; cleverness that needs a comment to survive is
  technical debt at creation. `gate: review`
- **YAGNI** - build what the ADR needs now; no speculative
  features, abstractions or config knobs. `gate: review`

### Control flow and memory (native-scope)
Rules that apply where the language has the concept (C, C++, Rust,
embedded; per-language interpretation in Reference.md):
- **No recursion** - the call graph is acyclic; verify by stack
  analysis or bounded-iteration rewrite. `gate: analyzer`
- **No hidden control flow** - no goto/setjmp/longjmp, no
  exceptions-as-normal-flow across module boundaries.
  `gate: analyzer`
- **Bounded allocation** - native cores allocate at init, not
  per-operation; where the domain forbids it, the deviation is an
  ADR. `gate: test` + `analyzer`
- **Minimal pointer indirection** - at most one level; no function
  pointers without an ADR justification (dispatch tables are the
  named exception). `gate: analyzer` + `review`
- **Fixed-width types** - `uint32_t` over `int`-guessing where
  width matters. `gate: analyzer`
- **Preprocessor discipline** - includes, guards and simple macros
  only; no conditional compilation that hides code from review.
  `gate: review`

### Process
- **Zero warnings** - pedantic warnings on, count is zero, the
  static analyzer is in the gate; rewrite, do not silence.
  `gate: analyzer`
- **Sketch performance at design time** - the back-of-envelope
  estimate lives in the ADR before the code does. `gate: review`
  (ADR field presence)
- **Dependencies are decisions** - a new dependency is gated by
  the developer (supply-chain + install cost). `gate: review`
- **Minimal logical interface** - fewest concepts exposed; fault
  model stated; control flow up, data down; wrap non-deterministic
  sources behind an interface. `gate: review`
- **Errors never pass silently** - unless explicitly silenced with
  a recorded reason (Zen of Python, applied universally).
  `gate: analyzer` + `review`

## Deviations and additions
- A deviation from a universal rule is an **ADR opt-out receipt**:
  which rule, why, scope. Absent receipt = rule applies.
- Language- or domain-specific practices are **verbatim additions**,
  not rewrites of the universal set - they live in
  [Reference.md](Reference.md) interpretation entries.
- The unified set is one tier. There is no spirit/strict split
  (assembly decision 2026-11-13).

## Sources and digests
Distilled rule digests per source in `refs/`: `power-of-ten.md`,
`tigerstyle.md` (ported from v1), `zen-of-python.md`, `yagni.md`,
`grug-brain.md`, and the MISRA stubs `misra-c.md` / `misra-cpp.md`
- pending distillation from the bought copies; paraphrase-only,
never verbatim rule text (copyright).

Constitution: `constitution/LodeStack.md` at `573391b`.
Context: [Reference.md](Reference.md).
