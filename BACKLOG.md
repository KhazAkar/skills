# Backlog

Adjacent problems and follow-ups that do not belong in a diff
(AGENTS.md, EDIT stage). Newest on top.

## BL-2026-11-15-001 — `lodectl check` — DONE 2026-11-17

Owner repo: gitlab.com/r3xxar/lodectl. Shipped in lodectl v0.6.0
(ADR-2026-11-16-002, ADR-2026-11-17-001):

- Presence: mermaid-presence finding on the model files.
- Syntax: mermaid-syntax finding via a built-in structural
  validator (standard library only) - `mmdc` / mermaid-cli dropped,
  no external mermaid tooling needed.
- Non-zero exit on violations, so VERIFY/LODE gates on it.

The `grep -L mermaid` fallback in lodestack-edit VERIFY.f is removed;
lodectl off PATH means record N/A and offer `go install`.
