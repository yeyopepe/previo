#!/usr/bin/env python3
"""Genera un codigo alfanumerico unico para una idea nueva de pv-todo.

Lista las subcarpetas ya existentes bajo {workFolder}/changes/todo/ y genera
un codigo aleatorio corto ([a-z0-9], 5 caracteres por defecto) que no
colisione con ninguna de ellas. Este codigo es local a
{workFolder}/changes/todo/ y no tiene ninguna relacion con el 'xxxx'
numerico de change/fix (ver next-change-number.py en pv-internal-workflow):
ninguna otra skill del framework cuenta ni consulta estas carpetas al
numerar.

workFolder se lee de .claude/pv-context.json (seccion framework) salvo que
se pase explicitamente por parametro. Es opcional (default "/", la raiz del
repo); la subcarpeta "changes" dentro de el es siempre de nombre fijo, no
configurable.

Imprime UNICAMENTE el codigo generado en stdout (p.ej. "a3f9k"), para poder
capturarlo directamente desde la skill sin parsear texto extra.

Uso:
  python new-todo-code.py
  a3f9k
"""

import argparse
import json
import random
import string
import sys
from pathlib import Path

ALPHABET = string.ascii_lowercase + string.digits
MAX_ATTEMPTS = 1000


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/pv-todo/scripts/
    return Path(__file__).resolve().parents[4]


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "changes"


def load_changes_dir(root: Path, override: str | None) -> Path:
    if override:
        return resolve_changes_dir(root, override)

    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"No se encuentra {context_path}. Ejecuta la skill pv-init antes de "
            "generar un codigo de idea."
        )
    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} no tiene la seccion 'framework'. Ejecuta pv-init "
            "para completarlo."
        )
    return resolve_changes_dir(root, framework.get("workFolder", "/"))


def existing_codes(todo_dir: Path) -> set[str]:
    if not todo_dir.is_dir():
        return set()
    return {p.name for p in todo_dir.iterdir() if p.is_dir()}


def generate_code(existing: set[str], length: int) -> str:
    for _ in range(MAX_ATTEMPTS):
        candidate = "".join(random.choices(ALPHABET, k=length))
        if candidate not in existing:
            return candidate
    raise SystemExit(
        f"No se ha podido generar un codigo unico de {length} caracteres tras "
        f"{MAX_ATTEMPTS} intentos (demasiadas colisiones)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=5,
        help="Numero de caracteres del codigo generado (por defecto 5).",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    changes_dir = load_changes_dir(root, args.work_folder)
    todo_dir = changes_dir / "todo"

    code = generate_code(existing_codes(todo_dir), args.length)
    print(code)


if __name__ == "__main__":
    main()
