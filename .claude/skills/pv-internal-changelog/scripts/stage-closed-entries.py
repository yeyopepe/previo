#!/usr/bin/env python3
"""Stages {workFolder}/changes/closed/'s current entries into closed/temp/.

Moves every direct subfolder of {workFolder}/changes/closed/ (except temp/
itself) into {workFolder}/changes/closed/temp/, creating temp/ if it doesn't
exist yet. From this point on, pv-internal-changelog reads/writes only
closed/temp/, so any change/fix moved into closed/ afterwards (while this
version is still being prepared) doesn't affect the changelog being drafted.

If temp/ already has entries (a previous versioning attempt was interrupted
before cleanup), the newly staged folders are added alongside them --
nothing already staged is touched or lost.

workFolder is read from .claude/pv-context.json (framework section) unless
passed explicitly as a parameter.

Prints ONLY a JSON on stdout:

  {"staged": ["00001", "00002"], "conflicts": []}

"conflicts" lists any xxxx that couldn't be staged because that name
already exists in temp/ (from a previous run) -- left untouched in closed/
rather than overwriting temp/'s copy.

Usage:
  python stage-closed-entries.py
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-internal-changelog/scripts/
    return Path(__file__).resolve().parents[4]


def load_work_folder(root: Path) -> str:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"Cannot find {context_path}. Run the pv-init skill before "
            "staging entries from closed."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} has no 'framework' section. Run the pv-init "
            "skill to complete it."
        )
    return framework.get("workFolder", "/")


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    # workFolder is always relative to the repo root, whether or not it
    # carries a leading "/" (that's only a convention to make it visually
    # explicit) -- Path("/a") / "/b" would otherwise discard "a" entirely,
    # since pathlib treats a leading-slash operand as its own absolute path.
    work_root = root / (work_folder_rel or "").lstrip("/")
    return work_root / "changes"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    work_folder_rel = args.work_folder or load_work_folder(root)
    closed_dir = resolve_changes_dir(root, work_folder_rel) / "closed"
    temp_dir = closed_dir / "temp"

    staged = []
    conflicts = []

    if closed_dir.is_dir():
        entries = sorted(
            p for p in closed_dir.iterdir() if p.is_dir() and p.name != "temp"
        )
        if entries:
            temp_dir.mkdir(parents=True, exist_ok=True)
            for entry_dir in entries:
                dest = temp_dir / entry_dir.name
                if dest.exists():
                    conflicts.append(entry_dir.name)
                    continue
                shutil.move(str(entry_dir), str(dest))
                staged.append(entry_dir.name)

    json.dump({"staged": staged, "conflicts": conflicts}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
