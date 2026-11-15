# Backlog

Adjacent problems and follow-ups that do not belong in a diff
(AGENTS.md, EDIT stage). Newest on top.

## BL-2026-11-15-001 — `lodectl check`

Owner repo: gitlab.com/r3xxar/lodectl.

Implement `lodectl check`, the tool half of the model-file mermaid
rule (lodestack-memory 1.0.5, lodestack-edit 1.0.4):

- Presence: `lode/adr/ADR-*.md`, `lode/plan/PLAN-*.md`,
  `lode/architecture/*.md` must contain a mermaid block - the check
  the grep fallback covers meanwhile.
- Syntax: when `mmdc` (@mermaid-js/mermaid-cli) is on PATH, validate
  every mermaid block parses.
- Non-zero exit on violations so VERIFY/LODE can gate on it.
