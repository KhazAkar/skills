# skills

Personal agent-skill collection for AI coding agents (Vibe, Devin and
friends). This repo is the canonical source of the skills below. Agents
edit it under the contract in [AGENTS.md](AGENTS.md).

## Layout

One skill per folder under `.agents/skills/`:

- `SKILL.md` - the skill itself (YAML frontmatter + Markdown body)
- `README.md` - one-line summary, skill ID, version
- `metadata.json` - id, version, sharing scope
- optional `Reference.md`, `refs/` and `templates/` support files

## Skills (live)

- **lodestack-memory** - LodeStack v2 Memory contract: lode/ structure,
  ADR (octet slots, sibling Verification section) and Plan specs, exploration lane.
  Ships AGENTS.template.md.
- **lodestack-edit** - LodeStack v2 Edit contract: REASON, LOCATE,
  ANALYZE, EDIT (tree-sitter-edit primary, text-diff fallback),
  VERIFY with the 3-attempt break rule.
- **lodestack-code-standards** - LodeStack v2 Code Standards: one
  universal rule set distilled from MISRA, Power of Ten, TigerStyle,
  Zen of Python, YAGNI, Grug-brain; junior-maintainable code; every
  rule carries a gate (test / analyzer / review).
- **lodestack-test-standards** - LodeStack v2 Test Standards: tests
  are executable specifications derived from ADR Verification blocks;
  integration-level default; one test = one rule; adversarial
  safety-critical mindset.
- **firmware-development** - embedded firmware path on the lode
  backbone: silicon first, pinned toolchain, host and emulator tests,
  safe flashing.
- **firmware-reverse-engineering** - dump and back up firmware before
  anything else; datasheets and errata as ground truth.
- `shared/` - cross-skill references promoted by the 2+ rule.

## Retired

The v1 skills (code-edit, code-standards, test-standards,
lode-programming) moved to [retired/](retired/README.md) on
2026-11-20, superseded by the v2 contracts. Content is kept verbatim
for history.

## Conventions

- Versioning: SKILL.md, metadata.json and README.md bump together.
- Commits: conventional titles; a change commit, then a bump commit.
- Mirrors: this repo is the single source for skill content. The
  Mistral Skills registry is a push-only mirror, never edited
  directly. The Devin org installs content snapshots of the repo
  state (since 2026-11-19); change the repo first, then re-install.
- The v2 contracts wire as the LodeStack: memory
  (lodestack-memory), process (lodestack-edit), code
  (lodestack-code-standards), tests (lodestack-test-standards);
  firmware-development and firmware-reverse-engineering are
  specialized paths on the lode backbone.

Editing this repo? Read [AGENTS.md](AGENTS.md) first.
