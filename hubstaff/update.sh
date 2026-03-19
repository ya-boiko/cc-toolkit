#!/usr/bin/env bash
# Pull the latest version of hubstaff.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Updating hubstaff..."
git -C "$SCRIPT_DIR" pull
echo "Done."
