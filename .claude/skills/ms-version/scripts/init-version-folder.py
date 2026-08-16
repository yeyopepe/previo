#!/usr/bin/env python3
"""Crea la carpeta de una entrega nueva del framework ms-* (skill ms-version).

Crea {workFolder}/versions/{xxxx}/ con dos subcarpetas vacias, 'files/' y
'docs/'. Si la carpeta de la version ya existe, termina en error sin tocar
nada (mismo criterio que move-change.py) -- quien invoca decide entonces si
regenerar sobre lo existente o pedir otro xxxx al usuario.

workFolder se lee de .claude/ms-context.json (seccion framework) salvo que
se pase explicitamente por parametro. Es opcional (default "/", la raiz del
repo); la subcarpeta "versions" dentro de el es siempre de nombre fijo, no
configurable, y totalmente independiente de "changes/" (numeracion xxxx de
change/fix) y de cualquier otra carpeta llamada "versions" que exista en el
repo (p.ej. la salida de build.py) -- este script nunca las lee ni las toca.

Imprime UNICAMENTE la ruta creada relativa a la raiz del repo en stdout
(p.ej. "versions/00001"), para poder capturarla directamente desde la skill
sin parsear texto extra.

Uso:
  python init-version-folder.py --xxxx 00001
  versions/00001
"""

import argparse
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/ms-version/scripts/
    return Path(__file__).resolve().parents[4]


def load_work_folder(root: Path) -> str:
    context_path = root / ".claude" / "ms-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"No se encuentra {context_path}. Ejecuta la skill ms-init antes de "
            "preparar una version."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} no tiene la seccion 'framework'. Ejecuta la skill "
            "ms-init para completarla."
        )
    return framework.get("workFolder", "/")


def resolve_versions_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "versions"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xxxx", required=True, help="Codigo de la version a preparar (texto libre).")
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/ms-context.json (default '/').",
    )
    args = parser.parse_args()

    root = repo_root()
    work_folder_rel = args.work_folder or load_work_folder(root)
    versions_dir = resolve_versions_dir(root, work_folder_rel)

    version_dir = versions_dir / args.xxxx
    if version_dir.exists():
        raise SystemExit(f"Ya existe una carpeta de version en: {version_dir}")

    (version_dir / "files").mkdir(parents=True)
    (version_dir / "docs").mkdir(parents=True)

    print(version_dir.relative_to(root).as_posix())


if __name__ == "__main__":
    main()
