"""projects/boards/columns/users — read-only helpers."""

from __future__ import annotations

import json

from yougile_api import YougileClient
from yougile_config import load_config
from yougile_format import render_table, short_id


def _client():
    cfg = load_config()
    return YougileClient(base_url=cfg.base_url, api_key=cfg.api_key)


def _maybe_json(args, payload) -> bool:
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return True
    return False


def cmd_projects_list(args) -> int:
    client = _client()
    result = client.projects_list()
    if _maybe_json(args, result):
        return 0
    rows = [{"id": short_id(p.get("id")), "title": p.get("title", "")}
            for p in result.get("content", [])]
    print(render_table(rows, [("id", "id"), ("title", "title")]))
    return 0


def cmd_projects_get(args) -> int:
    client = _client()
    result = client.projects_get(args.project_id)
    if _maybe_json(args, result):
        return 0
    print(f"id:    {result.get('id')}")
    print(f"title: {result.get('title')}")
    return 0


def cmd_boards_list(args) -> int:
    client = _client()
    result = client.boards_list(project_id=args.project)
    if _maybe_json(args, result):
        return 0
    rows = [{"id": short_id(b.get("id")), "title": b.get("title", ""),
             "projectId": short_id(b.get("projectId"))}
            for b in result.get("content", [])]
    print(render_table(rows, [("id", "id"), ("title", "title"), ("project", "projectId")]))
    return 0


def cmd_boards_get(args) -> int:
    client = _client()
    result = client.boards_get(args.board_id)
    if _maybe_json(args, result):
        return 0
    print(f"id:        {result.get('id')}")
    print(f"title:     {result.get('title')}")
    print(f"projectId: {result.get('projectId')}")
    return 0


def cmd_columns_list(args) -> int:
    client = _client()
    result = client.columns_list(board_id=args.board)
    if _maybe_json(args, result):
        return 0
    rows = [{"id": short_id(c.get("id")), "title": c.get("title", "")}
            for c in result.get("content", [])]
    print(render_table(rows, [("id", "id"), ("title", "title")]))
    return 0


def cmd_users_list(args) -> int:
    client = _client()
    result = client.users_list(query=args.query)
    if _maybe_json(args, result):
        return 0
    rows = [{"id": short_id(u.get("id")),
             "name": u.get("realName") or "",
             "email": u.get("email") or ""}
            for u in result.get("content", [])]
    print(render_table(rows, [("id", "id"), ("name", "name"), ("email", "email")]))
    return 0
