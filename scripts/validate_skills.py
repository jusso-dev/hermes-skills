#!/usr/bin/env python3
"""Check every SKILL.md in this repository against the Hermes Agent skill format.

The rules follow Hermes Agent's own validator (tools/skill_manager_tool.py):
frontmatter first, closed with ---, a YAML mapping with name and description,
a non-empty body, a filesystem-safe name of at most 64 characters, and a
description of at most 1024 characters. Skills under skills/ also keep the
description within the 60 characters Hermes shows in its skill index.

If Hermes Agent is importable (pip install it, or run from a checkout), its
validator and its install-time security scan are run as well.

Exit status is 0 when every skill passes.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
INDEX_LIMIT = 60

try:  # optional: Hermes Agent's own checks
    from tools.skill_manager_tool import _validate_frontmatter as hermes_validate
    from tools.skills_guard import scan_skill
except Exception:  # noqa: BLE001
    hermes_validate = None
    scan_skill = None


def check(path: Path, tap_skill: bool) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return ["must start with --- on the first line"]
    end = text.find("\n---\n", 3)
    if end == -1:
        return ["frontmatter is not closed with ---"]
    meta = yaml.safe_load(text[4:end])
    if not isinstance(meta, dict):
        return ["frontmatter is not a YAML mapping"]
    name, desc = meta.get("name"), meta.get("description")
    if not name or not desc:
        errors.append("name and description are required")
    else:
        if not NAME_RE.match(str(name)) or len(str(name)) > 64:
            errors.append(f"invalid name {name!r}")
        if str(name) != path.parent.name:
            errors.append(f"name {name!r} does not match folder {path.parent.name!r}")
        if len(str(desc)) > 1024:
            errors.append("description is longer than 1024 characters")
        if tap_skill and len(str(desc)) > INDEX_LIMIT:
            errors.append(f"description is {len(str(desc))} characters; keep it within {INDEX_LIMIT}")
    if not text[end + 5:].strip():
        errors.append("body is empty")
    if len(text) > 100_000:
        errors.append("SKILL.md is longer than 100,000 characters")
    if tap_skill and "\u2014" in text:
        errors.append("contains an em dash")
    if hermes_validate is not None:
        problem = hermes_validate(text, new_skill=tap_skill)
        if problem:
            errors.append(f"Hermes validator: {problem}")
    if scan_skill is not None:
        result = scan_skill(path.parent, source="community")
        bad = [f for f in result.findings if f.severity in ("critical", "high")]
        for f in bad:
            errors.append(f"Hermes skills guard: {f.severity} {f.pattern_id} at {f.file}:{f.line}")
    return errors


def main() -> int:
    paths = [(p, True) for p in sorted(ROOT.glob("skills/*/SKILL.md"))]
    paths += [(p, False) for p in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md"))]
    failed = 0
    for path, tap_skill in paths:
        errors = check(path, tap_skill)
        rel = path.relative_to(ROOT)
        if errors:
            failed += 1
            for error in errors:
                print(f"FAIL {rel}: {error}")
        else:
            print(f"ok   {rel}")
    extra = "with" if hermes_validate else "without"
    print(f"{len(paths)} skills checked {extra} Hermes Agent's validator, {failed} failed.")
    return 1 if failed or not paths else 0


if __name__ == "__main__":
    sys.exit(main())
