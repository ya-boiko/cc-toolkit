#!/usr/bin/env bash
# Search upward from $PWD for .workspace.md and output the mode value.
# Outputs: "work" or "personal" (default: personal)

dir="$PWD"

while true; do
  if [[ -f "$dir/.workspace.md" ]]; then
    mode=$(grep -m1 '^mode:' "$dir/.workspace.md" 2>/dev/null | sed 's/mode:[[:space:]]*//' | tr -d '[:space:]')
    echo "${mode:-personal}"
    exit 0
  fi
  [[ "$dir" == "$HOME" || "$dir" == "/" ]] && break
  dir="$(dirname "$dir")"
done

echo "personal"
