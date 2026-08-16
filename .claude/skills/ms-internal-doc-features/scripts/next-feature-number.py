"""Calcula el siguiente numero identificador de funcionalidad (prefijo del titulo, no del
nombre de fichero -- el nombre de fichero sigue siendo el slug del titulo). Un numero ya
asignado a una funcionalidad existente nunca se recalcula ni se reutiliza al borrarla.

Uso:
    python next-feature-number.py --folder design/docs/features
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
