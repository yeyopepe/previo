#!/usr/bin/env python3
"""Localiza la version anterior en {workFolder}/versions/ (skill ms-internal-changelog).

Recorre las subcarpetas directas de {workFolder}/versions/, excluye la que
se esta generando (--xxxx), y devuelve la de fecha de creacion mas reciente
segun el mtime de la propia carpeta -- no del xxxx (que es texto libre, no
ordenable cronologicamente). Quien invoca debe confirmar con el usuario que
la candidata devuelta es realmente la version anterior correcta antes de
usarla, por si hubiera ambiguedad.

workFolder se lee de .claude/ms-context.json (seccion framework) salvo que
se pase explicitamente por parametro.

Imprime UNICAMENTE un JSON en stdout:

  {"found": true, "xxxx": "00001", "changelogPath": "versions/00001/changelog.md", "changelogExists": true}
  {"found": false, "xxxx": null, "changelogPath": null, "changelogExists": false}

"found": false si no hay ninguna otra carpeta en versions/ aparte de la que
se esta generando. "changelogExists": false si la carpeta encontrada no
tiene changelog.md todavia (p.ej. una version a medio preparar).

Uso:
  python find-previous-version.py --xxxx 00002
"""

import argparse
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/ms-internal-changelog/scripts/
    return Path(__file__).resolve().parents[4]


def load_work_folder(root: Path) -> str:
    context_path = root / ".claude" / "ms-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"No se encuentra {context_path}. Ejecuta la skill ms-init antes de "
            "buscar la version anterior."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} no tiene la seccion 'framework'. Ejecuta la skill "
            "ms-init para completarla."
        )
    return framework.get("workFolder", "/")


def resolve_versions_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "versions"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xxxx", required=True, help="Codigo de la version que se esta generando (se excluye de la busqueda).")
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/ms-context.json (default '/').",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    work_folder_rel = args.work_folder or load_work_folder(root)
    versions_dir = resolve_versions_dir(root, work_folder_rel)

    candidates = []
    if versions_dir.is_dir():
        candidates = [
            p for p in versions_dir.iterdir() if p.is_dir() and p.name != args.xxxx
        ]

    if not candidates:
        json.dump(
            {"found": False, "xxxx": None, "changelogPath": None, "changelogExists": False},
            sys.stdout,
            ensure_ascii=False,
        )
        print()
        return

    most_recent = max(candidates, key=lambda p: p.stat().st_ctime)
    changelog_path = most_recent / "changelog.md"

    json.dump(
        {
            "found": True,
            "xxxx": most_recent.name,
            "changelogPath": changelog_path.relative_to(root).as_posix(),
            "changelogExists": changelog_path.is_file(),
        },
        sys.stdout,
        ensure_ascii=False,
    )
    print()


if __name__ == "__main__":
    main()
