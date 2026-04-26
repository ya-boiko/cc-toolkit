#!/usr/bin/env bash
set -euo pipefail

AGENTS_DIR="${HOME}/.claude/agents"
SCRIPTS_DIR="${HOME}/.claude/scripts/yougile"
WRAPPER="${HOME}/.local/bin/yougile"

echo "Uninstalling yougile..."
rm -f "${AGENTS_DIR}/yougile.md"
rm -rf "${SCRIPTS_DIR}"
rm -f "${WRAPPER}"
echo "Done. (Config at ~/.config/yougile/config.json was NOT removed; run 'rm ~/.config/yougile/config.json' if desired.)"
