#!/usr/bin/env python3
"""Hubstaff CLI wrapper. Calls the Hubstaff binary, parses JSON, outputs clean text."""
import datetime
import json
import os
import subprocess
import sys

_DEFAULT_CLI_PATH = os.path.expanduser("~/Hubstaff/HubstaffCLI.bin.x86_64")
_CONFIG_FILE = os.path.expanduser("~/.claude/scripts/hubstaff/config")


def _load_cli_path() -> str:
    """Resolve CLI path: config file → HUBSTAFF_CLI env var → default."""
    if os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith("HUBSTAFF_CLI="):
                    return line.split("=", 1)[1].strip()
    return os.environ.get("HUBSTAFF_CLI", _DEFAULT_CLI_PATH)


CLI_PATH = _load_cli_path()


def run_cli(*args):
    """Call Hubstaff CLI with args, parse JSON response, return dict."""
    try:
        result = subprocess.run(
            [CLI_PATH, *args],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError:
        print(f"Error: Hubstaff CLI not found at {CLI_PATH}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: Hubstaff CLI timed out", file=sys.stderr)
        sys.exit(1)

    stdout = result.stdout.strip()

    # Try parsing JSON
    if stdout:
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            data = None
    else:
        data = None

    # Check for errors
    if isinstance(data, dict) and "error" in data:
        print(f"Error: {data['error']}", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0 and data is None:
        err = result.stderr.strip() or "Unknown error"
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    return data


def _try_cli_command(*args):
    """Try a CLI command silently — return parsed JSON or None on any failure."""
    try:
        result = subprocess.run(
            [CLI_PATH, *args],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    stdout = result.stdout.strip()
    if not stdout:
        return None
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict) and "error" in data:
        return None
    return data


def _parse_daily_activities(data):
    """Parse CLI activities response into list of project dicts with tasks."""
    projects = {}
    activities = data.get("daily_activities") or data.get("activities") or []
    for act in activities:
        proj_name = (act.get("project") or {}).get("name") or act.get("project_name", "?")
        task_name = (act.get("task") or {}).get("name") or act.get("task_name", "?")
        tracked = act.get("tracked") or act.get("duration", "0:00:00")
        if proj_name not in projects:
            projects[proj_name] = {"name": proj_name, "tracked": "0:00:00", "tasks": []}
        projects[proj_name]["tasks"].append({"name": task_name, "tracked": tracked})
    return list(projects.values())


def cmd_status():
    data = run_cli("status")
    if not data or not data.get("tracking"):
        return "Not tracking"

    project = data.get("active_project", {})
    task = data.get("active_task")
    name = project.get("name", "Unknown")
    tracked = project.get("tracked_today", "0:00:00")

    if task and task.get("name"):
        return f"Tracking: {name} > {task['name']} ({tracked})"
    return f"Tracking: {name} ({tracked})"


def cmd_statusline():
    data = run_cli("status")
    if not data or not data.get("tracking"):
        return "⏸ not tracking"
    project = data.get("active_project", {})
    task = data.get("active_task")
    name = project.get("name", "?")
    tracked = project.get("tracked_today", "0:00:00")
    if task and task.get("name"):
        return f"⏱ {name} > {task['name']} ({tracked})"
    return f"⏱ {name} ({tracked})"


def cmd_projects():
    data = run_cli("projects")
    projects = data.get("projects", [])
    if not projects:
        return "No projects found"
    lines = [f"[{p['id']}] {p['name']}" for p in projects]
    return "\n".join(lines)


def cmd_tasks(project_id):
    if project_id is None:
        status = run_cli("status")
        if not status or not status.get("tracking"):
            print("Error: Not tracking. Specify project_id.", file=sys.stderr)
            sys.exit(1)
        project_id = str(status["active_project"]["id"])

    data = run_cli("tasks", project_id)
    tasks = data.get("tasks", [])
    if not tasks:
        return "No tasks found"
    lines = [f"[{t['id']}] {t['summary']}" for t in tasks]
    return "\n".join(lines)


def cmd_start(task_id):
    data = run_cli("start_task", task_id)
    task = (data or {}).get("active_task", {})
    name = task.get("name", task_id)
    return f"Started: {name}"


def cmd_stop():
    run_cli("stop")
    return "Stopped"


def cmd_resume():
    run_cli("resume")
    return "Resumed"


def cmd_summary():
    """Return today's task breakdown as a JSON string."""
    today = datetime.date.today().isoformat()

    # Experimental: try CLI commands for per-task time data
    for cmd in ("daily_activities", "activities", "time_entries"):
        data = _try_cli_command(cmd)
        if data is not None:
            projects = _parse_daily_activities(data)
            return json.dumps({"date": today, "per_task": True, "projects": projects})

    # Fallback: project-level only from status
    status = run_cli("status")
    project = (status or {}).get("active_project", {})
    projects = []
    if project:
        projects = [{"name": project.get("name", "?"), "tracked": project.get("tracked_today", "0:00:00"), "tasks": []}]
    return json.dumps({"date": today, "per_task": False, "projects": projects})


def main():
    if len(sys.argv) < 2:
        print("Usage: hubstaff_cli.py <status|statusline|projects|tasks|start|stop|resume|summary> [args]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        print(cmd_status())
    elif command == "statusline":
        print(cmd_statusline())
    elif command == "projects":
        print(cmd_projects())
    elif command == "tasks":
        project_id = sys.argv[2] if len(sys.argv) > 2 else None
        print(cmd_tasks(project_id))
    elif command == "start":
        if len(sys.argv) < 3:
            print("Usage: hubstaff_cli.py start <task_id>", file=sys.stderr)
            sys.exit(1)
        print(cmd_start(sys.argv[2]))
    elif command == "stop":
        print(cmd_stop())
    elif command == "resume":
        print(cmd_resume())
    elif command == "summary":
        print(cmd_summary())
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
