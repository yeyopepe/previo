"""Computes the next feature identifying number (title prefix, not the filename --
the filename is still the title's slug). A number already assigned to an existing
feature is never recomputed or reused when it's deleted.

Usage:
    python next-feature-number.py --folder docs/features
"""
import argparse
import re
from pathlib import Path

ID_RE = re.compile(r"^#\s+(\d+)\s+—")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    parser.add_argument("--width", type=int, default=3)
    args = parser.parse_args()

    folder = Path(args.folder)
    max_id = 0
    if folder.exists():
        for path in folder.glob("*.md"):
            if path.name == "INDEX.md":
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            if not lines:
                continue
            m = ID_RE.match(lines[0])
            if m:
                max_id = max(max_id, int(m.group(1)))

    print(str(max_id + 1).zfill(args.width))


if __name__ == "__main__":
    main()
