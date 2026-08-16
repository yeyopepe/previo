#!/usr/bin/env python3
"""Sincroniza .claude/ms-context.json#skillModels con el frontmatter de cada SKILL.md 'ms-*'.

El harness de Claude Code decide que modelo/esfuerzo usa una skill leyendo
los campos 'model'/'effort' del frontmatter de su propio SKILL.md, en el
momento de cargarla -- no lee .claude/ms-context.json. Por eso la seccion
'skillModels' de ms-context.json es solo la fuente de verdad "humana": este
script es el que de verdad propaga esos valores al frontmatter real.

Reglas:
- Recorre .claude/skills/ms-*/SKILL.md (ignora skills que no empiecen por 'ms-').
- Para cada skill, resuelve su modelo/esfuerzo: 'overrides[<name>]' si existe,
  si no 'default'. Si no hay seccion 'skillModels' en ms-context.json, no toca nada.
- Inserta o actualiza (en el nivel superior del frontmatter, junto a 'name'/
  'description') las claves 'model:' y 'effort:', justo antes de 'metadata:'
  (o antes del cierre '---' si esa skill no tiene bloque 'metadata:').
- Si el valor resuelto cambia respecto al que ya tenia el fichero, incrementa
  en 1 el patch de 'metadata.version' (x.y.z -> x.y.(z+1)). Si no cambia nada,
  no toca el fichero (ni su version).

Uso:
  python .claude/skills/ms-init/scripts/sync-skill-models.py [--dry-run]
"""

import argparse
import json
import re
import sys
from pathlib import Path


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/ms-init/scripts/
    return Path(__file__).resolve().parents[4]


def bump_patch(version: str) -> str:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version.strip())
    if not match:
        return version
    major, minor, patch = match.groups()
    return f"{major}.{minor}.{int(patch) + 1}"


def sync_skill_file(path: Path, model: str, effort: str) -> str | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    if not lines or lines[0].strip() != "---":
        return None
    try:
        close_idx = next(
            i for i in range(1, len(lines)) if lines[i].strip() == "---"
        )
    except StopIteration:
        return None

    frontmatter = lines[1:close_idx]
    rest = lines[close_idx:]

    existing_model = None
    existing_effort = None
    kept = []
    metadata_idx = None
    for line in frontmatter:
        key_match = re.match(r"^(model|effort):\s*(.*)$", line)
        if key_match:
            if key_match.group(1) == "model":
                existing_model = key_match.group(2).strip().strip('"').strip("'")
            else:
                existing_effort = key_match.group(2).strip().strip('"').strip("'")
            continue
        if metadata_idx is None and re.match(r"^metadata:\s*$", line):
            metadata_idx = len(kept)
        kept.append(line)

    if existing_model == model and existing_effort == effort:
        return None

    insert_at = metadata_idx if metadata_idx is not None else len(kept)
    new_lines = (
        kept[:insert_at]
        + [f"model: {model}\n", f"effort: {effort}\n"]
        + kept[insert_at:]
    )

    # Bump metadata.version patch, if a metadata block with a version exists.
    for i, line in enumerate(new_lines):
        version_match = re.match(r"^(\s+)version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", line)
        if version_match:
            indent, version = version_match.groups()
            new_lines[i] = f"{indent}version: {bump_patch(version)}\n"
            break

    new_text = "".join(["---\n"] + new_lines + rest)
    path.write_text(new_text, encoding="utf-8", newline="")
    return new_text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra que ficheros cambiarian sin escribir nada.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / ".claude/ms-context.json"
    if not context_path.is_file():
        print("No existe .claude/ms-context.json -- nada que sincronizar.")
        return

    context = json.loads(context_path.read_text(encoding="utf-8"))
    skill_models = context.get("skillModels")
    if not skill_models or "default" not in skill_models:
        print("No hay seccion 'skillModels.default' en ms-context.json -- nada que sincronizar.")
        return

    default = skill_models["default"]
    overrides = skill_models.get("overrides", {})

    skills_dir = root / ".claude/skills"
    changed = []
    for skill_md in sorted(skills_dir.glob("ms-*/SKILL.md")):
        skill_name = skill_md.parent.name
        resolved = overrides.get(skill_name, default)
        model, effort = resolved["model"], resolved["effort"]

        if args.dry_run:
            before = skill_md.read_text(encoding="utf-8")
            model_match = re.search(r"^model:\s*(.+)$", before, re.MULTILINE)
            effort_match = re.search(r"^effort:\s*(.+)$", before, re.MULTILINE)
            current_model = model_match.group(1).strip() if model_match else None
            current_effort = effort_match.group(1).strip() if effort_match else None
            if current_model != model or current_effort != effort:
                changed.append(f"{skill_name}: {current_model}/{current_effort} -> {model}/{effort}")
            continue

        if sync_skill_file(skill_md, model, effort) is not None:
            changed.append(f"{skill_name}: -> {model}/{effort}")

    if changed:
        print(("[dry-run] " if args.dry_run else "") + "Actualizado:")
        for line in changed:
            print(f"  - {line}")
    else:
        print("Todo el frontmatter ya estaba sincronizado con ms-context.json.")


if __name__ == "__main__":
    main()
