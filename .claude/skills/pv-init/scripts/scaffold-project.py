#!/usr/bin/env python3
"""Creates the pv-* framework's base folder structure and doc placeholders.

Invoked by pv-init right after writing .claude/pv-context.json, so it reads
the final resolved paths (workFolder, docs.tech.architectureDocDir,
docs.tech.styleBibleDocDir, docs.functional.featuresDocPathDir) directly
from that file instead of receiving them as arguments.

What it creates, only if nothing already exists at that path (never
overwrites or touches existing content):
- workFolder's fixed subfolders: changes/{inProgress,implemented,todo,closed},
  versions/, stuff/ -- empty, with a .gitkeep so git tracks them.
- docs.tech.architectureDocDir / styleBibleDocDir (if configured): folder +
  INDEX.md (minimal index table) + 01-overview.md (placeholder). The
  placeholder content is filled in later by pv-init (or pv-do over time),
  never by this script.
- docs.functional.featuresDocPathDir (if configured): this doc follows a
  different convention (pv-internal-doc-features) -- no 01-overview.md, and
  its INDEX.md is never hand-written. Only creates the empty folder and
  regenerates INDEX.md via that skill's own rebuild-index.py (which already
  handles the zero-file case), instead of inventing a placeholder here.

Always overwrites (it's a generated file, not user content):
- assets/pv.py -> {repo root}/pv.py

Before creating anything, verifies every resolved path stays inside the
repo root -- pv-context.json is local configuration that could in principle
be hand-edited with a path like "../.." for workFolder or a docs.* dir.

Prints ONLY a JSON summary on stdout, e.g.:

  {
    "workFolderSubfolders": {"created": ["previo-sdd/changes/inProgress", ...], "skipped": []},
    "docs": {
      "architecture": {"path": "previo-sdd/docs/architecture", "status": "created"},
      "style": {"path": "previo-sdd/docs/style", "status": "skipped"},
      "features": {"path": null, "status": "not_configured"}
    },
    "pvPy": {"path": "pv.py", "status": "overwritten"}
  }

'status' is one of "created", "skipped" (something already existed at that
path -- folder or, for docs, even a legacy single file -- left untouched) or
"not_configured" (the field isn't set in pv-context.json).

Usage:
  python .claude/skills/pv-init/scripts/scaffold-project.py
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

WORKFOLDER_SUBFOLDERS = (
    "changes/inProgress",
    "changes/implemented",
    "changes/todo",
    "changes/closed",
    "versions",
    "stuff",
)

INDEX_TEMPLATE = """# {title}

| File | Covers |
|---|---|
| [01-overview.md](01-overview.md) | Project overview |
"""

OVERVIEW_TEMPLATE = """# Overview

<Placeholder, generated empty by scaffold-project.py. Filled in afterwards \
with what's known about the project (type, stack, conventions) -- by \
pv-init on first setup, or expanded by pv-do over time.>
"""


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-init/scripts/
    return Path(__file__).resolve().parents[4]


def resolve_inside_repo(root: Path, relative: str) -> Path:
    resolved = (root / relative.lstrip("/")).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(
            f"Path '{relative}' resolves outside the repo root: {resolved}"
        )
    return resolved


def ensure_workfolder_subfolders(root: Path, work_folder: str) -> dict:
    created, skipped = [], []
    for sub in WORKFOLDER_SUBFOLDERS:
        folder = resolve_inside_repo(root, f"{work_folder.rstrip('/')}/{sub}")
        rel = folder.relative_to(root).as_posix()
        if folder.exists():
            skipped.append(rel)
            continue
        folder.mkdir(parents=True, exist_ok=True)
        (folder / ".gitkeep").touch()
        created.append(rel)
    return {"created": created, "skipped": skipped}


def ensure_overview_doc(
    root: Path, work_folder: str, relative_dir: str | None, title: str
) -> dict:
    if not relative_dir:
        return {"path": None, "status": "not_configured"}
    folder = resolve_inside_repo(root, f"{work_folder.rstrip('/')}/{relative_dir}")
    rel = folder.relative_to(root).as_posix()
    if folder.exists():
        return {"path": rel, "status": "skipped"}
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "INDEX.md").write_text(INDEX_TEMPLATE.format(title=title), encoding="utf-8")
    (folder / "01-overview.md").write_text(OVERVIEW_TEMPLATE, encoding="utf-8")
    return {"path": rel, "status": "created"}


def ensure_features_doc(root: Path, work_folder: str, relative_dir: str | None) -> dict:
    if not relative_dir:
        return {"path": None, "status": "not_configured"}
    folder = resolve_inside_repo(root, f"{work_folder.rstrip('/')}/{relative_dir}")
    rel = folder.relative_to(root).as_posix()
    if folder.exists():
        return {"path": rel, "status": "skipped"}
    folder.mkdir(parents=True, exist_ok=True)
    rebuild_index = root / ".claude/skills/pv-internal-doc-features/scripts/rebuild-index.py"
    subprocess.run(
        [sys.executable, str(rebuild_index), "--folder", str(folder)],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return {"path": rel, "status": "created"}


def copy_pv_py(root: Path) -> dict:
    src = root / ".claude/skills/pv-init/assets/pv.py"
    dst = resolve_inside_repo(root, "pv.py")
    shutil.copyfile(src, dst)
    return {"path": "pv.py", "status": "overwritten"}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / ".claude/pv-context.json"
    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework") or {}

    work_folder = framework.get("workFolder", "/previo-sdd")
    docs = framework.get("docs") or {}
    tech = docs.get("tech") or {}
    functional = docs.get("functional") or {}

    result = {
        "workFolderSubfolders": ensure_workfolder_subfolders(root, work_folder),
        "docs": {
            "architecture": ensure_overview_doc(
                root, work_folder, tech.get("architectureDocDir"), "Architecture"
            ),
            "style": ensure_overview_doc(
                root, work_folder, tech.get("styleBibleDocDir"), "Style bible"
            ),
            "features": ensure_features_doc(
                root, work_folder, functional.get("featuresDocPathDir")
            ),
        },
        "pvPy": copy_pv_py(root),
    }

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
