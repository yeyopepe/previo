#!/usr/bin/env python3
"""Copia el/los entregable(s) ya generado(s) a una version (skill ms-version).

Copia cada ruta de --source (fichero ya generado por el procedimiento de
how-to-compile-version.md, en el/los paso(s) que sean) a
{workFolder}/versions/{xxxx}/files/, conservando su nombre de fichero. Se
acepta mas de un --source para procesos de build en varios pasos que generan
mas de un artefacto (p.ej. build web + build de reglas en PDF), todos ellos
parte del mismo entregable completo.

Imprime UNICAMENTE un JSON en stdout con lo copiado:

  {"copied": ["files/index-v00167.html"]}

Si alguna ruta de --source no existe, termina en error sin copiar nada (para
no dejar una entrega a medias con solo parte de sus artefactos).

Uso:
  python copy-build-artifacts.py --xxxx 00001 --source src/_output/versions/index-v00167.html
  python copy-build-artifacts.py --xxxx 00001 --source out/game.html --source out/rules.pdf
"""

import argparse
import json
import shutil
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
            "copiar el entregable."
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
    parser.add_argument("--xxxx", required=True, help="Codigo de la version que se esta preparando.")
    parser.add_argument(
        "--source",
        required=True,
        action="append",
        help="Ruta (relativa a la raiz del repo) de un artefacto generado a copiar a files/. "
        "Repetible para procesos de build en varios pasos.",
    )
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/ms-context.json (default '/').",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    work_folder_rel = args.work_folder or load_work_folder(root)
    versions_dir = resolve_versions_dir(root, work_folder_rel)

    version_files_dir = versions_dir / args.xxxx / "files"
    if not version_files_dir.is_dir():
        raise SystemExit(
            f"No existe {version_files_dir}. Ejecuta primero init-version-folder.py "
            "para crear la carpeta de la version."
        )

    sources = [root / src for src in args.source]
    for source_path, src_rel in zip(sources, args.source):
        if not source_path.is_file():
            raise SystemExit(f"No existe el fichero fuente: {src_rel}")

    copied: list[str] = []
    for source_path in sources:
        dest_path = version_files_dir / source_path.name
        shutil.copy2(source_path, dest_path)
        copied.append(dest_path.relative_to(root).as_posix())

    json.dump({"copied": copied}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
