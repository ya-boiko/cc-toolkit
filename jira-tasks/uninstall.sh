#!/usr/bin/env bash
# Uninstall jira-tasks: remove symlinks from ~/.claude/
set -euo pipefail

PLUGIN="jira-tasks"
COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"

echo "Uninstalling ${PLUGIN}..."

[ -L "${COMMANDS_DIR}/jira.md" ]    && rm "${COMMANDS_DIR}/jira.md"    && echo "  removed command"
[ -L "${SKILLS_DIR}/jira-tasks" ]   && rm "${SKILLS_DIR}/jira-tasks"   && echo "  removed skill"

echo "Done."
