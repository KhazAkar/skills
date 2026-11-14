# lodestack-edit — Reference

Context and operational detail for the Edit contract. Consumed during
assembly: `constitution/LodeStack.md` @ `74386bb`, the 2026-11-14
assembly digest (sections 3, 4, 5), and the v1 `code-edit` skill
(rules ported per the per-rule review).

## Cognitive ownership in this contract

The stack's spine — you own decisions, the agent owns work and
memory — shows up here as three mechanics:

- **ANALYZE** produces the judgment surface: the agent's verdicts
  (ACCEPT/REJECT + reasons) are artifacts the developer reviews.
  Presence of verdicts is gated, never their content.
- **The break rule** turns failed automation into a decision: the
  table of problems and options hands judgment back to the developer
  instead of letting the loop burn attempts.
- **The report + commit proposal** keeps the last word human: the
  agent proposes, the developer checks, the trailer records who
  assisted.

Delegation (pre-approved bounded scope) lives in the AGENTS template
— it is one gate decision, recorded, not an ownership leak.

## Research ordering

"Research before solutions is mandatory" operationalized:

1. the codebase itself — how the same thing is already done there
2. official documentation of the library/framework/app
3. CLI help (`--help`, `-h`) and man pages

Model memory is not a source. If sources disagree or cannot confirm,
the change waits; record the gap.

## Reuse and scope

- Reuse first: existing code in this repo, then stdlib/platform/
  framework; state what was reused and why new code was needed.
- No drive-by refactors, no abstraction with a single caller.
- No new dependency without asking — a dependency is a supply-chain
  and install-time cost; the developer gates it.
- Adjacent problems go to the backlog, not into the diff.

## VERIFY edges

- Missing gate tool (linter, typechecker, scanner, formatter):
  checkbox = `N/A`-recorded, AND the agent offers to set it up. The
  offer is a proposal; the developer decides.
- `lode/` absent: LODE = `N/A`-recorded + offer setup
  (inform-and-offer-installation, AGENTS contract).
- tree-sitter-edit fallback triggers: binary missing, grammar
  unsupported, or the edit inexpressible as a query → text-diff.
  A failed VERIFY is inner-loop iteration, not a fallback.
- SECURITY scope: defensive coding strategies (input validation,
  bounded resources, safe defaults) AND tool scanning — both, not
  either.

## Metrics (slimmed)

v1 required per-change metrics in commit bodies. v2: the post-VERIFY
summary table doubles as the commit body — one report, two uses.
Endorsed by Damian 2026-11-15.

## OSMM / AMDD slices

Shared checklists:
[../shared/osmm-checklist.md](../shared/osmm-checklist.md),
[../shared/amdd-mapping.md](../shared/amdd-mapping.md).

Edit's slice in the development cycle: REASON cites the ADR (the
model); VERIFY's TEST box runs the executable specification derived
from it; LODE closes the loop back into memory. For OSMM, the VERIFY
checkboxes are the per-change assessment surface — a repo whose
gates cannot run shows it plainly in the `N/A` records.
