#!/usr/bin/env python3
"""Validates .claude/pv-context.json against schema.json's required fields.

'framework' no longer has any required field of its own (see schema.json):
'workFolder' is optional with default "/". So the only thing that determines
whether the framework is initialized is that the 'framework' section
exists -- created by pv-init, never any other skill.

Doesn't decide anything on its own (doesn't create or complete the file) --
only determines which required fields are missing, so pv-init knows whether
to ask the full questionnaire, only what's missing, or nothing.

Also reports 'hasLanguage': true if framework.interaction.language exists in
the file (regardless of its content) -- it's the only field whose absence
triggers the unconditional language question in pv-init; the other language
fields (changes/versions/docs.*) are optional refinements on top of that
default and don't gate this flag.

Prints ONLY a JSON on stdout:

  {"exists": true, "hasFramework": true, "missingRequired": [], "complete": true, "hasLanguage": true}
  {"exists": false, "hasFramework": false, "missingRequired": [], "complete": false, "hasLanguage": false}

Usage:
  python check-context.py
"""

import argparse
import json
import sys
from pathlib import Path

ALWAYS_REQUIRED = ()


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-init/scripts/
    return Path(__file__).resolve().parents[4]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--context-path",
        help="Path to pv-context.json relative to the repo root. Defaults to "
        ".claude/pv-context.json.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / (args.context_path or ".claude/pv-context.json")

    if not context_path.is_file():
        result = {
            "exists": False,
            "hasFramework": False,
            "missingRequired": list(ALWAYS_REQUIRED),
            "complete": False,
            "hasLanguage": False,
        }
        json.dump(result, sys.stdout, ensure_ascii=False)
        print()
        return

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework") or {}
    has_framework = bool(context.get("framework"))

    missing = [field for field in ALWAYS_REQUIRED if field not in framework]
    has_language = "language" in (framework.get("interaction") or {})

    result = {
        "exists": True,
        "hasFramework": has_framework,
        "missingRequired": missing,
        # No required fields of its own in 'framework' (workFolder has a
        # default), so "complete" means the 'framework' section exists.
        "complete": has_framework and not missing,
        "hasLanguage": has_language,
    }
    json.dump(result, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
