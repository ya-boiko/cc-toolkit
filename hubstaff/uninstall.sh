#!/usr/bin/env bash
# Uninstall hubstaff: remove symlinks from ~/.claude/
set -euo pipefail

PLUGIN="hubstaff"
COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"
SCRIPTS_DIR="${HOME}/.claude/scripts/hubstaff"

echo "Uninstalling ${PLUGIN}..."

[ -L "${COMMANDS_DIR}/hubstaff.md" ]       && rm "${COMMANDS_DIR}/hubstaff.md"       && echo "  removed command"
[ -L "${SKILLS_DIR}/hubstaff" ]            && rm "${SKILLS_DIR}/hubstaff"            && echo "  removed skill"
[ -L "${SCRIPTS_DIR}/hubstaff_cli.py" ]    && rm "${SCRIPTS_DIR}/hubstaff_cli.py"    && echo "  removed script"

rmdir --ignore-fail-on-non-empty "${SCRIPTS_DIR}" 2>/dev/null || true

echo "Done."
