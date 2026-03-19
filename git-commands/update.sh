#!/usr/bin/env bash
# Pull the latest version of git-commands.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Updating git-commands..."
git -C "$SCRIPT_DIR" pull
echo "Done."
