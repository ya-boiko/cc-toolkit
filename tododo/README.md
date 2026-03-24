# /tododo — TODO Manager for Claude Code

Slash command and skill for Claude Code that manages TODO/FIXME/HACK/XXX comments in your codebase.

## Features

- **`/tododo`** or **`/tododo list`** — scan and display all TODO comments
- **`/tododo edit <id> <new text>`** — edit an existing TODO by ID
- **`/tododo remove <id>`** — remove a TODO by ID
- **`/tododo run [id...]`** — execute (implement) TODO items and remove the comment after completion

Also works as a **skill** — Claude automatically manages TODOs when you ask without the explicit command.

Supports comment styles: `#`, `//`, `/* */`, `--`, `<!-- -->` and more.

## Installation

### Global (recommended)

Install once, works in every project:

```bash
git clone https://github.com/ya-boiko/tododo.git ~/.claude-plugins/tododo
cd ~/.claude-plugins/tododo && ./install.sh
```

### Per-project (git submodule)

Use when you want the plugin versioned alongside a specific project:

```bash
git submodule add https://github.com/ya-boiko/tododo.git .claude-plugins/tododo
cd .claude-plugins/tododo && ./install.sh
```

For teammates cloning the project:

```bash
git submodule update --init
cd .claude-plugins/tododo && ./install.sh
```

## Updating

```bash
cd ~/.claude-plugins/tododo && ./update.sh
```

For a submodule:

```bash
git submodule update --remote .claude-plugins/tododo
```

## Uninstalling

```bash
cd ~/.claude-plugins/tododo && ./uninstall.sh
```

## Requirements

- Python 3.10+
- Git (for `.gitignore`-aware scanning)

## Ignoring files with .todoignore

Create a `.todoignore` file in your project root to exclude files and directories from scanning. Patterns follow gitignore syntax.

```
# Ignore generated files
dist/
build/

# Ignore a specific file
src/generated/api.ts

# Wildcard patterns
**/*.min.js
*.pb.go

# Ignore a directory by name anywhere in the tree
**/fixtures/
```

**How it works:**
- `.todoignore` is searched upward from the project root — you can place it in a parent directory to apply it to multiple projects
- Each pattern is matched against the file's path relative to the directory containing `.todoignore`
- Patterns without a `/` also match against the bare filename
- `**` is supported as a multi-segment wildcard

The file uses the same comment syntax as `.gitignore`: lines starting with `#` are comments, blank lines are ignored.

## How it works

The scanner (`scripts/scan_todos.py`) walks project files respecting `.gitignore` and `.todoignore`, finds TODO/FIXME/HACK/XXX in common comment formats, and outputs a numbered list. Claude uses this list to perform edit/remove/run operations via the Edit tool.