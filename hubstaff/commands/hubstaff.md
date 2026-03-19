---
allowed-tools: Bash
description: "Manage Hubstaff time tracking — status, projects, tasks, start, stop"
argument-hint: "[status|projects|tasks|start|stop|resume]"
---

# /hubstaff — Time Tracking

Manage Hubstaff time tracking. Run the wrapper script for all operations:

```bash
python3 ~/.claude/scripts/hubstaff/hubstaff_cli.py <command> [args]
```

## Command: `$ARGUMENTS`

### `status` (or no arguments)

Run `status`. Display the result. If no arguments were provided, also ask what to do next.

### `projects`

Run `projects`. Display the list.

### `tasks [project_id]`

Run `tasks` with optional project_id. If omitted, the script uses the active project from status. Display the list.

### `start [task_id]`

If task_id provided — run `start <task_id>`.
If not — run `tasks` first, display the list, ask which task to start, then run `start <chosen_id>`.

### `stop`

Run `stop`. Confirm to user.

### `resume`

Run `resume`. Confirm to user.
