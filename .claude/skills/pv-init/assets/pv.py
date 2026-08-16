#!/usr/bin/env python3
"""Menú interactivo del framework ms-*, para uso directo desde terminal.

Este fichero lo genera/actualiza la skill ms-init en la raíz del repo — no
lo edites a mano, tus cambios se perderían la próxima vez que se
re-inicialice el framework (ficha maestra en
.claude/skills/ms-init/assets/ms.py).

Pensado para un usuario avanzado que quiere consultar o cerrar cambios del
framework ms-* sin pasar por Claude Code ni tener que recordar nombres de
scripts, rutas o parámetros: ejecuta este fichero y elige una opción del
menú.

La mayoría de las opciones son de solo lectura y delegan en los scripts de
la skill ms-status. La única que modifica algo es "Cerrar una entrada
implementada": mueve la carpeta de changes/implemented/{xxxx} a
changes/closed/{xxxx} (delegando en move-change.py de ms-internal-workflow,
que no toca el contenido de ningún fichero, solo la carpeta), y siempre
pide confirmación explícita antes de mover nada.

Uso:
  python3 ms.py
"""

import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATUS_SCRIPTS = ROOT / ".claude" / "skills" / "ms-status" / "scripts"
WORKFLOW_SCRIPTS = ROOT / ".claude" / "skills" / "ms-internal-workflow" / "scripts"
CHANGES_DIR = ROOT / "changes"
CONTEXT_PATH = ROOT / ".claude" / "ms-context.json"

WIDTH = 70
COLOR_RESET = "\033[0m"
GOLD = "\033[38;5;220m"
DARK_GRAY = "\033[38;5;238m"

# Degradado por densidad de carácter, calcado del anillo unico real: del
# brillo dorado palido de los trazos sueltos (".", ":", "-") a la sombra
# marron/granate del metal en las zonas mas densas ("#", "%").
RING_CHAR_COLORS = {
    ".": 223,
    ":": 220,
    "-": 214,
    "=": 208,
    "+": 166,
    "*": 130,
    "#": 94,
    "%": 52,
}

NOMBRE_RE = re.compile(r"\*\*Nombre\*\*\s*[:—-]\s*(.+)")


def supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def colorize(text: str, color: str) -> str:
    if not supports_color():
        return text
    return f"{color}{text}{COLOR_RESET}"


def colorize_ring_art(art: str) -> str:
    if not supports_color():
        return art

    out = []
    current_color = None
    for ch in art:
        color = RING_CHAR_COLORS.get(ch)
        if color != current_color:
            if current_color is not None:
                out.append(COLOR_RESET)
            if color is not None:
                out.append(f"\033[38;5;{color}m")
            current_color = color
        out.append(ch)
    if current_color is not None:
        out.append(COLOR_RESET)
    return "".join(out)


def enable_windows_ansi() -> None:
    if sys.platform != "win32":
        return
    import ctypes

    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    handle = ctypes.windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    if ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        ctypes.windll.kernel32.SetConsoleMode(
            handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        )


def hr(char: str = "=") -> None:
    print(colorize(char * WIDTH, DARK_GRAY))


def print_header(title: str) -> None:
    hr()
    print(colorize(title.center(WIDTH), GOLD))
    hr()


def wrap(text: str, indent: str = "") -> str:
    return textwrap.fill(
        text,
        width=WIDTH,
        initial_indent=indent,
        subsequent_indent=" " * len(indent),
    )

RING_ART = r"""
     ........                 
  :=. . ..:::::----:          
 -*:.:..:---=---:-====-.      
:*#-.       .:=*+==--==+=:    
++#*:            :-+*+==**+.  
++*##=              :+**==**: 	Previo: el framework de desarrollo
*+=*##*:              :**=+#*.	rápido y visual dirigido 100% por IA.
 *++***#*-.             +*=**:
  +*+******+-.           ***= 	Un script
   -**+++*####*+-:.      --:. 	para gobernarlos a todos.
     -++++**#*##***++===---:  
       .=*###+#****+**+--:    
           :=+*###%#*=:.   
"""


def run_script(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], cwd=ROOT)


def show_general_status() -> None:
    run_script(STATUS_SCRIPTS / "render_status.py", "--terminal")


def show_todo_ideas() -> None:
    run_script(STATUS_SCRIPTS / "list_todo.py", "--terminal")


def list_states() -> list[str]:
    if not CHANGES_DIR.is_dir():
        return []
    return sorted(p.name for p in CHANGES_DIR.iterdir() if p.is_dir())


def show_filtered_status() -> None:
    states = list_states()
    if not states:
        print(wrap(f"No hay carpetas de estado en {CHANGES_DIR}."))
        return

    print()
    hr("-")
    print("Estados disponibles:")
    for i, state in enumerate(states, start=1):
        print(wrap(f"{i}. {state}", indent="  "))
    hr("-")

    choice = input("Elige un estado (número, o vacío para cancelar): ").strip()
    if not choice:
        return

    try:
        state = states[int(choice) - 1]
    except (ValueError, IndexError):
        print("Opción no válida.")
        return

    run_script(STATUS_SCRIPTS / "filter_status.py", state, "--terminal")


def list_implemented_entries() -> list[tuple[str, str]]:
    implemented_dir = CHANGES_DIR / "implemented"
    if not implemented_dir.is_dir():
        return []

    entries = []
    for entry_dir in sorted(p for p in implemented_dir.iterdir() if p.is_dir()):
        nombre = "(sin nombre)"
        description_path = entry_dir / "description.md"
        if description_path.is_file():
            match = NOMBRE_RE.search(description_path.read_text(encoding="utf-8"))
            if match:
                nombre = match.group(1).splitlines()[0].strip().strip("` ")
        entries.append((entry_dir.name, nombre))
    return entries


def close_entry() -> None:
    entries = list_implemented_entries()
    if not entries:
        print(wrap("No hay ninguna entrada en changes/implemented/ pendiente de cerrar."))
        return

    print()
    hr("-")
    print("Entradas implementadas, pendientes de cerrar:")
    for i, (code, nombre) in enumerate(entries, start=1):
        print(wrap(f"{i}. {code} — {nombre}", indent="  "))
    print(wrap("t. Cerrar todos", indent="  "))
    hr("-")

    choice = input(
        "Elige una entrada a cerrar (número, 't' para cerrar todas, o vacío para cancelar): "
    ).strip().lower()
    if not choice:
        return

    if choice == "t":
        print(wrap(f"¿Confirmas mover las {len(entries)} entradas listadas a changes/closed/?"))
        confirm = input("(s/N): ").strip().lower()
        if confirm not in ("s", "si", "sí"):
            print("Cancelado.")
            return

        for code, _ in entries:
            close_change(code)
        return

    try:
        code, nombre = entries[int(choice) - 1]
    except (ValueError, IndexError):
        print("Opción no válida.")
        return

    print(wrap(f"¿Confirmas mover '{code} — {nombre}' a changes/closed/?"))
    confirm = input("(s/N): ").strip().lower()
    if confirm not in ("s", "si", "sí"):
        print("Cancelado.")
        return

    close_change(code)


def close_change(code: str) -> None:
    run_script(
        WORKFLOW_SCRIPTS / "move-change.py",
        "--xxxx", code,
        "--from", "implemented",
        "--to", "closed",
    )


MENU: list[tuple[str, "callable"]] = [
    ("Estado general del proyecto", show_general_status),
    ("Listado filtrado por estado (todo, inProgress, implemented...)", show_filtered_status),
    ("Ideas en todo/", show_todo_ideas),
    ("Cerrar una entrada implementada (mover a changes/closed/)", close_entry),
]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    enable_windows_ansi()

    if not CONTEXT_PATH.is_file():
        print(wrap("Este proyecto no tiene el framework ms-* inicializado."))
        print(wrap("Ejecuta primero /ms-init desde Claude Code."))
        return

    print(colorize_ring_art(RING_ART))
    
    exit_index = len(MENU) + 1

    while True:
        print()
        print_header("Previo: acciones")
        for i, (label, _) in enumerate(MENU, start=1):
            print(wrap(f"{i}. {label}", indent="  "))
        print(wrap(f"{exit_index}. Salir", indent="  "))
        hr()

        choice = input("Elige una opción: ").strip()
        if choice == "":
            continue

        try:
            index = int(choice)
        except ValueError:
            print("Opción no válida.")
            continue

        if index == exit_index:
            break

        try:
            _, action = MENU[index - 1]
        except IndexError:
            print("Opción no válida.")
            continue

        print()
        action()
        input("\nPulsa Enter para volver al menú...")


if __name__ == "__main__":
    main()
