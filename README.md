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
- **firmware-development** — embedded firmware path on the lode
  backbone: silicon first, pinned toolchain, host and emulator tests,
  safe flashing.
- **firmware-reverse-engineering** — dump and back up firmware before
  anything else; datasheets and errata as ground truth.
- `_shared/` — firmware topic references shared by both firmware
  skills.

## Conventions

- Versioning: SKILL.md, metadata.json and README.md bump together.
- Commits: conventional titles; a change commit, then a bump commit.
- code-edit and lode-programming are cross-wired: Code Discipline names
  the edit contract; the contract's Deployment carries the lode cadence.

Editing this repo? Read [AGENTS.md](AGENTS.md) first.
