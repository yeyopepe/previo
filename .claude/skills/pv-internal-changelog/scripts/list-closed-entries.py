#!/usr/bin/env python3
"""Lista las entradas pendientes de changelog en {workFolder}/changes/closed/.

Recorre las subcarpetas directas de {workFolder}/changes/closed/ y devuelve,
por cada una, su xxxx (nombre de la carpeta) y la ruta a su description.md
(relativa a la raiz del repo). No lee ni interpreta el contenido de esos
description.md -- eso lo hace la skill pv-internal-changelog, que necesita
juicio real para clasificar cada entrada (Nuevo/Cambios/Eliminado).

workFolder se lee de .claude/pv-context.json (seccion framework) salvo que
se pase explicitamente por parametro.

Imprime UNICAMENTE un JSON en stdout:

  {"entries": [{"xxxx": "00001", "descriptionPath": "changes/closed/00001/description.md"}, ...]}

Si closed/ no existe o esta vacia, "entries" es una lista vacia (no es un
error).

Uso:
  python list-closed-entries.py
"""

import argparse
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/pv-internal-changelog/scripts/
    return Path(__file__).resolve().parents[4]


def load_work_folder(root: Path) -> str:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"No se encuentra {context_path}. Ejecuta la skill pv-init antes de "
            "listar entradas de closed."
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
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/pv-context.json (default '/').",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    work_folder_rel = args.work_folder or load_work_folder(root)
    closed_dir = resolve_changes_dir(root, work_folder_rel) / "closed"

    entries = []
    if closed_dir.is_dir():
        for entry_dir in sorted(p for p in closed_dir.iterdir() if p.is_dir()):
            description_path = entry_dir / "description.md"
            entries.append(
                {
                    "xxxx": entry_dir.name,
                    "descriptionPath": description_path.relative_to(root).as_posix()
                    if description_path.is_file()
                    else None,
                }
            )

    json.dump({"entries": entries}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
