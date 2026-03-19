#!/usr/bin/env bash
# Remove tododo symlinks from ~/.claude/.
set -euo pipefail

COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"

echo "Uninstalling tododo..."

if [ -L "${COMMANDS_DIR}/tododo.md" ]; then
    rm "${COMMANDS_DIR}/tododo.md"
    echo "  removed command"
fi

if [ -L "${COMMANDS_DIR}/tododo:interface.md" ]; then
    rm "${COMMANDS_DIR}/tododo:interface.md"
    echo "  removed interface command"
fi

if [ -L "${SKILLS_DIR}/tododo" ]; then
    rm "${SKILLS_DIR}/tododo"
    echo "  removed skill"
fi

if [ -f "${HOME}/.claude/tododo_root" ]; then
    rm "${HOME}/.claude/tododo_root"
    echo "  removed root config"
fi

if [ -L "${HOME}/.claude/scripts/tododo/scan_todos.py" ]; then
    rm "${HOME}/.claude/scripts/tododo/scan_todos.py"
    echo "  removed scanner"
fi

if [ -L "${HOME}/.claude/scripts/tododo/tododo_web.py" ]; then
    rm "${HOME}/.claude/scripts/tododo/tododo_web.py"
    echo "  removed web server"
fi

rmdir --ignore-fail-on-non-empty "${HOME}/.claude/scripts/tododo" 2>/dev/null || true

echo "Done."
