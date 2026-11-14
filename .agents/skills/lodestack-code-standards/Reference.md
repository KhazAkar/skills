# lodestack-code-standards — Reference

Interpretations, mappings and per-language additions for the Code
Standards contract. Consumed during assembly:
`constitution/LodeStack.md` @ `74386bb`, the 2026-11-14 assembly
digest (sections 5, 6), v1 `code-standards` (rules ported per the
per-rule review).

## Junior-maintainable, not junior-readable

The first principle is the stack's spine applied to code: cognitive
ownership requires the human to be able to *change* the code, not
just comprehend it. The practical difference:

| Readable | Maintainable |
|---|---|
| Names explain intent | Invariants are asserted, not implied |
| Comments describe flow | Bounds are explicit constants, not habits |
| Style is consistent | A change's blast radius is visible in the ANALYZE table |
| Reviewer follows the logic | Tests fail loudly when the logic is violated |

Every universal rule exists to make modification safe: small units
bound the blast radius, assertions are the guardrails, zero warnings
keep the noise floor at zero so real problems are visible.

## Gate annotations

`gate: test` — the rule is behavioral; a targeted test executes it
(bounded-loop breach, assert-on-bad-input). Lodestack-test-standards
owns how that test is written — for standard-derived tests, one
test = one rule.

`gate: analyzer` — the rule is a static property; a linter,
typechecker or static analyzer enforces it (unchecked returns,
implicit conversions, zero warnings). No unit test can check "no
implicit widening" — the gate is the analyzer config, recorded in
`lode/practices.md`.

`gate: review` — the rule needs judgment; the check is the presence
of an artifact (ADR field, ANALYZE verdict, deviation receipt).
Never the content — the human judges content.

## Per-language / per-domain interpretation entries

Additions are verbatim — they extend, never rewrite, the universal
set. Entry format: scope, the addition, source, gate.

- **Rust** — `unsafe` blocks are ADR-visible; each carries a SAFETY
  comment stating the upheld invariant. `gate: review`
- **Python** — type annotations at public interfaces make the
  TYPECHECK gate real; `Any` is a deviation. `gate: analyzer`
- **Go** — `err != nil` is the check-every-return rule's idiom;
  `context.Context` cancellation is the bounded-behavior rule's.
  `gate: analyzer`
- **C/C++** — the native-scope control-flow/memory block applies in
  full; MISRA alignment work rides the `refs/misra-*.md` digests
  once distilled. `gate: analyzer`
- **QML/UI** — bounded behavior means bound the handler: no
  unbounded work in signal handlers. `gate: review`

## Deviation receipts

An ADR opt-out names the rule, the scope, and the reason — e.g.
"recursion allowed in `parser/` for the grammar AST; call depth
bounded by input-size limit in ADR-2026-11-15-001". The receipt is
the artifact whose presence is gated.

## Where rules meet VERIFY

| VERIFY box | Rules it exercises |
|---|---|
| LINT | check returns, no implicit conversions, zero warnings, small units |
| TYPECHECK | fixed-width types, no implicit type surprises, Python annotations |
| SECURITY | bounded behavior, errors never pass silently, minimal interface |
| TEST | bounded behavior, assert at boundaries, bounded allocation |
| FORMAT | (style is the linter's/formatters job — not a rule here) |
| LODE | deviation receipts, performance sketches, dependency ADRs present |

## MISRA status

The bought MISRA C:2025 and C++:2023 copies are pending
distillation into `refs/misra-c.md` / `refs/misra-cpp.md`
(paraphrase-only). Until then, MISRA-derived expectations are the
native-scope rules above — most are Power-of-Ten-aligned and
consistent with MISRA's direction, but they are NOT yet verified
against the bought texts.

## OSMM slice

Shared checklist: [../shared/osmm-checklist.md](../shared/osmm-checklist.md).
Code standards feed OSMM product quality: `lode/practices.md`
records which analyzer configs run the `gate: analyzer` rules —
that record is the assessable artifact.
