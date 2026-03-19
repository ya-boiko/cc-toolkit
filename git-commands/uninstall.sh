#!/usr/bin/env bash
# Remove git-commands symlinks from ~/.claude/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="${HOME}/.claude/commands"

echo "Uninstalling git-commands..."

for cmd in "${SCRIPT_DIR}"/commands/*.md; do
    name="$(basename "$cmd")"
    if [ -L "${COMMANDS_DIR}/${name}" ]; then
        rm "${COMMANDS_DIR}/${name}"
        echo "  removed ${name}"
    fi
done

echo "Done."
