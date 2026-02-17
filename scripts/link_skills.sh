#!/bin/bash
# Create symlinks from ~/.claude/skills/ to project skills.
# This makes skills available to Claude Desktop when the upload API is down.
#
# Usage:
#   ./scripts/link_skills.sh          # create symlinks
#   ./scripts/link_skills.sh --clean  # remove symlinks

set -euo pipefail

SKILLS_DIR="$HOME/.claude/skills"
PROJECT_SKILLS="$(cd "$(dirname "$0")/../skills" && pwd)"

mkdir -p "$SKILLS_DIR"

if [ "${1:-}" = "--clean" ]; then
    for skill_dir in "$PROJECT_SKILLS"/*/; do
        skill_name=$(basename "$skill_dir")
        link="$SKILLS_DIR/$skill_name"
        if [ -L "$link" ]; then
            rm "$link"
            echo "Removed: $link"
        fi
    done
    exit 0
fi

for skill_dir in "$PROJECT_SKILLS"/*/; do
    skill_name=$(basename "$skill_dir")
    link="$SKILLS_DIR/$skill_name"
    if [ -L "$link" ]; then
        echo "Already linked: $skill_name"
    elif [ -e "$link" ]; then
        echo "Skipped: $link exists and is not a symlink"
    else
        ln -s "$skill_dir" "$link"
        echo "Linked: $skill_name -> $skill_dir"
    fi
done
