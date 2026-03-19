#!/usr/bin/env bash
# Remove hubstaff symlinks from ~/.claude/.
set -euo pipefail

COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"
SCRIPTS_DIR="${HOME}/.claude/scripts/hubstaff"

echo "Uninstalling hubstaff..."

if [ -L "${COMMANDS_DIR}/hubstaff.md" ]; then
    rm "${COMMANDS_DIR}/hubstaff.md"
    echo "  removed command"
fi

if [ -L "${SKILLS_DIR}/hubstaff" ]; then
    rm "${SKILLS_DIR}/hubstaff"
    echo "  removed skill"
fi

if [ -L "${SCRIPTS_DIR}/hubstaff_cli.py" ]; then
    rm "${SCRIPTS_DIR}/hubstaff_cli.py"
    echo "  removed script"
fi

rmdir --ignore-fail-on-non-empty "${SCRIPTS_DIR}" 2>/dev/null || true

echo "Done."
