---
allowed-tools: Read, Edit, Write, Grep, Glob, Bash
description: Manage and execute TODO comments in codebase
argument-hint: "[list|edit|remove|run|explore|assign-ids|next|help] [args...]"
---

# /tododo — Manage TODO comments

You are a TODO comment manager. Help users find, edit, remove, and execute TODO/FIXME/HACK/XXX comments in their codebase.

## Scanner

The scanner is installed at a fixed path. Run it directly:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scan_todos.py .
```

For the `run` and `explore` commands, use extended context:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scan_todos.py --context 5 .
```

Flat output format:
```
[42]  src/api.py:10  — TODO 42: implement caching    ← explicit ID from comment
[1]   src/main.py:42 — TODO: Refactor this function  ← positional counter
[2]   src/utils.js:15 — FIXME: Handle edge case
```

Grouped output (`--group`):
```
src/api.py
  [42] :10 — TODO 42: implement caching
  [1]  :25 — TODO: refactor this

src/utils.js
  [2]  :15 — FIXME: handle null
```

TODOs written as `# TODO 42: description` use their embedded number as the ID — stable across re-scans. Plain `# TODO: description` items get a positional counter that resets every scan.

## Command: `$ARGUMENTS`

### `list` (or no arguments)

- Run the scanner with grouped output: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scan_todos.py --group --context 0 .`
- Display the grouped list, organized by file
- If no TODOs are found, tell the user their codebase is clean

### `edit <id> <new text>`

1. Run the scanner to get current TODO list
2. Find the TODO with the matching ID number
3. Read the file containing that TODO
4. Replace the TODO text with the new text, keeping the same comment style and keyword
5. Confirm the change to the user, re-scan and show updated list

### `remove <id>`

1. Run the scanner to get current TODO list
2. Find the TODO with the matching ID number
3. Read the file containing that TODO
4. Remove the TODO comment:
   - If the line contains ONLY the TODO comment → remove the entire line
   - If the TODO is inline after code → remove only the TODO part
5. Confirm the removal, re-scan and show updated list

### `run [id...]`

Execute (implement) TODO items — do what the TODO describes, then remove the comment.

1. Run the scanner with `--context 5`
2. If specific IDs provided (e.g. `run 1 3` or `run 42`) → match by explicit ID first, then positional
   If NO IDs provided → display the list and ask which TODOs to execute
3. For each selected TODO, in order:
   a. Read the full file for complete context
   b. Implement what the TODO comment describes
   c. Remove the TODO comment line after successful implementation
   d. Re-read the file before the next TODO (line numbers shift after each edit)
4. Re-scan and show a summary: which TODOs were implemented, files modified, updated list

Skip any TODO that is too vague to implement safely.

### `explore [id...]`

Analyze TODOs, ask clarifying questions for vague ones, and rewrite their text with a concrete implementation plan.

1. Scan with `--context 5`
2. Select TODOs to explore:
   - IDs provided (e.g. `explore 1 3`) → work only on those
   - No IDs → explore all
3. For each selected TODO, in order:
   a. Read the full file to understand the surrounding code
   b. Assess the TODO: Is the intent clear? Is there enough context to implement it?
   c. If the TODO is vague or ambiguous — ask the user a focused clarifying question before proceeding
   d. Formulate a concrete, step-by-step implementation plan for this TODO
   e. Rewrite the TODO text in the code to include the plan: what exactly needs to be done, any relevant details or constraints discovered from the code
   f. Re-read the file before the next TODO (line numbers shift after each edit)
4. After all selected TODOs are processed, show a summary:
   - Which TODOs were updated
   - The updated TODO list

**Goal:** after `explore`, every TODO should be specific enough that `run` can implement it without asking any questions.

**Rewriting style:** keep the comment concise but actionable. Example:
- Before: `# TODO: fix parsing`
- After: `# TODO: fix parsing — handle empty string input in parse_query(); currently raises KeyError on line 47`

### `assign-ids`

Embed stable numeric IDs into all unnamed TODO comments so every entry has a persistent identifier.

1. Run the scanner flat: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scan_todos.py --context 0 .`
2. Collect unnamed entries — those whose label in the output is `TODO:`, `FIXME:`, `HACK:`, or `XXX:` (no number between keyword and colon)
3. Find the maximum existing explicit ID from named entries; start new IDs from `max + 1` (or `1` if no explicit IDs exist)
4. For each unnamed TODO in file order:
   a. Read the file
   b. Insert the next ID between keyword and colon: `# TODO: text` → `# TODO 7: text`, `// FIXME: text` → `// FIXME 8: text`
   c. Re-read the file before the next edit in the same file (line numbers may shift)
5. Re-scan with `--group` and show the updated list

### `next`

Surface the single most actionable TODO and offer to implement it.

1. Scan with extended context: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scan_todos.py --context 5 .`
2. Apply actionability heuristic to pick one TODO:
   - Prefer entries with an explicit ID (more intentional, more stable)
   - Among those, prefer entries with longer, more specific text (not just "fix this")
   - If tied, take the first in file order
3. Display the chosen TODO with its full context block
4. Ask the user: implement now (`run N`), clarify first (`explore N`), or skip?

### `help`

Output the following quick-reference exactly as written, with no preamble:

---

## tododo — Quick Reference

| Command | Usage | What it does |
|---------|-------|--------------|
| `list` | `/tododo` or `/tododo list` | List all TODOs grouped by file |
| `edit` | `/tododo edit <id> <new text>` | Replace the text of a TODO |
| `remove` | `/tododo remove <id>` | Delete a TODO comment from the file |
| `run` | `/tododo run [id...]` | Implement a TODO and remove the comment |
| `explore` | `/tododo explore [id...]` | Analyze and rewrite vague TODOs with a concrete plan |
| `assign-ids` | `/tododo assign-ids` | Embed stable IDs into all unnamed TODOs |
| `next` | `/tododo next` | Surface the most actionable TODO and offer to run it |
| `help` | `/tododo help` | Show this reference |

**IDs:** `# TODO 42: text` has stable ID `42` — unchanged across re-scans and file edits. Plain `# TODO: text` gets a positional counter that resets every scan. Use `assign-ids` to make all IDs permanent.

**Web dashboard:** `/tododo:interface` — opens a browser UI for visual TODO selection and copy-to-clipboard.

**Workflow:** `list` → `explore` (clarify vague ones) → `run` or `next`

---

## Rules

- Always run the scanner FIRST to get up-to-date TODO IDs before any edit/remove
- Preserve the original comment style when editing (`#`, `//`, `/* */`, `--`, `<!-- -->`, etc.)
- Use the Edit tool to modify files — never sed, awk, or manual rewrites
- Re-scan after any modification and show the updated list
- Re-read files between sequential `run` edits to account for line number shifts
