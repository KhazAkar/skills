#!/usr/bin/env python3
"""Push one skill directory to the Mistral skill registry.

write_skill replaces content wholesale, so this sends the complete
SKILL.md body plus every other file in the directory as an asset
(except metadata.json and README.md - repo ledgers, not skill
content).

After the push it fetches the skill's catalogue row and mirrors the
registry truth back into the ledgers: metadata.json version /
latestVersion / updatedAt / sharingScope and README.md ## Version.
The registry assigns revisions per push, never per local bump - the
ledger mirrors the server, not the other way round.

Usage: registry_sync.py .agents/skills/<name>
Needs MISTRAL_MCP_API_KEY in the environment.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://api.mistral.ai/mcp"
LEDGER_FILES = {"metadata.json", "README.md"}


def rpc(tool, arguments, key):
    rpc_body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                "params": {"name": tool, "arguments": arguments}}
    req = urllib.request.Request(
        URL, data=json.dumps(rpc_body).encode(),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode()
    for line in raw.splitlines():
        line = line.removeprefix("data:").strip()
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "error" in msg:
            raise SystemExit(f"registry error: {msg['error']}")
        if "result" not in msg:
            continue
        for block in msg["result"].get("content", []):
            if block.get("type") == "text":
                return json.loads(block["text"])
        return msg["result"]
    raise SystemExit("registry: no result in response")


def frontmatter_field(body, field):
    for line in body.splitlines():
        if line.startswith(field + ":"):
            return line.split(":", 1)[1].strip().strip('"')
    raise SystemExit(f"SKILL.md: no {field} field in frontmatter")


def fetch_skill_row(name, meta_id, key):
    """The skill's catalogue row from list_skills: match by id, then
    name (the registry allows same-name skills; the ledger id wins)."""
    cursor = None
    while True:
        args = {"limit": 200}
        if cursor:
            args["cursor"] = cursor
        data = rpc("list_skills", args, key)
        rows = data.get("skills", [])
        for row in rows:
            if meta_id and row.get("id") == meta_id:
                return row
        for row in rows:
            if row.get("name") == name:
                return row
        cursor = data.get("next_cursor")
        if not cursor:
            return None


def mirror_ledgers(d, row):
    """Write the registry truth into the repo ledgers; return the list
    of files mirrored (or warnings for anything missing)."""
    mirrored = []
    meta_path = d / "metadata.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["version"] = meta["latestVersion"] = row["version"]
        if row.get("updated_at"):
            meta["updatedAt"] = row["updated_at"]
        if row.get("sharing"):
            meta["sharingScope"] = row["sharing"]
        meta_path.write_text(json.dumps(meta, indent=2) + "\n",
                             encoding="utf-8")
        mirrored.append("metadata.json")
    else:
        mirrored.append("metadata.json MISSING")
    readme = d / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        new, n = re.subn(r"(## Version\s*\n)\d+",
                         rf"\g<1>{row['version']}", text, count=1)
        if n:
            readme.write_text(new, encoding="utf-8")
            mirrored.append("README.md")
        else:
            mirrored.append("README.md: no ## Version line")
    else:
        mirrored.append("README.md MISSING")
    return mirrored


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: registry_sync.py <skill-dir>")
    d = Path(sys.argv[1])
    skill_md = d / "SKILL.md"
    if not skill_md.is_file():
        raise SystemExit(f"{d}: no SKILL.md")
    body = skill_md.read_text(encoding="utf-8")
    assets = {
        str(p.relative_to(d)): p.read_text(encoding="utf-8")
        for p in sorted(d.rglob("*"))
        if p.is_file() and p.name not in LEDGER_FILES | {"SKILL.md"}
    }
    key = os.environ.get("MISTRAL_MCP_API_KEY")
    if not key:
        raise SystemExit("MISTRAL_MCP_API_KEY not set in environment")
    res = rpc("write_skill", {
        "name": d.name,
        "description": frontmatter_field(body, "description"),
        "body": body,
        "assets": assets,
    }, key)
    meta_id = None
    meta_path = d / "metadata.json"
    if meta_path.is_file():
        meta_id = json.loads(meta_path.read_text(encoding="utf-8")).get("id")
    row = fetch_skill_row(d.name, meta_id, key)
    mirrored = mirror_ledgers(d, row) if row else ["registry row not found"]
    print(json.dumps({"name": res.get("name"), "version": res.get("version"),
                      "deduplicated": res.get("deduplicated", False),
                      "assets": len(assets), "mirrored": mirrored}))


if __name__ == "__main__":
    main()
