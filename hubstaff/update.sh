#!/usr/bin/env bash
# Update hubstaff: git pull (symlinks update automatically)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Updating hubstaff..."
git -C "${SCRIPT_DIR}" pull
echo "Done."
