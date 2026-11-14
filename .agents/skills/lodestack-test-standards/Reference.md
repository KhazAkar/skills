# lodestack-test-standards - Reference

Interpretations and context for the Test Standards contract.
Consumed during assembly: `constitution/LodeStack.md` @ `573391b`,
the 2026-11-14 assembly digest (sections 5-7), v1 `test-standards`
(rules ported nearly whole per the per-rule review).

## Cognitive ownership in tests

The developer owns the specification; the test makes it executable.
That is why the derivation is mechanical - Given/When/Then from the
ADR's Verification block - and why "one test = one rule" matters:
when a test fails, the failure names the broken *decision*, not just
the broken code. Cognitive ownership survives the failure report.

The ask-the-developer rule exists because test levels are judgment
calls: which contract needs E2E proof is not decidable by the agent.

## The AMDD mapping slice

Shared checklist:
[../shared/amdd-mapping.md](../shared/amdd-mapping.md).
In the ADR-Test-Code cycle this contract owns the middle:

- **ADR** (the model) ends in a Verification block - testable
  assertions written as Given/When/Then.
- **Test** (this contract) applies them verbatim. Mechanical
  derivation is the point: a test that needed interpretation is a
  specification that needs sharpening first - push back to the ADR.
- **Code** satisfies both. A test that cannot be satisfied while
  respecting the ADR is a contradiction in the model, not a bad test.

Models are permanent: when the implementation teaches something the
ADR didn't know, the ADR iterates - never the test alone.

## Level decisions

| Level | When it fits |
|---|---|
| System/integration | Default - the contract across real collaborators |
| Unit | Isolated algorithms, parsers, transforms, paths integration can't trigger |
| E2E | Rare - contracts spanning deployed systems only |

Skipping a level = ask the developer. The record of adopted levels
lives in `lode/practices.md` so the decision is auditable.

## "One test = one rule" for standard-derived tests

When code-standards marks a rule `gate: test` (bounded behavior,
assert at boundaries, bounded allocation), the verification is one
targeted test per rule per application point - the test that
breaches the bound, feeds the bad input, exceeds the allocation.
Do not fold several rules into one integration test that fails
ambiguously; the name must identify the rule.

## Adversarial categories - usage note

The category list in SKILL.md is a checklist, not a quota: pick the
categories that fit the contract, name which were considered. A
component with no concurrency has no race tests; "considered and
rejected" is a valid outcome - record it like an ANALYZE REJECT.

## OSMM slice

Shared checklist: [../shared/osmm-checklist.md](../shared/osmm-checklist.md).
Testing feeds OSMM's test-coverage and quality dimensions; the
executable-specification chain (ADR Verification -> test -> VERIFY
TEST box) is the assessable traceability artifact.
