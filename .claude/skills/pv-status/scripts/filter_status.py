#!/usr/bin/env python3
"""Lista filtrada de un unico estado (carpeta) de {changesDir}, para /pv-status <estado>.

A diferencia de collect_status.py (que da totales y agregados de todos los
estados), este script devuelve el detalle completo de las entradas de UN
solo estado, ya renderizado en markdown segun la plantilla
STATUS.filtered.template.md (no un JSON) -- asi el modelo que invoca este
script no necesita gastar tokens aplicando la plantilla el mismo, solo pegar
la salida tal cual.

Para cada entrada de la carpeta de estado se calculan cuatro columnas:
  - code: nombre de la subcarpeta.
  - tipo: 'todo' si el estado es 'todo' (pv-todo no usa campo Tipo); en
    cualquier otro estado, el campo '**Tipo**' de description.md
    ('change'/'fix'/'fast'); 'unknown' si no se encuentra o no hay
    description.md.
  - description: primeros 250 caracteres de la seccion '## Descripcion
    completa' de description.md (con "..." al final si se trunco); si esa
    seccion esta vacia o no existe, None. No se usa history.md como
    fallback: es historial de prompts de uso exclusivo de pv-new/pv-fix,
    ninguna otra skill (incluido pv-status) debe leerlo.
  - fecha: el campo '**Fecha**' de description.md si existe (formato tal
    cual esta escrito); si no, la fecha de modificacion (mtime) de
    description.md formateada como YYYY-MM-DD; si no hay description.md, la
    mtime de la propia carpeta.

La plantilla (STATUS.filtered.template.md, en la carpeta del skill) define
el formato de salida: un cuerpo con placeholders {estado}, {fechaGeneracion} y
{filas}, mas dos lineas de comentario HTML que el script
extrae y no imprime:
  <!-- ROW_TEMPLATE: ... -->   patron de una fila, con {código}/{tipo}/{descripción}/{fecha}
  <!-- EMPTY_TEMPLATE: ... --> texto a usar en {filas} si no hay entradas

No escribe nada en disco: imprime el markdown final por stdout.

Uso:
  python filter_status.py <estado>
  python filter_status.py closed --work-folder /
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import terminal_output as term  # noqa: E402

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "STATUS.filtered.template.md"

FECHA_RE = re.compile(r"\*\*Fecha\*\*\s*[:—-]\s*(.+)")
TIPO_RE = re.compile(r"\*\*Tipo\*\*\s*[:—-]\s*([A-Za-z]+)", re.IGNORECASE)
KNOWN_TYPES = {"change", "fix", "fast"}

TIPO_LABELS = {
    "change": "🆕 Change",
    "fix": "👾 Fix",
    "fast": "⚡ Fast",
    "todo": "💡 Todo",
    "unknown": "❓ Unknown",
}

# description.md tiene dos formatos segun la antiguedad de la entrada:
#  - antiguo: campo de lista "- **Descripcion completa**:" (contenido indentado)
#  - actual: cabecera markdown "## Descripcion completa"
# Ambos se soportan por alternancia; el limite de captura es el siguiente
# campo de lista a nivel superior ("- **Campo**") o la siguiente cabecera
# "##" (pero no "###" u otras subcabeceras), o el fin de fichero.
_BOUNDARY = r"(?=\n##\s|\n-\s*\*\*[^\n]+\*\*|\Z)"
DESCRIPCION_FULL_RE = re.compile(
    r"(?:^##\s*Descripci[oó]n completa\s*\n+|^-\s*\*\*Descripci[oó]n completa\*\*:?\s*\n*)(.+?)"
    + _BOUNDARY,
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/pv-status/scripts/
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
            "consultar el estado."
        )
    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} no tiene la seccion 'framework'. Ejecuta pv-init "
            "para completarlo."
        )
    return resolve_changes_dir(root, framework.get("workFolder", "/"))


DESCRIPTION_MAX_CHARS = 250


def summarize(text: str) -> str:
    # Colapsa saltos de linea/espacios repetidos antes de truncar, para que
    # el resumen no arrastre formato markdown.
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= DESCRIPTION_MAX_CHARS:
        return collapsed
    return collapsed[:DESCRIPTION_MAX_CHARS].rstrip() + "..."


def extract_description(text: str) -> str | None:
    match = DESCRIPCION_FULL_RE.search(text)
    if match and match.group(1).strip():
        return summarize(match.group(1))

    return None


def extract_fecha(text: str) -> str | None:
    match = FECHA_RE.search(text)
    if match:
        return match.group(1).strip()
    return None


def extract_tipo(text: str) -> str:
    match = TIPO_RE.search(text)
    tipo = match.group(1).strip().lower() if match else None
    return tipo if tipo in KNOWN_TYPES else "unknown"


def mtime_str(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")


def build_entry(state: str, entry_dir: Path) -> dict:
    description_path = entry_dir / "description.md"

    description = None
    fecha = None
    tipo = "todo" if state == "todo" else "unknown"

    if description_path.is_file():
        text = description_path.read_text(encoding="utf-8")
        description = extract_description(text)
        fecha = extract_fecha(text) or mtime_str(description_path)
        if state != "todo":
            tipo = extract_tipo(text)
    else:
        fecha = mtime_str(entry_dir)

    return {
        "code": entry_dir.name,
        "tipo": tipo,
        "description": description,
        "fecha": fecha,
    }


def collect(changes_dir: Path, state: str) -> dict:
    if not changes_dir.is_dir():
        raise SystemExit(f"No existe la carpeta de changes: {changes_dir}")

    available = sorted(p.name for p in changes_dir.iterdir() if p.is_dir())
    state_dir = changes_dir / state
    if not state_dir.is_dir():
        raise SystemExit(
            f"No existe el estado '{state}' en {changes_dir}. "
            f"Estados disponibles: {', '.join(available) if available else '(ninguno)'}."
        )

    entries = [
        build_entry(state, entry_dir)
        for entry_dir in sorted(p for p in state_dir.iterdir() if p.is_dir())
    ]

    return {
        "changesDir": str(changes_dir),
        "state": state,
        "total": len(entries),
        "entries": entries,
    }


ROW_TEMPLATE_RE = re.compile(r"<!--\s*ROW_TEMPLATE:\s*(.+?)\s*-->\n?")
EMPTY_TEMPLATE_RE = re.compile(r"<!--\s*EMPTY_TEMPLATE:\s*(.+?)\s*-->\n?")


def render_report(result: dict) -> str:
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    row_match = ROW_TEMPLATE_RE.search(template_text)
    empty_match = EMPTY_TEMPLATE_RE.search(template_text)
    if not row_match or not empty_match:
        raise SystemExit(
            f"La plantilla {TEMPLATE_PATH} no tiene los marcadores "
            "ROW_TEMPLATE/EMPTY_TEMPLATE esperados."
        )
    row_template = row_match.group(1)
    empty_template = empty_match.group(1)

    body = ROW_TEMPLATE_RE.sub("", template_text)
    body = EMPTY_TEMPLATE_RE.sub("", body)
    body = body.rstrip("\n") + "\n"

    if result["entries"]:
        filas = "\n".join(
            row_template.format(
                código=entry["code"],
                tipo=TIPO_LABELS.get(entry["tipo"], entry["tipo"]),
                descripción=entry["description"] or "—",
                fecha=entry["fecha"] or "—",
            )
            for entry in result["entries"]
        )
    else:
        filas = empty_template.format(estado=result["state"])

    return body.format(
        estado=result["state"],
        fechaGeneracion=datetime.now().strftime("%Y-%m-%d"),
        filas=filas,
    )


def render_terminal(result: dict) -> str:
    lines = [
        term.title(
            f"ESTADO DEL PROYECTO — {result['state']}",
            f"Generado: {datetime.now().strftime('%Y-%m-%d')}",
        ),
    ]

    if not result["entries"]:
        lines.append("")
        lines.append(term.wrap(f'(No hay ninguna entrada en el estado "{result["state"]}".)'))
        lines.append("")
        lines.append(term.hr())
        return "\n".join(lines) + "\n"

    for entry in result["entries"]:
        tipo = TIPO_LABELS.get(entry["tipo"], entry["tipo"])
        lines.append("")
        lines.append(f"{entry['code']}  [{tipo}]  {entry['fecha'] or '—'}")
        lines.append(term.wrap(entry["description"] or "—", indent="  "))

    lines.append("")
    lines.append(term.hr())
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", help="Nombre de la carpeta de estado a listar (p.ej. closed, implemented, inProgress, todo).")
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="Salida en texto plano sin markdown, ajustada a 70 columnas, para "
        "pegar en una terminal clasica. Uso exclusivo de pv.py: la skill "
        "pv-status (invocada desde el chat) no debe pasar este flag.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    changes_dir = load_changes_dir(root, args.work_folder)
    result = collect(changes_dir, args.state)
    print(render_terminal(result) if args.terminal else render_report(result))


if __name__ == "__main__":
    main()
