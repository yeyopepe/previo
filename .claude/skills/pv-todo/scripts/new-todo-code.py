#!/usr/bin/env python3
"""Generates a unique alphanumeric code for a new pv-todo idea.

Lists the subfolders already existing under {workFolder}/changes/todo/ and
generates a short random code ([a-z0-9], 5 characters by default) that
doesn't collide with any of them. This code is local to
{workFolder}/changes/todo/ and has no relation to change/fix's numeric
'xxxx' (see next-change-number.py in pv-internal-workflow): no other skill
in the framework counts or checks these folders when numbering.

workFolder is read from .claude/pv-context.json (framework section) unless
passed explicitly as a parameter. It's optional (default "/", the repo
root); the "changes" subfolder inside it always has a fixed name, not
configurable.

Prints ONLY the generated code on stdout (e.g. "a3f9k"), so it can be
captured directly from the skill without parsing extra text.

Usage:
  python new-todo-code.py
  a3f9k
"""

import argparse
import json
import random
import string
import sys
from pathlib import Path

ALPHABET = string.ascii_lowercase + string.digits
MAX_ATTEMPTS = 1000


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-todo/scripts/
    return Path(__file__).resolve().parents[4]


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "changes"


def load_changes_dir(root: Path, override: str | None) -> Path:
    if override:
        return resolve_changes_dir(root, override)

    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"Cannot find {context_path}. Run the pv-init skill before "
            "generating an idea code."
        )
    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} has no 'framework' section. Run pv-init "
            "to complete it."
        )
    return resolve_changes_dir(root, framework.get("workFolder", "/"))


def existing_codes(todo_dir: Path) -> set[str]:
    if not todo_dir.is_dir():
        return set()
    return {p.name for p in todo_dir.iterdir() if p.is_dir()}


def generate_code(existing: set[str], length: int) -> str:
    for _ in range(MAX_ATTEMPTS):
        candidate = "".join(random.choices(ALPHABET, k=length))
        if candidate not in existing:
            return candidate
    raise SystemExit(
        f"Could not generate a unique {length}-character code after "
        f"{MAX_ATTEMPTS} attempts (too many collisions)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=5,
        help="Number of characters in the generated code (default 5).",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    changes_dir = load_changes_dir(root, args.work_folder)
    todo_dir = changes_dir / "todo"

    code = generate_code(existing_codes(todo_dir), args.length)
    print(code)


if __name__ == "__main__":
    main()
