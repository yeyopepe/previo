#!/usr/bin/env python3
"""Mueve la carpeta de un change/fix entre subestados del framework pv-*.

Mueve {workFolder}/changes/{from}/{xxxx}/ (con todo su contenido) a
{workFolder}/changes/{to}/{xxxx}/, creando {workFolder}/changes/{to}/ si no
existe.

workFolder se lee de .claude/pv-context.json (seccion framework) salvo que
se pase explicitamente por parametro. Es opcional (default "/", la raiz del
repo); la subcarpeta "changes" dentro de el es siempre de nombre fijo, no
configurable.

Imprime UNICAMENTE la ruta destino relativa a la raiz del repo en stdout
(p.ej. "changes/implemented/0002"), para poder capturarla directamente
desde otro script o skill sin parsear texto extra. Cualquier error (origen
inexistente, destino ya ocupado, workFolder sin resolver...) termina con
SystemExit y un mensaje claro en stderr, sin mover nada.

Uso:
  python move-change.py --xxxx 0002 --from inProgress --to implemented
  changes/implemented/0002
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/pv-internal-workflow/scripts/
    return Path(__file__).resolve().parents[4]


def load_work_folder(root: Path) -> str:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"No se encuentra {context_path}. Ejecuta la skill pv-init antes de "
            "mover un change/fix."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} no tiene la seccion 'framework'. Ejecuta la skill "
            "pv-init para completarla."
        )
    return framework.get("workFolder", "/")


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "changes"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xxxx", required=True, help="Codigo del change/fix a mover.")
    parser.add_argument(
        "--from",
        dest="from_state",
        required=True,
        help="Subcarpeta origen de changes/ (p.ej. inProgress, implemented, closed).",
    )
    parser.add_argument(
        "--to",
        dest="to_state",
        required=True,
        help="Subcarpeta destino de changes/ (p.ej. inProgress, implemented, closed).",
    )
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder, relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/pv-context.json (default '/').",
    )
    args = parser.parse_args()

    root = repo_root()

    work_folder_rel = args.work_folder or load_work_folder(root)
    changes_dir = resolve_changes_dir(root, work_folder_rel)

    source = changes_dir / args.from_state / args.xxxx
    dest_dir = changes_dir / args.to_state
    dest = dest_dir / args.xxxx

    if not source.is_dir():
        raise SystemExit(f"No existe la carpeta origen: {source}")
    if dest.exists():
        raise SystemExit(f"Ya existe una carpeta en el destino: {dest}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(dest))

    print(dest.relative_to(root).as_posix())


if __name__ == "__main__":
    main()
