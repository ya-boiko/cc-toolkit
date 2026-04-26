"""tasks list/get/create/update/move/done/add-subtask/remove-subtask + assignee mutators."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from yougile_api import YougileClient
from yougile_config import Config, load_config
from yougile_format import render_table, short_id


def _client_from_config() -> tuple[YougileClient, Config]:
    cfg = load_config()
    return YougileClient(base_url=cfg.base_url, api_key=cfg.api_key), cfg


def cmd_tasks_list(args) -> int:
    client, _ = _client_from_config()
    result = client.tasks_list(
        limit=args.limit,
        offset=args.offset,
        column_id=args.column,
        assigned_to=args.assignee,
        title=args.title,
        sticker_id=args.sticker,
        sticker_state_id=args.sticker_state,
        include_deleted=args.include_deleted,
    )
    items = result.get("content", []) if isinstance(result, dict) else result
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    rows = []
    for t in items:
        rows.append({
            "id":      short_id(t.get("id")),
            "title":   (t.get("title") or "")[:60],
            "column":  short_id(t.get("columnId")),
            "assignee": short_id((t.get("assigned") or [None])[0]),
            "done":    "✓" if t.get("completed") else "",
        })
    print(render_table(rows, [
        ("id", "id"), ("title", "title"), ("column", "column"),
        ("assignee", "assignee"), ("done", "done"),
    ]))
    if not args.column and not args.assignee and not args.title:
        print("\n(показано до --limit; уточните --column / --assignee / --title для фильтра)")
    return 0


def cmd_tasks_get(args) -> int:
    client, _ = _client_from_config()
    task = client.tasks_get(args.task_id)
    if getattr(args, "json", False):
        print(json.dumps(task, ensure_ascii=False, indent=2))
        return 0
    print(f"id:          {task.get('id')}")
    print(f"title:       {task.get('title')}")
    print(f"columnId:    {task.get('columnId')}")
    print(f"completed:   {task.get('completed')}")
    print(f"archived:    {task.get('archived')}")
    if task.get("assigned"):
        print(f"assigned:    {', '.join(task['assigned'])}")
    if task.get("description"):
        print(f"description: {task['description']}")
    if task.get("deadline"):
        print(f"deadline:    {task['deadline']}")
    if task.get("subtasks"):
        print(f"subtasks:    {len(task['subtasks'])} шт.")
    return 0


def _parse_deadline(value: str) -> dict:
    """'2026-05-01' or '2026-05-01T18:30' → {deadline: <ms>, withTime: bool}."""
    with_time = "T" in value
    fmt = "%Y-%m-%dT%H:%M" if with_time else "%Y-%m-%d"
    dt = datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
    return {"deadline": int(dt.timestamp() * 1000), "withTime": with_time}


def _bool_flag(value: str | None) -> bool | None:
    if value is None:
        return None
    if value.lower() in ("true", "1", "yes", "y"):
        return True
    if value.lower() in ("false", "0", "no", "n"):
        return False
    raise ValueError(f"ожидалось true|false, получено {value!r}")


def cmd_tasks_create(args) -> int:
    client, _ = _client_from_config()
    body: dict = {"title": args.title}
    if args.column:
        body["columnId"] = args.column
    if args.description:
        body["description"] = args.description
    if args.assignee:
        body["assigned"] = list(args.assignee)
    if args.deadline:
        body["deadline"] = _parse_deadline(args.deadline)
    result = client.tasks_create(body)
    print(f"✓ создано: {result.get('id')}")
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    if getattr(args, "subtask_of", None):
        parent = client.tasks_get(args.subtask_of)
        subtasks = list(parent.get("subtasks") or [])
        if result["id"] not in subtasks:
            subtasks.append(result["id"])
            client.tasks_update(args.subtask_of, {"subtasks": subtasks})
            print(f"✓ привязано к родителю {args.subtask_of}")
    return 0


def cmd_tasks_update(args) -> int:
    client, _ = _client_from_config()
    body: dict = {}
    if args.title:
        body["title"] = args.title
    if args.column:
        body["columnId"] = args.column  # supports literal "-" to detach
    if args.description:
        body["description"] = args.description
    if args.deadline:
        body["deadline"] = _parse_deadline(args.deadline)
    if getattr(args, "no_deadline", False):
        body["deadline"] = {"deleted": True}
    if getattr(args, "completed", None) is not None:
        body["completed"] = _bool_flag(args.completed)
    if getattr(args, "archived", None) is not None:
        body["archived"] = _bool_flag(args.archived)

    needs_assignee_fetch = bool(getattr(args, "assignee_add", None) or getattr(args, "assignee_remove", None))
    if getattr(args, "assignee_set", None):
        body["assigned"] = [u for u in args.assignee_set.split(",") if u]
    elif needs_assignee_fetch:
        current = client.tasks_get(args.task_id)
        assigned = list(current.get("assigned") or [])
        for u in args.assignee_add or []:
            if u not in assigned:
                assigned.append(u)
        for u in args.assignee_remove or []:
            assigned = [x for x in assigned if x != u]
        body["assigned"] = assigned

    if not body:
        print("нет изменений (не передан ни один флаг)", file=sys.stderr)
        return 1
    result = client.tasks_update(args.task_id, body)
    print(f"✓ обновлено: {args.task_id}")
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_tasks_move(args) -> int:
    client, _ = _client_from_config()
    client.tasks_update(args.task_id, {"columnId": args.column})
    print(f"✓ перемещено: {args.task_id} → колонка {args.column}")
    return 0


def cmd_tasks_done(args) -> int:
    client, _ = _client_from_config()
    client.tasks_update(args.task_id, {"completed": True})
    print(f"✓ закрыто: {args.task_id}")
    return 0


def cmd_tasks_add_subtask(args) -> int:
    client, _ = _client_from_config()
    parent = client.tasks_get(args.parent_id)
    subtasks = list(parent.get("subtasks") or [])
    if args.child_id not in subtasks:
        subtasks.append(args.child_id)
    client.tasks_update(args.parent_id, {"subtasks": subtasks})
    print(f"✓ {args.child_id} → подзадача {args.parent_id}")
    return 0


def cmd_tasks_remove_subtask(args) -> int:
    client, _ = _client_from_config()
    parent = client.tasks_get(args.parent_id)
    subtasks = [s for s in (parent.get("subtasks") or []) if s != args.child_id]
    client.tasks_update(args.parent_id, {"subtasks": subtasks})
    print(f"✓ {args.child_id} убрано из подзадач {args.parent_id}")
    return 0
