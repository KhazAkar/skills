# lodestack-memory - Reference

Context, interpretations and mappings for the Memory contract.
Consumed during assembly: `constitution/LodeStack.md` @ `573391b`,
the 2026-11-14 assembly digest (sections 2, 6, 7, 8), and the v1
`lode-programming` skill (ported folklore per the per-rule review).

## Source of truth model

Three layers, each truthful at its own level:

| Layer | Truth | Question it answers |
|---|---|---|
| Code | Implementation | What does the system do? |
| ADR + Test + Code | System/integration package | What was decided, proven, built? |
| + Plan | Feature level | Where is the work going? |

If the lode contradicts the code, the code wins at its layer -
summarize the gap and ask before fixing the lode.

## ADR-first

ADR-first is real, not aspirational. The ADR is the model: written at
the decision, before the code it justifies. Iterating on a Proposed
ADR while its cycle is in flight is normal - that is the architecture
part of AMDD. The lode (status flip, linked artifacts, updated
lode-map) catches up at acceptance.

## OSMM mapping

The shared, canonical checklist lives at
[../shared/osmm-checklist.md](../shared/osmm-checklist.md) - one
checklist, not per-skill copies.

Memory's slice: the OSMM dimensions are satisfied BY the lode
composition. `summary.md` covers product identification,
`practices.md` covers setup/running/testing, `lode/` itself covers
documentation, git history covers versioning. The dated pass table
at `lode/osmm.md` is the presence-checkable artifact; the developer
judges its content.

## AMDD mapping

The shared mapping lives at
[../shared/amdd-mapping.md](../shared/amdd-mapping.md).

Memory's slice: ADR = the model (diagram/architecture), test = the
written executable specification derived from the ADR's Verification
block, code = the implementation satisfying the architecture. The
LodeStack distinction: **models are permanent** - an ADR is iterated
through its own implementation cycle and kept as decision memory
(Proposed -> Accepted -> Superseded), never thrown away after coding.

## Gates doctrine

The gate rules ship in [AGENTS.template.md](AGENTS.template.md):
the developer is the gate; gate the presence of judgment artifacts,
never their content; judge every option including the recommended
one; delegation is a scope-bound pre-approval recorded as one gate
decision.

## v1 -> v2 lode schema migration

For projects on the old (`lode-programming`) layout - pure renames
plus a few creates:

1. `lode/decisions/` -> `lode/adr/`; rename each `[number]-[name].md`
   to `ADR-<YYYY-MM-DD>-<seq>.md` (date = its git creation date).
2. `lode/plans/` -> `lode/plan/`; rename files to
   `PLAN-<YYYY-MM-DD>-<seq>.md`.
3. Create `lode/quirks-and-gotchas/README.md` (empty index is fine),
   `lode/architecture/` with `system.md`, and `lode/osmm.md` on the
   first pass.
4. Update `lode/lode-map.md` links; keep `lode/tmp/` as is.
5. Old AGENTS.md stage names map: INTENT = REASON, IMPACT = ANALYZE,
   PROPAGATE absorbed into VERIFY.

Old repos may stay on v1 schema until touched; migrate a lode when
the next ADR in it lands.
