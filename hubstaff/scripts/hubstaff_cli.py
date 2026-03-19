#!/usr/bin/env python3
"""Hubstaff CLI wrapper. Calls the Hubstaff binary, parses JSON, outputs clean text."""
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


def main():
    if len(sys.argv) < 2:
        print("Usage: hubstaff_cli.py <status|projects|tasks|start|stop|resume> [args]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        print(cmd_status())
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
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
