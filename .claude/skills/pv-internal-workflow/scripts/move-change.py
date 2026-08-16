#!/usr/bin/env python3
"""Moves a change/fix folder between pv-* framework substates.

Moves {workFolder}/changes/{from}/{xxxx}/ (with all its content) to
{workFolder}/changes/{to}/{xxxx}/, creating {workFolder}/changes/{to}/ if it
doesn't exist.

workFolder is read from .claude/pv-context.json (framework section) unless
passed explicitly as a parameter. It's optional (default "/", the repo
root); the "changes" subfolder inside it always has a fixed name, not
configurable.

Prints ONLY the destination path, relative to the repo root, on stdout
(e.g. "changes/implemented/0002"), so it can be captured directly from
another script or skill without parsing extra text. Any error (missing
source, destination already occupied, unresolved workFolder...) exits with
SystemExit and a clear message on stderr, without moving anything.

Usage:
  python move-change.py --xxxx 0002 --from inProgress --to implemented
  changes/implemented/0002
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-internal-workflow/scripts/
    return Path(__file__).resolve().parents[4]


def load_work_folder(root: Path) -> str:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"Cannot find {context_path}. Run the pv-init skill before "
            "moving a change/fix."
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
    parser.add_argument("--xxxx", required=True, help="Code of the change/fix to move.")
    parser.add_argument(
        "--from",
        dest="from_state",
        required=True,
        help="Source subfolder of changes/ (e.g. inProgress, implemented, closed).",
    )
    parser.add_argument(
        "--to",
        dest="to_state",
        required=True,
        help="Destination subfolder of changes/ (e.g. inProgress, implemented, closed).",
    )
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder, relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    args = parser.parse_args()

    root = repo_root()

    work_folder_rel = args.work_folder or load_work_folder(root)
    changes_dir = resolve_changes_dir(root, work_folder_rel)

    source = changes_dir / args.from_state / args.xxxx
    dest_dir = changes_dir / args.to_state
    dest = dest_dir / args.xxxx

    if not source.is_dir():
        raise SystemExit(f"Source folder doesn't exist: {source}")
    if dest.exists():
        raise SystemExit(f"A folder already exists at the destination: {dest}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(dest))

    print(dest.relative_to(root).as_posix())


if __name__ == "__main__":
    main()
