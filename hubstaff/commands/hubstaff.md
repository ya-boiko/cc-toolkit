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

Run `stop`. Confirm to user. Then automatically generate the daily summary (same as `summary`).

### `resume`

Run `resume`. Confirm to user.

### `summary`

1. Run `python3 ~/.claude/scripts/hubstaff/hubstaff_cli.py summary` — outputs JSON with `{date, per_task, projects: [{name, tracked, tasks: [{name, tracked}]}]}`.
2. Read today's Claude Code session files:
   - Get the current working directory.
   - Sanitize it: replace each `/` with `-` (e.g. `/home/user/myproject` → `-home-user-myproject`).
   - List all `.jsonl` files in `~/.claude/projects/<sanitized>/` that were modified today.
   - Read each file line by line; each line is a JSON object. Extract text from fields: `message.content` (string or array of `{type: "text", text: "..."}` blocks), role `user` and `assistant` only.
3. For each task in the summary JSON, search the session text for the task name and related keywords. Write 1-2 sentences describing what was accomplished.
   - If no relevant session content found for a task, omit the description (just show the time).
4. Build the markdown report:
   ```
   # YYYY-MM-DD

   ## ProjectName — H:MM:SS

   ### Task name — H:MM:SS
   Description of what was done.
   ```
5. Create `~/.hubstaff-daily/` if it does not exist.
6. Save to `~/.hubstaff-daily/YYYY-MM-DD.md` (overwrite if exists).
7. Tell the user the report was saved and show the file path.
