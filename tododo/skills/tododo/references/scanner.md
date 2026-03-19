# scan_todos.py — Reference

## CLI Usage

```bash
python3 scan_todos.py [--context N] [--group] [--json] [root]
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `root` | `.` | Project root directory to scan |
| `--context N` | `2` | Lines of surrounding code to show per TODO |
| `--group` | off | Group output by file with file headers |
| `--json` | off | Output as JSON array (ignores `--group`) |

### Examples

```bash
# Scan current directory with default context (2 lines)
python3 scan_todos.py .

# Show 5 lines of context (recommended for `run` operations)
python3 scan_todos.py --context 5 .

# Grouped output for overview (recommended for `list`)
python3 scan_todos.py --group --context 0 .

# Scan a specific project
python3 scan_todos.py /home/user/myproject
```

## Output Format

Each TODO is printed as:

```
[ID] relative/path/to/file.py:LINE_NUMBER — KEYWORD [ID]: text
    |  LINE-2: surrounding code
    |  LINE-1: surrounding code
    |> LINE:   the TODO line itself
    |  LINE+1: surrounding code
    |  LINE+2: surrounding code
```

- `[ID]` — explicit ID if the comment contains `TODO 42:`, otherwise a 1-based positional counter
- `relative/path/to/file.py` — path relative to the scanned root
- `LINE_NUMBER` — 1-based line number in the file
- `KEYWORD` — `TODO`, `FIXME`, `HACK`, or `XXX` (always uppercase in output)
- `text` — the comment text after the keyword and optional colon
- Context lines: `|>` marks the TODO line; `| ` marks surrounding lines

Without context (or `--context 0`), context lines are omitted:

```
[42] src/api.py:10  — TODO 42: implement caching
[1]  src/main.py:42 — TODO: Refactor this function
[2]  src/utils.js:15 — FIXME: Handle null edge case
```

## Grouped Output (`--group`)

When `--group` is set, entries are grouped under file headers. The file path is omitted from each entry line (only the line number is shown):

```
src/api.py
  [42] :10 — TODO 42: implement caching
  [1]  :25 — TODO: refactor this

src/utils.js
  [2]  :15 — FIXME: handle null
```

With context (`--group --context 2`):

```
src/api.py
  [42] :10 — TODO 42: implement caching
      |  9: previous line
      |> 10: # TODO 42: implement caching
      |  11: next line
  [1]  :25 — TODO: refactor this
      |  24: previous line
      |> 25: # TODO: refactor this
      |  26: next line

src/utils.js
  [2]  :15 — FIXME: handle null
```

Use `--group` for human-readable overview output (`list` command). Use flat output (no `--group`) when Claude needs to parse IDs for `run`, `explore`, or `assign-ids`.

## JSON Output (`--json`)

When `--json` is set, the scanner outputs a JSON array to stdout. All text formatting and `--group` are ignored.

```bash
python3 scan_todos.py --json --context 0 .
```

Each entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `display_id` | string | Display ID (explicit or positional) |
| `relpath` | string | Path relative to scan root |
| `line_no` | integer | 1-based line number |
| `keyword` | string | `TODO`, `FIXME`, `HACK`, or `XXX` |
| `label` | string | Display label (e.g. `TODO 42` or `TODO`) |
| `text` | string | Comment text after keyword |
| `explicit_id` | integer | Only present if comment has an explicit numeric ID |

Example output:

```json
[
  {"display_id": "42", "relpath": "src/api.py", "line_no": 10, "keyword": "TODO", "label": "TODO 42", "text": "implement caching", "explicit_id": 42},
  {"display_id": "1", "relpath": "src/main.py", "line_no": 25, "keyword": "TODO", "label": "TODO", "text": "refactor this"}
]
```

## Explicit IDs

Embed a numeric ID directly in a comment to make it stable:

```python
# TODO 42: implement caching
```
```javascript
// FIXME 7: handle null input
```

- Explicit IDs appear as `[42]` in output and are stable across re-scans and file edits
- Positional IDs (plain `TODO:`) reset on every scan and shift when files change
- If the same explicit ID appears more than once, the scanner appends a warning:
  ```
  [!] duplicate ID 42 (2 occurrences)
  ```

## Keyword Detection

Matches these keywords (case-insensitive):

| Keyword | Typical usage |
|---------|---------------|
| `TODO` | General task or planned improvement |
| `FIXME` | Known bug or broken code that needs fixing |
| `HACK` | Workaround or non-ideal solution |
| `XXX` | Attention-required, often dangerous or fragile code |

## Supported Comment Styles

| Prefix | Languages |
|--------|-----------|
| `#` | Python, Shell, Ruby, YAML, TOML |
| `//` | JavaScript, TypeScript, C, C++, Java, Go, Rust, Swift, Kotlin |
| `/* */` | C-style block comment opening (`/*`) and continuation lines (`*`) |
| `--` | SQL, Lua, Haskell |
| `<!-- -->` | HTML, XML, Vue, Svelte |
| `{- -}` | Haskell block comments |
| `%` | LaTeX, Erlang |

When editing a TODO, preserve the original comment prefix exactly as found in the file.

## File Filtering

### Git Integration

In a git repository, the scanner calls:

```bash
git ls-files --cached --others --exclude-standard
```

This includes:
- **Cached** (staged) files
- **Untracked** files not excluded by `.gitignore`

Falls back to `os.walk` with the hardcoded skip list below when `git` is unavailable or the directory is not a git repository.

### Skipped Directories

Always skipped regardless of git tracking:

```
.git            .claude         .claude-plugins
node_modules    __pycache__     .venv
venv            .tox            .mypy_cache
.pytest_cache   dist            build
.next           .nuxt           vendor
.bundle         target
```

### Skipped Files

Always skipped by filename:

```
CLAUDE.md    README.md
```

### Skipped Extensions (Binary Files)

```
Images:    .png .jpg .jpeg .gif .bmp .ico .svg .webp
Audio:     .mp3 .wav .flac .ogg
Video:     .mp4 .avi .mov .mkv
Archives:  .zip .tar .gz .bz2 .xz .7z .rar
Documents: .pdf .doc .docx .xls .xlsx .ppt .pptx
Compiled:  .exe .dll .so .dylib .o .a .class .jar .pyc .pyo .wasm
Fonts:     .woff .woff2 .ttf .eot .otf
Database:  .sqlite .db .sqlite3
Other:     .bin .lock
```

## Text Cleanup

The scanner strips trailing comment closers from matched text:

| Stripped suffix | Comment style |
|-----------------|---------------|
| `*/` | C-style block comment closer |
| `-->` | HTML comment closer |
| `-}` | Haskell block comment closer |

So `/* TODO: refactor this */` outputs `— TODO: refactor this` (without the `*/`).

## File Encoding

Files are read with `encoding="utf-8", errors="replace"` — non-UTF-8 bytes are substituted rather than raising an error. Files that cannot be opened (permissions, missing, etc.) are silently skipped.
