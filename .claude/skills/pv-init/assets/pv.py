#!/usr/bin/env python3
"""Interactive menu for the pv-* framework, for direct use from a terminal.

This file is generated/updated at the repo root by install.sh/install.ps1 on
every install or update, and also by the pv-init skill on every run — don't
edit it by hand, your changes would be lost the next time either happens
(master copy at .claude/skills/pv-init/assets/pv.py).

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
- "Sync skill models per pv-context.json" (inside the "Configuration"
  submenu): delegates to pv-init's sync-skill-models.py, which propagates
  pv-context.json's skillModels to each 'pv-*' SKILL.md's frontmatter
  (model/effort).

"Check versions" opens a submenu that lists {workFolder}/versions/{XXXX}/
folders and prints the chosen one's changelog.md.

Design notes (screen types, colors, how to extend this menu) live in
.claude/pv-design-onescript.es.md -- read it before adding a new menu,
submenu, or screen type.

Usage:
  python3 pv.py
"""

import json
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
CONTEXT_PATH = ROOT / ".claude" / "pv-context.json"


# =============================================================================
# Rendering primitives (color, width, low-level text helpers)
# =============================================================================
#
# Two-level color hierarchy, applied per whole screen block, never mixed
# within the same block:
#   - GOLD:      menu screens (print_header/run_menu) -- "you're navigating"
#   - DARK_GRAY: selection and info screens (show_selection/show_info) --
#                "you're viewing or picking data"
# See .claude/pv-design-onescript.es.md > "Estilo por Tipo de Pantalla" for
# the full rationale and exact mockups.

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


def hr(char: str = "=", color: str = DARK_GRAY) -> None:
    print(colorize(char * WIDTH, color))


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
  +*+******+-.           ***= 	One script, growing
   -**+++*####*+-:.      --:. 	to manage more.
     -++++**#*##***++===---:
       .=*###+#****+**+--:
           :=+*###%#*=:.
"""


# =============================================================================
# Screen-type helpers
# =============================================================================
#
# Every interactive screen in this file is one of these building blocks.
# Adding a new menu, submenu, or list should mean calling one of these --
# not hand-rolling hr()/print() calls. See .claude/pv-design-onescript.es.md
# for the full catalogue of screen types and their exact appearance.


def print_header(title: str) -> None:
    """Menu-screen header: GOLD rule + centered GOLD title + GOLD rule."""
    hr("=", GOLD)
    print(colorize(title.center(WIDTH), GOLD))
    hr("=", GOLD)


def show_selection(
    title: str, options: list[str], prompt: str, extra_option: tuple[str, str] | None = None
) -> int | str | None:
    """Selection screen: numbered list framed by DARK_GRAY '-' rules.

    Returns the chosen option's 0-based index into `options`, the
    extra_option's key (lowercased) if picked, or None if the user
    cancelled (empty input) or entered something invalid. Returning an
    index rather than the option's text avoids ambiguity when two options
    render the same label. `extra_option` is a (key, label) pair for a
    non-numeric choice, e.g. ("a", "Close all") -- see close_entry() for a
    real usage.
    """
    print()
    hr("-")
    print(title)
    for i, option in enumerate(options, start=1):
        print(wrap(f"{i}. {option}", indent="  "))
    if extra_option:
        key, label = extra_option
        print(wrap(f"{key}. {label}", indent="  "))
    hr("-")

    choice = input(prompt).strip()
    if not choice:
        return None

    if extra_option and choice.lower() == extra_option[0].lower():
        return choice.lower()

    index = int(choice) - 1 if choice.lstrip("-").isdigit() else -1
    if 0 <= index < len(options):
        return index

    print("Invalid option.")
    return None


def show_info(lines: list[str], framed: bool = True) -> None:
    """Info screen: plain content, optionally framed by DARK_GRAY '-' rules.

    Use framed=True for content worth setting apart (e.g. a changelog's raw
    text); framed=False for a short paragraph that doesn't need a frame
    (e.g. a one-off status message).
    """
    print()
    if framed:
        hr("-")
    for line in lines:
        print(line)
    if framed:
        hr("-")


def confirm(question: str) -> bool:
    """Yes/no confirmation, no frame of its own -- nests inside whatever
    screen (usually a Selection) triggered it."""
    print(wrap(question))
    answer = input("(y/N): ").strip().lower()
    return answer in ("y", "yes")


# =============================================================================
# Framework paths and shared lookups
# =============================================================================


def run_script(script: Path, *args: str) -> None:
    subprocess.run([sys.executable, str(script), *args], cwd=ROOT)


def work_root() -> Path:
    # workFolder is always relative to the repo root, whether or not it
    # carries a leading "/" (that's only a convention to make it visually
    # explicit) -- Path("/a") / "/b" would otherwise discard "a" entirely,
    # since pathlib treats a leading-slash operand as its own absolute path.
    context = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
    work_folder_rel = context.get("framework", {}).get("workFolder", "/")
    return ROOT / (work_folder_rel or "").lstrip("/")


def changes_dir() -> Path:
    return work_root() / "changes"


def versions_dir() -> Path:
    return work_root() / "versions"


# =============================================================================
# Actions -- root menu
# =============================================================================


# render_status.py/list_todo.py/filter_status.py (below) draw their own
# "--terminal" output via the sibling module pv-status/scripts/terminal_output.py
# -- a separate color/hr()/title() implementation, not this file's. If a
# screen delegated to one of these three scripts looks wrong, the fix is
# there, not here. See .claude/pv-design-onescript.es.md > "Diagrama de
# Componentes" / "Info delegada".


def show_general_status() -> None:
    run_script(STATUS_SCRIPTS / "render_status.py", "--terminal")


def show_todo_ideas() -> None:
    run_script(STATUS_SCRIPTS / "list_todo.py", "--terminal")


def list_states() -> list[str]:
    changes = changes_dir()
    if not changes.is_dir():
        return []
    return sorted(p.name for p in changes.iterdir() if p.is_dir())


def show_filtered_status() -> None:
    states = list_states()
    if not states:
        show_info([wrap("There are no changes yet in this project.")], framed=False)
        return

    index = show_selection(
        "Available states:", states, "Choose a state (number, or empty to cancel): "
    )
    if index is None:
        return

    run_script(STATUS_SCRIPTS / "filter_status.py", states[index], "--terminal")


def list_implemented_entries() -> list[tuple[str, str]]:
    implemented_dir = changes_dir() / "implemented"
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
        show_info(
            [wrap("There's no entry in changes/implemented/ pending closure.")], framed=False
        )
        return

    labels = [f"{code} — {name}" for code, name in entries]
    choice = show_selection(
        "Implemented entries, pending closure:",
        labels,
        "Choose an entry to close (number, 'a' to close all, or empty to cancel): ",
        extra_option=("a", "Close all"),
    )
    if choice is None:
        return

    if choice == "a":
        if confirm(f"Confirm moving the {len(entries)} listed entries to changes/closed/?"):
            for code, _ in entries:
                close_change(code)
        else:
            print("Cancelled.")
        return

    code, _ = entries[choice]
    if confirm(f"Confirm moving '{labels[choice]}' to changes/closed/?"):
        close_change(code)
    else:
        print("Cancelled.")


def close_change(code: str) -> None:
    run_script(
        WORKFLOW_SCRIPTS / "move-change.py",
        "--xxxx", code,
        "--from", "implemented",
        "--to", "closed",
    )


# =============================================================================
# Actions -- Configuration submenu
# =============================================================================


def sync_skill_models() -> None:
    run_script(INIT_SCRIPTS / "sync-skill-models.py")


def show_settings_menu() -> None:
    run_menu(
        "Previo: settings",
        [("Sync skill models per pv-context.json", sync_skill_models)],
        "Back",
    )


show_settings_menu.is_submenu = True


# =============================================================================
# Actions -- Versions submenu
# =============================================================================


def list_versions() -> list[str]:
    versions = versions_dir()
    if not versions.is_dir():
        return []
    return sorted(p.name for p in versions.iterdir() if p.is_dir())


def show_version_changelog() -> None:
    versions = list_versions()
    if not versions:
        show_info([wrap("There are no versions yet in this project.")], framed=False)
        return

    index = show_selection(
        "Available versions:", versions, "Choose a version (number, or empty to cancel): "
    )
    if index is None:
        return

    version = versions[index]
    changelog_path = versions_dir() / version / "changelog.md"
    if not changelog_path.is_file():
        show_info([wrap(f"'{version}' has no changelog.md.")], framed=False)
        return

    show_info([changelog_path.read_text(encoding="utf-8")])


def check_closed_temp() -> None:
    temp_dir = changes_dir() / "closed" / "temp"
    if not temp_dir.is_dir():
        show_info([wrap("changes/closed/temp/ doesn't exist. Nothing pending.")], framed=False)
        return

    entries = sorted(p.name for p in temp_dir.iterdir())
    if not entries:
        show_info(
            [wrap("changes/closed/temp/ exists but is empty. Nothing pending.")], framed=False
        )
        return

    lines = [
        wrap(
            "changes/closed/temp/ isn't empty — the versioning process (pv-version) "
            "has either failed or is currently in progress:"
        )
    ]
    lines += [wrap(f"- {entry}", indent="  ") for entry in entries]
    show_info(lines, framed=False)


def show_versions_menu() -> None:
    run_menu(
        "Previo: versions",
        [
            ("List versions and read their changelog", show_version_changelog),
            ("Check changes/closed/temp/ is clear", check_closed_temp),
        ],
        "Back",
    )


show_versions_menu.is_submenu = True


# =============================================================================
# Root menu definition
# =============================================================================
#
# To add a new top-level option: write an action function above (or a new
# `show_*_menu()` + mark it `.is_submenu = True` for a submenu), then append
# a (label, action) tuple here. To add a new submenu, follow the pattern of
# show_settings_menu()/show_versions_menu() above.

MENU: list[tuple[str, "callable"]] = [
    ("General project status", show_general_status),
    ("Listing filtered by state (todo, inProgress, implemented...)", show_filtered_status),
    ("Ideas in todo/", show_todo_ideas),
    ("Close an implemented entry (move to changes/closed/)", close_entry),
    ("Configuration", show_settings_menu),
    ("Check versions", show_versions_menu),
]


# =============================================================================
# Menu engine
# =============================================================================


def run_menu(
    title: str, items: list[tuple[str, "callable"]], last_label: str
) -> None:
    last_index = len(items) + 1

    while True:
        print()
        print_header(title)
        for i, (label, _) in enumerate(items, start=1):
            print(wrap(f"{i}. {label}", indent="  "))
        print(wrap(f"{last_index}. {last_label}", indent="  "))
        hr("=", GOLD)

        choice = input("Choose an option: ").strip()
        if choice == "":
            continue

        try:
            index = int(choice)
        except ValueError:
            print("Invalid option.")
            continue

        if index == last_index:
            return

        try:
            _, action = items[index - 1]
        except IndexError:
            print("Invalid option.")
            continue

        print()
        action()
        if not getattr(action, "is_submenu", False):
            input("\nPress Enter to return to the menu...")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    enable_windows_ansi()

    if not CONTEXT_PATH.is_file():
        print(wrap("This project doesn't have the pv-* framework initialized."))
        print(wrap("Run /pv-init first from Claude Code."))
        return

    print(colorize_ring_art(RING_ART))

    run_menu("Previo MAIN MENU", MENU, "Exit")


if __name__ == "__main__":
    main()
