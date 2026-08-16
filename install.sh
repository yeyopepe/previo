#!/bin/sh
# Instala o actualiza Previo en el proyecto actual.
# Uso: curl -fsSL https://raw.githubusercontent.com/yeyopepe/previo/main/install.sh | sh
set -e

REPO="yeyopepe/previo"
BRANCH="main"
TARBALL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "Descargando Previo (${BRANCH})..."
curl -fsSL "$TARBALL" | tar -xz -C "$TMP" --strip-components=1

SRC_SKILLS="$TMP/.claude/skills"
DEST_SKILLS=".claude/skills"
mkdir -p "$DEST_SKILLS"

# Sincroniza solo las skills del framework (prefijo pv-), sin tocar skills propias del usuario.
for dir in "$SRC_SKILLS"/pv-*; do
  name=$(basename "$dir")
  rm -rf "$DEST_SKILLS/$name"
  cp -r "$dir" "$DEST_SKILLS/$name"
done

for dir in "$DEST_SKILLS"/pv-*; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  if [ ! -d "$SRC_SKILLS/$name" ]; then
    echo "Eliminando skill obsoleta: $name"
    rm -rf "$dir"
  fi
done

# Sincroniza la documentación del framework.
for doc in pv-guide.md pv-guide.en.md pv-design.md pv-design.en.md; do
  if [ -f "$TMP/.claude/$doc" ]; then
    cp "$TMP/.claude/$doc" ".claude/$doc"
  fi
done

echo "Previo instalado/actualizado en .claude/skills."
echo "Si es la primera instalación, ejecuta /pv-init en tu agente para configurarlo."
