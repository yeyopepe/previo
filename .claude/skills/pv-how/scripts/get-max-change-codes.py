#!/usr/bin/env python3
"""Obtiene el codigo (xxxx) mas alto existente en cada estado del framework pv-*.

Busca, por separado, el numero mas alto entre las subcarpetas puramente
numericas de {workFolder}/changes/inProgress, {workFolder}/changes/implemented
y {workFolder}/changes/closed. Se usa como verificacion previa de pv-how: si
el xxxx que se va a planificar es menor que el maximo de cualquiera de estos
tres estados, significa que se ha creado despues de otro cambio/fix mas
reciente y conviene reanalizarlo antes de planificar.

workFolder y numberWidth se leen de .claude/pv-context.json (seccion
framework) salvo que se pasen explicitamente por parametro. workFolder es
opcional (default "/", la raiz del repo); la subcarpeta "changes" dentro de
el es siempre de nombre fijo, no configurable.

Imprime UNICAMENTE un JSON en stdout con los tres codigos ya formateados con
numberWidth digitos y ceros a la izquierda, o null si ese estado no tiene
ninguna carpeta numerada:

  {"inProgress": "00003", "implemented": "00002", "closed": null}

Uso:
  python get-max-change-codes.py
"""

import argparse
import json
import re
import sys
from pathlib import Path

NUMERIC_NAME = re.compile(r"^\d+$")
STATES = ("inProgress", "implemented", "closed")
# "todo" (usada por la skill pv-todo) queda deliberadamente fuera: no forma
# parte del flujo de change/fix.


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/pv-how/scripts/
    return Path(__file__).resolve().parents[4]


def load_framework_defaults(root: Path) -> dict:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"No se encuentra {context_path}. Ejecuta la skill pv-init antes de "
            "comprobar los codigos existentes."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} no tiene la seccion 'framework'. Ejecuta la skill "
            "pv-init para completarla."
        )
    return framework


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "changes"


def max_number_in(state_dir: Path) -> int | None:
    if not state_dir.is_dir():
        return None

    max_number = None
    for entry_dir in state_dir.iterdir():
        if entry_dir.is_dir() and NUMERIC_NAME.match(entry_dir.name):
            number = int(entry_dir.name)
            if max_number is None or number > max_number:
                max_number = number
    return max_number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder, relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--number-width",
        type=int,
        help="Numero de digitos para el padding. Si no se indica, se lee de "
        ".claude/pv-context.json.",
    )
    args = parser.parse_args()

    root = repo_root()

    work_folder_rel = args.work_folder
    number_width = args.number_width

    if not work_folder_rel or not number_width:
        framework = load_framework_defaults(root)
        if not work_folder_rel:
            work_folder_rel = framework.get("workFolder", "/")
        if not number_width:
            number_width = framework.get("numberWidth")

    if not number_width:
        raise SystemExit(
            "No se ha podido determinar 'numberWidth' (ni por parametro ni desde "
            "pv-context.json)."
        )

    changes_dir = resolve_changes_dir(root, work_folder_rel)

    result = {}
    for state in STATES:
        number = max_number_in(changes_dir / state)
        result[state] = str(number).zfill(number_width) if number is not None else None

    json.dump(result, sys.stdout)
    print()


if __name__ == "__main__":
    main()
