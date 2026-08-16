#!/usr/bin/env python3
"""Creates a new pv-* framework release's folder (pv-version skill).

Creates {workFolder}/versions/{xxxx}/ with two empty subfolders, 'files/'
and 'docs/'. If the version's folder already exists, exits with an error
without touching anything (same criteria as move-change.py) -- the caller
then decides whether to regenerate over the existing one or ask the user
for another xxxx.

workFolder is read from .claude/pv-context.json (framework section) unless
passed explicitly as a parameter. It's optional (default "/", the repo
root); the "versions" subfolder inside it always has a fixed name, not
configurable, and entirely independent from "changes/" (change/fix's xxxx
numbering) and from any other folder called "versions" that exists in the
repo (e.g. build.py's output) -- this script never reads or touches those.

Prints ONLY the created path relative to the repo root on stdout
(e.g. "versions/00001"), so it can be captured directly from the skill
without parsing extra text.

Usage:
  python init-version-folder.py --xxxx 00001
  versions/00001
"""

import argparse
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-version/scripts/
    return Path(__file__).resolve().parents[4]


def load_work_folder(root: Path) -> str:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"Cannot find {context_path}. Run the pv-init skill before "
            "preparing a version."
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
    parser.add_argument("--xxxx", required=True, help="Code of the version to prepare (free text).")
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    args = parser.parse_args()

    root = repo_root()
    work_folder_rel = args.work_folder or load_work_folder(root)
    versions_dir = resolve_versions_dir(root, work_folder_rel)

    version_dir = versions_dir / args.xxxx
    if version_dir.exists():
        raise SystemExit(f"A version folder already exists at: {version_dir}")

    (version_dir / "files").mkdir(parents=True)
    (version_dir / "docs").mkdir(parents=True)

    print(version_dir.relative_to(root).as_posix())


if __name__ == "__main__":
    main()
