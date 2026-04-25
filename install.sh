#!/usr/bin/env bash
# Install koko-ship skill into ~/.claude/skills/ by copying the skill folder.

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_BASE="$HOME/.claude/skills"
TARGET="$TARGET_BASE/koko-ship"

mkdir -p "$TARGET_BASE"

if [ -d "$TARGET" ]; then
  echo "existing koko-ship skill found at: $TARGET"
  echo "replacing with new version from: $SKILL_DIR"
  rm -rf "$TARGET"
elif [ -L "$TARGET" ]; then
  echo "removing existing symlink: $TARGET"
  rm "$TARGET"
elif [ -e "$TARGET" ]; then
  echo "ERROR: $TARGET exists and is not a directory or symlink. remove it manually first."
  exit 1
fi

cp -r "$SKILL_DIR" "$TARGET"

echo ""
echo "installed koko-ship skill to $TARGET"
echo ""
echo "usage (in any project you're building):"
echo "  cd /path/to/your/project"
echo "  claude"
echo "  > set up my voice    (first time only)"
echo "  > make a bip post"
echo ""
echo "to update: re-run this script."
echo "to uninstall: rm -rf $TARGET"
