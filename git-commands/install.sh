#!/usr/bin/env bash
# Install git-commands globally for the current user.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="${HOME}/.claude/commands"

echo "Installing git-commands..."

mkdir -p "$COMMANDS_DIR"

for cmd in "${SCRIPT_DIR}"/commands/*.md; do
    name="$(basename "$cmd")"
    rm -f "${COMMANDS_DIR}/${name}"
    ln -s "$cmd" "${COMMANDS_DIR}/${name}"
    echo "  command → ${COMMANDS_DIR}/${name}"
done

echo ""
echo "Done. Commands are now available in all Claude Code sessions."
echo "To update: cd '${SCRIPT_DIR}' && git pull"
echo "To uninstall: ${SCRIPT_DIR}/uninstall.sh"
