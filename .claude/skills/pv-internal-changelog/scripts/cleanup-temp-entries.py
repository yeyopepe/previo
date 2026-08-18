#!/usr/bin/env python3
"""Cleans up {workFolder}/changes/closed/temp/ once versioning is done.

Moves any folder still left in {workFolder}/changes/closed/temp/ (entries
that were staged but whose deletion the user didn't confirm) back to
{workFolder}/changes/closed/, then removes temp/ if it ends up empty.
Always safe to run, even if temp/ doesn't exist or is already empty.

workFolder is read from .claude/pv-context.json (framework section) unless
passed explicitly as a parameter.

Prints ONLY a JSON on stdout:

  {"movedBack": ["00003"], "tempRemoved": true, "conflicts": []}

"conflicts" lists any xxxx that couldn't be moved back because that name
already exists in closed/ (e.g. re-closed while the version was being
prepared) -- left in temp/ rather than overwriting closed/'s copy, which
also means temp/ isn't removed in that case.

Usage:
  python cleanup-temp-entries.py
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
            "cleaning up closed/temp."
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

    moved_back = []
    conflicts = []

    if temp_dir.is_dir():
        for entry_dir in sorted(p for p in temp_dir.iterdir() if p.is_dir()):
            dest = closed_dir / entry_dir.name
            if dest.exists():
                conflicts.append(entry_dir.name)
                continue
            shutil.move(str(entry_dir), str(dest))
            moved_back.append(entry_dir.name)

    temp_removed = False
    if temp_dir.is_dir() and not any(temp_dir.iterdir()):
        temp_dir.rmdir()
        temp_removed = True

    json.dump(
        {"movedBack": moved_back, "tempRemoved": temp_removed, "conflicts": conflicts},
        sys.stdout,
        ensure_ascii=False,
    )
    print()


if __name__ == "__main__":
    main()
