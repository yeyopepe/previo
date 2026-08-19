#!/bin/sh
# Instala o actualiza Previo en el proyecto actual.
# Uso: curl -fsSL https://raw.githubusercontent.com/yeyopepe/previo-sdd/main/install.sh | sh
# Uso (versión concreta): curl -fsSL https://raw.githubusercontent.com/yeyopepe/previo-sdd/main/install.sh | sh -s -- v1.2.3
set -e

REPO="yeyopepe/previo-sdd"
REQUESTED_TAG="$1"

if [ -n "$REQUESTED_TAG" ]; then
  RELEASE_JSON=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/tags/${REQUESTED_TAG}") || {
    echo "La versión '${REQUESTED_TAG}' no existe en los releases de Previo." >&2
    exit 1
  }
  TAG=$(echo "$RELEASE_JSON" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')
else
  TAG=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')
fi
if [ -z "$TAG" ]; then
  echo "No se ha podido determinar la versión de Previo a instalar." >&2
  exit 1
fi
TARBALL="https://github.com/${REPO}/archive/refs/tags/${TAG}.tar.gz"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "Descargando Previo (${TAG})..."
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
mkdir -p ".claude/pv-doc"
for doc in pv-guide.en.md pv-guide.es.md; do
  if [ -f "$TMP/.claude/pv-doc/$doc" ]; then
    cp "$TMP/.claude/pv-doc/$doc" ".claude/pv-doc/$doc"
  fi
done

# Sincroniza el lanzador pv.py en la raíz del repo (fichero generado, se sobrescribe siempre).
if [ -f "$SRC_SKILLS/pv-init/assets/pv.py" ]; then
  cp "$SRC_SKILLS/pv-init/assets/pv.py" "pv.py"
fi

echo "Previo instalado/actualizado en .claude/skills."
echo "Si es la primera instalación, ejecuta /pv-init en tu agente para configurarlo."
