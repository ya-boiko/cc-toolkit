#!/usr/bin/env python3
"""Bump version field in package.json, pyproject.toml, or Cargo.toml.

Usage: bump_version.py <file-path> <new-version>

Exit codes:
  0  success
  1  error (file not found, version field not found, unsupported file type)
"""

import json
import re
import sys
from pathlib import Path


def bump_package_json(path: Path, new_version: str) -> None:
    content = json.loads(path.read_text(encoding="utf-8"))
    if "version" not in content:
        print(f"Error: no 'version' field in {path}", file=sys.stderr)
        sys.exit(1)
    content["version"] = new_version
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def bump_toml(path: Path, new_version: str) -> None:
    text = path.read_text(encoding="utf-8")
    # Match `version = "x.y.z"` or `version = "x.y"` at the start of a line
    pattern = re.compile(r'^(version\s*=\s*")[^"]*(")', re.MULTILINE)
    if not pattern.search(text):
        print(f"Error: no 'version' field found in {path}", file=sys.stderr)
        sys.exit(1)
    updated = pattern.sub(rf'\g<1>{new_version}\g<2>', text)
    path.write_text(updated, encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: bump_version.py <file-path> <new-version>", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])
    new_version = sys.argv[2]

    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    name = file_path.name

    if name == "package.json":
        bump_package_json(file_path, new_version)
    elif name == "pyproject.toml" or name == "Cargo.toml":
        bump_toml(file_path, new_version)
    else:
        print(f"Error: unsupported file type: {name}", file=sys.stderr)
        sys.exit(1)

    print(f"Bumped version to {new_version} in {file_path}")


if __name__ == "__main__":
    main()
