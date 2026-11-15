#!/usr/bin/env python3
"""Push one skill directory to the Mistral skill registry.

write_skill replaces content wholesale, so this sends the complete
SKILL.md body plus every other file in the directory as an asset
(except metadata.json and README.md - repo ledgers, not skill
content). Prints the resulting revision and updated_at so the
metadata.json ledger can mirror them.

Usage: registry_sync.py .agents/skills/<name>
Needs MISTRAL_API_KEY in the environment.
"""
import json
import os
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
    key = os.environ.get("MISTRAL_API_KEY")
    if not key:
        raise SystemExit("MISTRAL_API_KEY not set in environment")
    res = rpc("write_skill", {
        "name": d.name,
        "description": frontmatter_field(body, "description"),
        "body": body,
        "assets": assets,
    }, key)
    print(json.dumps({"name": res.get("name"), "version": res.get("version"),
                      "assets": len(assets)}))


if __name__ == "__main__":
    main()
