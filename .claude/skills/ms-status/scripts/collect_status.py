#!/usr/bin/env python3
"""Recopila el estado actual del framework ms-* a partir de {changesDir}.

Recorre todas las subcarpetas directas de {changesDir} (cada una es un
"estado": normalmente 'todo', 'inProgress', 'implemented', 'closed', pero el
script no asume una lista fija -- cuenta cualquiera que exista). Dentro de
cada estado, cada subcarpeta es una entrada (change/fix/idea) identificada
por su nombre (xxxx o codigo alfanumerico de ms-todo).

Para cada entrada determina:
  - type: 'todo' si esta bajo el estado 'todo' (ms-todo no usa campo Tipo);
    en cualquier otro estado, se parsea '**Tipo**' dentro de description.md
    ('change', 'fix' o 'fast' -- este ultimo es el atajo trivial de ms-fix,
    que crea la entrada en 'inProgress' y la mueve a 'implemented' en la
    misma invocacion, sin generar plan.md). Si no se encuentra o no es
    description.md, 'unknown'.
  - name: para 'todo', el texto completo (sin truncar) de la seccion
    '## Idea' de description.md (formato propio de ms-todo); en el resto de
    estados, el campo '**Nombre**' (formato de ms-new/ms-fix). Solo
    informativo.
  - notas: solo para el estado 'todo' -- texto completo (sin truncar) de la
    seccion '## Notas' de description.md. Null en el resto de estados o si
    la idea no tiene esa seccion.
  - hasDescription / hasPlan: si existen description.md / plan.md.
  - subStatus: solo relevante para el estado 'inProgress' (para poder
    distinguir 'descrito' de 'listo_para_implementar'); en el resto de
    estados se deja a null.

No escribe nada: imprime un unico JSON por stdout con el detalle completo y
los totales agregados, para que la skill los use al redactar el informe.

Uso:
  python collect_status.py
  python collect_status.py --work-folder /
"""

import argparse
import json
import re
import sys
from pathlib import Path

TIPO_RE = re.compile(r"\*\*Tipo\*\*\s*[:—-]\s*([A-Za-z]+)", re.IGNORECASE)
NOMBRE_RE = re.compile(r"\*\*Nombre\*\*\s*[:—-]\s*(.+)")
# ms-todo no usa el formato "- **Campo**:" de ms-new/ms-fix; usa cabeceras
# markdown ("## Idea", "## Notas") sin negrita.
# Capturan todo el bloque de cada seccion, hasta la siguiente cabecera '##' o fin de fichero.
IDEA_FULL_RE = re.compile(
    r"^##\s*Idea\s*\n+(.+?)(?=\n##\s|\Z)", re.IGNORECASE | re.MULTILINE | re.DOTALL
)
NOTAS_FULL_RE = re.compile(
    r"^##\s*Notas\s*\n+(.+?)(?=\n##\s|\Z)", re.IGNORECASE | re.MULTILINE | re.DOTALL
)

KNOWN_TYPES = {"change", "fix", "fast"}


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/ms-status/scripts/
    return Path(__file__).resolve().parents[4]


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "changes"


def load_changes_dir(root: Path, override: str | None) -> Path:
    if override:
        return resolve_changes_dir(root, override)

    context_path = root / ".claude" / "ms-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"No se encuentra {context_path}. Ejecuta la skill ms-init antes de "
            "consultar el estado."
        )
    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} no tiene la seccion 'framework'. Ejecuta ms-init "
            "para completarlo."
        )
    return resolve_changes_dir(root, framework.get("workFolder", "/"))


def parse_description(description_path: Path) -> dict:
    """Extrae 'Tipo' y 'Nombre' de un description.md, sin fallar si faltan."""
    result: dict[str, str | None] = {"tipo": None, "nombre": None}
    try:
        text = description_path.read_text(encoding="utf-8")
    except OSError:
        return result

    tipo_match = TIPO_RE.search(text)
    if tipo_match:
        result["tipo"] = tipo_match.group(1).strip().lower()

    nombre_match = NOMBRE_RE.search(text)
    if nombre_match:
        # Corta en el primer salto de linea y quita adornos markdown sueltos.
        nombre = nombre_match.group(1).splitlines()[0].strip()
        result["nombre"] = nombre.strip("` ")

    return result


def parse_todo_description(description_path: Path) -> dict:
    """Extrae el texto completo de 'Idea' y 'Notas' de un description.md de ms-todo.

    ms-todo usa cabeceras markdown ('## Idea', '## Notas'), no el formato
    '**Campo**:' de ms-new/ms-fix, asi que necesita su propio parser.
    """
    result: dict[str, str | None] = {"idea": None, "notas": None}
    try:
        text = description_path.read_text(encoding="utf-8")
    except OSError:
        return result

    idea_match = IDEA_FULL_RE.search(text)
    if idea_match:
        result["idea"] = idea_match.group(1).strip()

    notas_full_match = NOTAS_FULL_RE.search(text)
    if notas_full_match:
        result["notas"] = notas_full_match.group(1).strip()

    return result


def build_entry(state_name: str, entry_dir: Path) -> dict:
    description_path = entry_dir / "description.md"
    plan_path = entry_dir / "plan.md"
    has_description = description_path.is_file()
    has_plan = plan_path.is_file()

    notas = None
    if state_name == "todo":
        entry_type = "todo"
        nombre = None
        if has_description:
            parsed_todo = parse_todo_description(description_path)
            nombre = parsed_todo.get("idea")
            notas = parsed_todo.get("notas")
    else:
        parsed = parse_description(description_path) if has_description else {"tipo": None, "nombre": None}
        entry_type = parsed.get("tipo") if parsed.get("tipo") in KNOWN_TYPES else "unknown"
        nombre = parsed.get("nombre")

    sub_status = None
    if state_name == "inProgress":
        if has_description and has_plan:
            sub_status = "listo_para_implementar"
        elif has_description:
            sub_status = "descrito"
        else:
            sub_status = "sin_descripcion"

    return {
        "code": entry_dir.name,
        "type": entry_type,
        "name": nombre,
        "notas": notas,
        "hasDescription": has_description,
        "hasPlan": has_plan,
        "subStatus": sub_status,
    }


def collect(changes_dir: Path) -> dict:
    states: dict[str, dict] = {}
    warnings: list[str] = []

    if not changes_dir.is_dir():
        raise SystemExit(f"No existe la carpeta de changes: {changes_dir}")

    for state_dir in sorted(p for p in changes_dir.iterdir() if p.is_dir()):
        entries = []
        for entry_dir in sorted(p for p in state_dir.iterdir() if p.is_dir()):
            entry = build_entry(state_dir.name, entry_dir)
            entries.append(entry)
            if entry["type"] == "unknown":
                warnings.append(
                    f"{state_dir.name}/{entry_dir.name}: no se pudo determinar "
                    "'Tipo' (falta description.md o el campo '**Tipo**')."
                )
            if state_dir.name == "inProgress" and entry["subStatus"] == "sin_descripcion":
                warnings.append(
                    f"inProgress/{entry_dir.name}: no tiene description.md."
                )

        by_type: dict[str, int] = {}
        for entry in entries:
            by_type[entry["type"]] = by_type.get(entry["type"], 0) + 1

        state_info = {
            "total": len(entries),
            "byType": by_type,
            "entries": entries,
        }

        if state_dir.name == "inProgress":
            sub_counts = {"descrito": 0, "listo_para_implementar": 0, "sin_descripcion": 0}
            for entry in entries:
                sub_counts[entry["subStatus"]] = sub_counts.get(entry["subStatus"], 0) + 1
            state_info["subStatus"] = sub_counts

        states[state_dir.name] = state_info

    totals_by_type: dict[str, int] = {}
    grand_total = 0
    for state_info in states.values():
        grand_total += state_info["total"]
        for type_name, count in state_info["byType"].items():
            totals_by_type[type_name] = totals_by_type.get(type_name, 0) + count

    return {
        "changesDir": str(changes_dir),
        "states": states,
        "totalsByType": totals_by_type,
        "grandTotal": grand_total,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/ms-context.json (default '/').",
    )
    args = parser.parse_args()

    # En consola de Windows, stdout puede usar un codepage distinto de UTF-8;
    # forzarlo evita mojibake en nombres/descripciones con acentos.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    changes_dir = load_changes_dir(root, args.work_folder)
    result = collect(changes_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
