---
name: hubstaff
description: "Manage Hubstaff time tracking. Use when the user mentions 'hubstaff', 'хабстафф', 'хб', 'hb', 'трекер', or 'трекинг' with intent to check status, start/stop tracking, or view tasks — e.g., 'включи трекер', 'останови трекер', 'статус трекера', 'покажи задачи в хб', 'запусти трекинг'"
---

# Hubstaff — Time Tracking

Manage Hubstaff time tracking via CLI wrapper.

## Script

Run all operations through the wrapper:

```bash
python3 ~/.claude/scripts/hubstaff/hubstaff_cli.py <command> [args]
```

Commands: `status`, `projects`, `tasks [project_id]`, `start <task_id>`, `stop`, `resume`.

## Behavior

1. Detect intent from the user's message (start, stop, check status, list tasks/projects).
2. Run the appropriate script command via Bash.
3. If starting and no task specified — show task list, ask which one.
4. If task list needed but not tracking — show project list first, ask which project, then show tasks.
