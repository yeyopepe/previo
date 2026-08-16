#!/usr/bin/env python3
"""Valida .claude/ms-context.json contra los campos obligatorios de schema.json.

'framework' ya no tiene ningun campo obligatorio propio (ver schema.json):
'workFolder' es opcional con default "/". Por tanto lo unico que determina
si el framework esta inicializado es que la seccion 'framework' exista --
la crea ms-init, nunca otra skill.

No decide nada por si mismo (no crea ni completa el fichero) -- solo
determina que campos obligatorios faltan, para que ms-init sepa si debe
preguntar el cuestionario completo, solo lo que falta, o nada.

Imprime UNICAMENTE un JSON en stdout:

  {"exists": true, "hasFramework": true, "missingRequired": [], "complete": true}
  {"exists": false, "hasFramework": false, "missingRequired": [], "complete": false}

Uso:
  python check-context.py
"""

import argparse
import json
import sys
from pathlib import Path

ALWAYS_REQUIRED = ()


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/ms-init/scripts/
    return Path(__file__).resolve().parents[4]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--context-path",
        help="Ruta a ms-context.json relativa a la raiz del repo. Por defecto "
        ".claude/ms-context.json.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / (args.context_path or ".claude/ms-context.json")

    if not context_path.is_file():
        result = {
            "exists": False,
            "hasFramework": False,
            "missingRequired": list(ALWAYS_REQUIRED),
            "complete": False,
        }
        json.dump(result, sys.stdout, ensure_ascii=False)
        print()
        return

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework") or {}
    has_framework = bool(context.get("framework"))

    missing = [field for field in ALWAYS_REQUIRED if field not in framework]

    result = {
        "exists": True,
        "hasFramework": has_framework,
        "missingRequired": missing,
        # Sin campos obligatorios propios en 'framework' (workFolder tiene
        # default), "completo" significa que la seccion 'framework' existe.
        "complete": has_framework and not missing,
    }
    json.dump(result, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
