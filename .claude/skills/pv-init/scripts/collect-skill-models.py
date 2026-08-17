#!/usr/bin/env python3
"""Reads each 'pv-*' SKILL.md's real 'model'/'effort' frontmatter and
proposes a 'skillModels' section (default + overrides) that mirrors it.

Used by pv-init when writing/updating .claude/pv-context.json: 'skillModels'
must always be written, even if the user doesn't want to customize anything,
so it starts as an accurate mirror of what's already on disk instead of
missing entirely. 'default' is the most common (model, effort) pair across
all pv-* skills; every skill whose own frontmatter differs from that pair
goes into 'overrides'. Ties broken by skill name (first alphabetically).

Doesn't write anything -- only prints the proposed section as JSON on
stdout, for pv-init to merge into pv-context.json (keeping any 'default'/
'overrides' the user explicitly asked to change on top of this baseline).

Usage:
  python .claude/skills/pv-init/scripts/collect-skill-models.py
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-init/scripts/
    return Path(__file__).resolve().parents[4]


def read_model_effort(path: Path) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        close_idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    frontmatter = lines[1:close_idx]

    model = None
    effort = None
    for line in frontmatter:
        match = re.match(r"^(model|effort):\s*(.*)$", line)
        if not match:
            continue
        value = match.group(2).strip().strip('"').strip("'")
        if match.group(1) == "model":
            model = value
        else:
            effort = value
    if model is None or effort is None:
        return None
    return model, effort


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    skills_dir = root / ".claude/skills"

    per_skill: dict[str, tuple[str, str]] = {}
    for skill_md in sorted(skills_dir.glob("pv-*/SKILL.md")):
        resolved = read_model_effort(skill_md)
        if resolved is not None:
            per_skill[skill_md.parent.name] = resolved

    if not per_skill:
        json.dump({"default": None, "overrides": {}}, sys.stdout, ensure_ascii=False)
        print()
        return

    counts = Counter(per_skill.values())
    max_count = max(counts.values())
    # Tie-break deterministically: among the most common pairs, keep the one
    # that first appears when skills are walked in alphabetical order.
    default_pair = next(
        pair for pair in per_skill.values() if counts[pair] == max_count
    )

    overrides = {
        name: {"model": pair[0], "effort": pair[1]}
        for name, pair in sorted(per_skill.items())
        if pair != default_pair
    }

    result = {
        "default": {"model": default_pair[0], "effort": default_pair[1]},
        "overrides": overrides,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
