#!/usr/bin/env python3
"""Locates the previous version in {workFolder}/versions/ (pv-internal-changelog skill).

Walks {workFolder}/versions/'s direct subfolders, excludes the one being
generated (--xxxx), and returns the most recently created one per the
folder's own mtime -- not the xxxx (which is free text, not chronologically
sortable). The caller must confirm with the user that the returned candidate
is really the correct previous version before using it, in case of
ambiguity.

workFolder is read from .claude/pv-context.json (framework section) unless
passed explicitly as a parameter.

Prints ONLY a JSON on stdout:

  {"found": true, "xxxx": "00001", "changelogPath": "versions/00001/changelog.md", "changelogExists": true}
  {"found": false, "xxxx": null, "changelogPath": null, "changelogExists": false}

"found": false if there's no other folder in versions/ besides the one
being generated. "changelogExists": false if the folder found doesn't have
a changelog.md yet (e.g. a version half-prepared).

Usage:
  python find-previous-version.py --xxxx 00002
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
            "looking for the previous version."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} has no 'framework' section. Run the pv-init "
            "skill to complete it."
        )
    return framework.get("workFolder", "/")


def resolve_versions_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "versions"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xxxx", required=True, help="Code of the version being generated (excluded from the search).")
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
    versions_dir = resolve_versions_dir(root, work_folder_rel)

    candidates = []
    if versions_dir.is_dir():
        candidates = [
            p for p in versions_dir.iterdir() if p.is_dir() and p.name != args.xxxx
        ]

    if not candidates:
        json.dump(
            {"found": False, "xxxx": None, "changelogPath": None, "changelogExists": False},
            sys.stdout,
            ensure_ascii=False,
        )
        print()
        return

    most_recent = max(candidates, key=lambda p: p.stat().st_ctime)
    changelog_path = most_recent / "changelog.md"

    json.dump(
        {
            "found": True,
            "xxxx": most_recent.name,
            "changelogPath": changelog_path.relative_to(root).as_posix(),
            "changelogExists": changelog_path.is_file(),
        },
        sys.stdout,
        ensure_ascii=False,
    )
    print()


if __name__ == "__main__":
    main()
