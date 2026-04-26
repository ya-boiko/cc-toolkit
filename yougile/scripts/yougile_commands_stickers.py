"""stickers list/states (string + sprint)."""

from __future__ import annotations

import json

from yougile_api import YougileClient
from yougile_config import load_config
from yougile_format import render_table, short_id


def _client():
    cfg = load_config()
    return YougileClient(base_url=cfg.base_url, api_key=cfg.api_key)


def cmd_stickers_list(args) -> int:
    client = _client()
    rows = []
    if args.type in (None, "string"):
        for s in client.string_stickers_list().get("content", []):
            rows.append({"type": "string", "id": short_id(s.get("id")),
                         "name": s.get("name", "")})
    if args.type in (None, "sprint"):
        for s in client.sprint_stickers_list().get("content", []):
            rows.append({"type": "sprint", "id": short_id(s.get("id")),
                         "name": s.get("name", "")})
    if getattr(args, "json", False):
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    print(render_table(rows, [("type", "type"), ("id", "id"), ("name", "name")]))
    return 0


def cmd_stickers_states(args) -> int:
    client = _client()
    if args.type == "sprint":
        info = client.sprint_sticker_get(args.sticker_id)
    else:
        info = client.string_sticker_get(args.sticker_id)
    states = info.get("states") or []
    if getattr(args, "json", False):
        print(json.dumps(states, ensure_ascii=False, indent=2))
        return 0
    rows = [{"id": short_id(s.get("id")), "name": s.get("name", "")} for s in states]
    print(render_table(rows, [("id", "id"), ("name", "name")]))
    return 0
