#!/usr/bin/env bash
# Install jira-tasks globally for the current user.
# Symlinks the command and skill into ~/.claude/ so /jira and the skill
# are available in every Claude Code session.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"

echo "Installing jira-tasks..."

mkdir -p "$COMMANDS_DIR" "$SKILLS_DIR"

rm -f "${COMMANDS_DIR}/jira.md"
ln -s "${SCRIPT_DIR}/commands/jira.md" "${COMMANDS_DIR}/jira.md"
echo "  command → ${COMMANDS_DIR}/jira.md"

rm -f "${SKILLS_DIR}/jira-tasks"
ln -s "${SCRIPT_DIR}/skills/jira-tasks" "${SKILLS_DIR}/jira-tasks"
echo "  skill   → ${SKILLS_DIR}/jira-tasks"

echo ""
echo "Done. /jira is now available in all Claude Code sessions."
echo "To update: cd '${SCRIPT_DIR}' && git pull"
echo "To uninstall: ${SCRIPT_DIR}/uninstall.sh"
