# AMDD ↔ LodeStack — shared mapping

Source: [Agile Model Driven Development](http://agilemodeling.com/essays/amdd.htm).
One mapping for all lodestack-* contracts — link, do not copy.

AMDD in one line: models that are just barely good enough, made just
in time, tested through implementation.

## The map

| AMDD element | LodeStack element |
|---|---|
| Diagram / Architecture | **ADR** — the model, written ADR-first |
| Test | **Written test** — the executable specification derived from the ADR's Verification block |
| Code | **Code** — the implementation satisfying the architecture |

ADR → Test → Code makes **one development cycle**.

## The distinction

AMDD iterates models and then moves on; LodeStack models are
**permanent**. An ADR is iterated through its own implementation
cycle (Proposed → Accepted) and kept as decision memory; change
means Superseded, never mutation. Same loop — the artifact survives.

A Plan raises the package one level: ADR + Test + Code is the
system/integration truth; plus Plan is the feature-level truth.

## Consequences for contracts

- **Memory** owns the model artifacts: ADR spec, Proposed-status
  iteration rules, the Verification block that makes ADR→test
  mechanical.
- **Edit** runs inside the cycle: REASON cites the ADR; VERIFY's TEST
  box runs the derived specification; LODE closes the loop.
- **Standards** keep the artifacts honest: tests are the gates, and
  every ADR derives tests — proportionality lives in test size, not
  in ADR ceremony.
