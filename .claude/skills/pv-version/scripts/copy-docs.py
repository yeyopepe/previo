#!/usr/bin/env python3
"""Comprime y copia la documentacion vigente a una entrega (skill ms-version).

Comprime en un .zip cada una de las rutas configuradas en
framework.docs.tech.architectureDocDir, framework.docs.tech.styleBibleDocDir
y framework.docs.functional.featuresDocPathDir de .claude/ms-context.json, y
guarda cada .zip en {workFolder}/versions/{xxxx}/docs/. Cada ruta puede ser
una carpeta (se comprime entera, incluido su INDEX.md si lo tiene) o un
unico fichero .md (caso valido de featuresDocPathDir en proyectos que no
migraron a carpeta) -- en ambos casos el .zip resultante se llama como el
nombre base de la ruta (carpeta o fichero sin extension) + ".zip". Las que
no esten configuradas se omiten sin error (igual que el resto del framework
trata estos campos opcionales).

Imprime UNICAMENTE un JSON en stdout con lo copiado, para que la skill lo
use al confirmar al usuario:

  {"copied": ["design/docs/architecture", "design/docs/style"], "skipped": ["featuresDocPathDir"]}

Uso:
  python copy-docs.py --xxxx 00001
"""

import argparse
import json
import sys
import zipfile
from pathlib import Path


def repo_root() -> Path:
    # Este script vive en {repo}/.claude/skills/ms-version/scripts/
    return Path(__file__).resolve().parents[4]


def load_framework(root: Path) -> dict:
    context_path = root / ".claude" / "ms-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"No se encuentra {context_path}. Ejecuta la skill ms-init antes de "
            "copiar documentacion."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} no tiene la seccion 'framework'. Ejecuta la skill "
            "ms-init para completarla."
        )
    return framework


def resolve_versions_dir(root: Path, work_folder_rel: str) -> Path:
    work_folder_rel = work_folder_rel or "/"
    work_root = root if work_folder_rel in ("/", "") else root / work_folder_rel
    return work_root / "versions"


def zip_dir(source_dir: Path, dest_zip: Path) -> None:
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(source_dir))


def zip_file(source_file: Path, dest_zip: Path) -> None:
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(source_file, source_file.name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xxxx", required=True, help="Codigo de la version que se esta preparando.")
    parser.add_argument(
        "--work-folder",
        help="Ruta a workFolder relativa a la raiz del repo. Si no se indica, "
        "se lee de .claude/ms-context.json (default '/').",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    framework = load_framework(root)
    work_folder_rel = args.work_folder or framework.get("workFolder", "/")
    versions_dir = resolve_versions_dir(root, work_folder_rel)

    version_docs_dir = versions_dir / args.xxxx / "docs"
    if not version_docs_dir.is_dir():
        raise SystemExit(
            f"No existe {version_docs_dir}. Ejecuta primero init-version-folder.py "
            "para crear la carpeta de la version."
        )

    docs = framework.get("docs") or {}
    tech_docs = docs.get("tech") or {}
    functional_docs = docs.get("functional") or {}
    candidates = {
        "architectureDocDir": tech_docs.get("architectureDocDir"),
        "styleBibleDocDir": tech_docs.get("styleBibleDocDir"),
        "featuresDocPathDir": functional_docs.get("featuresDocPathDir"),
    }

    copied: list[str] = []
    skipped: list[str] = []

    for field, doc_path_rel in candidates.items():
        if not doc_path_rel:
            skipped.append(field)
            continue

        source_path = root / doc_path_rel
        if source_path.is_dir():
            dest_zip = version_docs_dir / f"{source_path.name}.zip"
            zip_dir(source_path, dest_zip)
        elif source_path.is_file():
            dest_zip = version_docs_dir / f"{source_path.stem}.zip"
            zip_file(source_path, dest_zip)
        else:
            raise SystemExit(
                f"'{field}' apunta a {source_path}, pero esa ruta no existe."
            )

        copied.append(doc_path_rel)

    json.dump({"copied": copied, "skipped": skipped}, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
