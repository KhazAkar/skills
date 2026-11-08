---
name: "code-standards"
description: "Load when writing, reviewing, or designing code alongside code-edit, when creating or updating lode/practices.md, or when a repo adopts a standards tier. What good code looks like: TigerStyle and NASA Power of Ten distilled into a spirit tier (every repo) and a strict tier (unattended native cores, adopted by ADR)."
version: "1.1.0"
author: "Damian Zaręba"
license: "GPL-3.0-or-later"
tags:
  - programming
  - standards
  - safety
  - tigerstyle
  - power-of-ten
---

# Skill: code-standards

## Purpose
What good code looks like. The standards layer of the stack:

- **lode-programming** owns memory — why it was decided.
- **code-edit** owns the change process — how a change moves.
- **code-standards** owns the code itself — what good looks like.

Sources: TigerStyle (https://tigerstyle.dev) and NASA JPL Power of Ten
(G. J. Holzmann, https://spinroot.com/gerard/pdf/P10.pdf). This text
distills both; the distilled rules win over the sources. Paraphrased
rationale digests live in [reference/tigerstyle.md](reference/tigerstyle.md)
and [reference/power-of-ten.md](reference/power-of-ten.md): consult
them for the reasoning behind a rule during review or ADR work, and
the sources for original wording. Where a rule is C- or Zig-specific,
it names its scope or moves to the strict tier.

## Values, in order
1. **Safety** — correctness is necessary but not sufficient. Verify
   the program while it runs, defend in depth, fail loud. Never limp.
2. **Performance** — solve it at design time, when you cannot profile.
   A back-of-envelope sketch beats a retrofit.
3. **Experience** — optimize for those who read and run the code many
   times, not for the one who writes it once.

## Development principles (always)
Judgment-level, moved from the lode Code Discipline on 2026-11-07, so
the lode keeps pointers only:
1. **YAGNI.** Build what is needed now. No speculative features,
   abstractions, or config knobs.
2. **Test first.** Chat and design first (AMDD). Once the architecture
   skeleton exists, a failing test drives the implementation, red to
   green to blue. The failing test is the code-edit INTENT evidence.
3. **Junior-readable.** Clear naming, small files and functions,
   obvious structure over cleverness. A human of junior level
   experience must be able to pick up the code without the AI.

## Tiers
- **Spirit tier** — every repo, every language. No adoption needed.
- **Strict tier** — native code that runs unattended: firmware,
  device-side code, hot loops, inference cores. A repo adopts it by
  ADR. The adopted tier is recorded in `lode/practices.md`.

## Spirit rules (every repo)
1. **Explicit limits on everything.** Bound queues, retries, timeouts,
   concurrency. Prefer scheduled work at fixed intervals over reacting
   to stimuli; where the domain is event-driven (UI, servers,
   interrupts), bound the handler instead: bounded queue, bounded work
   per event, no re-entrancy.
2. **Check returns.** Check every return value you can act on. Mark a
   deliberate ignore explicitly: `(void)`, `_ =`, or a comment that
   says why. (P10 R7)
3. **Assert at boundaries.** Assertions are side-effect-free and cover
   the positive and negative space: what you expect and what must
   never happen. On breach, fail loud or return an error. (P10 R5)
4. **Small units.** A function fits one sheet of paper, about 60
   lines. Data lives at the smallest possible scope. Define variables
   near their use. (P10 R4, R6)
5. **Nouns and verbs.** A name says what a thing is or does. Order
   words most-significant first. Do not abbreviate. One word, one
   meaning — same rule as the STE language rule.
6. **Zero warnings.** Compile at the most pedantic setting with zero
   warnings. Run at least one static analyzer in CI. If a tool gets
   confused, rewrite the code; do not silence the tool. (P10 R10)
7. **Sketch performance at design time.** For any hot path, record a
   back-of-envelope estimate in the ADR: network, storage, memory,
   compute; bandwidth and latency. Roughly right beats precisely late.
8. **Dependencies are decisions.** A new dependency is a supply-chain
   and install-time cost. No new one without asking — the code-edit
   rule; the rationale lives here.
9. **Logical interfaces.** Minimal surface. Defined fault model.
   Control flow up, data flow down. Wrap non-deterministic interfaces
   with deterministic ones.

## Strict rules (on top of spirit, adopted by ADR)
1. No recursion. The function call graph is acyclic. (P10 R1)
2. Every loop has a static upper bound. When the bound is exceeded, an
   assertion fails and the function returns an error. (P10 R2)
3. No heap allocation after initialization. (P10 R3)
4. No `goto`, `setjmp`, `longjmp`. (P10 R1)
5. Fixed-width types (`u32`), no architecture-specific types
   (`usize`). (TigerStyle)
6. At most one level of pointer dereference. No function pointers.
   (C and C++; P10 R9)
7. The preprocessor carries only header includes and simple macros. No
   token pasting, no variadic macros, no recursive macros. (C and C++;
   P10 R8)
8. At least two assertions per function, each with a recovery action.
   (P10 R5)

## Boundaries with the neighbors
- The YAGNI principle bounds scope. The rules bound quality inside
  the scope. Do the hard thing at the ADR, never as a drive-by
  refactor inside a diff — code-edit already forbids those.
- TDD and assertions are complements. Tests catch defects at dev time.
  Assertions guard invariants at runtime and multiply fuzzing.
- Project dials — cache-line alignment, batching, zero-copy, static
  pools — live in the repo's `lode/practices.md`. This file stays
  universal.

## When to Load
- Writing or reviewing code, alongside code-edit.
- Designing an interface, or an ADR with performance weight.
- Creating or updating a repo's `lode/practices.md`.
- Adopting the strict tier for a repo.

## Deployment
Same pipeline as code-edit. Canonical text: this repo. Per repo:
1. An ADR records the adopted tier. Spirit-only repos record it too,
   in one line.
2. The tier and the project dials go into `lode/practices.md`.
3. CI gates: zero warnings, at least one static analyzer, in repos
   with buildable code. Docs-only repos (this one) gate on file
   verification and version sync instead, per AGENTS.md.
Advisory-only adoption is rejected: rules without gates drift.
