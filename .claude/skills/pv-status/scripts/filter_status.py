#!/usr/bin/env python3
"""Filtered listing of a single {changesDir} state (folder), for /pv-status <state>.

Unlike collect_status.py (which gives totals and aggregates across all
states), this script returns the full detail of ONE state's entries,
already rendered as markdown per the STATUS.filtered.template.md template
(not JSON) -- so the model invoking this script doesn't need to spend
tokens applying the template itself, just paste the output as-is.

For each entry in the state folder, five columns are computed:
  - code: the subfolder's name.
  - type: 'todo' if the state is 'todo' (pv-todo doesn't use a Type
    field); in any other state, description.md's '**Type**' field
    ('change'/'fix'/'fast'); 'unknown' if not found or there's no
    description.md.
  - description: the first 250 characters of description.md's '## Full
    description' section (with "..." at the end if truncated); None if
    that section is empty or missing. history.md is never used as a
    fallback: it's prompt history for the exclusive use of pv-new/pv-fix,
    no other skill (including pv-status) should read it.
  - risk: plan.md's '**Risk**' header field (written by pv-how once the
    technical solution is planned), shown as '{value}/10'; None if there's
    no plan.md yet or it doesn't have that field written (e.g. 'fast'
    entries, which skip plan.md entirely, or entries still pending
    pv-how).
  - date: description.md's '**Creation date**' field if present (verbatim
    as written); otherwise description.md's modification time (mtime)
    formatted as YYYY-MM-DD; if there's no description.md, the folder's own
    mtime.
  - extra_files: count of files directly inside the entry folder that
    aren't the framework's own (description.md, plan.md, history.md) --
    e.g. design_*.html/design_*.txt mockups, or anything else a change/fix
    folder may accumulate. Only surfaces in --terminal mode's detail card
    (see TERMINAL_FRAMEWORK_FILES below); 'todo/' entries never show it,
    same reasoning as Risk/planned (todo/ folders only ever hold
    description.md).

Two more fields, name (description.md's '**Name**' field) and planned_date
(plan.md's '**Creation date**' field, same bold-inline format as
description.md's -- None/"pending" if plan.md doesn't exist yet or lacks
the field), are also computed but only surface in --terminal mode (pv.py)
as part of each entry's detail card -- the markdown table below has no
Name/Planned columns, to stay consistent with STATUS.filtered.template.md.

The template (STATUS.filtered.template.md, in the skill's folder) defines
the output format: a body with {state}, {generatedDate} and {rows}
placeholders, plus two HTML comment lines the script extracts and doesn't
print:
  <!-- ROW_TEMPLATE: ... -->   pattern for one row, with {code}/{type}/{description}/{risk}/{date}
  <!-- EMPTY_TEMPLATE: ... --> text to use for {rows} if there are no entries

Writes nothing to disk: prints the final markdown to stdout.

Two more modes ignore <state> and scan every state instead:
  --search-id TEXT       Keeps only entries whose code (change id) matches
                          TEXT exactly (case-insensitive). Cheap: never
                          reads description.md for non-matching entries,
                          only for the (usually zero or one) matches.
  --search-content TEXT  Keeps only entries whose description.md contains
                          TEXT (case-insensitive substring). Always reads
                          every entry's description.md -- there's no way
                          to avoid that for a content search.
Both are --terminal-only, for pv.py's "Search by id" / "Search by
content" options -- the pv-status skill (chat) never uses either, so they
reuse render_terminal() only, never render_report()/the markdown template.

Usage:
  python filter_status.py <state>
  python filter_status.py closed --work-folder /
  python filter_status.py --search-id 1001 --terminal
  python filter_status.py --search-content "auth" --terminal
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_status import parse_todo_description  # noqa: E402
import terminal_output as term  # noqa: E402

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "STATUS.filtered.template.md"

DATE_RE = re.compile(r"\*\*Creation date\*\*\s*[:—-]\s*(.+)")
TYPE_RE = re.compile(r"\*\*Type\*\*\s*[:—-]\s*([A-Za-z]+)", re.IGNORECASE)
RISK_RE = re.compile(r"\*\*Risk\*\*\s*[:—-]\s*(\d{1,2})\s*/\s*10")
NAME_RE = re.compile(r"\*\*Name\*\*\s*[:—-]\s*(.+)")
# pv-todo doesn't use pv-new/pv-fix's "**Field**:" format -- description.md
# uses a plain markdown heading ('## Creation date') instead of a bold
# inline field, so it needs its own date pattern (see parse_todo_description
# in collect_status.py for the same distinction applied to 'idea'/'notes').
TODO_DATE_RE = re.compile(r"^##\s*Creation date\s*\n+(.+?)(?=\n##\s|\Z)", re.IGNORECASE | re.MULTILINE | re.DOTALL)
KNOWN_TYPES = {"change", "fix", "fast"}

TYPE_LABELS = {
    "change": "🆕 Change",
    "fix": "👾 Fix",
    "fast": "⚡ Fast",
    "todo": "💡 Todo",
    "unknown": "❓ Unknown",
}

DESCRIPTION_FULL_RE = re.compile(
    r"^##\s*Full description\s*\n+(.+?)(?=\n##\s|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-status/scripts/
    return Path(__file__).resolve().parents[4]


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    # workFolder is always relative to the repo root, whether or not it
    # carries a leading "/" (that's only a convention to make it visually
    # explicit) -- Path("/a") / "/b" would otherwise discard "a" entirely,
    # since pathlib treats a leading-slash operand as its own absolute path.
    work_root = root / (work_folder_rel or "").lstrip("/")
    return work_root / "changes"


def load_changes_dir(root: Path, override: str | None) -> Path:
    if override:
        return resolve_changes_dir(root, override)

    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"Cannot find {context_path}. Run the pv-init skill before "
            "checking status."
        )
    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} has no 'framework' section. Run pv-init "
            "to complete it."
        )
    return resolve_changes_dir(root, framework.get("workFolder", "/"))


DESCRIPTION_MAX_CHARS = 250

# Files an entry folder always carries as part of the pv-new/pv-fix/pv-how
# workflow -- everything else directly inside the folder (design_*.html,
# design_*.txt, or anything else a change/fix accumulates) counts as
# "extra" for the detail card's file count.
TERMINAL_FRAMEWORK_FILES = {"description.md", "plan.md", "history.md"}


def summarize(text: str) -> str:
    # Collapses repeated line breaks/whitespace before truncating, so the
    # summary doesn't drag along markdown formatting.
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= DESCRIPTION_MAX_CHARS:
        return collapsed
    return collapsed[:DESCRIPTION_MAX_CHARS].rstrip() + "..."


def extract_description(text: str) -> str | None:
    match = DESCRIPTION_FULL_RE.search(text)
    if match and match.group(1).strip():
        return summarize(match.group(1))

    return None


def extract_date(text: str) -> str | None:
    match = DATE_RE.search(text)
    if match:
        return match.group(1).strip()
    return None


def extract_type(text: str) -> str:
    match = TYPE_RE.search(text)
    type_ = match.group(1).strip().lower() if match else None
    return type_ if type_ in KNOWN_TYPES else "unknown"


def extract_name(text: str) -> str | None:
    match = NAME_RE.search(text)
    if not match:
        return None
    # Cuts at the first line break and strips loose markdown decoration.
    return match.group(1).splitlines()[0].strip().strip("` ")


def extract_risk(text: str) -> str | None:
    match = RISK_RE.search(text)
    return match.group(1) if match else None


def mtime_str(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")


def count_extra_files(entry_dir: Path) -> int:
    return sum(
        1
        for p in entry_dir.iterdir()
        if p.is_file() and p.name not in TERMINAL_FRAMEWORK_FILES
    )


def build_entry(state: str, entry_dir: Path) -> dict:
    description_path = entry_dir / "description.md"
    plan_path = entry_dir / "plan.md"

    description = None
    date = None
    name = None
    type_ = "todo" if state == "todo" else "unknown"

    if description_path.is_file():
        text = description_path.read_text(encoding="utf-8")
        if state == "todo":
            # pv-todo's description.md uses its own format ('## Idea',
            # '## Creation date' headings, not pv-new/pv-fix's '**Field**:'
            # inline style) -- parse_todo_description() already knows this
            # (see list_todo.py). The idea's text doubles as both title and
            # content here since pv-todo has no separate name/description
            # split -- shown as the name (line 2), description stays empty.
            name = parse_todo_description(description_path).get("idea")
            date_match = TODO_DATE_RE.search(text)
            date = date_match.group(1).strip() if date_match else mtime_str(description_path)
        else:
            description = extract_description(text)
            date = extract_date(text) or mtime_str(description_path)
            name = extract_name(text)
            type_ = extract_type(text)
    else:
        date = mtime_str(entry_dir)

    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else None
    risk = extract_risk(plan_text) if plan_text else None
    # plan.md uses the same "**Creation date**: [YYYY-MM-DD]" bold-inline
    # field as description.md (see PLAN.template.md) -- reuse extract_date()
    # rather than a second date pattern. None here (no plan.md, or a plan.md
    # missing the field) means "pending" to the caller, not "unknown yet".
    planned_date = extract_date(plan_text) if plan_text else None
    extra_files = None if state == "todo" else count_extra_files(entry_dir)

    return {
        "code": entry_dir.name,
        "state": state,
        "type": type_,
        "name": name,
        "description": description,
        "date": date,
        "planned_date": planned_date,
        "risk": risk,
        "extra_files": extra_files,
    }


def collect(changes_dir: Path, state: str) -> dict:
    # A missing changes_dir or state subfolder just means there are no
    # entries in that state yet -- not an error condition. Treated the same
    # as an existing-but-empty folder, so the caller reports "no entries"
    # instead of failing.
    state_dir = changes_dir / state
    entries = (
        [
            build_entry(state, entry_dir)
            for entry_dir in sorted(p for p in state_dir.iterdir() if p.is_dir())
        ]
        if state_dir.is_dir()
        else []
    )

    return {
        "changesDir": str(changes_dir),
        "state": state,
        "total": len(entries),
        "entries": entries,
    }


def iter_all_entries(changes_dir: Path) -> list[tuple[str, Path]]:
    # Scans every state subfolder (not just one), unlike collect() -- a
    # search by id or content isn't scoped to a single state.
    if not changes_dir.is_dir():
        return []
    return [
        (state_dir.name, entry_dir)
        for state_dir in sorted(p for p in changes_dir.iterdir() if p.is_dir())
        for entry_dir in sorted(p for p in state_dir.iterdir() if p.is_dir())
        # closed/temp/ is pv-internal-changelog's transient staging area
        # (while a version is being prepared, or leftover from a run
        # interrupted before cleanup) -- not a real entry.
        if not (state_dir.name == "closed" and entry_dir.name == "temp")
    ]


def ids_match(code: str, query: str) -> bool:
    # Change/fix ids are zero-padded numbers (e.g. "00001"); todo/ ids are
    # short alphanumeric codes (e.g. "a3f9k") that aren't purely numeric.
    # When both sides are digits-only, compare as integers so the padding
    # doesn't matter ("1" must find "00001"); otherwise fall back to a
    # plain case-insensitive string match.
    if code.isdigit() and query.isdigit():
        return int(code) == int(query)
    return code.lower() == query.lower()


def collect_search_by_id(changes_dir: Path, query: str) -> dict:
    # Cheap by construction: only compares folder names (no disk reads) --
    # build_entry() (which reads description.md/plan.md) only runs for the
    # handful of entries that actually match, not the whole tree.
    entries = [
        build_entry(state, entry_dir)
        for state, entry_dir in iter_all_entries(changes_dir)
        if ids_match(entry_dir.name, query)
    ]

    return {
        "changesDir": str(changes_dir),
        "query": query,
        "searchKind": "id",
        "total": len(entries),
        "entries": entries,
    }


def collect_search_by_content(changes_dir: Path, query: str) -> dict:
    # Unlike search-by-id, this has no shortcut: every entry's
    # description.md must be read to know whether it matches.
    entries = []
    for state, entry_dir in iter_all_entries(changes_dir):
        description_path = entry_dir / "description.md"
        if not description_path.is_file():
            continue
        if query.lower() in description_path.read_text(encoding="utf-8").lower():
            entries.append(build_entry(state, entry_dir))

    return {
        "changesDir": str(changes_dir),
        "query": query,
        "searchKind": "content",
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
            f"Template {TEMPLATE_PATH} is missing the expected "
            "ROW_TEMPLATE/EMPTY_TEMPLATE markers."
        )
    row_template = row_match.group(1)
    empty_template = empty_match.group(1)

    body = ROW_TEMPLATE_RE.sub("", template_text)
    body = EMPTY_TEMPLATE_RE.sub("", body)
    body = body.rstrip("\n") + "\n"

    if result["entries"]:
        rows = "\n".join(
            row_template.format(
                code=entry["code"],
                type=TYPE_LABELS.get(entry["type"], entry["type"]),
                description=entry["description"] or "—",
                risk=f"{entry['risk']}/10" if entry["risk"] else "?",
                date=entry["date"] or "—",
            )
            for entry in result["entries"]
        )
    else:
        rows = empty_template.format(state=result["state"])

    return body.format(
        state=result["state"],
        generatedDate=datetime.now().strftime("%Y-%m-%d"),
        rows=rows,
    )


TERMINAL_DESCRIPTION_MAX_CHARS = 500


SEARCH_KIND_LABELS = {"id": "id", "content": "content"}


def render_terminal(result: dict, width: int = term.DEFAULT_WIDTH) -> str:
    is_search = "query" in result
    title = f"PROJECT STATUS — search: {result['query']}" if is_search else f"PROJECT STATUS — {result['state']}"
    empty_message = (
        f'(No entry matches "{result["query"]}" by {SEARCH_KIND_LABELS[result["searchKind"]]}.)'
        if is_search
        else f'(There are no entries in the "{result["state"]}" state.)'
    )

    lines = [
        term.title(title, f"Generated: {datetime.now().strftime('%Y-%m-%d')}", width=width),
    ]

    if not result["entries"]:
        lines.append("")
        lines.append(term.wrap(empty_message, width=width))
        lines.append("")
        lines.append(term.hr(width=width))
        return "\n".join(lines) + "\n"

    for entry in result["entries"]:
        # Row format is the same regardless of mode (by state, by id, by
        # content) -- the (state) prefix used to be search-only (redundant
        # with the "Search by state" screen's own title), now it's always
        # shown so every row looks identical no matter how you got there.
        type_ = TYPE_LABELS.get(entry["type"], entry["type"])
        planned = entry["planned_date"] or "pending"
        lines.append("")

        if entry["state"] == "todo":
            # todo/ ideas never have plan.md, so Risk/planned would always
            # be "?"/"pending" -- shown as noise, not information. 3 lines
            # instead of 4: no separate description line either (line 3's
            # ## Idea text already doubles as both name and content).
            lines.append(f"({entry['state']})  {entry['code']}  [{type_}]")
            lines.append(f"created: {entry['date'] or '—'}")
            lines.append(term.wrap(entry["name"] or "(no name)", indent="> ", width=width))
            continue

        risk = f"{entry['risk']}/10" if entry["risk"] else "?"
        description = entry["description"] or "—"
        if len(description) > TERMINAL_DESCRIPTION_MAX_CHARS:
            description = description[:TERMINAL_DESCRIPTION_MAX_CHARS].rstrip() + "..."
        extra_files = entry["extra_files"] or 0
        lines.append(f"({entry['state']})  {entry['code']}  [{type_}]  Risk: {risk}")
        lines.append(f"created: {entry['date'] or '—'}, planned: {planned}")
        lines.append(term.wrap(entry["name"] or "(no name)", indent="> ", width=width))
        lines.append(term.wrap(description, indent="  ", width=width))
        lines.append(f"extra files: {extra_files}")

    lines.append("")
    lines.append(term.hr(width=width))
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "state",
        nargs="?",
        help="Name of the state folder to list (e.g. closed, implemented, inProgress, todo). "
        "Required unless --search-id/--search-content is given.",
    )
    parser.add_argument(
        "--search-id",
        metavar="TEXT",
        help="Search every state for an entry whose id (folder name) matches TEXT "
        "exactly (case-insensitive). Ignores <state>. Cheap: doesn't read any "
        "description.md except the match's. --terminal-only, for pv.py's "
        "'Search by id' option.",
    )
    parser.add_argument(
        "--search-content",
        metavar="TEXT",
        help="Search every state for entries whose description.md contains TEXT "
        "(case-insensitive substring). Ignores <state>. Reads every entry's "
        "description.md. --terminal-only, for pv.py's 'Search by content' option.",
    )
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="Plain-text output without markdown, for pasting into a "
        "classic terminal. Exclusive use of pv.py: the pv-status skill "
        "(invoked from chat) must not pass this flag.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=term.DEFAULT_WIDTH,
        help="Column width for --terminal output (also used by "
        "--search-id/--search-content, which are --terminal-only "
        "already). The caller decides this -- pv.py passes its own WIDTH "
        f"so delegated screens match its menu's width. Default {term.DEFAULT_WIDTH}.",
    )
    args = parser.parse_args()

    if args.search_id and args.search_content:
        parser.error("--search-id and --search-content are mutually exclusive")

    if not args.search_id and not args.search_content and not args.state:
        parser.error(
            "the following arguments are required: state (unless --search-id "
            "or --search-content is given)"
        )

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    changes_dir = load_changes_dir(root, args.work_folder)

    if args.search_id:
        result = collect_search_by_id(changes_dir, args.search_id)
        print(render_terminal(result, width=args.width))
        return

    if args.search_content:
        result = collect_search_by_content(changes_dir, args.search_content)
        print(render_terminal(result, width=args.width))
        return

    result = collect(changes_dir, args.state)
    print(render_terminal(result, width=args.width) if args.terminal else render_report(result))


if __name__ == "__main__":
    main()
