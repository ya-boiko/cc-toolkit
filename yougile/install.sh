#!/usr/bin/env bash
# Install yougile: symlink agent and CLI into ~/.claude/, wrapper into ~/.local/bin/.
set -euo pipefail

PLUGIN="yougile"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="${HOME}/.claude/agents"
SCRIPTS_DIR="${HOME}/.claude/scripts/yougile"
BIN_DIR="${HOME}/.local/bin"
WRAPPER="${BIN_DIR}/yougile"

echo "Installing ${PLUGIN}..."
mkdir -p "${AGENTS_DIR}" "${SCRIPTS_DIR}" "${BIN_DIR}"

ln -sfn "${SCRIPT_DIR}/agents/yougile.md" "${AGENTS_DIR}/yougile.md"
echo "  agent  → ${AGENTS_DIR}/yougile.md"

for f in yougile_cli.py yougile_api.py yougile_config.py yougile_resolve.py yougile_format.py \
         yougile_commands_auth.py yougile_commands_context.py yougile_commands_tasks.py \
         yougile_commands_helpers.py yougile_commands_comments.py yougile_commands_stickers.py; do
    ln -sfn "${SCRIPT_DIR}/scripts/${f}" "${SCRIPTS_DIR}/${f}"
done
echo "  scripts → ${SCRIPTS_DIR}/"

# Wrapper that finds a working python and runs the CLI.
cat > "${WRAPPER}" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
SCRIPTS_DIR="${HOME}/.claude/scripts/yougile"
PY="$(command -v python3 || command -v python)"
PYTHONPATH="${SCRIPTS_DIR}${PYTHONPATH:+:$PYTHONPATH}" exec "$PY" "${SCRIPTS_DIR}/yougile_cli.py" "$@"
EOF
chmod +x "${WRAPPER}"
echo "  wrapper → ${WRAPPER}"

echo ""
echo "Done. Make sure ${BIN_DIR} is in your PATH."
echo "Run: yougile bootstrap"
