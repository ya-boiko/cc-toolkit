#!/usr/bin/env bash
# Uninstall tododo: remove symlinks from ~/.claude/
set -euo pipefail

PLUGIN="tododo"
COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"
SCRIPTS_DIR="${HOME}/.claude/scripts/tododo"

echo "Uninstalling ${PLUGIN}..."

[ -L "${COMMANDS_DIR}/tododo.md" ]           && rm "${COMMANDS_DIR}/tododo.md"           && echo "  removed command"
[ -L "${COMMANDS_DIR}/tododo:interface.md" ] && rm "${COMMANDS_DIR}/tododo:interface.md" && echo "  removed interface command"
[ -L "${SKILLS_DIR}/tododo" ]                && rm "${SKILLS_DIR}/tododo"                && echo "  removed skill"
[ -L "${SCRIPTS_DIR}/scan_todos.py" ]        && rm "${SCRIPTS_DIR}/scan_todos.py"        && echo "  removed scanner"
[ -L "${SCRIPTS_DIR}/tododo_web.py" ]        && rm "${SCRIPTS_DIR}/tododo_web.py"        && echo "  removed web server"
[ -f "${HOME}/.claude/tododo_root" ]         && rm "${HOME}/.claude/tododo_root"         && echo "  removed root config"

rmdir --ignore-fail-on-non-empty "${SCRIPTS_DIR}" 2>/dev/null || true

echo "Done."
