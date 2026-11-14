# OSMM <-> LodeStack - shared checklist

Source: Petrinja, Nambakam, Sillitti, "Introducing the OpenSource
Maturity Model" (ICSE 2009 workshop). One checklist for all
lodestack-* contracts - link, do not copy.

## What gets assessed

Scope: **projects the stack operates on. Only.** The skills repo
itself is exempt. Target: OSMM **Basic** level - the product is
identifiable, licensed, documented, installable and testable.

OSMM dimensions were written for open-source products with users.
Translated to the solo-developer-plus-agents context, some survive,
some are honestly N/A:

| OSMM dimension | Survives? | Satisfied by | Pass check |
|---|---|---|---|
| Product identification | Yes | `lode/summary.md` | Exists, current, technical (not a README) |
| License | Yes | `LICENSE` at repo root | Present, or explicitly marked N/A by the developer |
| Documentation | Yes | `lode/` + `lode-map.md` | Index exists and is current |
| Setup / installability | Yes | `lode/practices.md` -> "First setup" | A fresh dev or agent can build/run from it |
| Testing | Yes | `lode/practices.md` -> "Testing" + suite | Test command documented; tests are gates |
| Versioning / releases | Yes | git history | Conventional commits; tags where applicable |
| Support | N/A | - | Solo: the developer is support |
| Community | N/A | - | Solo: an agent fleet is not a community |

## How assessment runs

- **Cadence** - continuous, riding existing checkpoints: ADR
  acceptance, release bumps, lode sync. No new ceremony.
- **Division of labor** - the agent runs the pass and presents it as
  a dated table; the developer judges content. Presence-checkable:
  a dated pass table exists at `lode/osmm.md`.
- N/A rows are recorded, not gamed - a dimension marked N/A with a
  reason is a valid pass.
