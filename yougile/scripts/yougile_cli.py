"""yougile CLI — entry point. Subcommands are added per task."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from yougile_api import (
    AuthError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    YougileClient,
    YougileError,
)
from yougile_config import Config, ConfigMissing, load_config


EXIT_OK = 0
EXIT_USAGE = 1
EXIT_CONFIG_MISSING = 2
EXIT_AUTH = 3
EXIT_FORBIDDEN = 4
EXIT_NOT_FOUND = 5
EXIT_RATE_LIMITED = 6
EXIT_SERVER = 7
EXIT_TIMEOUT = 8
EXIT_BAD_RESPONSE = 9
EXIT_OTHER = 10


def _client(cfg: Config) -> YougileClient:
    return YougileClient(base_url=cfg.base_url, api_key=cfg.api_key)


def _err(msg: str) -> None:
    print(msg, file=sys.stderr)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="yougile")
    p.add_argument("--json", dest="json", action="store_true", help="raw JSON output")
    p.add_argument("--config", help="override config path (default: $YOUGILE_CONFIG or ~/.config/yougile/config.json)")
    sub = p.add_subparsers(dest="cmd", required=True)

    # auth
    auth = sub.add_parser("auth", help="authentication")
    auth_sub = auth.add_subparsers(dest="action", required=True)
    auth_sub.add_parser("status", help="check key validity")
    auth_sub.add_parser("reset", help="delete local config")

    # bootstrap
    boot = sub.add_parser("bootstrap", help="set up API key for a company")
    boot.add_argument("--login", help="email; if omitted, prompt interactively")
    boot.add_argument("--company", help="companyId; if omitted, ask after listing")

    # context
    ctx = sub.add_parser("context", help="default project/board/column")
    ctx_sub = ctx.add_subparsers(dest="action", required=True)
    ctx_sub.add_parser("show")
    ctx_set = ctx_sub.add_parser("set")
    ctx_set.add_argument("--project")
    ctx_set.add_argument("--board")
    ctx_set.add_argument("--column")
    ctx_sub.add_parser("clear")

    # tasks
    tasks = sub.add_parser("tasks", help="task operations")
    tasks_sub = tasks.add_subparsers(dest="action", required=True)

    t_list = tasks_sub.add_parser("list")
    t_list.add_argument("--column")
    t_list.add_argument("--assignee")
    t_list.add_argument("--title")
    t_list.add_argument("--sticker")
    t_list.add_argument("--sticker-state", dest="sticker_state")
    t_list.add_argument("--limit", type=int, default=50)
    t_list.add_argument("--offset", type=int, default=0)
    t_list.add_argument("--include-deleted", dest="include_deleted", action="store_true")

    t_get = tasks_sub.add_parser("get")
    t_get.add_argument("task_id")

    sub.add_parser("projects", help="(added later)")
    sub.add_parser("boards", help="(added later)")
    sub.add_parser("columns", help="(added later)")
    sub.add_parser("users", help="(added later)")
    sub.add_parser("comments", help="(added later)")
    sub.add_parser("stickers", help="(added later)")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.config:
        os.environ["YOUGILE_CONFIG"] = args.config
    try:
        return _dispatch(args)
    except ConfigMissing as e:
        _err(f"конфигурация YouGile не найдена: {e}\nзапустите: yougile bootstrap")
        return EXIT_CONFIG_MISSING
    except AuthError as e:
        _err(f"401: {e.message}\nключ невалиден — перезапустите bootstrap")
        return EXIT_AUTH
    except ForbiddenError as e:
        _err(f"403: {e.message}\nнедостаточно прав")
        return EXIT_FORBIDDEN
    except NotFoundError as e:
        _err(f"404: {e.message}")
        return EXIT_NOT_FOUND
    except RateLimitError as e:
        _err(f"429: лимит 50 запросов/мин (Retry-After: {e.retry_after} сек)")
        return EXIT_RATE_LIMITED
    except ServerError as e:
        _err(f"5xx: {e.message}\nсервер YouGile вернул ошибку, попробуйте позже")
        return EXIT_SERVER
    except YougileError as e:
        _err(f"{e.status_code}: {e.message}")
        return EXIT_OTHER


def _dispatch(args) -> int:
    if args.cmd == "auth" and args.action == "status":
        from yougile_commands_auth import cmd_auth_status
        return cmd_auth_status(args)
    if args.cmd == "auth" and args.action == "reset":
        from yougile_commands_auth import cmd_auth_reset
        return cmd_auth_reset(args)
    if args.cmd == "bootstrap":
        from yougile_commands_auth import cmd_bootstrap
        return cmd_bootstrap(args)
    if args.cmd == "context":
        from yougile_commands_context import (
            cmd_context_clear,
            cmd_context_set,
            cmd_context_show,
        )
        if args.action == "show":
            return cmd_context_show(args)
        if args.action == "set":
            return cmd_context_set(args)
        if args.action == "clear":
            return cmd_context_clear(args)
    if args.cmd == "tasks":
        from yougile_commands_tasks import cmd_tasks_get, cmd_tasks_list
        if args.action == "list":
            return cmd_tasks_list(args)
        if args.action == "get":
            return cmd_tasks_get(args)
    _err(f"команда не реализована: {args.cmd}")
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
