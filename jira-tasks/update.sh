#!/usr/bin/env bash
# Update jira-tasks: git pull (symlinks update automatically)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Updating jira-tasks..."
git -C "${SCRIPT_DIR}" pull
echo "Done."
