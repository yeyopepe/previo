#!/usr/bin/env python3
"""Deletes specific entries already folded into the changelog (pv-internal-changelog skill).

Deletes, ONLY, the {workFolder}/changes/closed/ subfolders whose xxxx is
explicitly passed in --xxxx-list -- never "all of closed/" blindly, in case
new entries appeared between when they were listed (list-closed-entries.py)
and the user confirming the deletion. Only invoked after the user's explicit
confirmation: this action is irreversible and isn't decided by this script.

workFolder is read from .claude/pv-context.json (framework section) unless
passed explicitly as a parameter.

Prints ONLY a JSON on stdout with what was actually deleted:

  {"deleted": ["00001", "00002"], "notFound": []}

If any xxxx from --xxxx-list doesn't exist in closed/, it's reported in
"notFound" instead of failing -- that's not a reason to skip deleting the
rest.

Usage:
  python delete-closed-entries.py --xxxx-list 00001,00002
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
            "deleting entries from closed."
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
        "--xxxx-list",
        required=True,
        help="Comma-separated list of xxxx codes to delete from closed/ (e.g. 00001,00002).",
    )
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

    xxxx_list = [x.strip() for x in args.xxxx_list.split(",") if x.strip()]

    deleted = []
    not_found = []
    for xxxx in xxxx_list:
        entry_dir = closed_dir / xxxx
        if entry_dir.is_dir():
            shutil.rmtree(entry_dir)
            deleted.append(xxxx)
        else:
            not_found.append(xxxx)

    json.dump({"deleted": deleted, "notFound": not_found}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
