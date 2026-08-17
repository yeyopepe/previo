#!/usr/bin/env python3
"""Filtered listing of a single {changesDir} state (folder), for /pv-status <state>.

Unlike collect_status.py (which gives totals and aggregates across all
states), this script returns the full detail of ONE state's entries,
already rendered as markdown per the STATUS.filtered.template.md template
(not JSON) -- so the model invoking this script doesn't need to spend
tokens applying the template itself, just paste the output as-is.

For each entry in the state folder, four columns are computed:
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
  - date: description.md's '**Creation date**' field if present (verbatim
    as written); otherwise description.md's modification time (mtime)
    formatted as YYYY-MM-DD; if there's no description.md, the folder's own
    mtime.

The template (STATUS.filtered.template.md, in the skill's folder) defines
the output format: a body with {state}, {generatedDate} and {rows}
placeholders, plus two HTML comment lines the script extracts and doesn't
print:
  <!-- ROW_TEMPLATE: ... -->   pattern for one row, with {code}/{type}/{description}/{date}
  <!-- EMPTY_TEMPLATE: ... --> text to use for {rows} if there are no entries

Writes nothing to disk: prints the final markdown to stdout.

Usage:
  python filter_status.py <state>
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

DATE_RE = re.compile(r"\*\*Creation date\*\*\s*[:—-]\s*(.+)")
TYPE_RE = re.compile(r"\*\*Type\*\*\s*[:—-]\s*([A-Za-z]+)", re.IGNORECASE)
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
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
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


def mtime_str(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")


def build_entry(state: str, entry_dir: Path) -> dict:
    description_path = entry_dir / "description.md"

    description = None
    date = None
    type_ = "todo" if state == "todo" else "unknown"

    if description_path.is_file():
        text = description_path.read_text(encoding="utf-8")
        description = extract_description(text)
        date = extract_date(text) or mtime_str(description_path)
        if state != "todo":
            type_ = extract_type(text)
    else:
        date = mtime_str(entry_dir)

    return {
        "code": entry_dir.name,
        "type": type_,
        "description": description,
        "date": date,
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


def render_terminal(result: dict) -> str:
    lines = [
        term.title(
            f"PROJECT STATUS — {result['state']}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
        ),
    ]

    if not result["entries"]:
        lines.append("")
        lines.append(term.wrap(f'(There are no entries in the "{result["state"]}" state.)'))
        lines.append("")
        lines.append(term.hr())
        return "\n".join(lines) + "\n"

    for entry in result["entries"]:
        type_ = TYPE_LABELS.get(entry["type"], entry["type"])
        lines.append("")
        lines.append(f"{entry['code']}  [{type_}]  {entry['date'] or '—'}")
        lines.append(term.wrap(entry["description"] or "—", indent="  "))

    lines.append("")
    lines.append(term.hr())
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", help="Name of the state folder to list (e.g. closed, implemented, inProgress, todo).")
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
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
    result = collect(changes_dir, args.state)
    print(render_terminal(result) if args.terminal else render_report(result))


if __name__ == "__main__":
    main()
