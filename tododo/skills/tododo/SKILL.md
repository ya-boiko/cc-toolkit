---
name: tododo
description: This skill should be used when the user asks to "show TODOs", "list TODO comments", "find all TODOs", "edit a TODO", "fix a TODO", "remove a TODO", "run TODO #N", "implement a TODO", "explore TODO #N", "analyze TODOs", "clarify TODOs", "assign IDs to TODOs", "assign-ids", "next TODO", "most actionable TODO", "tododo help", "how do I use tododo", or mentions managing TODO/FIXME/HACK/XXX comments in their codebase.
---

# Tododo — TODO Comment Manager

Manage TODO/FIXME/HACK/XXX comments across a codebase: list them by number, edit their text, remove them, explore and clarify them, and execute (implement) what they describe. Uses a bundled Python scanner that finds all TODO-style comments while respecting `.gitignore`.

## Scanner

The scanner is installed at a fixed path. Run it directly:

```bash
python3 ~/.claude/scripts/tododo/scan_todos.py .
```

Extended context (for `run`, `explore`, `next`):

```bash
python3 ~/.claude/scripts/tododo/scan_todos.py --context 5 .
```

Grouped output (for `list`, `assign-ids` summary):

```bash
python3 ~/.claude/scripts/tododo/scan_todos.py --group --context 0 .
```

Grouped output format:
```
src/api.py
  [42] :10 — TODO 42: implement caching
  [1]  :25 — TODO: refactor this

src/utils.js
  [2]  :15 — FIXME: handle null
```

TODOs written as `# TODO 42: description` use their embedded number as the ID — stable across re-scans and file edits. Plain `# TODO: description` items receive a positional counter that resets every scan; always re-scan immediately before referencing a positional ID.

## Operations

### list

Show all TODO comments with their IDs and locations, organized by file.

1. Run the scanner with grouped output: `python3 ~/.claude/scripts/tododo/scan_todos.py --group --context 0 .`
2. Display the grouped list
3. If no TODOs found, report that the codebase is clean

### edit `<id> <new text>`

Change the text of an existing TODO comment while keeping its style and keyword.

1. Run the scanner to get current IDs and locations
2. Find the entry matching `<id>`
3. Read the file at the reported path
4. Replace the text after the keyword with `<new text>`, preserving:
   - Comment prefix (`#`, `//`, `/*`, `--`, `<!--`, etc.)
   - Keyword (`TODO`, `FIXME`, `HACK`, or `XXX`)
   - Colon if present
5. Save with the Edit tool
6. Confirm the change, then re-scan and display the updated list

Example: `edit 2 Validate input and raise ValueError` changes only the text; the original `# FIXME:` prefix stays intact.

### remove `<id>`

Delete a TODO comment from source code.

1. Run the scanner to get current IDs and locations
2. Find the entry matching `<id>`
3. Read the file at the reported path
4. Remove the comment using one of two strategies:
   - **Standalone line** (`    # TODO: fix this` with nothing else on the line) → delete the entire line
   - **Inline comment** (`result = compute()  # TODO: cache this`) → strip only the TODO portion, preserving the code before it
5. Save with the Edit tool
6. Confirm the removal, then re-scan and display the updated list

### run `[id...]`

Implement what a TODO describes, then remove the comment once done.

1. Scan with extended context: `python3 ~/.claude/scripts/tododo/scan_todos.py --context 5 .`
2. Determine which TODOs to implement:
   - IDs specified (e.g. `run 1 3` or `run 42`) → match explicit IDs first, then positional
   - No IDs → display the list and ask the user which ones to execute
3. For each selected TODO, in order:
   a. Read the full file for complete context
   b. Implement the described change — write the actual code, add the missing logic, fix the bug
   c. Remove the TODO comment line after successful implementation:
      - Whole line if it contains only the comment
      - Inline portion only if the comment follows code
   d. Re-read the file before the next TODO in the same file (line numbers shift after each edit)
4. After all TODOs are processed, re-scan and show a summary:
   - Which TODOs were implemented
   - Which files were modified
   - Updated TODO list

Skip any TODO that is too vague to implement safely; report which were skipped and why.

### explore `[id...]`

Analyze TODOs, ask clarifying questions for vague ones, then rewrite their text with a concrete implementation plan. Use before `run` to make vague TODOs actionable.

1. Scan with `--context 5`: `python3 ~/.claude/scripts/tododo/scan_todos.py --context 5 .`
2. Select TODOs to explore:
   - IDs provided (e.g. `explore 1 3`) → work only on those
   - No IDs → explore all
3. For each selected TODO:
   a. Read the full file to understand surrounding code
   b. Assess clarity: is the intent unambiguous? is there enough context to implement without guessing?
   c. If vague or ambiguous — ask the user one focused clarifying question before proceeding
   d. Formulate a concrete implementation plan based on the code and user answers
   e. Rewrite the TODO text in the code to embed the plan: what exactly needs to be done, relevant details from the codebase
   f. Re-read the file before the next TODO in the same file
4. Show a summary of updated TODOs and the new TODO list

**Goal:** after `explore`, every TODO must be specific enough that `run` can implement it without questions.

**Rewriting style:** keep the comment concise but actionable:
- Before: `# TODO: fix parsing`
- After: `# TODO: fix parsing — handle empty string input in parse_query(); currently raises KeyError on line 47`

### assign-ids

Embed stable numeric IDs into all unnamed TODO comments so every entry has a persistent identifier.

1. Run the scanner flat: `python3 ~/.claude/scripts/tododo/scan_todos.py --context 0 .`
2. Collect unnamed entries — those whose label in the output is `TODO:`, `FIXME:`, `HACK:`, or `XXX:` (no number between keyword and colon)
3. Find the maximum existing explicit ID from named entries; start new IDs from `max + 1` (or `1` if no explicit IDs exist)
4. For each unnamed TODO in file order:
   a. Read the file
   b. Insert the next ID between keyword and colon: `# TODO: text` → `# TODO 7: text`, `// FIXME: text` → `// FIXME 8: text`
   c. Re-read the file before the next edit in the same file (line numbers may shift)
5. Re-scan with `--group` and show the updated list

### next

Surface the single most actionable TODO and offer to implement it.

1. Scan with extended context: `python3 ~/.claude/scripts/tododo/scan_todos.py --context 5 .`
2. Apply actionability heuristic to pick one TODO:
   - Prefer entries with an explicit ID (more intentional, more stable)
   - Among those, prefer entries with longer, more specific text (not just "fix this")
   - If tied, take the first in file order
3. Display the chosen TODO with its full context block
4. Ask the user: implement now (`run N`), clarify first (`explore N`), or skip?

### help

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

**Workflow:** `list` → `explore` (clarify vague ones) → `run` or `next`

---

## Rules

**Scan first.** Always run the scanner immediately before any edit or remove operation. IDs shift whenever a file changes.

**Re-scan after changes.** After every modification, run the scanner again and show the updated list.

**Preserve comment style.** When editing, keep the original comment prefix and keyword exactly as found. `// FIXME:` stays `// FIXME:`, not `# FIXME:` or `// TODO:`.

**Edit tool only.** Use the Edit tool for all file changes — never sed, awk, or string replacement scripts.

**Re-read between run steps.** When implementing multiple TODOs sequentially, read the file fresh before each one to get accurate line numbers.

## Edge Cases

**Vague TODOs.** If a TODO says something like `# TODO: fix this`, ask the user for clarification before attempting implementation.

**Multiple TODOs in the same file.** Process them top-to-bottom. Re-read the file before each subsequent edit to account for line shifts.

**Inline TODOs.** When removing `result = compute()  # TODO: cache this result`, leave `result = compute()` intact — strip only from the comment marker onward.

**Block comment TODOs.** When removing a TODO from inside a `/* ... */` or `<!-- ... -->` block that contains other content, preserve the surrounding block comment structure.

## Additional Resources

### Reference Files

- **`references/scanner.md`** — CLI options, supported comment styles, file filtering rules, skip lists, and output format details
