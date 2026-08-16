#!/usr/bin/env python3
"""Borra entradas concretas ya incorporadas al changelog (skill pv-internal-changelog).

Borra, UNICAMENTE, las subcarpetas de {workFolder}/changes/closed/ cuyo xxxx
se pase explicitamente en --xxxx-list -- nunca "todo closed/" a ciegas, por
si aparecieron entradas nuevas entre que se listaron (list-closed-entries.py)
y que el usuario confirmara el borrado. Solo se invoca tras confirmacion
explicita del usuario: esta accion es irreversible y no la decide este
script.

workFolder se lee de .claude/pv-context.json (seccion framework) salvo que
se pase explicitamente por parametro.

Imprime UNICAMENTE un JSON en stdout con lo realmente borrado:

  {"deleted": ["00001", "00002"], "notFound": []}

Si algun xxxx de --xxxx-list no existe en closed/, se reporta en "notFound"
en vez de fallar -- no es motivo para no borrar el resto.

Uso:
  python delete-closed-entries.py --xxxx-list 00001,00002
"""

import argparse
import json
import shutil
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
            "borrar entradas de closed."
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
        "--xxxx-list",
        required=True,
        help="Lista de codigos xxxx a borrar de closed/, separados por comas (p.ej. 00001,00002).",
    )
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

    xxxx_list = [x.strip() for x in args.xxxx_list.split(",") if x.strip()]

    deleted = []
    not_found = []
    for xxxx in xxxx_list:
        entry_dir = closed_dir / xxxx
        if entry_dir.is_dir():
            shutil.rmtree(entry_dir)
            deleted.append(xxxx)
        else:
            not_found.append(xxxx)

    json.dump({"deleted": deleted, "notFound": not_found}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
