#!/bin/sh
# Installs or updates Previo in the current project.
# Usage: curl -fsSL https://raw.githubusercontent.com/yeyopepe/previo-sdd/main/install.sh | sh
# Usage (specific version): curl -fsSL https://raw.githubusercontent.com/yeyopepe/previo-sdd/main/install.sh | sh -s -- v1.2.3
set -e

REPO="yeyopepe/previo-sdd"
REQUESTED_TAG="$1"

# Detect, before overwriting anything, whether this project already had the
# framework installed -- used at the end to show the right next-step message.
WAS_ALREADY_INSTALLED=0
[ -d ".claude/skills/pv-init" ] && WAS_ALREADY_INSTALLED=1

if [ -n "$REQUESTED_TAG" ]; then
  RELEASE_JSON=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/tags/${REQUESTED_TAG}") || {
    echo "Version '${REQUESTED_TAG}' doesn't exist in Previo's releases." >&2
    exit 1
  }
  TAG=$(echo "$RELEASE_JSON" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')
else
  TAG=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')
fi
if [ -z "$TAG" ]; then
  echo "Couldn't determine which version of Previo to install." >&2
  exit 1
fi
TARBALL="https://github.com/${REPO}/archive/refs/tags/${TAG}.tar.gz"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "Downloading Previo (${TAG})..."
curl -fsSL "$TARBALL" | tar -xz -C "$TMP" --strip-components=1

SRC_SKILLS="$TMP/.claude/skills"
DEST_SKILLS=".claude/skills"
mkdir -p "$DEST_SKILLS"

# Syncs only the framework's own skills (pv- prefix), without touching the user's own skills.
for dir in "$SRC_SKILLS"/pv-*; do
  name=$(basename "$dir")
  rm -rf "$DEST_SKILLS/$name"
  cp -r "$dir" "$DEST_SKILLS/$name"
done

for dir in "$DEST_SKILLS"/pv-*; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  if [ ! -d "$SRC_SKILLS/$name" ]; then
    echo "Removing obsolete skill: $name"
    rm -rf "$dir"
  fi
done

# Syncs the framework's documentation.
mkdir -p ".claude/pv-doc"
for doc in pv-guide.en.md pv-guide.es.md; do
  if [ -f "$TMP/.claude/pv-doc/$doc" ]; then
    cp "$TMP/.claude/pv-doc/$doc" ".claude/pv-doc/$doc"
  fi
done

# Syncs the framework's changelog.
CHANGELOG_MISSING=0
for doc in pv-changelog.en.md pv-changelog.es.md; do
  if [ -f "$TMP/.claude/$doc" ]; then
    cp "$TMP/.claude/$doc" ".claude/$doc"
  else
    CHANGELOG_MISSING=1
  fi
done

# Syncs the pv.py launcher at the repo root (generated file, always overwritten).
if [ -f "$SRC_SKILLS/pv-init/assets/pv.py" ]; then
  cp "$SRC_SKILLS/pv-init/assets/pv.py" "pv.py"
fi

echo "Previo installed/updated in .claude/skills."
echo ""
if [ "$CHANGELOG_MISSING" = "1" ]; then
  echo "=========================================================="
  echo " Warning: the new version was installed, but something"
  echo " went wrong and the changelog for this release is missing."
  echo " You won't have information about what changed."
  echo "=========================================================="
  echo ""
fi
if [ "$WAS_ALREADY_INSTALLED" = "1" ]; then
  echo "=========================================================="
  echo " You're updating from a previous version: run /pv-update"
  echo " in your agent to check and repair the configuration."
  echo "=========================================================="
else
  echo "=========================================================="
  echo " First install: run /pv-init in your agent to set it up."
  echo "=========================================================="
fi
