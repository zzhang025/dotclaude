#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create target directories if they don't exist
mkdir -p "$HOME/.claude"
mkdir -p "$HOME/.config/ccstatusline"

# Create a symlink, backing up any existing non-symlink file or directory first
link() {
  local src="$1"
  local dst="$2"

  if [ -L "$dst" ]; then
    # Already a symlink — remove and replace
    rm "$dst"
  elif [ -e "$dst" ]; then
    echo "Backing up: $dst -> $dst.bak"
    mv "$dst" "$dst.bak"
  fi

  ln -s "$src" "$dst"
  echo "Linked: $dst -> $src"
}

link "$REPO_DIR/CLAUDE.md"                  "$HOME/.claude/CLAUDE.md"
link "$REPO_DIR/settings.json"              "$HOME/.claude/settings.json"
link "$REPO_DIR/skills"                     "$HOME/.claude/skills"
link "$REPO_DIR/ccstatusline/settings.json" "$HOME/.config/ccstatusline/settings.json"

echo ""
echo "Done. Claude Code config linked from $REPO_DIR"
echo "Run 'claude' to authenticate if this is a new machine."
