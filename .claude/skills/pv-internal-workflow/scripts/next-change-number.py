#!/usr/bin/env python3
"""Computes the next change/fix number (xxxx) for the pv-* framework.

Finds the highest number among ALL purely numeric subfolders that exist
under any subtree of {workFolder}/changes (inProgress, implemented, closed,
or any other added in the future) and returns that number + 1, formatted
with numberWidth digits and leading zeros.

Exception: {workFolder}/changes/todo/ (used by the pv-todo skill, outside
the change/fix flow) is always ignored, even if it contains numeric
subfolders.

workFolder and numberWidth are read from .claude/pv-context.json (framework
section) unless passed explicitly as parameters. workFolder is optional
(default "/", the repo root); the "changes" subfolder inside it always has
a fixed name, not configurable.

Prints ONLY the next number on stdout (e.g. "0002"), so it can be captured
directly from another script or skill without parsing extra text.

Usage:
  python next-change-number.py
  0002
"""

import argparse
import json
import re
import sys
from pathlib import Path

NUMERIC_NAME = re.compile(r"^\d+$")
EXCLUDED_STATE_DIRS = {"todo"}


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-internal-workflow/scripts/
    return Path(__file__).resolve().parents[4]


def load_framework_defaults(root: Path) -> dict:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"Cannot find {context_path}. Run the pv-init skill before "
            "computing the next number."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} has no 'framework' section. Run the pv-init "
            "skill to complete it."
        )
    return framework


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "changes"


def compute_next_number(changes_dir: Path) -> int:
    max_number = 0

    if not changes_dir.is_dir():
        return max_number + 1

    # Every direct subfolder of changes/ is a "state" (inProgress,
    # implemented, closed...). ALL of them are walked, not just
    # inProgress/implemented, so an xxxx already used in closed isn't
    # reassigned.
    for state_dir in changes_dir.iterdir():
        if not state_dir.is_dir() or state_dir.name in EXCLUDED_STATE_DIRS:
            continue
        for entry_dir in state_dir.iterdir():
            if entry_dir.is_dir() and NUMERIC_NAME.match(entry_dir.name):
                max_number = max(max_number, int(entry_dir.name))

    return max_number + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder, relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--number-width",
        type=int,
        help="Number of digits for zero-padding. If not given, read from "
        ".claude/pv-context.json.",
    )
    args = parser.parse_args()

    root = repo_root()

    work_folder_rel = args.work_folder
    number_width = args.number_width

    if not work_folder_rel or not number_width:
        framework = load_framework_defaults(root)
        if not work_folder_rel:
            work_folder_rel = framework.get("workFolder", "/")
        if not number_width:
            number_width = framework.get("numberWidth")

    if not number_width:
        raise SystemExit(
            "Could not determine 'numberWidth' (neither via parameter nor "
            "from pv-context.json)."
        )

    changes_dir = resolve_changes_dir(root, work_folder_rel)
    next_number = compute_next_number(changes_dir)

    print(str(next_number).zfill(number_width))


if __name__ == "__main__":
    main()
