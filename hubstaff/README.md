# hubstaff

Manage Hubstaff time tracking from Claude Code. Wraps the Hubstaff CLI binary with a Python script that parses JSON and returns clean text output.

## Requirements

- Hubstaff desktop app installed and running at `/home/ya_boiko/Hubstaff/HubstaffCLI.bin.x86_64`
- Python 3.10+

## Install

```bash
./install.sh    # symlink command, skill and script into ~/.claude/
./update.sh     # git pull (symlinks update automatically)
./uninstall.sh  # remove symlinks
```

## Command `/hubstaff`

```
/hubstaff [status|projects|tasks|start|stop|resume]
```

### Subcommands

#### `status` (or no arguments)

Shows what is currently being tracked:

```
Tracking: Proko > migrate the transcription data from database replica to the knowledgebase (3:58:27)
```

or

```
Not tracking
```

When called without arguments, also asks what to do next.

#### `projects`

Lists all available projects:

```
[657263] Proko
[123456] Other Project
```

#### `tasks [project_id]`

Lists tasks for a project. If `project_id` is omitted, uses the active project from `status`.

```
[159784427] migrate the transcription data from database replica to the knowledgebase
[160963741] Add role-based access control for authorized users
...
```

#### `start [task_id]`

Starts tracking a task. If `task_id` is omitted, shows the task list and asks which one to start.

#### `stop`

Stops the tracker.

#### `resume`

Resumes the last tracked task.

## Skill `hubstaff`

Auto-triggers when the message contains one of the keywords with intent to interact with the tracker.

**Trigger keywords:** `hubstaff`, `хабстафф`, `хб`, `hb`, `трекер`, `трекинг`

**Example phrases:**

> "включи трекер", "останови трекер", "статус трекера", "покажи задачи в хб", "запусти трекинг"

**Does not trigger** on keywords used in an unrelated context (e.g., "трекер посылок").

### Interaction flow

1. Detects intent from the message (start, stop, status, list tasks/projects)
2. Calls the wrapper script
3. If starting without a task — shows the list, asks which one
4. If listing tasks without an active project — shows projects first, then tasks

## Architecture

```
hubstaff/
├── scripts/
│   ├── hubstaff_cli.py        # Python wrapper — calls CLI, parses JSON, outputs clean text
│   └── test_hubstaff_cli.py   # Unit tests (mocked CLI)
├── commands/hubstaff.md       # /hubstaff command prompt
└── skills/hubstaff/SKILL.md   # Auto-trigger skill
```

The Python wrapper (`hubstaff_cli.py`) handles:
- Calling the CLI binary via `subprocess`
- Parsing JSON responses
- Two-call flow for `tasks` without `project_id` (status → tasks)
- Both JSON and plain-text error output from the CLI

## Uninstall

```bash
./uninstall.sh
```
