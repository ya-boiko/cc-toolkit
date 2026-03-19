#!/usr/bin/env bash
# Remove jira-tasks symlinks from ~/.claude/.
set -euo pipefail

COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"

echo "Uninstalling jira-tasks..."

if [ -L "${COMMANDS_DIR}/jira.md" ]; then
    rm "${COMMANDS_DIR}/jira.md"
    echo "  removed command"
fi

if [ -L "${SKILLS_DIR}/jira-tasks" ]; then
    rm "${SKILLS_DIR}/jira-tasks"
    echo "  removed skill"
fi

echo "Done."
