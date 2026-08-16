#!/usr/bin/env python3
"""One-off: set every skill's version to 1.0.0 in its SKILL.md frontmatter.

Rewrites the `  version: X.Y.Z` line under `metadata:` in every
.claude/skills/*/SKILL.md. Run once from the repo root, then review the diff.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"
VERSION_RE = re.compile(r"^(\s*version:\s*)\S+(\s*)$", re.MULTILINE)
TARGET_VERSION = "0.9.0"


def main():
    changed = []
    skipped = []
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        content = skill_md.read_text(encoding="utf-8")
        new_content, count = VERSION_RE.subn(rf"\g<1>{TARGET_VERSION}\g<2>", content, count=1)
        if count == 0:
            skipped.append(skill_md)
            continue
        if new_content != content:
            skill_md.write_text(new_content, encoding="utf-8")
            changed.append(skill_md)

    print(f"Updated {len(changed)} SKILL.md file(s) to version {TARGET_VERSION}:")
    for f in changed:
        print(f"  {f.relative_to(ROOT)}")

    if skipped:
        print(f"\nSkipped {len(skipped)} file(s) with no 'version:' field:")
        for f in skipped:
            print(f"  {f.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
