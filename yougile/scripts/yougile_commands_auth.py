"""auth + bootstrap commands."""

from __future__ import annotations

import getpass
import os
import sys
from datetime import datetime, timezone

from yougile_api import YougileClient
from yougile_config import (
    DEFAULT_BASE_URL,
    Config,
    clear_config,
    config_path,
    load_config,
    save_config,
)


def _err(msg: str) -> None:
    print(msg, file=sys.stderr)


def _read_password() -> str | None:
    env = os.environ.get("YOUGILE_PASSWORD")
    if env:
        return env
    if sys.stdin.isatty():
        return getpass.getpass("Пароль: ")
    return None


def _read_login(supplied: str | None) -> str | None:
    if supplied:
        return supplied
    if sys.stdin.isatty():
        return input("Логин (email): ").strip() or None
    return None


def _ask_yes_no(prompt: str, default: str = "n") -> str:
    try:
        return (input(prompt).strip().lower() or default)
    except EOFError:
        return default


def cmd_bootstrap(args) -> int:
    login = _read_login(args.login)
    if not login:
        _err("логин не указан (--login или ввод в терминале)")
        return 1
    password = _read_password()
    if not password:
        _err("пароль не указан (env YOUGILE_PASSWORD или ввод в терминале)")
        return 1

    cfg_path = config_path()
    if cfg_path.exists() and sys.stdin.isatty():
        ans = _ask_yes_no(f"конфиг {cfg_path} уже существует — перезаписать? (y/N): ")
        if ans != "y":
            print("отменено")
            return 0

    client = YougileClient(base_url=DEFAULT_BASE_URL, api_key="")  # no key yet
    companies = client.companies_list(login=login, password=password)
    if not companies:
        _err("у этого аккаунта нет ни одной компании в YouGile")
        return 1

    chosen = None
    if args.company:
        chosen = next((c for c in companies if c.get("id") == args.company), None)
        if not chosen:
            _err(f"companyId {args.company} не найден в списке доступных")
            return 1
    elif len(companies) == 1:
        chosen = companies[0]
    else:
        if not sys.stdin.isatty():
            _err("найдено несколько компаний; укажите --company <id>:")
            for c in companies:
                _err(f"  {c.get('id')}  {c.get('name') or c.get('title') or ''}")
            return 1
        for i, c in enumerate(companies, 1):
            print(f"  [{i}] {c.get('name') or c.get('title') or ''}  ({c.get('id')})")
        try:
            idx = input("выберите номер: ").strip()
            chosen = companies[int(idx) - 1]
        except (ValueError, IndexError, EOFError):
            _err("неверный номер")
            return 1

    company_id = chosen["id"]
    company_title = chosen.get("name") or chosen.get("title") or ""

    existing = client.keys_list(login=login, password=password, company_id=company_id)
    if existing:
        api_key = existing[0]["key"]
    else:
        api_key = client.keys_create(login=login, password=password, company_id=company_id)

    cfg = Config(
        base_url=DEFAULT_BASE_URL,
        api_key=api_key,
        company_id=company_id,
        company_title=company_title,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    )
    saved = save_config(cfg)
    print(f"✓ настроено: компания «{company_title}», ключ сохранён в {saved}")
    return 0


def cmd_auth_status(args) -> int:
    cfg = load_config()
    client = YougileClient(base_url=cfg.base_url, api_key=cfg.api_key)
    info = client.companies_get(cfg.company_id)
    title = info.get("title") or info.get("name") or cfg.company_title
    print(f"компания: {title}")
    print(f"companyId: {cfg.company_id}")
    print(f"конфиг: {config_path()} (создан {cfg.created_at})")
    if cfg.context:
        print("контекст по умолчанию:")
        if cfg.context.project_title:
            print(f"  проект:  {cfg.context.project_title} ({cfg.context.project_id})")
        if cfg.context.board_title:
            print(f"  доска:   {cfg.context.board_title} ({cfg.context.board_id})")
        if cfg.context.column_title:
            print(f"  колонка: {cfg.context.column_title} ({cfg.context.column_id})")
    else:
        print("контекст по умолчанию: не задан (yougile context set ...)")
    return 0


def cmd_auth_reset(args) -> int:
    cfg_path = config_path()
    if not cfg_path.exists():
        print("конфиг не найден — нечего удалять")
        return 0
    ans = _ask_yes_no(f"удалить {cfg_path}? (y/N): ")
    if ans == "y":
        clear_config()
        print(f"удалено: {cfg_path}")
    else:
        print("отменено")
    return 0
