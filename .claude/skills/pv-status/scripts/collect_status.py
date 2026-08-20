#!/usr/bin/env python3
"""Collects the current state of the pv-* framework from {changesDir}.

Walks every direct subfolder of {changesDir} (each one is a "state":
normally 'todo', 'inProgress', 'implemented', 'closed', but the script
doesn't assume a fixed list -- it counts whatever exists). Inside each
state, every subfolder is an entry (change/fix/idea) identified by its
name (xxxx or the alphanumeric code from pv-todo).

For each entry it determines:
  - type: 'todo' if it's under the 'todo' state (pv-todo doesn't use a Type
    field); in any other state, parsed from '**Type**' inside
    description.md ('change', 'fix' or 'fast' -- the latter is pv-fix's
    trivial shortcut, which creates the entry in 'inProgress' and moves it
    to 'implemented' in the same invocation, without generating plan.md).
    'unknown' if not found or there's no description.md.
  - name: for 'todo', the full (untruncated) text of description.md's
    '## Idea' section (pv-todo's own format); for every other state, the
    '**Name**' field (pv-new/pv-fix's format). Informational only.
  - notes: only for the 'todo' state -- full (untruncated) text of
    description.md's '## Notes' section. Null for every other state, or if
    the idea has no such section.
  - hasDescription / hasPlan: whether description.md / plan.md exist.
  - subStatus: only relevant for the 'inProgress' state (to distinguish
    'described' from 'ready_to_implement'); null for every other state.
  - risk: integer 0-10 parsed from plan.md's '**Risk**' header field
    (written by pv-how once the technical solution is planned). Null if
    there's no plan.md yet, or plan.md exists but doesn't have that field
    written (shouldn't normally happen once pv-how finishes, but handled
    defensively).

Writes nothing: prints a single JSON on stdout with the full detail and the
aggregated totals, for the skill to use when drafting the report.

Usage:
  python collect_status.py
  python collect_status.py --work-folder /
"""

import argparse
import json
import re
import sys
from pathlib import Path

TYPE_RE = re.compile(r"\*\*Type\*\*\s*[:—-]\s*([A-Za-z]+)", re.IGNORECASE)
NAME_RE = re.compile(r"\*\*Name\*\*\s*[:—-]\s*(.+)")
RISK_RE = re.compile(r"\*\*Risk\*\*\s*[:—-]\s*(\d{1,2})\s*/\s*10")
# pv-todo doesn't use pv-new/pv-fix's "- **Field**:" format; it uses
# markdown headings ('## Idea', '## Notes') without bold.
# Both capture the whole block of each section, up to the next '##' heading
# or end of file.
IDEA_FULL_RE = re.compile(
    r"^##\s*Idea\s*\n+(.+?)(?=\n##\s|\Z)", re.IGNORECASE | re.MULTILINE | re.DOTALL
)
NOTES_FULL_RE = re.compile(
    r"^##\s*Notes\s*\n+(.+?)(?=\n##\s|\Z)", re.IGNORECASE | re.MULTILINE | re.DOTALL
)

KNOWN_TYPES = {"change", "fix", "fast"}


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


def parse_description(description_path: Path) -> dict:
    """Extracts 'Type' and 'Name' from a description.md, without failing if missing."""
    result: dict[str, str | None] = {"type": None, "name": None}
    try:
        text = description_path.read_text(encoding="utf-8")
    except OSError:
        return result

    type_match = TYPE_RE.search(text)
    if type_match:
        result["type"] = type_match.group(1).strip().lower()

    name_match = NAME_RE.search(text)
    if name_match:
        # Cuts at the first line break and strips loose markdown decoration.
        name = name_match.group(1).splitlines()[0].strip()
        result["name"] = name.strip("` ")

    return result


def parse_risk(plan_path: Path) -> int | None:
    """Extracts the numeric median from plan.md's '**Risk**: {median}/10 — ...' field.

    Returns None if plan.md doesn't exist or the field isn't written yet
    (pv-how always writes it before considering plan.md finished, but older
    or in-progress entries may not have it).
    """
    try:
        text = plan_path.read_text(encoding="utf-8")
    except OSError:
        return None

    match = RISK_RE.search(text)
    return int(match.group(1)) if match else None


def parse_todo_description(description_path: Path) -> dict:
    """Extracts the full 'Idea' and 'Notes' text from a pv-todo description.md.

    pv-todo uses markdown headings ('## Idea', '## Notes'), not
    pv-new/pv-fix's '**Field**:' format, so it needs its own parser.
    """
    result: dict[str, str | None] = {"idea": None, "notes": None}
    try:
        text = description_path.read_text(encoding="utf-8")
    except OSError:
        return result

    idea_match = IDEA_FULL_RE.search(text)
    if idea_match:
        result["idea"] = idea_match.group(1).strip()

    notes_match = NOTES_FULL_RE.search(text)
    if notes_match:
        result["notes"] = notes_match.group(1).strip()

    return result


def build_entry(state_name: str, entry_dir: Path) -> dict:
    description_path = entry_dir / "description.md"
    plan_path = entry_dir / "plan.md"
    has_description = description_path.is_file()
    has_plan = plan_path.is_file()

    notes = None
    if state_name == "todo":
        entry_type = "todo"
        name = None
        if has_description:
            parsed_todo = parse_todo_description(description_path)
            name = parsed_todo.get("idea")
            notes = parsed_todo.get("notes")
    else:
        parsed = parse_description(description_path) if has_description else {"type": None, "name": None}
        entry_type = parsed.get("type") if parsed.get("type") in KNOWN_TYPES else "unknown"
        name = parsed.get("name")

    sub_status = None
    if state_name == "inProgress":
        if has_description and has_plan:
            sub_status = "ready_to_implement"
        elif has_description:
            sub_status = "described"
        else:
            sub_status = "no_description"

    risk = parse_risk(plan_path) if has_plan else None

    return {
        "code": entry_dir.name,
        "type": entry_type,
        "name": name,
        "notes": notes,
        "hasDescription": has_description,
        "hasPlan": has_plan,
        "subStatus": sub_status,
        "risk": risk,
    }


def collect(changes_dir: Path) -> dict:
    states: dict[str, dict] = {}
    warnings: list[str] = []

    # A missing changes_dir just means nothing has been tracked yet -- not an
    # error condition. Treated the same as an existing-but-empty folder, so
    # every consumer below reports "no entries" instead of failing.
    state_dirs = (
        sorted(p for p in changes_dir.iterdir() if p.is_dir())
        if changes_dir.is_dir()
        else []
    )

    for state_dir in state_dirs:
        entries = []
        for entry_dir in sorted(p for p in state_dir.iterdir() if p.is_dir()):
            # closed/temp/ is pv-internal-changelog's transient staging area
            # (while a version is being prepared, or leftover from a run
            # interrupted before cleanup) -- not a real change/fix entry.
            if state_dir.name == "closed" and entry_dir.name == "temp":
                continue
            entry = build_entry(state_dir.name, entry_dir)
            entries.append(entry)
            if entry["type"] == "unknown":
                warnings.append(
                    f"{state_dir.name}/{entry_dir.name}: could not determine "
                    "'Type' (missing description.md or the '**Type**' field)."
                )
            if state_dir.name == "inProgress" and entry["subStatus"] == "no_description":
                warnings.append(
                    f"inProgress/{entry_dir.name}: has no description.md."
                )

        by_type: dict[str, int] = {}
        for entry in entries:
            by_type[entry["type"]] = by_type.get(entry["type"], 0) + 1

        state_info = {
            "total": len(entries),
            "byType": by_type,
            "entries": entries,
        }

        if state_dir.name == "inProgress":
            sub_counts = {"described": 0, "ready_to_implement": 0, "no_description": 0}
            for entry in entries:
                sub_counts[entry["subStatus"]] = sub_counts.get(entry["subStatus"], 0) + 1
            state_info["subStatus"] = sub_counts

        states[state_dir.name] = state_info

    totals_by_type: dict[str, int] = {}
    grand_total = 0
    for state_info in states.values():
        grand_total += state_info["total"]
        for type_name, count in state_info["byType"].items():
            totals_by_type[type_name] = totals_by_type.get(type_name, 0) + count

    return {
        "changesDir": str(changes_dir),
        "states": states,
        "totalsByType": totals_by_type,
        "grandTotal": grand_total,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    args = parser.parse_args()

    # On the Windows console, stdout may use a codepage other than UTF-8;
    # forcing it avoids mojibake in names/descriptions with accents.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    changes_dir = load_changes_dir(root, args.work_folder)
    result = collect(changes_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
