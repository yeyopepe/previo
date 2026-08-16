#!/usr/bin/env python3
"""Renderiza el informe completo de /pv-status a partir de STATUS.template.md.

Reutiliza collect_status.collect() para reunir todos los datos (estados,
totales por tipo, subStatus de inProgress, avisos) y aplica el mapeo
completo descrito en el paso 2 de SKILL.md sobre la plantilla
STATUS.template.md, igual que filter_status.py ya hace para el modo de un
solo estado -- asi el modelo que invoca este script no gasta tokens
mapeando campos ni redactando las listas, solo pega la salida tal cual.

La plantilla define, ademas de los placeholders escalares de la tabla,
cuatro patrones de fila reutilizables y tres secciones opcionales que se
eliminan enteras (cabecera incluida) cuando no aplican:

  <!-- ROW_ENTRY: ... -->    fila de "implementando"/"pendientes" (xxxx/nombre/tipo)
  <!-- EMPTY_ENTRY: ... -->  texto si una de esas dos listas esta vacia
  <!-- ROW_FAST: ... -->     fila de "cambios fast implementados"
  <!-- ROW_IDEA: ... -->     fila de "ideas en todo/"
  <!-- ROW_AVISO: ... -->    fila de "avisos"
  <!-- EMPTY_IDEAS: ... -->  texto si no hay ninguna idea en todo/

  <!-- SECTION:sinDescripcion --> ... <!-- /SECTION:sinDescripcion -->
  <!-- SECTION:fast --> ... <!-- /SECTION:fast -->
  <!-- SECTION:avisos --> ... <!-- /SECTION:avisos -->

La seccion "Cambios fast implementados" se omite por defecto aunque haya
entradas fast: solo se incluye si se pasa --show-fast (usar unicamente
cuando el usuario la pida explicitamente).

No escribe nada en disco: imprime el markdown final por stdout.

Uso:
  python render_status.py
  python render_status.py --work-folder /
  python render_status.py --show-fast
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_status import collect, load_changes_dir, repo_root  # noqa: E402
import terminal_output as term  # noqa: E402

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "STATUS.template.md"

FECHA_RE = re.compile(r"\*\*Fecha\*\*\s*[:—-]\s*(.+)")

ROW_RE_TEMPLATE = r"<!--\s*{name}:\s*(.+?)\s*-->\n?"
SECTION_RE_TEMPLATE = r"<!--\s*SECTION:{name}\s*-->\n?(.*?)<!--\s*/SECTION:{name}\s*-->\n?"

TYPE_ICONS = {"change": "🆕", "fix": "👾", "fast": "⚡", "unknown": "❓"}

BAR_WIDTH = 20
STATE_ORDER = ["todo", "inProgress", "implemented", "closed"]
STATE_LABELS = {
    "todo": "💡 Todo",
    "inProgress": "🔧 En progreso",
    "implemented": "✅ Implementado",
    "closed": "📦 Cerrado",
}


def render_bars(counts: dict[str, int]) -> str:
    """Barras de texto proporcionales al estado con mas entradas, deterministas."""
    values = [counts.get(state, 0) for state in STATE_ORDER]
    max_count = max(values) or 1
    label_width = max(term.display_width(STATE_LABELS[state]) for state in STATE_ORDER)
    count_width = max(len(str(v)) for v in values)

    lines = []
    for state in STATE_ORDER:
        count = counts.get(state, 0)
        filled = round(count / max_count * BAR_WIDTH)
        bar = "█" * filled + "░" * (BAR_WIDTH - filled)
        label = term.pad_display(STATE_LABELS[state], label_width)
        lines.append(f"{label}  {bar}  {str(count).rjust(count_width)}")
    return "\n".join(lines)


def extract_fecha(entry_dir: Path) -> str:
    description_path = entry_dir / "description.md"
    if description_path.is_file():
        text = description_path.read_text(encoding="utf-8")
        match = FECHA_RE.search(text)
        if match:
            return match.group(1).strip()
        return datetime.fromtimestamp(description_path.stat().st_mtime).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(entry_dir.stat().st_mtime).strftime("%Y-%m-%d")


def extract_marker(template_text: str, name: str) -> str:
    match = re.search(ROW_RE_TEMPLATE.format(name=name), template_text)
    if not match:
        raise SystemExit(f"La plantilla {TEMPLATE_PATH} no tiene el marcador {name}.")
    return match.group(1)


def strip_markers(text: str, *names: str) -> str:
    for name in names:
        text = re.sub(ROW_RE_TEMPLATE.format(name=name), "", text)
    return text


def apply_section(text: str, name: str, keep: bool) -> str:
    pattern = re.compile(SECTION_RE_TEMPLATE.format(name=name), re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"La plantilla {TEMPLATE_PATH} no tiene la seccion {name}.")
    replacement = match.group(1) if keep else ""
    return pattern.sub(replacement, text)


def entry_lines(entries: list[dict], row_template: str, empty_template: str) -> str:
    if not entries:
        return empty_template
    return "\n".join(
        row_template.format(
            xxxx=entry["code"],
            nombre=entry["name"] or "(sin nombre)",
            tipo=entry["type"],
            icono=TYPE_ICONS.get(entry["type"], "❓"),
        )
        for entry in entries
    )


def split_in_progress(states: dict) -> tuple[list[dict], list[dict], list[dict]]:
    entries = states.get("inProgress", {}).get("entries", [])
    to_implement = [e for e in entries if e["subStatus"] == "listo_para_implementar"]
    pending = [e for e in entries if e["subStatus"] == "descrito"]
    sin_descripcion = [e for e in entries if e["subStatus"] == "sin_descripcion"]
    return to_implement, pending, sin_descripcion


def collect_fast_entries(states: dict) -> list[dict]:
    implemented_entries = states.get("implemented", {}).get("entries", [])
    closed_entries = states.get("closed", {}).get("entries", [])
    return [e for e in implemented_entries if e["type"] == "fast"] + [
        e for e in closed_entries if e["type"] == "fast"
    ]


def render(result: dict, changes_dir: Path, show_fast: bool = False) -> str:
    states = result["states"]
    totals = result["totalsByType"]

    def state_count(state: str, type_: str) -> int:
        return states.get(state, {}).get("byType", {}).get(type_, 0)

    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")

    row_entry = extract_marker(template_text, "ROW_ENTRY")
    empty_entry = extract_marker(template_text, "EMPTY_ENTRY")
    row_fast = extract_marker(template_text, "ROW_FAST")
    row_idea = extract_marker(template_text, "ROW_IDEA")
    row_aviso = extract_marker(template_text, "ROW_AVISO")
    empty_ideas = extract_marker(template_text, "EMPTY_IDEAS")

    # Las lineas de marcador (ROW_*/EMPTY_*) contienen sus propios
    # placeholders literales ({xxxx}, {código}...) que no forman parte de
    # los kwargs del format() final: hay que quitarlas del texto ANTES de
    # aplicar secciones y formatear, o format() fallaria con KeyError.
    template_text = strip_markers(
        template_text, "ROW_ENTRY", "EMPTY_ENTRY", "ROW_FAST", "ROW_IDEA", "ROW_AVISO", "EMPTY_IDEAS"
    )

    to_implement, pending, sin_descripcion = split_in_progress(states)
    implemented_entries = states.get("implemented", {}).get("entries", [])
    fast_entries = collect_fast_entries(states)
    todo_entries = states.get("todo", {}).get("entries", [])

    body = apply_section(template_text, "sinDescripcion", keep=bool(sin_descripcion))
    body = apply_section(body, "fast", keep=show_fast and bool(fast_entries))
    body = apply_section(body, "avisos", keep=bool(result["warnings"]))

    body = body.format(
        fechaGeneracion=datetime.now().strftime("%Y-%m-%d"),
        resumenBarras=render_bars(
            {state: states.get(state, {}).get("total", 0) for state in STATE_ORDER}
        ),
        todoTotal=states.get("todo", {}).get("total", 0),
        inProgressChange=state_count("inProgress", "change"),
        inProgressFix=state_count("inProgress", "fix"),
        inProgressTotal=states.get("inProgress", {}).get("total", 0),
        implementedChange=state_count("implemented", "change"),
        implementedFix=state_count("implemented", "fix"),
        implementedFast=state_count("implemented", "fast"),
        implementedTotal=states.get("implemented", {}).get("total", 0),
        closedChange=state_count("closed", "change"),
        closedFix=state_count("closed", "fix"),
        closedFast=state_count("closed", "fast"),
        closedTotal=states.get("closed", {}).get("total", 0),
        changeTotal=totals.get("change", 0),
        fixTotal=totals.get("fix", 0),
        fastTotal=totals.get("fast", 0),
        totalTotal=result["grandTotal"],
        toImplementTotal=len(to_implement),
        filasImplementar=entry_lines(to_implement, row_entry, empty_entry),
        pendingTotal=len(pending),
        filasPendientes=entry_lines(pending, row_entry, empty_entry),
        toCloseTotal=states.get("implemented", {}).get("total", 0),
        filasListas=entry_lines(implemented_entries, row_entry, empty_entry),
        filasSinDescripcion=", ".join(e["code"] for e in sin_descripcion),
        filasFast="\n".join(
            row_fast.format(código=e["code"], nombre=e["name"] or "(sin nombre)", fecha=extract_fecha(changes_dir / ("implemented" if e in implemented_entries else "closed") / e["code"]))
            for e in fast_entries
        ),
        filasIdeas=(
            "\n".join(row_idea.format(codigo=e["code"], idea=e["name"] or "(sin idea)") for e in todo_entries)
            if todo_entries
            else empty_ideas
        ),
        filasAvisos="\n".join(row_aviso.format(aviso=w) for w in result["warnings"]),
    )

    return body.rstrip("\n") + "\n"


def render_terminal_table(states: dict, totals: dict, grand_total: int) -> list[str]:
    def state_count(state: str, type_: str) -> int:
        return states.get(state, {}).get("byType", {}).get(type_, 0)

    def row(label: str, change, fix, fast, todo, total) -> str:
        return (
            term.pad_display(str(label), 16)
            + str(change).rjust(8)
            + str(fix).rjust(6)
            + str(fast).rjust(7)
            + str(todo).rjust(7)
            + str(total).rjust(8)
        )

    todo_total = states.get("todo", {}).get("total", 0)
    lines = [
        row("Estado", "Change", "Fix", "Fast", "Todo", "Total"),
        row(
            STATE_LABELS["todo"], "—", "—", "—", todo_total, todo_total
        ),
        row(
            STATE_LABELS["inProgress"],
            state_count("inProgress", "change"),
            state_count("inProgress", "fix"),
            "—",
            "—",
            states.get("inProgress", {}).get("total", 0),
        ),
        row(
            STATE_LABELS["implemented"],
            state_count("implemented", "change"),
            state_count("implemented", "fix"),
            state_count("implemented", "fast"),
            "—",
            states.get("implemented", {}).get("total", 0),
        ),
        row(
            STATE_LABELS["closed"],
            state_count("closed", "change"),
            state_count("closed", "fix"),
            state_count("closed", "fast"),
            "—",
            states.get("closed", {}).get("total", 0),
        ),
        row(
            "Total",
            totals.get("change", 0),
            totals.get("fix", 0),
            totals.get("fast", 0),
            todo_total,
            grand_total,
        ),
    ]
    return lines


def render_terminal_entries(title_text: str, entries: list[dict]) -> list[str]:
    block = ["", term.colorize(f"{title_text} ({len(entries)})")]
    if not entries:
        block.append(term.wrap("(ninguno)", indent="  "))
    else:
        for entry in entries:
            nombre = entry["name"] or "(sin nombre)"
            block.append(term.wrap(f"- {entry['code']} — {nombre}", indent="  "))
    return block


def render_terminal(result: dict, changes_dir: Path, show_fast: bool = False) -> str:
    states = result["states"]
    totals = result["totalsByType"]

    to_implement, pending, sin_descripcion = split_in_progress(states)
    implemented_entries = states.get("implemented", {}).get("entries", [])
    fast_entries = collect_fast_entries(states)
    todo_entries = states.get("todo", {}).get("entries", [])

    lines = [
        term.title("ESTADO DEL PROYECTO", f"Generado: {datetime.now().strftime('%Y-%m-%d')}"),
        "",
        render_bars({state: states.get(state, {}).get("total", 0) for state in STATE_ORDER}),
        "",
        term.hr("-"),
        *render_terminal_table(states, totals, result["grandTotal"]),
        term.hr("-"),
        "",
        term.heading("🔧 EN PROGRESO"),
    ]

    lines += render_terminal_entries("🟢 Listos para revisar y cerrar", implemented_entries)
    lines += render_terminal_entries("🟡 Pendientes de analisis tecnico", pending)
    lines += render_terminal_entries("🟠 Planificados, pendientes de implementar", to_implement)

    if sin_descripcion:
        lines.append("")
        lines.append(
            term.wrap(
                "Entradas sin description.md (anomalas): "
                + ", ".join(e["code"] for e in sin_descripcion)
            )
        )

    if show_fast and fast_entries:
        lines.append("")
        lines.append(term.heading("⚡ CAMBIOS FAST IMPLEMENTADOS"))
        for entry in fast_entries:
            state_dir = "implemented" if entry in implemented_entries else "closed"
            fecha = extract_fecha(changes_dir / state_dir / entry["code"])
            nombre = entry["name"] or "(sin nombre)"
            lines.append(term.wrap(f"- {entry['code']} — {nombre} ({fecha})", indent="  "))

    lines.append("")
    lines.append(term.heading("💡 IDEAS EN TODO/"))
    if todo_entries:
        for entry in todo_entries:
            idea = entry["name"] or "(sin idea)"
            lines.append(term.wrap(f"- {entry['code']}: {idea}", indent="  "))
    else:
        lines.append(term.wrap("(No hay ninguna idea apuntada en todo/.)"))

    if result["warnings"]:
        lines.append("")
        lines.append(term.heading("⚠️ AVISOS"))
        for warning in result["warnings"]:
            lines.append(term.wrap(f"- {warning}", indent="  "))

    lines.append("")
    lines.append(term.hr())

    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--show-fast",
        action="store_true",
        help="Incluye la seccion 'Cambios fast implementados'. Omitida por defecto: "
        "solo pasar este flag cuando el usuario la pida explicitamente.",
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
    result = collect(changes_dir)
    if args.terminal:
        print(render_terminal(result, changes_dir, show_fast=args.show_fast))
    else:
        print(render(result, changes_dir, show_fast=args.show_fast))


if __name__ == "__main__":
    main()
