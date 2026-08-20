#!/usr/bin/env python3
"""Audits .claude/pv-context.json and everything it configures against the
real state of the repo: schema shape, referenced skills, on-disk paths,
skillModels vs each SKILL.md's real frontmatter, the [[[...]]]-marked
structural labels (see pv-design.en.md's "Marker convention in templates")
in every template-derived document under workFolder's changes/ subtree, and
version consistency -- every pv-* skill's metadata.version should share the
same major.minor (skill-version-mismatch:*), and pv-context.json's
frameworkStatus.lastVerifiedVersion should match pv-init/SKILL.md's real
metadata.version (version-check-outdated / version-check-downgrade).

Doesn't decide anything or write anything -- purely read-only diagnostics,
for pv-update to turn into a report and, only with user approval, fixes.
Distinguishes REQUIRED checks (the framework is effectively broken if they
fail) from OPTIONAL checks (only checked if the corresponding field is
configured; an unconfigured optional field is never a problem on its own).

Prints ONLY a JSON on stdout:

  {
    "contextPath": ".claude/pv-context.json",
    "exists": true,
    "validJson": true,
    "schemaOk": true,
    "problems": [
      {
        "id": "workfolder-missing",
        "severity": "required",
        "field": "framework.workFolder",
        "message": "...",
        "expected": "...",
        "actual": "..."
      }
    ]
  }

Usage:
  python .claude/skills/pv-update/scripts/audit-context.py
"""

import json
import re
import sys
from pathlib import Path

KNOWN_TOP_LEVEL = {"_warning", "skillModels", "framework"}
KNOWN_FRAMEWORK_FIELDS = {
    "workFolder",
    "sourcecodeDir",
    "interaction",
    "changes",
    "versions",
    "_comments",
    "skills",
    "numberWidth",
    "docs",
    "frameworkStatus",
}
WORKFOLDER_SUBFOLDERS = (
    "changes/inProgress",
    "changes/implemented",
    "changes/todo",
    "changes/closed",
    "versions",
    "stuff",
)


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-update/scripts/
    return Path(__file__).resolve().parents[4]


def add(problems: list, id_: str, severity: str, field: str, message: str,
        expected=None, actual=None) -> None:
    entry = {"id": id_, "severity": severity, "field": field, "message": message}
    if expected is not None:
        entry["expected"] = expected
    if actual is not None:
        entry["actual"] = actual
    problems.append(entry)


def strip_leading_slash(value: str) -> str:
    return value.lstrip("/")


def resolve_under(root: Path, base: str) -> Path:
    return root / strip_leading_slash(base)


def read_model_effort(path: Path) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        close_idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    model = effort = None
    for line in lines[1:close_idx]:
        match = re.match(r"^(model|effort):\s*(.*)$", line)
        if not match:
            continue
        value = match.group(2).strip().strip('"').strip("'")
        if match.group(1) == "model":
            model = value
        else:
            effort = value
    if model is None or effort is None:
        return None
    return model, effort


# Versions in this framework aren't strict semver -- they carry an optional
# 'bN' beta suffix with no separator (e.g. "0.9.5b8"). The suffix is captured
# but never used for ordering: two versions differing only in suffix compare
# equal for every check in this script.
VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)([a-zA-Z][\w.-]*)?$")


def parse_version(version: str) -> tuple[int, int, int, str] | None:
    match = VERSION_RE.match(version.strip())
    if not match:
        return None
    major, minor, patch, suffix = match.groups()
    return int(major), int(minor), int(patch), suffix or ""


def read_skill_version(path: Path) -> str | None:
    """Reads metadata.version from a SKILL.md's YAML frontmatter, manually
    (no PyYAML) -- same frontmatter-detection style as read_model_effort(),
    but 'version:' lives indented under a 'metadata:' block instead of at the
    frontmatter's top level."""
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


MARKER_RE = re.compile(r"\[\[\[(.+?)\]\]\]")

# Maps each template that uses the [[[...]]] marker convention (see
# pv-design.en.md's "Marker convention in templates") to the glob(s), relative
# to workFolder, of the real files derived from it. The template itself is the
# source of truth for which labels are protected -- this script never
# hardcodes the label list, only where to look for files written from it.
MARKED_TEMPLATES = (
    (".claude/skills/pv-internal-workflow/description.template.md",
     ("changes/inProgress/*/description.md", "changes/implemented/*/description.md")),
    (".claude/skills/pv-how/PLAN.template.md",
     ("changes/inProgress/*/plan.md",)),
    (".claude/skills/pv-todo/description.template.md",
     ("changes/todo/*/description.md",)),
)


def extract_markers(template_path: Path) -> list[str]:
    """Returns each [[[Label]]] found in a template, in file order, deduped."""
    text = template_path.read_text(encoding="utf-8")
    seen: list[str] = []
    for match in MARKER_RE.finditer(text):
        label = match.group(1).strip()
        if label not in seen:
            seen.append(label)
    return seen


def marker_pattern(label: str) -> re.Pattern:
    # A marked label appears in a template either as a bold-inline field
    # ("**[[[Label]]]**:") or as a heading ("## [[[Label]]]"); check the
    # generated file for either form, unmarked, so the check doesn't care
    # which shape a given template used.
    escaped = re.escape(label)
    return re.compile(rf"(\*\*{escaped}\*\*|^#{{1,6}}\s*{escaped}\s*$)", re.MULTILINE)


def check_marked_documents(root: Path, work_folder: str, problems: list) -> None:
    wf_path = resolve_under(root, work_folder)
    for template_rel, file_globs in MARKED_TEMPLATES:
        template_path = root / template_rel
        if not template_path.is_file():
            continue
        labels = extract_markers(template_path)
        if not labels:
            continue
        for file_glob in file_globs:
            for doc_path in sorted(wf_path.glob(file_glob)):
                text = doc_path.read_text(encoding="utf-8")
                missing = [label for label in labels if not marker_pattern(label).search(text)]
                if missing:
                    rel = doc_path.relative_to(root).as_posix()
                    add(problems, f"marker-missing:{rel}", "optional", rel,
                        f"'{rel}' is missing the structural marker(s) {', '.join(missing)} "
                        f"expected from '{template_rel}' -- likely translated or otherwise altered by hand, "
                        f"which breaks pv-status's literal parsing of them.",
                        expected=", ".join(labels), actual=", ".join(l for l in labels if l not in missing) or "(none found)")


def check_docs_dir(root: Path, work_folder: str, relative_dir: str, field: str,
                    problems: list, requires_index: bool = True) -> None:
    folder = resolve_under(root, f"{work_folder.rstrip('/')}/{relative_dir}")
    if not folder.is_dir():
        add(problems, f"{field}-missing-dir", "optional", field,
            f"'{field}' is configured as '{relative_dir}' but that folder doesn't exist on disk.",
            expected=f"directory at {folder.relative_to(root).as_posix()}",
            actual="missing")
        return
    if requires_index and not (folder / "INDEX.md").is_file():
        add(problems, f"{field}-missing-index", "optional", field,
            f"'{field}' folder exists but has no INDEX.md.",
            expected=f"{folder.relative_to(root).as_posix()}/INDEX.md",
            actual="missing")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / ".claude/pv-context.json"
    problems: list[dict] = []

    result = {
        "contextPath": ".claude/pv-context.json",
        "exists": context_path.is_file(),
        "validJson": None,
        "schemaOk": None,
        "problems": problems,
    }

    if not result["exists"]:
        add(problems, "context-missing", "required", "(file)",
            "'.claude/pv-context.json' doesn't exist -- run pv-init first, not pv-update.")
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    raw = context_path.read_text(encoding="utf-8")
    try:
        context = json.loads(raw)
    except json.JSONDecodeError as exc:
        result["validJson"] = False
        add(problems, "context-invalid-json", "required", "(file)",
            f"'.claude/pv-context.json' isn't valid JSON: {exc}")
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return
    result["validJson"] = True

    # --- Top-level shape ---
    unknown_top = sorted(set(context.keys()) - KNOWN_TOP_LEVEL)
    for key in unknown_top:
        add(problems, "unknown-top-level-field", "required", key,
            f"'{key}' isn't a field declared in schema.json (additionalProperties: false at the top level).")

    framework = context.get("framework")
    if not isinstance(framework, dict) or not framework:
        add(problems, "framework-missing", "required", "framework",
            "'framework' section is missing or empty -- the project isn't initialized.")
        result["schemaOk"] = False
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    unknown_fw = sorted(set(framework.keys()) - KNOWN_FRAMEWORK_FIELDS)
    for key in unknown_fw:
        add(problems, "unknown-framework-field", "required", f"framework.{key}",
            f"'framework.{key}' isn't a field declared in schema.json (additionalProperties: false).")

    # --- workFolder + fixed subfolders (required) ---
    work_folder = framework.get("workFolder", "/previo-sdd")
    if not isinstance(work_folder, str) or not work_folder.strip():
        add(problems, "workfolder-invalid", "required", "framework.workFolder",
            "'workFolder' must be a non-empty string.", actual=work_folder)
    else:
        wf_path = resolve_under(root, work_folder)
        if not wf_path.is_dir():
            add(problems, "workfolder-dir-missing", "required", "framework.workFolder",
                f"Configured workFolder '{work_folder}' doesn't exist as a directory in the repo.",
                expected=wf_path.relative_to(root).as_posix() if root in wf_path.parents or wf_path == root else str(wf_path),
                actual="missing")
        else:
            for sub in WORKFOLDER_SUBFOLDERS:
                sub_path = wf_path / sub
                if not sub_path.is_dir():
                    add(problems, f"workfolder-subfolder-missing:{sub}", "required",
                        f"framework.workFolder ({sub})",
                        f"Fixed subfolder '{sub}' is missing under workFolder.",
                        expected=f"{work_folder.rstrip('/')}/{sub}", actual="missing")

    # --- {xxxx} code collisions between inProgress and implemented (required) ---
    if isinstance(work_folder, str) and work_folder.strip():
        wf_path = resolve_under(root, work_folder)
        in_progress = wf_path / "changes/inProgress"
        implemented = wf_path / "changes/implemented"
        if in_progress.is_dir() and implemented.is_dir():
            codes_ip = {p.name for p in in_progress.iterdir() if p.is_dir()}
            codes_impl = {p.name for p in implemented.iterdir() if p.is_dir()}
            collisions = sorted(codes_ip & codes_impl)
            for code in collisions:
                add(problems, f"change-code-collision:{code}", "required",
                    "changes/{inProgress,implemented}",
                    f"Change code '{code}' exists in both inProgress/ and implemented/ -- codes must never repeat.",
                    actual=code)

    # --- structural markers in changes/**-derived documents (optional) ---
    if isinstance(work_folder, str) and work_folder.strip():
        check_marked_documents(root, work_folder, problems)

    # --- sourcecodeDir (required to exist if set, has a default) ---
    source_dir = framework.get("sourcecodeDir", "/src")
    if isinstance(source_dir, str) and source_dir.strip():
        src_path = resolve_under(root, source_dir)
        if not src_path.is_dir():
            add(problems, "sourcecodedir-missing", "optional", "framework.sourcecodeDir",
                f"'sourcecodeDir' is configured as '{source_dir}' but that folder doesn't exist.",
                expected=source_dir, actual="missing")

    # --- skills.mockups / skills.diagrams (required: must resolve to a real skill) ---
    skills_cfg = framework.get("skills") or {}
    skills_dir = root / ".claude/skills"
    for key in ("mockups", "diagrams"):
        name = skills_cfg.get(key)
        if not name:
            continue
        skill_md = skills_dir / name / "SKILL.md"
        if not skill_md.is_file():
            add(problems, f"skill-ref-missing:{key}", "required", f"framework.skills.{key}",
                f"'{key}' points to skill '{name}', but '.claude/skills/{name}/SKILL.md' doesn't exist.",
                expected=f".claude/skills/{name}/SKILL.md", actual="missing")

    # --- docs.* (optional: only checked if configured) ---
    docs = framework.get("docs") or {}
    functional = docs.get("functional") or {}
    tech = docs.get("tech") or {}
    if isinstance(work_folder, str) and work_folder.strip():
        if functional.get("featuresDocPathDir"):
            check_docs_dir(root, work_folder, functional["featuresDocPathDir"],
                            "framework.docs.functional.featuresDocPathDir", problems)
        if tech.get("architectureDocDir"):
            check_docs_dir(root, work_folder, tech["architectureDocDir"],
                            "framework.docs.tech.architectureDocDir", problems)
        if tech.get("styleBibleDocDir"):
            check_docs_dir(root, work_folder, tech["styleBibleDocDir"],
                            "framework.docs.tech.styleBibleDocDir", problems)

    # --- pv.py must match assets/pv.py exactly (required) ---
    pv_py = root / "pv.py"
    asset_pv_py = root / ".claude/skills/pv-init/assets/pv.py"
    if not pv_py.is_file():
        add(problems, "pvpy-missing", "required", "(repo root)/pv.py",
            "'pv.py' doesn't exist at the repo root.", expected="pv.py", actual="missing")
    elif asset_pv_py.is_file() and pv_py.read_bytes() != asset_pv_py.read_bytes():
        add(problems, "pvpy-stale", "required", "(repo root)/pv.py",
            "'pv.py' at the repo root doesn't match '.claude/skills/pv-init/assets/pv.py' -- it's out of date with the installed framework version.")

    # --- skillModels vs real SKILL.md frontmatter (optional: drift detection) ---
    skill_models = context.get("skillModels")
    if isinstance(skill_models, dict) and skill_models.get("default"):
        default = skill_models["default"]
        overrides = skill_models.get("overrides") or {}
        for skill_md in sorted(skills_dir.glob("pv-*/SKILL.md")):
            name = skill_md.parent.name
            real = read_model_effort(skill_md)
            if real is None:
                add(problems, f"skillmodel-unreadable:{name}", "optional", f"skillModels ({name})",
                    f"Couldn't read model/effort frontmatter from '{name}/SKILL.md'.")
                continue
            expected_pair = overrides.get(name, default)
            expected = (expected_pair.get("model"), expected_pair.get("effort"))
            if real != expected:
                add(problems, f"skillmodel-drift:{name}", "optional", f"skillModels ({name})",
                    f"'{name}/SKILL.md' frontmatter (model={real[0]}, effort={real[1]}) doesn't match what pv-context.json's skillModels resolves for it (model={expected[0]}, effort={expected[1]}).",
                    expected=f"{expected[0]}/{expected[1]}", actual=f"{real[0]}/{real[1]}")
        # skills referenced in overrides but that no longer exist
        for name in sorted(overrides.keys()):
            if not (skills_dir / name / "SKILL.md").is_file():
                add(problems, f"skillmodel-override-missing-skill:{name}", "required",
                    f"skillModels.overrides.{name}",
                    f"'skillModels.overrides' has an entry for '{name}', but '.claude/skills/{name}/SKILL.md' doesn't exist.",
                    expected=f".claude/skills/{name}/SKILL.md", actual="missing")

    # --- Check B: every pv-* skill should share the same major.minor version (required) ---
    versions_by_skill: dict[str, str] = {}
    for skill_md in sorted(skills_dir.glob("pv-*/SKILL.md")):
        name = skill_md.parent.name
        raw_version = read_skill_version(skill_md)
        if raw_version is None:
            add(problems, f"skill-version-unreadable:{name}", "optional", f"metadata.version ({name})",
                f"Couldn't read 'metadata.version' from '{name}/SKILL.md''s frontmatter.")
            continue
        versions_by_skill[name] = raw_version

    if versions_by_skill:
        mm_counts: dict[tuple[int, int], int] = {}
        parsed_by_skill: dict[str, tuple[int, int, int, str]] = {}
        for name, raw_version in versions_by_skill.items():
            parsed = parse_version(raw_version)
            if parsed is None:
                add(problems, f"skill-version-unreadable:{name}", "optional", f"metadata.version ({name})",
                    f"'{name}/SKILL.md''s metadata.version ('{raw_version}') doesn't match the expected 'X.Y.Z' or 'X.Y.ZbN' format.")
                continue
            parsed_by_skill[name] = parsed
            mm = (parsed[0], parsed[1])
            mm_counts[mm] = mm_counts.get(mm, 0) + 1

        if mm_counts:
            majority_mm = max(mm_counts.items(), key=lambda kv: kv[1])[0]
            majority_str = f"{majority_mm[0]}.{majority_mm[1]}"
            for name, parsed in sorted(parsed_by_skill.items()):
                mm = (parsed[0], parsed[1])
                if mm != majority_mm:
                    add(problems, f"skill-version-mismatch:{name}", "required", f"metadata.version ({name})",
                        f"'{name}/SKILL.md' is at version {versions_by_skill[name]} (major.minor {mm[0]}.{mm[1]}), "
                        f"which differs from the majority of pv-* skills at {majority_str} -- looks like a partial "
                        f"or interrupted framework update.",
                        expected=majority_str, actual=versions_by_skill[name])

    # --- Check A: pv-context.json's last verified version vs. the real installed version (required) ---
    framework_status = framework.get("frameworkStatus") or {}
    last_verified = framework_status.get("lastVerifiedVersion")
    if last_verified:
        pv_init_md = skills_dir / "pv-init" / "SKILL.md"
        real_raw = read_skill_version(pv_init_md) if pv_init_md.is_file() else None
        real_parsed = parse_version(real_raw) if real_raw else None
        verified_parsed = parse_version(last_verified)
        if real_parsed is not None and verified_parsed is not None:
            real_mmp = real_parsed[:3]
            verified_mmp = verified_parsed[:3]
            if real_mmp > verified_mmp:
                add(problems, "version-check-outdated", "required", "framework.frameworkStatus.lastVerifiedVersion",
                    f"Installed pv-init/SKILL.md is at version {real_raw}, but pv-context.json last verified "
                    f"{last_verified} -- an update was installed and pv-update hasn't run since. This audit run "
                    "itself resolves it (see mark-verified.py --clear).",
                    expected=real_raw, actual=last_verified)
            elif real_mmp < verified_mmp:
                add(problems, "version-check-downgrade", "required", "framework.frameworkStatus.lastVerifiedVersion",
                    f"Installed pv-init/SKILL.md is at version {real_raw}, OLDER than {last_verified} already "
                    "verified in pv-context.json -- looks like a downgrade, a hand-edit, or a restored stale "
                    "backup. This blocks the framework until resolved: inspect git history for these files to "
                    "understand what happened before deciding how to fix it.",
                    expected=f">= {last_verified}", actual=real_raw)

    result["schemaOk"] = not any(p["id"].startswith(("unknown-", "framework-missing")) for p in problems)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
