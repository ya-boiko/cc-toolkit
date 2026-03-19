#!/usr/bin/env bash
# Install hubstaff: symlink command, skill, and script into ~/.claude/
set -euo pipefail

PLUGIN="hubstaff"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"
SCRIPTS_DIR="${HOME}/.claude/scripts/hubstaff"
CONFIG_FILE="${SCRIPTS_DIR}/config"

echo "Installing ${PLUGIN}..."
mkdir -p "${COMMANDS_DIR}" "${SKILLS_DIR}" "${SCRIPTS_DIR}"

rm -f "${COMMANDS_DIR}/hubstaff.md"
ln -s "${SCRIPT_DIR}/commands/hubstaff.md" "${COMMANDS_DIR}/hubstaff.md"
echo "  command → ${COMMANDS_DIR}/hubstaff.md"

rm -f "${SKILLS_DIR}/hubstaff"
ln -s "${SCRIPT_DIR}/skills/hubstaff" "${SKILLS_DIR}/hubstaff"
echo "  skill   → ${SKILLS_DIR}/hubstaff"

rm -f "${SCRIPTS_DIR}/hubstaff_cli.py"
ln -s "${SCRIPT_DIR}/scripts/hubstaff_cli.py" "${SCRIPTS_DIR}/hubstaff_cli.py"
echo "  script  → ${SCRIPTS_DIR}/hubstaff_cli.py"

# Detect Hubstaff CLI binary
echo ""
echo "Looking for Hubstaff CLI binary..."

SEARCH_PATHS=(
    "${HOME}/Hubstaff/HubstaffCLI.bin.x86_64"
    "${HOME}/Applications/Hubstaff/HubstaffCLI.bin.x86_64"
    "/opt/Hubstaff/HubstaffCLI.bin.x86_64"
    "/usr/local/bin/HubstaffCLI"
)

CLI_PATH=""
for path in "${SEARCH_PATHS[@]}"; do
    if [ -x "${path}" ]; then
        CLI_PATH="${path}"
        echo "  found   → ${CLI_PATH}"
        break
    fi
done

if [ -z "${CLI_PATH}" ]; then
    echo "  not found in common locations."
    read -rp "  Enter path to Hubstaff CLI binary: " CLI_PATH
    if [ ! -x "${CLI_PATH}" ]; then
        echo "  Warning: '${CLI_PATH}' is not executable or does not exist."
        echo "  You can update the path later in: ${CONFIG_FILE}"
    fi
fi

echo "HUBSTAFF_CLI=${CLI_PATH}" > "${CONFIG_FILE}"
echo "  config  → ${CONFIG_FILE}"

echo ""
echo "Done. /hubstaff is now available in all Claude Code sessions."
