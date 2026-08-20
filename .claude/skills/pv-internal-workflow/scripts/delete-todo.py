#!/usr/bin/env python3
"""Deletes an idea folder from the pv-* framework's todo/ substate.

Deletes {workFolder}/changes/todo/{xxxx}/ (with all its content). Unlike
move-change.py, this doesn't move the folder anywhere -- todo/ is the only
substate this script touches, since ideas there haven't accumulated any
plan.md/history.md worth preserving elsewhere.

workFolder is read from .claude/pv-context.json (framework section) unless
passed explicitly as a parameter. It's optional (default "/", the repo
root); the "changes" subfolder inside it always has a fixed name, not
configurable.

Prints nothing on success. Any error (missing source, unresolved
workFolder...) exits with SystemExit and a clear message on stderr, without
deleting anything.

Usage:
  python delete-todo.py --xxxx a3f9k
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
            "deleting an idea."
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
    parser.add_argument("--xxxx", required=True, help="Code of the idea to delete.")
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder, relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    args = parser.parse_args()

    root = repo_root()

    work_folder_rel = args.work_folder or load_work_folder(root)
    changes_dir = resolve_changes_dir(root, work_folder_rel)

    target = changes_dir / "todo" / args.xxxx

    if not target.is_dir():
        raise SystemExit(f"Idea folder doesn't exist: {target}")

    shutil.rmtree(target)


if __name__ == "__main__":
    main()
