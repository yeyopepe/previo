#!/usr/bin/env python3
"""Lists the entries pending changelog inclusion in {workFolder}/changes/closed/.

Walks {workFolder}/changes/closed/'s direct subfolders and returns, for
each one, its xxxx (folder name) and the path to its description.md
(relative to the repo root). Doesn't read or interpret those
description.md's content -- that's the pv-internal-changelog skill's job,
which needs real judgment to classify each entry (New/Changed/Removed).

workFolder is read from .claude/pv-context.json (framework section) unless
passed explicitly as a parameter.

Prints ONLY a JSON on stdout:

  {"entries": [{"xxxx": "00001", "descriptionPath": "changes/closed/00001/description.md"}, ...]}

If closed/ doesn't exist or is empty, "entries" is an empty list (not an
error).

Usage:
  python list-closed-entries.py
"""

import argparse
import json
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
            "listing entries from closed."
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
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
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

    entries = []
    if closed_dir.is_dir():
        for entry_dir in sorted(p for p in closed_dir.iterdir() if p.is_dir()):
            description_path = entry_dir / "description.md"
            entries.append(
                {
                    "xxxx": entry_dir.name,
                    "descriptionPath": description_path.relative_to(root).as_posix()
                    if description_path.is_file()
                    else None,
                }
            )

    json.dump({"entries": entries}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
