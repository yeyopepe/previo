#!/usr/bin/env python3
"""Renders /pv-status's full report from STATUS.template.md.

Reuses collect_status.collect() to gather all the data (states, totals by
type, inProgress subStatus, warnings) and applies the full mapping
described in SKILL.md's step 2 onto the STATUS.template.md template, same
as filter_status.py already does for single-state mode -- this way the
model invoking this script doesn't spend tokens mapping fields or drafting
the lists, it just pastes the output as-is.

Besides the table's scalar placeholders, the template defines four
reusable row patterns and three optional sections that get removed
entirely (including their heading) when they don't apply:

  <!-- ROW_ENTRY: ... -->    "in progress"/"pending" row (xxxx/name/type/risk)
  <!-- EMPTY_ENTRY: ... -->  text if one of those two lists is empty
  <!-- ROW_FAST: ... -->     "implemented fast changes" row
  <!-- ROW_IDEA: ... -->     "ideas in todo/" row
  <!-- ROW_WARNING: ... -->  "warnings" row
  <!-- EMPTY_IDEAS: ... -->  text if there are no ideas in todo/

  <!-- SECTION:noDescription --> ... <!-- /SECTION:noDescription -->
  <!-- SECTION:fast --> ... <!-- /SECTION:fast -->
  <!-- SECTION:warnings --> ... <!-- /SECTION:warnings -->

The "Implemented fast changes" section is omitted by default even if there
are fast entries: it's only included if --show-fast is passed (use only
when the user explicitly asks for it).

Writes nothing to disk: prints the final markdown to stdout.

Usage:
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

ROW_RE_TEMPLATE = r"<!--\s*{name}:\s*(.+?)\s*-->\n?"
SECTION_RE_TEMPLATE = r"<!--\s*SECTION:{name}\s*-->\n?(.*?)<!--\s*/SECTION:{name}\s*-->\n?"

TYPE_ICONS = {"change": "🆕", "fix": "👾", "fast": "⚡", "unknown": "❓"}

BAR_WIDTH = 20
STATE_ORDER = ["todo", "inProgress", "implemented", "closed"]
STATE_LABELS = {
    "todo": "💡 Todo",
    "inProgress": "🔧 In progress",
    "implemented": "✅ Implemented",
    "closed": "📦 Closed",
}


def render_bars(counts: dict[str, int]) -> str:
    """Text bars proportional to the state with the most entries, deterministic."""
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


def count_versions(changes_dir: Path) -> int:
    # versions/ is a sibling of changes/ under the same workFolder --
    # collect_status.py only resolves changes_dir, so versions_dir is
    # derived from it here rather than duplicating workFolder resolution.
    versions_dir = changes_dir.parent / "versions"
    if not versions_dir.is_dir():
        return 0
    return sum(1 for p in versions_dir.iterdir() if p.is_dir())


def extract_date(entry_dir: Path) -> str:
    description_path = entry_dir / "description.md"
    if description_path.is_file():
        text = description_path.read_text(encoding="utf-8")
        match = re.search(r"\*\*Creation date\*\*\s*[:—-]\s*(.+)", text)
        if match:
            return match.group(1).strip()
        return datetime.fromtimestamp(description_path.stat().st_mtime).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(entry_dir.stat().st_mtime).strftime("%Y-%m-%d")


def extract_marker(template_text: str, name: str) -> str:
    match = re.search(ROW_RE_TEMPLATE.format(name=name), template_text)
    if not match:
        raise SystemExit(f"Template {TEMPLATE_PATH} is missing the {name} marker.")
    return match.group(1)


def strip_markers(text: str, *names: str) -> str:
    for name in names:
        text = re.sub(ROW_RE_TEMPLATE.format(name=name), "", text)
    return text


def apply_section(text: str, name: str, keep: bool) -> str:
    pattern = re.compile(SECTION_RE_TEMPLATE.format(name=name), re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"Template {TEMPLATE_PATH} is missing the {name} section.")
    replacement = match.group(1) if keep else ""
    return pattern.sub(replacement, text)


def format_risk(entry: dict) -> str:
    risk = entry.get("risk")
    return f"{risk}/10" if risk is not None else "—"


def entry_lines(entries: list[dict], row_template: str, empty_template: str) -> str:
    if not entries:
        return empty_template
    return "\n".join(
        row_template.format(
            xxxx=entry["code"],
            name=entry["name"] or "(no name)",
            type=entry["type"],
            icon=TYPE_ICONS.get(entry["type"], "❓"),
            risk=format_risk(entry),
        )
        for entry in entries
    )


def split_in_progress(states: dict) -> tuple[list[dict], list[dict], list[dict]]:
    entries = states.get("inProgress", {}).get("entries", [])
    to_implement = [e for e in entries if e["subStatus"] == "ready_to_implement"]
    pending = [e for e in entries if e["subStatus"] == "described"]
    no_description = [e for e in entries if e["subStatus"] == "no_description"]
    return to_implement, pending, no_description


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
    row_warning = extract_marker(template_text, "ROW_WARNING")
    empty_ideas = extract_marker(template_text, "EMPTY_IDEAS")

    # The marker lines (ROW_*/EMPTY_*) contain their own literal
    # placeholders ({xxxx}, {code}...) that aren't part of the final
    # format() kwargs: they must be stripped from the text BEFORE applying
    # sections and formatting, or format() would fail with a KeyError.
    template_text = strip_markers(
        template_text, "ROW_ENTRY", "EMPTY_ENTRY", "ROW_FAST", "ROW_IDEA", "ROW_WARNING", "EMPTY_IDEAS"
    )

    to_implement, pending, no_description = split_in_progress(states)
    implemented_entries = states.get("implemented", {}).get("entries", [])
    fast_entries = collect_fast_entries(states)
    todo_entries = states.get("todo", {}).get("entries", [])

    body = apply_section(template_text, "noDescription", keep=bool(no_description))
    body = apply_section(body, "fast", keep=show_fast and bool(fast_entries))
    body = apply_section(body, "warnings", keep=bool(result["warnings"]))

    body = body.format(
        generatedDate=datetime.now().strftime("%Y-%m-%d"),
        versionsTotal=count_versions(changes_dir),
        summaryBars=render_bars(
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
        toImplementRows=entry_lines(to_implement, row_entry, empty_entry),
        pendingTotal=len(pending),
        pendingRows=entry_lines(pending, row_entry, empty_entry),
        toCloseTotal=states.get("implemented", {}).get("total", 0),
        readyRows=entry_lines(implemented_entries, row_entry, empty_entry),
        noDescriptionRows=", ".join(e["code"] for e in no_description),
        fastRows="\n".join(
            row_fast.format(code=e["code"], name=e["name"] or "(no name)", date=extract_date(changes_dir / ("implemented" if e in implemented_entries else "closed") / e["code"]))
            for e in fast_entries
        ),
        ideaRows=(
            "\n".join(row_idea.format(code=e["code"], idea=e["name"] or "(no idea)") for e in todo_entries)
            if todo_entries
            else empty_ideas
        ),
        warningRows="\n".join(row_warning.format(warning=w) for w in result["warnings"]),
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
        row("State", "Change", "Fix", "Fast", "Todo", "Total"),
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
        block.append(term.wrap("(none)", indent="  "))
    else:
        for entry in entries:
            name = entry["name"] or "(no name)"
            risk = format_risk(entry)
            block.append(term.wrap(f"- {entry['code']} — {name} (Risk: {risk})", indent="  "))
    return block


def render_terminal_page_summary(result: dict, changes_dir: Path) -> str:
    """Page 1: title, version count, state bars, and the totals table --
    the "at a glance" view, with no per-entry detail."""
    states = result["states"]
    totals = result["totalsByType"]

    lines = [
        term.title("PROJECT STATUS", f"Generated: {datetime.now().strftime('%Y-%m-%d')}"),
        "",
        f"Versions: {count_versions(changes_dir)}",
        "",
        render_bars({state: states.get(state, {}).get("total", 0) for state in STATE_ORDER}),
        "",
        term.hr("-"),
        *render_terminal_table(states, totals, result["grandTotal"]),
        term.hr("-"),
        "",
        term.hr(),
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def render_terminal_page_in_progress(result: dict) -> str:
    """Page 2: the "IN PROGRESS" breakdown (ready/pending/planned)."""
    states = result["states"]
    to_implement, pending, no_description = split_in_progress(states)
    implemented_entries = states.get("implemented", {}).get("entries", [])

    lines = [term.heading("🔧 IN PROGRESS")]
    lines += render_terminal_entries("🟢 Ready to review and close", implemented_entries)
    lines += render_terminal_entries("🟡 Pending technical analysis", pending)
    lines += render_terminal_entries("🟠 Planned, pending implementation", to_implement)

    if no_description:
        lines.append("")
        lines.append(
            term.wrap(
                "Entries without description.md (anomalous): "
                + ", ".join(e["code"] for e in no_description)
            )
        )

    lines.append("")
    lines.append(term.hr())
    return "\n".join(lines).rstrip("\n") + "\n"


def render_terminal_page_rest(result: dict, changes_dir: Path, show_fast: bool = False) -> str:
    """Page 3: everything after IN PROGRESS -- fast changes (if
    --show-fast), todo/ ideas, and warnings."""
    states = result["states"]
    implemented_entries = states.get("implemented", {}).get("entries", [])
    fast_entries = collect_fast_entries(states)
    todo_entries = states.get("todo", {}).get("entries", [])

    lines = []

    if show_fast and fast_entries:
        lines.append(term.heading("⚡ IMPLEMENTED FAST CHANGES"))
        for entry in fast_entries:
            state_dir = "implemented" if entry in implemented_entries else "closed"
            date = extract_date(changes_dir / state_dir / entry["code"])
            name = entry["name"] or "(no name)"
            lines.append(term.wrap(f"- {entry['code']} — {name} ({date})", indent="  "))
        lines.append("")

    lines.append(term.heading("💡 IDEAS IN TODO/"))
    if todo_entries:
        for entry in todo_entries:
            idea = entry["name"] or "(no idea)"
            lines.append(term.wrap(f"- {entry['code']}: {idea}", indent="  "))
    else:
        lines.append(term.wrap("(No ideas noted in todo/.)"))

    if result["warnings"]:
        lines.append("")
        lines.append(term.heading("⚠️ WARNINGS"))
        for warning in result["warnings"]:
            lines.append(term.wrap(f"- {warning}", indent="  "))

    lines.append("")
    lines.append(term.hr())

    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--show-fast",
        action="store_true",
        help="Includes the 'Implemented fast changes' section. Omitted by "
        "default: only pass this flag when the user explicitly asks for it.",
    )
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="Plain-text output without markdown, fixed to 70 columns, for "
        "pasting into a classic terminal. Exclusive use of pv.py: the "
        "pv-status skill (invoked from chat) must not pass this flag.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    changes_dir = load_changes_dir(root, args.work_folder)
    result = collect(changes_dir)
    if args.terminal:
        # Three pages, paced with an Enter prompt between them, so the
        # summary (glanceable) isn't buried under the full in-progress/
        # ideas/warnings detail on a small terminal.
        print(render_terminal_page_summary(result, changes_dir))
        input("Press Enter to see IN PROGRESS detail...")
        print(render_terminal_page_in_progress(result))
        input("Press Enter to continue...")
        print(render_terminal_page_rest(result, changes_dir, show_fast=args.show_fast))
    else:
        print(render(result, changes_dir, show_fast=args.show_fast))


if __name__ == "__main__":
    main()
