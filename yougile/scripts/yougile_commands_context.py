"""context show/set/clear."""

from __future__ import annotations

from yougile_api import YougileClient
from yougile_config import ContextDefaults, load_config, save_config


def cmd_context_show(args) -> int:
    cfg = load_config()
    if not cfg.context:
        print("контекст по умолчанию: не задан")
        return 0
    c = cfg.context
    if c.project_title:
        print(f"проект:  {c.project_title} ({c.project_id})")
    if c.board_title:
        print(f"доска:   {c.board_title} ({c.board_id})")
    if c.column_title:
        print(f"колонка: {c.column_title} ({c.column_id})")
    return 0


def cmd_context_set(args) -> int:
    cfg = load_config()
    client = YougileClient(base_url=cfg.base_url, api_key=cfg.api_key)
    ctx = cfg.context or ContextDefaults()
    if args.project:
        info = client.projects_get(args.project)
        ctx.project_id = args.project
        ctx.project_title = info.get("title") or info.get("name") or ""
    if args.board:
        info = client.boards_get(args.board)
        ctx.board_id = args.board
        ctx.board_title = info.get("title") or info.get("name") or ""
    if args.column:
        info = client.columns_get(args.column)
        ctx.column_id = args.column
        ctx.column_title = info.get("title") or info.get("name") or ""
    cfg.context = ctx
    save_config(cfg)
    print("контекст обновлён:")
    return cmd_context_show(args)


def cmd_context_clear(args) -> int:
    cfg = load_config()
    cfg.context = None
    save_config(cfg)
    print("контекст очищен")
    return 0
