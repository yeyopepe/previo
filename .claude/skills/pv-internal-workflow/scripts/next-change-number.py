#!/usr/bin/env python3
"""Calcula el siguiente numero de change/fix (xxxx) del framework ms-*.

Busca el numero mas alto entre TODAS las subcarpetas puramente numericas
que existan bajo cualquier subarbol de {workFolder}/changes (inProgress,
implemented, closed, o cualquier otro que se anada en el futuro) y devuelve
ese numero + 1, formateado con numberWidth digitos y ceros a la izquierda.

Excepcion: {workFolder}/changes/todo/ (usada por la skill ms-todo, ajena al
flujo de change/fix) se ignora siempre, aunque contenga subcarpetas
numericas.

workFolder y numberWidth se leen de .claude/ms-context.json (seccion
framework) salvo que se pasen explicitamente por parametro. workFolder es
opcional (default "/", la raiz del repo); la subcarpeta "changes" dentro de
el es siempre de nombre fijo, no configurable.

Imprime UNICAMENTE el numero siguiente en stdout (p.ej. "0002"), para poder
capturarlo directamente desde otro script o skill sin parsear texto extra.

Uso:
  python next-change-number.py
  0002
"""

import argparse
import json
import re
import sys
from pathlib import Path

NUMERIC_NAME = re.compile(r"^\d+$")
EXCLUDED_STATE_DIRS = {"todo"}


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/ms-internal-workflow/scripts/
    return Path(__file__).resolve().parents[4]


def load_framework_defaults(root: Path) -> dict:
    context_path = root / ".claude" / "ms-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"No se encuentra {context_path}. Ejecuta la skill ms-init antes de "
            "calcular el siguiente numero."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} no tiene la seccion 'framework'. Ejecuta la skill "
            "ms-init para completarla."
        )
    return framework


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "changes"


def compute_next_number(changes_dir: Path) -> int:
    max_number = 0

    if not changes_dir.is_dir():
        return max_number + 1

    # Cada subcarpeta directa de changes/ es un "estado" (inProgress,
    # implemented, closed...). Se recorren TODOS, no solo inProgress/implemented,
    # para no reasignar un xxxx que ya se uso en closed.
    for state_dir in changes_dir.iterdir():
        if not state_dir.is_dir() or state_dir.name in EXCLUDED_STATE_DIRS:
            continue
        for entry_dir in state_dir.iterdir():
            if entry_dir.is_dir() and NUMERIC_NAME.match(entry_dir.name):
                max_number = max(max_number, int(entry_dir.name))

    return max_number + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder, relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/ms-context.json (default '/').",
    )
    parser.add_argument(
        "--number-width",
        type=int,
        help="Numero de digitos para el padding. Si no se indica, se lee de "
        ".claude/ms-context.json.",
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
            "ms-context.json)."
        )

    changes_dir = resolve_changes_dir(root, work_folder_rel)
    next_number = compute_next_number(changes_dir)

    print(str(next_number).zfill(number_width))


if __name__ == "__main__":
    main()
