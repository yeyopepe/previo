#!/usr/bin/env python3
"""One-off migration: rename the 'ms' skill/framework prefix to 'pv' everywhere.

Renames files/directories named ms-*, ms_*, or .claude/ms-context.json,
and rewrites text occurrences of 'ms-' and 'ms_' to 'pv-' / 'pv_' inside
every tracked text file. Run once from the repo root, then review the diff.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TEXT_SUFFIXES = {".md", ".json", ".py", ".txt", ".template.md"}


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [ROOT / p for p in out.stdout.splitlines() if p]


def rewrite_text(files):
    changed = []
    for f in files:
        if not f.is_file():
            continue
        if f.suffix not in TEXT_SUFFIXES:
            continue
        try:
            content = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new_content = content.replace("ms-", "pv-").replace("ms_", "pv_")
        if new_content != content:
            f.write_text(new_content, encoding="utf-8")
            changed.append(f)
    return changed


def rename_paths():
    # Deepest paths first so renaming a dir doesn't break child paths we still need.
    candidates = sorted(ROOT.rglob("ms-*"), key=lambda p: len(p.parts), reverse=True)
    candidates += sorted(ROOT.rglob("ms_*"), key=lambda p: len(p.parts), reverse=True)
    renamed = []
    for p in candidates:
        if ".git" in p.parts:
            continue
        new_name = p.name.replace("ms-", "pv-", 1).replace("ms_", "pv_", 1)
        if new_name == p.name:
            continue
        target = p.with_name(new_name)
        subprocess.run(["git", "mv", str(p), str(target)], cwd=ROOT, check=True)
        renamed.append((p, target))
    return renamed


def main():
    files = tracked_files()
    changed = rewrite_text(files)
    print(f"Rewrote text in {len(changed)} file(s):")
    for f in changed:
        print(f"  {f.relative_to(ROOT)}")

    renamed = rename_paths()
    print(f"\nRenamed {len(renamed)} path(s):")
    for old, new in renamed:
        print(f"  {old.relative_to(ROOT)} -> {new.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
