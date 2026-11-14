# lode-stone — shared knowledge hub (optional)

> Deferred to LodeStack v2.1 — not a launch blocker. This file records
> the locked design so the runbook is ready when needed.

Transforms the Memory contract into a multi-user, multi-project
collective knowledge repository for one team. `lode/` stops being a
plain directory and becomes a **shared knowledge hub mounted as a git
submodule**: it holds shared knowledge plus per-project slices.

## Marker

Each project repo using lode-stone carries ONE marker line in its
AGENTS.md:

```
Lode-stone transformed this project memory and now it lives here: <link_to_repository>, linked as submodule named 'lode' with project memory entry point living here: lode/projects/<name>/lode-map.md. For shared knowledge entry point, use lode/stone-map.md.
```

## Layout

```
lode/                          # the hub — a git submodule
├── stone-map.md               # hub index; shared-knowledge entry point
├── projects/
│   └── <name>/                # one project's full lode structure
│       └── lode-map.md        # project memory entry point
├── systems/
│   ├── <system>.md            # system-level overview
│   └── <system>/
│       ├── <project>.md           # per project in the system
│       └── <project>-<module>.md  # per module, in depth
└── shared/
    └── <topic>/               # common knowledge: practices, quirks,
                               # gotchas usable by more than one project
```

`lode/tmp` moves OUT of the submodule to `tmp/` at the project repo
root — scratch stays per-project; the hub carries only memory worth
sharing.

The **2+ promotion rule**: an entry moves from a project slice into
`shared/` when at least two projects need it, keeping provenance back
to the origin project.

## Migration runbook

1. `lode` → `lode-project` (rename in the project repo).
2. Add the knowledge hub as a submodule at `lode/`.
3. `mkdir -p lode/projects/<project_name_taken_from_git>`; transfer
   `lode-project` content EXCEPT `lode/tmp` into it.
4. Move `lode/tmp` contents to repo-root `tmp/`.
5. Edit `.gitignore`: replace `lode/tmp` with `tmp`.
6. Delete `lode-project` and `lode/tmp`.
7. Add the marker line to AGENTS.md.
8. Commit and push the hub repo changes (the new project slice +
   stone-map entry).
9. Bump the submodule pin in the project repo.
10. Self-verify the result in an adversarial manner: entry points
    resolve, no memory stranded in `tmp`, marker exact.
11. Propose the push; the developer verifies before accepting.

Steps 8–9 close the two gaps found in the original 9-step sketch:
without the hub push and the pin bump, teammates clone a marker that
points at an old hub state.
