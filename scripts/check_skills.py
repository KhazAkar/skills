#!/usr/bin/env python3
"""Consistency gates for the skills repo (the AGENTS.md contract).

Per skill under .agents/skills/ (excluding _shared):
- SKILL.md frontmatter: name matches the folder, description <= 1024 chars,
  version is semver MAJOR.MINOR.PATCH
- metadata.json: name matches the folder, version == latestVersion (integers)
- README.md: ## Skill ID matches metadata id, ## Version matches metadata version

Plus: every relative Markdown link in the repo resolves to an existing file.

Exits non-zero and prints every violation if any check fails.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents" / "skills"
MAX_DESCRIPTION = 1024
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
# Illustrative example links that point at files a project would create,
# not at files in this repo (kept as examples, not real links).
EXAMPLE_LINKS = {"../decisions/adr-001.md", "subsystem-name/"}

errors = []


def err(msg):
    errors.append(msg)


def frontmatter_fields(text):
    m = FRONTMATTER.match(text)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        fm = re.match(r'^(\w+):\s*"?(.*?)"?\s*$', line)
        if fm:
            fields[fm.group(1)] = fm.group(2)
    return fields


for skill_dir in sorted(p for p in SKILLS.iterdir() if p.is_dir() and p.name != "_shared"):
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    meta_path = skill_dir / "metadata.json"
    readme = skill_dir / "README.md"
    if not (skill_md.is_file() and meta_path.is_file() and readme.is_file()):
        err(f"{name}: missing SKILL.md, metadata.json or README.md")
        continue

    fields = frontmatter_fields(skill_md.read_text(encoding="utf-8"))
    if fields is None:
        err(f"{name}: SKILL.md has no YAML frontmatter")
        continue
    if fields.get("name") != name:
        err(f"{name}: frontmatter name is {fields.get('name')!r}")
    desc = fields.get("description", "")
    if len(desc) > MAX_DESCRIPTION:
        err(f"{name}: description is {len(desc)} chars (max {MAX_DESCRIPTION})")
    version = fields.get("version", "")
    if not SEMVER.match(version):
        err(f"{name}: SKILL.md version {version!r} is not MAJOR.MINOR.PATCH")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("name") != name:
        err(f"{name}: metadata name is {meta.get('name')!r}")
    v, lv = meta.get("version"), meta.get("latestVersion")
    if not (isinstance(v, int) and isinstance(lv, int) and v == lv):
        err(f"{name}: metadata version/latestVersion must be equal integers, got {v!r}/{lv!r}")

    readme_text = readme.read_text(encoding="utf-8")
    rid = re.search(r"## Skill ID\s*\n\s*(\S+)", readme_text)
    rver = re.search(r"## Version\s*\n\s*(\d+)", readme_text)
    if not rid or rid.group(1) != meta.get("id"):
        err(f"{name}: README Skill ID does not match metadata id")
    if not rver or rver.group(1) != str(v):
        err(f"{name}: README Version {rver.group(1) if rver else None!r} != metadata version {v!r}")

for md in sorted(ROOT.rglob("*.md")):
    if ".git" in md.parts:
        continue
    for link in LINK.findall(md.read_text(encoding="utf-8")):
        if link.startswith(("http://", "https://", "mailto:")) or link in EXAMPLE_LINKS:
            continue
        target = (md.parent / link).resolve()
        if not target.exists():
            err(f"{md.relative_to(ROOT)}: broken link -> {link}")

if errors:
    print("SKILL CHECK FAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print("skill checks passed")
