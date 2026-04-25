#!/usr/bin/env bash
# Install koko-ship skill suite into ~/.claude/skills/
# Each skill gets its own top-level directory for Claude Code discovery.
# Shared resources (references, scripts) go in koko-ship-shared/.

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_BASE="$HOME/.claude/skills"

echo "installing koko-ship skill suite..."

# Clean up old monolithic install if present
if [ -d "$TARGET_BASE/koko-ship" ] || [ -L "$TARGET_BASE/koko-ship" ]; then
  echo "  removing old koko-ship install..."
  rm -rf "$TARGET_BASE/koko-ship"
fi

# Install each skill as a separate top-level directory
for skill in writer editor qa voice-setup; do
  target="$TARGET_BASE/koko-ship-$skill"
  if [ -d "$target" ]; then
    rm -rf "$target"
  elif [ -L "$target" ]; then
    rm "$target"
  fi
  mkdir -p "$target"
  cp "$REPO_DIR/skills/$skill/SKILL.md" "$target/"
  echo "  installed koko-ship-$skill"
done

# Install shared resources
shared="$TARGET_BASE/koko-ship-shared"
if [ -d "$shared" ]; then
  rm -rf "$shared"
elif [ -L "$shared" ]; then
  rm "$shared"
fi
mkdir -p "$shared"
cp -r "$REPO_DIR/references" "$shared/"
cp -r "$REPO_DIR/scripts" "$shared/"
echo "  installed koko-ship-shared (references + scripts)"

echo ""
echo "done. installed 4 skills + shared resources to $TARGET_BASE/"
echo ""
echo "usage:"
echo "  cd /path/to/your/project"
echo "  claude"
echo "  > set up my voice    (first time)"
echo "  > make a bip post"
echo ""
echo "to update: re-run this script."
echo "to uninstall:"
echo "  rm -rf ~/.claude/skills/koko-ship-writer"
echo "  rm -rf ~/.claude/skills/koko-ship-editor"
echo "  rm -rf ~/.claude/skills/koko-ship-qa"
echo "  rm -rf ~/.claude/skills/koko-ship-voice-setup"
echo "  rm -rf ~/.claude/skills/koko-ship-shared"
