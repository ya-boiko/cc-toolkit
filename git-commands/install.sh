#!/usr/bin/env bash
# Install git-commands: symlink all commands into ~/.claude/commands/
set -euo pipefail

PLUGIN="git-commands"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="${HOME}/.claude/commands"

echo "Installing ${PLUGIN}..."
mkdir -p "${COMMANDS_DIR}"

for cmd in "${SCRIPT_DIR}"/commands/*.md; do
    name="$(basename "${cmd}")"
    rm -f "${COMMANDS_DIR}/${name}"
    ln -s "${cmd}" "${COMMANDS_DIR}/${name}"
    echo "  command → ${COMMANDS_DIR}/${name}"
done

echo ""
echo "Done. Commands are now available in all Claude Code sessions."
