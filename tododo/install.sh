#!/usr/bin/env bash
# Install tododo: symlink commands, skill, and scripts into ~/.claude/
set -euo pipefail

PLUGIN="tododo"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"
SCRIPTS_DIR="${HOME}/.claude/scripts/tododo"

echo "Installing ${PLUGIN}..."
mkdir -p "${COMMANDS_DIR}" "${SKILLS_DIR}" "${SCRIPTS_DIR}"

rm -f "${COMMANDS_DIR}/tododo.md"
ln -s "${SCRIPT_DIR}/commands/tododo.md" "${COMMANDS_DIR}/tododo.md"
echo "  command → ${COMMANDS_DIR}/tododo.md"

rm -f "${COMMANDS_DIR}/tododo:interface.md"
ln -s "${SCRIPT_DIR}/commands/tododo:interface.md" "${COMMANDS_DIR}/tododo:interface.md"
echo "  command → ${COMMANDS_DIR}/tododo:interface.md"

rm -f "${SKILLS_DIR}/tododo"
ln -s "${SCRIPT_DIR}/skills/tododo" "${SKILLS_DIR}/tododo"
echo "  skill   → ${SKILLS_DIR}/tododo"

echo "${SCRIPT_DIR}" > "${HOME}/.claude/tododo_root"
echo "  root    → ${HOME}/.claude/tododo_root"

rm -f "${SCRIPTS_DIR}/scan_todos.py"
ln -s "${SCRIPT_DIR}/scripts/scan_todos.py" "${SCRIPTS_DIR}/scan_todos.py"
echo "  script  → ${SCRIPTS_DIR}/scan_todos.py"

rm -f "${SCRIPTS_DIR}/tododo_web.py"
ln -s "${SCRIPT_DIR}/scripts/tododo_web.py" "${SCRIPTS_DIR}/tododo_web.py"
echo "  script  → ${SCRIPTS_DIR}/tododo_web.py"

echo ""
echo "Done. /tododo is now available in all Claude Code sessions."
