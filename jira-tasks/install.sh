#!/usr/bin/env bash
# Install jira-tasks: symlink command and skill into ~/.claude/
set -euo pipefail

PLUGIN="jira-tasks"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"

echo "Installing ${PLUGIN}..."
mkdir -p "${COMMANDS_DIR}" "${SKILLS_DIR}"

rm -f "${COMMANDS_DIR}/jira.md"
ln -s "${SCRIPT_DIR}/commands/jira.md" "${COMMANDS_DIR}/jira.md"
echo "  command → ${COMMANDS_DIR}/jira.md"

rm -f "${SKILLS_DIR}/jira-tasks"
ln -s "${SCRIPT_DIR}/skills/jira-tasks" "${SKILLS_DIR}/jira-tasks"
echo "  skill   → ${SKILLS_DIR}/jira-tasks"

echo ""
echo "Done. /jira is now available in all Claude Code sessions."
