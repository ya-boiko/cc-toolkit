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

## How it works

The scanner (`scripts/scan_todos.py`) walks project files respecting `.gitignore`, finds TODO/FIXME/HACK/XXX in common comment formats, and outputs a numbered list. Claude uses this list to perform edit/remove/run operations via the Edit tool.