# skills

Personal agent-skill collection for AI coding agents (Vibe, Devin and
friends). This repo is the canonical source of the skills below. Agents
edit it under the contract in [AGENTS.md](AGENTS.md).

## Layout

One skill per folder under `.agents/skills/`:

- `SKILL.md` — the skill itself (YAML frontmatter + Markdown body)
- `README.md` — one-line summary, skill ID, version
- `metadata.json` — id, version, sharing scope
- optional `reference/` and `templates/` support files

## Skills

- **code-edit** — the surgical edit contract: five non-negotiable stages
  (INTENT, LOCATE, IMPACT, EDIT, PROPAGATE) for every code change, in
  any project.
- **lode-programming** — Lode Coding: durable project memory in `lode/`,
  ADRs at decision, lode updates at acceptance.
- **lodestack-memory** — LodeStack v2 Memory contract: lode/ structure,
  ADR (6xW, Verification block) and Plan specs, exploration lane.
  Ships AGENTS.template.md.
- **lodestack-edit** — LodeStack v2 Edit contract: REASON, LOCATE,
  ANALYZE, EDIT (tree-sitter-edit primary, text-diff fallback),
  VERIFY with the 3-attempt break rule.
- **lodestack-code-standards** — LodeStack v2 Code Standards: one
  universal rule set distilled from MISRA, Power of Ten, TigerStyle,
  Zen of Python, YAGNI, Grug-brain; junior-maintainable code; every
  rule carries a gate (test / analyzer / review).
- **lodestack-test-standards** — LodeStack v2 Test Standards: tests
  are executable specifications derived from ADR Verification blocks;
  integration-level default; one test = one rule; adversarial
  safety-critical mindset.
- **lode-stone** - the Lode-stone add-on from the constitution:
  one hub repository for per-project lode memory plus shared
  knowledge; membership by the AGENTS.md marker, two-sided
  verification, sync at acceptance, commons promotion by the
  2+ rule.
- **code-standards** — engineering standards distilled from TigerStyle
  (tigerstyle.dev) and NASA JPL's Power of Ten: spirit tier in every
  repo, strict tier for unattended native cores, adopted by ADR.
- **test-standards** — how to write tests: system/integration level by
  default, executable specifications as contracts, few E2E and unit
  tests only where integration does not fit (ask first, per code-edit),
  one test file per specification, adversarial safety-critical mindset.
- **firmware-development** — embedded firmware path on the lode
  backbone: silicon first, pinned toolchain, host and emulator tests,
  safe flashing.
- **firmware-reverse-engineering** — dump and back up firmware before
  anything else; datasheets and errata as ground truth.
- `shared/` — cross-skill references promoted by the 2+ rule
  (currently firmware topic references shared by both firmware
  skills).

## Conventions

- Versioning: SKILL.md, metadata.json and README.md bump together.
- Commits: conventional titles; a change commit, then a bump commit.
- code-edit and lode-programming are cross-wired: Code Discipline names
  the edit contract; the contract's Deployment carries the lode cadence.
- code-standards joins the wiring: Code Discipline names it; its
  Deployment carries the tier-adoption cadence (ADR, practices.md, CI
  gates). test-standards completes the stack: Code Discipline names it;
  it owns test design. Together they form the Lode Stack: memory
  (lode-programming), process (code-edit), code (code-standards), tests
  (test-standards).

Editing this repo? Read [AGENTS.md](AGENTS.md) first.
