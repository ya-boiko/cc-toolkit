#!/usr/bin/env bash
# Install hubstaff globally for the current user.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"
SCRIPTS_DIR="${HOME}/.claude/scripts/hubstaff"

echo "Installing hubstaff..."

mkdir -p "$COMMANDS_DIR" "$SKILLS_DIR" "$SCRIPTS_DIR"

rm -f "${COMMANDS_DIR}/hubstaff.md"
ln -s "${SCRIPT_DIR}/commands/hubstaff.md" "${COMMANDS_DIR}/hubstaff.md"
echo "  command → ${COMMANDS_DIR}/hubstaff.md"

rm -f "${SKILLS_DIR}/hubstaff"
ln -s "${SCRIPT_DIR}/skills/hubstaff" "${SKILLS_DIR}/hubstaff"
echo "  skill   → ${SKILLS_DIR}/hubstaff"

rm -f "${SCRIPTS_DIR}/hubstaff_cli.py"
ln -s "${SCRIPT_DIR}/scripts/hubstaff_cli.py" "${SCRIPTS_DIR}/hubstaff_cli.py"
echo "  script  → ${SCRIPTS_DIR}/hubstaff_cli.py"

echo ""
echo "Done. /hubstaff is now available in all Claude Code sessions."
echo "To update: cd '${SCRIPT_DIR}' && git pull"
echo "To uninstall: ${SCRIPT_DIR}/uninstall.sh"
