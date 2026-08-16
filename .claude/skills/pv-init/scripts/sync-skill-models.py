#!/usr/bin/env python3
"""Syncs .claude/pv-context.json#skillModels with each 'pv-*' SKILL.md's frontmatter.

The Claude Code harness decides which model/effort a skill uses by reading
the 'model'/'effort' fields from its own SKILL.md's frontmatter, at load
time -- it doesn't read .claude/pv-context.json. That's why pv-context.json's
'skillModels' section is only the "human" source of truth: this script is
what actually propagates those values to the real frontmatter.

Rules:
- Walks .claude/skills/pv-*/SKILL.md (skips skills not starting with 'pv-').
- For each skill, resolves its model/effort: 'overrides[<name>]' if present,
  otherwise 'default'. If pv-context.json has no 'skillModels' section, does
  nothing.
- Inserts or updates (at the top level of the frontmatter, alongside 'name'/
  'description') the 'model:' and 'effort:' keys, right before 'metadata:'
  (or before the closing '---' if that skill has no 'metadata:' block).
- If the resolved value differs from what the file already had, bumps
  'metadata.version''s patch by 1 (x.y.z -> x.y.(z+1)). If nothing changes,
  leaves the file (and its version) untouched.

Usage:
  python .claude/skills/pv-init/scripts/sync-skill-models.py [--dry-run]
"""

import argparse
import json
import re
import sys
from pathlib import Path


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-init/scripts/
    return Path(__file__).resolve().parents[4]


def bump_patch(version: str) -> str:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version.strip())
    if not match:
        return version
    major, minor, patch = match.groups()
    return f"{major}.{minor}.{int(patch) + 1}"


def sync_skill_file(path: Path, model: str, effort: str) -> str | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    if not lines or lines[0].strip() != "---":
        return None
    try:
        close_idx = next(
            i for i in range(1, len(lines)) if lines[i].strip() == "---"
        )
    except StopIteration:
        return None

    frontmatter = lines[1:close_idx]
    rest = lines[close_idx:]

    existing_model = None
    existing_effort = None
    kept = []
    metadata_idx = None
    for line in frontmatter:
        key_match = re.match(r"^(model|effort):\s*(.*)$", line)
        if key_match:
            if key_match.group(1) == "model":
                existing_model = key_match.group(2).strip().strip('"').strip("'")
            else:
                existing_effort = key_match.group(2).strip().strip('"').strip("'")
            continue
        if metadata_idx is None and re.match(r"^metadata:\s*$", line):
            metadata_idx = len(kept)
        kept.append(line)

    if existing_model == model and existing_effort == effort:
        return None

    insert_at = metadata_idx if metadata_idx is not None else len(kept)
    new_lines = (
        kept[:insert_at]
        + [f"model: {model}\n", f"effort: {effort}\n"]
        + kept[insert_at:]
    )

    # Bump metadata.version patch, if a metadata block with a version exists.
    for i, line in enumerate(new_lines):
        version_match = re.match(r"^(\s+)version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", line)
        if version_match:
            indent, version = version_match.groups()
            new_lines[i] = f"{indent}version: {bump_patch(version)}\n"
            break

    new_text = "".join(["---\n"] + new_lines + rest)
    path.write_text(new_text, encoding="utf-8", newline="")
    return new_text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Shows which files would change without writing anything.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / ".claude/pv-context.json"
    if not context_path.is_file():
        print("No .claude/pv-context.json -- nothing to sync.")
        return

    context = json.loads(context_path.read_text(encoding="utf-8"))
    skill_models = context.get("skillModels")
    if not skill_models or "default" not in skill_models:
        print("No 'skillModels.default' section in pv-context.json -- nothing to sync.")
        return

    default = skill_models["default"]
    overrides = skill_models.get("overrides", {})

    skills_dir = root / ".claude/skills"
    changed = []
    for skill_md in sorted(skills_dir.glob("pv-*/SKILL.md")):
        skill_name = skill_md.parent.name
        resolved = overrides.get(skill_name, default)
        model, effort = resolved["model"], resolved["effort"]

        if args.dry_run:
            before = skill_md.read_text(encoding="utf-8")
            model_match = re.search(r"^model:\s*(.+)$", before, re.MULTILINE)
            effort_match = re.search(r"^effort:\s*(.+)$", before, re.MULTILINE)
            current_model = model_match.group(1).strip() if model_match else None
            current_effort = effort_match.group(1).strip() if effort_match else None
            if current_model != model or current_effort != effort:
                changed.append(f"{skill_name}: {current_model}/{current_effort} -> {model}/{effort}")
            continue

        if sync_skill_file(skill_md, model, effort) is not None:
            changed.append(f"{skill_name}: -> {model}/{effort}")

    if changed:
        print(("[dry-run] " if args.dry_run else "") + "Updated:")
        for line in changed:
            print(f"  - {line}")
    else:
        print("All frontmatter was already in sync with pv-context.json.")


if __name__ == "__main__":
    main()
