#!/usr/bin/env bash
# Uninstall git-commands: remove symlinks from ~/.claude/commands/
set -euo pipefail

PLUGIN="git-commands"
COMMANDS_DIR="${HOME}/.claude/commands"

echo "Uninstalling ${PLUGIN}..."

for name in commit.md generate-pr.md mr.md; do
    [ -L "${COMMANDS_DIR}/${name}" ] && rm "${COMMANDS_DIR}/${name}" && echo "  removed ${name}"
done

echo "Done."
