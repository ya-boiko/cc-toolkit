"""comments list/add for task chat."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from yougile_api import YougileClient
from yougile_config import load_config
from yougile_format import render_table, short_id


def _client():
    cfg = load_config()
    return YougileClient(base_url=cfg.base_url, api_key=cfg.api_key)


def cmd_comments_list(args) -> int:
    client = _client()
    result = client.messages_list(args.task_id, limit=args.limit)
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    rows = []
    for m in result.get("content", []):
        ts = m.get("timestamp")
        when = ""
        if ts:
            try:
                when = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat(timespec="minutes")
            except (TypeError, ValueError, OSError):
                when = str(ts)
        rows.append({
            "id":   short_id(m.get("id")),
            "from": short_id(m.get("fromUserId")),
            "when": when,
            "text": (m.get("text") or "")[:80],
        })
    print(render_table(rows, [("id", "id"), ("when", "when"),
                              ("from", "from"), ("text", "text")]))
    return 0


def cmd_comments_add(args) -> int:
    client = _client()
    result = client.messages_create(args.task_id, args.text)
    print(f"✓ комментарий добавлен: {result.get('id')}")
    return 0
