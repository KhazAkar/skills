# YAGNI — distilled digest

Source: "You Aren't Gonna Need It" — XP principle (Kent Beck /
Ron Jeffries), public domain idea.

- **Build what the ADR needs now** — no speculative features,
  abstractions, parameters, config knobs or plugin points. The
  next requirement gets built when it arrives, as its own REASON.
- **Speculation is not free** — unused generality is code a junior
  must still understand, tests must still cover, and refactors
  must still move. It is cost paid for zero return.
- **The escape hatch is the ADR** — when a future need is real
  enough to shape today's interface, it belongs in the ADR's
  Specification (documented anticipation), not in unexplained
  generality.
- **Deletion is the cheapest cleanup** — remove removed code
  completely (lodestack-edit). Dead generality is not a safety net.
