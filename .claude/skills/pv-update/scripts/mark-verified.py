#!/usr/bin/env python3
"""Writes .claude/pv-context.json#framework.frameworkStatus after a pv-update
run -- the deterministic counterpart to audit-context.py's version checks
(version-check-outdated / version-check-downgrade). Doesn't decide anything:
the caller (pv-update) has already resolved which mode applies.

Version comes from pv-init/SKILL.md's real metadata.version on disk (same
frontmatter-reading logic as audit-context.py's read_skill_version(),
duplicated here rather than shared -- each pv-* script is self-contained).

Modes (mutually exclusive, exactly one required):
  --clear             Healthy state (or an outdated-but-not-downgraded case
                       just resolved): sets lastVerifiedVersion to the real
                       current version, blocked=false, drops blockedReason.
  --block "<reason>"  A downgrade was detected: sets blocked=true and
                       blockedReason, WITHOUT touching lastVerifiedVersion
                       (it must stay at the higher, already-verified value --
                       that's what makes the downgrade detectable).
  --confirm-downgrade The user confirmed the downgrade was intentional: same
                       end state as --clear (lastVerifiedVersion becomes the
                       real current version, blocked=false), kept as a
                       separate flag so the calling SKILL.md is explicit
                       about which decision branch it's in.

Prints ONLY a JSON with the resulting frameworkStatus on stdout.

Usage:
  python mark-verified.py --clear
  python mark-verified.py --block "pv-init/SKILL.md reports 0.9.4, but pv-context.json last verified 0.9.5b8."
  python mark-verified.py --confirm-downgrade
"""

import argparse
import json
import re
import sys
from pathlib import Path


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-update/scripts/
    return Path(__file__).resolve().parents[4]


def read_skill_version(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        close_idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    in_metadata = False
    for line in lines[1:close_idx]:
        if re.match(r"^metadata:\s*$", line):
            in_metadata = True
            continue
        if not in_metadata:
            continue
        version_match = re.match(r"^\s+version:\s*(.+?)\s*$", line)
        if version_match:
            return version_match.group(1).strip().strip('"').strip("'")
        if not line.startswith((" ", "\t")):
            in_metadata = False
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--clear", action="store_true",
                       help="Healthy state: lastVerifiedVersion = real current version, blocked=false.")
    mode.add_argument("--block", metavar="REASON",
                       help="Downgrade detected: blocked=true with this reason, lastVerifiedVersion untouched.")
    mode.add_argument("--confirm-downgrade", action="store_true",
                       help="User confirmed the downgrade was intentional: same effect as --clear.")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / ".claude/pv-context.json"
    if not context_path.is_file():
        raise SystemExit(f"Cannot find {context_path}. Run pv-init before pv-update.")

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.setdefault("framework", {})

    if args.block:
        status = framework.setdefault("frameworkStatus", {})
        status["blocked"] = True
        status["blockedReason"] = args.block
    else:
        pv_init_md = root / ".claude/skills/pv-init/SKILL.md"
        real_version = read_skill_version(pv_init_md) if pv_init_md.is_file() else None
        if not real_version:
            raise SystemExit(f"Couldn't read metadata.version from {pv_init_md}.")
        status = framework.setdefault("frameworkStatus", {})
        status["lastVerifiedVersion"] = real_version
        status["blocked"] = False
        status.pop("blockedReason", None)

    context_path.write_text(
        json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps(framework["frameworkStatus"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
