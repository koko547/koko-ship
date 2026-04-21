#!/usr/bin/env bash
# Install koko-ship skill into ~/.claude/skills/ via symlink.
# Symlink (not copy) so edits in this repo apply immediately to the installed skill.

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_BASE="$HOME/.claude/skills"
TARGET="$TARGET_BASE/koko-ship"

mkdir -p "$TARGET_BASE"

if [ -L "$TARGET" ]; then
  echo "removing existing symlink: $TARGET"
  rm "$TARGET"
elif [ -e "$TARGET" ]; then
  echo "ERROR: $TARGET exists and is not a symlink. remove it manually first."
  exit 1
fi

ln -s "$SKILL_DIR" "$TARGET"
echo "✓ installed → $TARGET → $SKILL_DIR"
echo ""
echo "verify:"
echo "  ls -la $TARGET"
echo ""
echo "test in any project:"
echo "  cd /path/to/some/project"
echo "  claude  # then ask: 'make a BIP post about today'"
echo ""
echo "to update voice or templates: edit files in this repo, changes apply immediately."
echo "to uninstall: rm $TARGET"
