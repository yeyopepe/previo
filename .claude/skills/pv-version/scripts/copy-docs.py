#!/usr/bin/env python3
"""Zips and copies the current documentation into a release (pv-version skill).

Zips each of the paths configured in .claude/pv-context.json's
framework.docs.tech.architectureDocDir, framework.docs.tech.styleBibleDocDir
and framework.docs.functional.featuresDocPathDir, and saves each .zip at
{workFolder}/versions/{xxxx}/docs/. Each path can be a folder (zipped whole,
including its INDEX.md if it has one) or a single .md file (a valid case for
featuresDocPathDir in projects that haven't migrated to a folder) -- in both
cases the resulting .zip is named after the path's base name (folder or file
without extension) + ".zip". Ones not configured are skipped without error
(same as the rest of the framework treats these optional fields).

Prints ONLY a JSON on stdout with what was copied, for the skill to use when
confirming to the user:

  {"copied": ["docs/architecture", "docs/style"], "skipped": ["featuresDocPathDir"]}

Usage:
  python copy-docs.py --xxxx 00001
"""

import argparse
import json
import sys
import zipfile
from pathlib import Path


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-version/scripts/
    return Path(__file__).resolve().parents[4]


def load_framework(root: Path) -> dict:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"Cannot find {context_path}. Run the pv-init skill before "
            "copying documentation."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} has no 'framework' section. Run the pv-init "
            "skill to complete it."
        )
    return framework


def resolve_versions_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "versions"


def zip_dir(source_dir: Path, dest_zip: Path) -> None:
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(source_dir))


def zip_file(source_file: Path, dest_zip: Path) -> None:
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(source_file, source_file.name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xxxx", required=True, help="Code of the version being prepared.")
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    framework = load_framework(root)
    work_folder_rel = args.work_folder or framework.get("workFolder", "/")
    versions_dir = resolve_versions_dir(root, work_folder_rel)

    version_docs_dir = versions_dir / args.xxxx / "docs"
    if not version_docs_dir.is_dir():
        raise SystemExit(
            f"{version_docs_dir} doesn't exist. Run init-version-folder.py "
            "first to create the version's folder."
        )

    docs = framework.get("docs") or {}
    tech_docs = docs.get("tech") or {}
    functional_docs = docs.get("functional") or {}
    candidates = {
        "architectureDocDir": tech_docs.get("architectureDocDir"),
        "styleBibleDocDir": tech_docs.get("styleBibleDocDir"),
        "featuresDocPathDir": functional_docs.get("featuresDocPathDir"),
    }

    copied: list[str] = []
    skipped: list[str] = []

    for field, doc_path_rel in candidates.items():
        if not doc_path_rel:
            skipped.append(field)
            continue

        source_path = root / doc_path_rel
        if source_path.is_dir():
            dest_zip = version_docs_dir / f"{source_path.name}.zip"
            zip_dir(source_path, dest_zip)
        elif source_path.is_file():
            dest_zip = version_docs_dir / f"{source_path.stem}.zip"
            zip_file(source_path, dest_zip)
        else:
            raise SystemExit(
                f"'{field}' points to {source_path}, but that path doesn't exist."
            )

        copied.append(doc_path_rel)

    json.dump({"copied": copied, "skipped": skipped}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
