#!/usr/bin/env python3
"""Interactive menu for the pv-* framework, for direct use from a terminal.

This file is generated/updated by the pv-init skill at the repo root — don't
edit it by hand, your changes would be lost the next time the framework is
re-initialized (master copy at
.claude/skills/pv-init/assets/pv.py).

Meant for an advanced user who wants to check or close pv-* framework
changes without going through Claude Code or having to remember script
names, paths, or parameters: run this file and choose a menu option.

Most options are read-only and delegate to the pv-status skill's scripts.
Two options modify something:
- "Close an implemented entry": moves the folder from
  changes/implemented/{xxxx} to changes/closed/{xxxx} (delegating to
  pv-internal-workflow's move-change.py, which doesn't touch any file's
  content, only the folder), and always asks for explicit confirmation
  before moving anything.
- "Sync skill models per pv-context.json": delegates to pv-init's
  sync-skill-models.py, which propagates pv-context.json's skillModels to
  each 'pv-*' SKILL.md's frontmatter (model/effort).

Usage:
  python3 pv.py
"""

import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATUS_SCRIPTS = ROOT / ".claude" / "skills" / "pv-status" / "scripts"
WORKFLOW_SCRIPTS = ROOT / ".claude" / "skills" / "pv-internal-workflow" / "scripts"
INIT_SCRIPTS = ROOT / ".claude" / "skills" / "pv-init" / "scripts"
CHANGES_DIR = ROOT / "changes"
CONTEXT_PATH = ROOT / ".claude" / "pv-context.json"

WIDTH = 70
COLOR_RESET = "\033[0m"
GOLD = "\033[38;5;220m"
DARK_GRAY = "\033[38;5;238m"

# Gradient by character density, modeled on the actual One Ring: from the
# pale golden glow of the loose strokes (".", ":", "-") to the brown/maroon
# shadow of the metal in the densest areas ("#", "%").
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

NAME_RE = re.compile(r"\*\*Name\*\*\s*[:—-]\s*(.+)")


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
++*##=              :+**==**: 	Previo: the AI-driven, visual,
*+=*##*:              :**=+#*.	rapid-development framework.
 *++***#*-.             +*=**:
  +*+******+-.           ***= 	One script
   -**+++*####*+-:.      --:. 	to rule them all.
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
        print(wrap("There are no changes yet in this project."))
        return

    print()
    hr("-")
    print("Available states:")
    for i, state in enumerate(states, start=1):
        print(wrap(f"{i}. {state}", indent="  "))
    hr("-")

    choice = input("Choose a state (number, or empty to cancel): ").strip()
    if not choice:
        return

    try:
        state = states[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid option.")
        return

    run_script(STATUS_SCRIPTS / "filter_status.py", state, "--terminal")


def list_implemented_entries() -> list[tuple[str, str]]:
    implemented_dir = CHANGES_DIR / "implemented"
    if not implemented_dir.is_dir():
        return []

    entries = []
    for entry_dir in sorted(p for p in implemented_dir.iterdir() if p.is_dir()):
        name = "(no name)"
        description_path = entry_dir / "description.md"
        if description_path.is_file():
            match = NAME_RE.search(description_path.read_text(encoding="utf-8"))
            if match:
                name = match.group(1).splitlines()[0].strip().strip("` ")
        entries.append((entry_dir.name, name))
    return entries


def close_entry() -> None:
    entries = list_implemented_entries()
    if not entries:
        print(wrap("There's no entry in changes/implemented/ pending closure."))
        return

    print()
    hr("-")
    print("Implemented entries, pending closure:")
    for i, (code, name) in enumerate(entries, start=1):
        print(wrap(f"{i}. {code} — {name}", indent="  "))
    print(wrap("a. Close all", indent="  "))
    hr("-")

    choice = input(
        "Choose an entry to close (number, 'a' to close all, or empty to cancel): "
    ).strip().lower()
    if not choice:
        return

    if choice == "a":
        print(wrap(f"Confirm moving the {len(entries)} listed entries to changes/closed/?"))
        confirm = input("(y/N): ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Cancelled.")
            return

        for code, _ in entries:
            close_change(code)
        return

    try:
        code, name = entries[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid option.")
        return

    print(wrap(f"Confirm moving '{code} — {name}' to changes/closed/?"))
    confirm = input("(y/N): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Cancelled.")
        return

    close_change(code)


def close_change(code: str) -> None:
    run_script(
        WORKFLOW_SCRIPTS / "move-change.py",
        "--xxxx", code,
        "--from", "implemented",
        "--to", "closed",
    )


def sync_skill_models() -> None:
    run_script(INIT_SCRIPTS / "sync-skill-models.py")


MENU: list[tuple[str, "callable"]] = [
    ("General project status", show_general_status),
    ("Listing filtered by state (todo, inProgress, implemented...)", show_filtered_status),
    ("Ideas in todo/", show_todo_ideas),
    ("Close an implemented entry (move to changes/closed/)", close_entry),
    ("Sync skill models per pv-context.json", sync_skill_models),
]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    enable_windows_ansi()

    if not CONTEXT_PATH.is_file():
        print(wrap("This project doesn't have the pv-* framework initialized."))
        print(wrap("Run /pv-init first from Claude Code."))
        return

    print(colorize_ring_art(RING_ART))

    exit_index = len(MENU) + 1

    while True:
        print()
        print_header("Previo: actions")
        for i, (label, _) in enumerate(MENU, start=1):
            print(wrap(f"{i}. {label}", indent="  "))
        print(wrap(f"{exit_index}. Exit", indent="  "))
        hr()

        choice = input("Choose an option: ").strip()
        if choice == "":
            continue

        try:
            index = int(choice)
        except ValueError:
            print("Invalid option.")
            continue

        if index == exit_index:
            break

        try:
            _, action = MENU[index - 1]
        except IndexError:
            print("Invalid option.")
            continue

        print()
        action()
        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main()
