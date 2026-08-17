#!/usr/bin/env python3
"""Gets the highest existing code (xxxx) in each pv-* framework state.

Separately finds the highest number among the purely numeric subfolders of
{workFolder}/changes/inProgress, {workFolder}/changes/implemented and
{workFolder}/changes/closed. Used as a pre-check by pv-how: if the xxxx
about to be planned is lower than the max of any of these three states, it
means it was created before another, more recent change/fix, and it should
be re-analyzed before planning.

workFolder and numberWidth are read from .claude/pv-context.json (framework
section) unless passed explicitly as parameters. workFolder is optional
(default "/", the repo root); the "changes" subfolder inside it always has
a fixed name, not configurable.

Prints ONLY a JSON on stdout with the three codes already formatted with
numberWidth digits and leading zeros, or null if that state has no
numbered folder:

  {"inProgress": "00003", "implemented": "00002", "closed": null}

Usage:
  python get-max-change-codes.py
"""

import argparse
import json
import re
import sys
from pathlib import Path

NUMERIC_NAME = re.compile(r"^\d+$")
STATES = ("inProgress", "implemented", "closed")
# "todo" (used by the pv-todo skill) is deliberately left out: it's not
# part of the change/fix flow.


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-how/scripts/
    return Path(__file__).resolve().parents[4]


def load_framework_defaults(root: Path) -> dict:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"Cannot find {context_path}. Run the pv-init skill before "
            "checking existing codes."
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
    # workFolder is always relative to the repo root, whether or not it
    # carries a leading "/" (that's only a convention to make it visually
    # explicit) -- Path("/a") / "/b" would otherwise discard "a" entirely,
    # since pathlib treats a leading-slash operand as its own absolute path.
    work_root = root / (work_folder_rel or "").lstrip("/")
    return work_root / "changes"


def max_number_in(state_dir: Path) -> int | None:
    if not state_dir.is_dir():
        return None

    max_number = None
    for entry_dir in state_dir.iterdir():
        if entry_dir.is_dir() and NUMERIC_NAME.match(entry_dir.name):
            number = int(entry_dir.name)
            if max_number is None or number > max_number:
                max_number = number
    return max_number


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

    result = {}
    for state in STATES:
        number = max_number_in(changes_dir / state)
        result[state] = str(number).zfill(number_width) if number is not None else None

    json.dump(result, sys.stdout)
    print()


if __name__ == "__main__":
    main()
