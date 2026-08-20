#!/usr/bin/env python3
"""Formatting helpers for pv-status scripts' --terminal mode.

Plain-text output without markdown, fixed to a 70-column width so it can be
pasted as-is into a classic terminal. Used directly by pv.py (the pv-*
framework's terminal menu) when invoking render_status.py / filter_status.py
/ list_todo.py with --terminal; the pv-status skill itself (used from chat)
must never pass that flag -- its reference output is still the default
markdown.
"""

import os
import sys
import textwrap
import unicodedata

WIDTH = 70

# Same gold as pv.py's ring core (RING_CHAR_COLORS['#']), reused here for
# section titles.
TITLE_COLOR = "\033[38;5;220m"
COLOR_RESET = "\033[0m"


def supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def colorize(text: str, color: str = TITLE_COLOR) -> str:
    if not supports_color():
        return text
    return f"{color}{text}{COLOR_RESET}"


def hr(char: str = "=") -> str:
    return colorize(char * WIDTH)


def title(text: str, subtitle: str = "") -> str:
    lines = [hr(), colorize(text.center(WIDTH))]
    if subtitle:
        lines.append(subtitle.center(WIDTH))
    lines.append(hr())
    return "\n".join(lines)


def heading(text: str) -> str:
    underline = colorize("-" * min(display_width(text), WIDTH))
    return f"{colorize(text)}\n{underline}"


def wrap(text: str, indent: str = "") -> str:
    return textwrap.fill(
        text,
        width=WIDTH,
        initial_indent=indent,
        subsequent_indent=" " * len(indent),
    )


def display_width(text: str) -> int:
    """Approximate visual width (emoji take 2 columns in a monospace font,
    but len() counts them as 1 character)."""
    width = 0
    for ch in text:
        cp = ord(ch)
        is_emoji = (
            0x1F300 <= cp <= 0x1FAFF
            or 0x2600 <= cp <= 0x27BF
            or 0x2190 <= cp <= 0x21FF
            or unicodedata.east_asian_width(ch) in ("W", "F")
        )
        width += 2 if is_emoji else 1
    return width


def pad_display(text: str, target_width: int) -> str:
    return text + " " * max(0, target_width - display_width(text))
