#!/usr/bin/env python3
"""Full listing of ideas from {changesDir}/todo/, for /pv-status todo.

Unlike collect_status.py (which gives a JSON with every state), this
script returns only the 'todo' ideas, already rendered as markdown per the
STATUS.todo.template.md template (not JSON) -- so the model invoking this
script doesn't need to draft the listing itself or truncate anything, just
paste the output as-is.

Reuses collect_status.py's parse_todo_description to extract the full
(untruncated) text of each description.md's '## Idea' section. If an idea
has no such section (or no description.md), the row says so explicitly
instead of omitting the entry.

Writes nothing to disk: prints the final markdown to stdout.

Usage:
  python list_todo.py
  python list_todo.py --work-folder /
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_status import load_changes_dir, parse_todo_description, repo_root  # noqa: E402
import terminal_output as term  # noqa: E402

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "STATUS.todo.template.md"

ROW_IDEA_RE = re.compile(r"<!--\s*ROW_IDEA:\s*(.+?)\s*-->\n?")
EMPTY_TEMPLATE_RE = re.compile(r"<!--\s*EMPTY_TEMPLATE:\s*(.+?)\s*-->\n?")


def collect_todo(changes_dir: Path) -> list[dict]:
    todo_dir = changes_dir / "todo"
    if not todo_dir.is_dir():
        return []

    entries = []
    for entry_dir in sorted(p for p in todo_dir.iterdir() if p.is_dir()):
        description_path = entry_dir / "description.md"
        idea = None
        if description_path.is_file():
            idea = parse_todo_description(description_path).get("idea")
        entries.append({"code": entry_dir.name, "idea": idea})
    return entries


def render_report(entries: list[dict]) -> str:
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    row_match = ROW_IDEA_RE.search(template_text)
    empty_match = EMPTY_TEMPLATE_RE.search(template_text)
    if not row_match or not empty_match:
        raise SystemExit(
            f"Template {TEMPLATE_PATH} is missing the expected "
            "ROW_IDEA/EMPTY_TEMPLATE markers."
        )
    row_template = row_match.group(1)
    empty_template = empty_match.group(1)

    body = ROW_IDEA_RE.sub("", template_text)
    body = EMPTY_TEMPLATE_RE.sub("", body)
    body = body.rstrip("\n") + "\n"

    if entries:
        rows = "\n".join(
            row_template.format(
                code=entry["code"],
                idea=entry["idea"] if entry["idea"] else "*(no '## Idea' section in description.md)*",
            )
            for entry in entries
        )
    else:
        rows = empty_template

    from datetime import datetime

    return body.format(generatedDate=datetime.now().strftime("%Y-%m-%d"), rows=rows)


def render_terminal(entries: list[dict]) -> str:
    from datetime import datetime

    lines = [
        term.title("IDEAS IN TODO/", f"Generated: {datetime.now().strftime('%Y-%m-%d')}"),
    ]

    if not entries:
        lines.append("")
        lines.append(term.wrap("(No ideas noted in todo/.)"))
        lines.append("")
        lines.append(term.hr())
        return "\n".join(lines) + "\n"

    for entry in entries:
        idea = entry["idea"] or "(no '## Idea' section in description.md)"
        lines.append("")
        lines.append(entry["code"])
        lines.append(term.wrap(idea, indent="  "))

    lines.append("")
    lines.append(term.hr())
    return "\n".join(lines) + "\n"


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
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
    entries = collect_todo(changes_dir)
    print(render_terminal(entries) if args.terminal else render_report(entries))


if __name__ == "__main__":
    main()
