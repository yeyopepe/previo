#!/usr/bin/env python3
"""Helpers de formato para el modo --terminal de los scripts de pv-status.

Salida en texto plano sin markdown, ajustada a un ancho fijo de 70
columnas para pegarse tal cual en una terminal clasica. Lo usa
directamente pv.py (el menu de terminal del framework pv-*) al invocar
render_status.py / filter_status.py / list_todo.py con --terminal; la
propia skill pv-status (uso desde el chat) nunca debe pasar ese flag,
su salida de referencia sigue siendo el markdown por defecto.
"""

import os
import sys
import textwrap
import unicodedata

WIDTH = 70

# Mismo dorado que el nucleo del anillo de pv.py (RING_CHAR_COLORS['#']),
# reutilizado aqui para los titulos de seccion.
TITLE_COLOR = "\033[38;5;220m"
COLOR_RESET = "\033[0m"


def hr(char: str = "=") -> str:
    return char * WIDTH


def supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def colorize(text: str, color: str = TITLE_COLOR) -> str:
    if not supports_color():
        return text
    return f"{color}{text}{COLOR_RESET}"


def title(text: str, subtitle: str = "") -> str:
    lines = [hr(), colorize(text.center(WIDTH))]
    if subtitle:
        lines.append(subtitle.center(WIDTH))
    lines.append(hr())
    return "\n".join(lines)


def heading(text: str) -> str:
    underline = "-" * min(display_width(text), WIDTH)
    return f"{colorize(text)}\n{underline}"


def wrap(text: str, indent: str = "") -> str:
    return textwrap.fill(
        text,
        width=WIDTH,
        initial_indent=indent,
        subsequent_indent=" " * len(indent),
    )


def display_width(text: str) -> int:
    """Ancho visual aproximado (los emojis ocupan 2 columnas en fuente
    monoespaciada, pero len() los cuenta como 1 caracter)."""
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
