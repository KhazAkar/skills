#!/usr/bin/env python3
"""Consistency gates for the skills repo (the AGENTS.md contract).

Per skill under .agents/skills/ (excluding _shared):
- SKILL.md frontmatter: all required fields present (name, description,
  version, author, license, tags), description nonempty and <= 1024 chars,
  version is semver MAJOR.MINOR.PATCH
- metadata.json: name matches the folder, version == latestVersion (integers),
  createdAt/updatedAt are valid ISO 8601 UTC timestamps, updatedAt does not
  go backwards vs the baseline ref
- README.md: ## Skill ID matches metadata id, ## Version matches metadata version

Plus: every relative Markdown link in the repo resolves to an existing file.

Exits non-zero and prints every violation if any check fails.
"""
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents" / "skills"
MAX_DESCRIPTION = 1024
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
ISO8601 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
REQUIRED_FIELDS = ["name", "description", "version", "author", "license", "tags"]
TARGET_REF = "origin/main"
# Illustrative example links that point at files a project would create,
# not at files in this repo (kept as examples, not real links).
EXAMPLE_LINKS = {"../decisions/adr-001.md", "subsystem-name/", "decisions/xxx-lode-stone-membership.md"}

errors = []


def err(msg):
    errors.append(msg)


def parse_ts(ts):
    """Parse an ISO 8601 UTC timestamp; return None if invalid or impossible."""
    if not isinstance(ts, str) or not ISO8601.match(ts):
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


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
    for field in REQUIRED_FIELDS:
        if field not in fields:
            err(f"{name}: SKILL.md frontmatter is missing required field {field!r}")
    if fields.get("name") != name:
        err(f"{name}: frontmatter name is {fields.get('name')!r}")
    desc = fields.get("description", "")
    if not desc:
        err(f"{name}: description is empty")
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
    for ts_field in ("createdAt", "updatedAt"):
        ts = meta.get(ts_field, "")
        if parse_ts(ts) is None:
            err(f"{name}: metadata {ts_field} is not a valid ISO 8601 UTC timestamp: {ts!r}")
    baseline = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", TARGET_REF],
        capture_output=True, text=True,
    )
    if baseline.returncode != 0:
        err(f"{name}: cannot read baseline ref {TARGET_REF}; fetch it before running the gate")
    else:
        old = subprocess.run(
            ["git", "show", f"{TARGET_REF}:{meta_path.relative_to(ROOT)}"],
            capture_output=True, text=True,
        )
        if old.returncode == 0:
            try:
                old_ts = parse_ts(json.loads(old.stdout).get("updatedAt", ""))
            except json.JSONDecodeError:
                old_ts = None
            new_ts = parse_ts(meta.get("updatedAt", ""))
            if old_ts is not None and new_ts is not None and new_ts < old_ts:
                err(f"{name}: updatedAt went backwards vs {TARGET_REF} ({old.stdout and json.loads(old.stdout).get('updatedAt')} -> {meta.get('updatedAt')})")
        # returncode != 0 with a valid baseline ref means the skill is new on
        # this branch: no baseline metadata exists, which is legitimate.

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
