#!/usr/bin/env bash
# Pull the latest version of tododo.
# Symlinks created by install.sh update automatically — no re-install needed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Updating tododo..."
git -C "$SCRIPT_DIR" pull
echo "Done."
