#!/usr/bin/env bash
# Pull latest from git and re-run install (symlinks regenerate).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."
git pull --ff-only
bash "${SCRIPT_DIR}/install.sh"
