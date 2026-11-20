# retired

Skills superseded by the LodeStack v2 contracts, moved out of
`.agents/skills/` on 2026-11-20. Content is kept verbatim for
history and provenance. Do not load these skills and do not link
them from live skills; edit the v2 successor instead. Git history
carries the full lineage.

| Retired skill | Superseded by |
| --- | --- |
| code-edit | lodestack-edit |
| code-standards | lodestack-code-standards |
| test-standards | lodestack-test-standards |
| lode-programming | lodestack-memory |

Notes:
- The digests in `code-standards/reference/` have canonical
  successors in `lodestack-code-standards/refs/` (power-of-ten,
  tigerstyle).
- The v1 ADR format in `lode-programming/templates/decisions/`
  conflicts with the lodestack-memory ADR spec (6xW); the v2 spec
  wins. Do not port it.
- The Mistral skill registry carries only the six v2 skills
  (verified 2026-11-20); nothing here is registered.
