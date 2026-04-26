"""Config storage for the yougile CLI: ~/.config/yougile/config.json (chmod 600)."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_BASE_URL = "https://yougile.com"


@dataclass
class ContextDefaults:
    project_id: Optional[str] = None
    project_title: Optional[str] = None
    board_id: Optional[str] = None
    board_title: Optional[str] = None
    column_id: Optional[str] = None
    column_title: Optional[str] = None


@dataclass
class Config:
    base_url: str
    api_key: str
    company_id: str
    company_title: str
    context: Optional[ContextDefaults] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


class ConfigMissing(Exception):
    """Raised when ~/.config/yougile/config.json doesn't exist."""


def config_path() -> Path:
    override = os.environ.get("YOUGILE_CONFIG")
    if override:
        return Path(override)
    home = Path(os.environ.get("HOME", str(Path.home())))
    return home / ".config" / "yougile" / "config.json"


def _to_json(cfg: Config) -> str:
    payload = {
        "baseUrl": cfg.base_url,
        "apiKey": cfg.api_key,
        "companyId": cfg.company_id,
        "companyTitle": cfg.company_title,
        "context": None,
        "createdAt": cfg.created_at,
    }
    if cfg.context:
        c = asdict(cfg.context)
        payload["context"] = {
            "projectId": c["project_id"],
            "projectTitle": c["project_title"],
            "boardId": c["board_id"],
            "boardTitle": c["board_title"],
            "columnId": c["column_id"],
            "columnTitle": c["column_title"],
        }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _from_json(raw: str) -> Config:
    data = json.loads(raw)
    ctx = None
    if data.get("context"):
        c = data["context"]
        ctx = ContextDefaults(
            project_id=c.get("projectId"),
            project_title=c.get("projectTitle"),
            board_id=c.get("boardId"),
            board_title=c.get("boardTitle"),
            column_id=c.get("columnId"),
            column_title=c.get("columnTitle"),
        )
    return Config(
        base_url=data.get("baseUrl", DEFAULT_BASE_URL),
        api_key=data["apiKey"],
        company_id=data["companyId"],
        company_title=data.get("companyTitle", ""),
        context=ctx,
        created_at=data.get("createdAt", ""),
    )


def load_config() -> Config:
    path = config_path()
    if not path.exists():
        raise ConfigMissing(str(path))
    return _from_json(path.read_text(encoding="utf-8"))


def save_config(cfg: Config) -> Path:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    path.write_text(_to_json(cfg), encoding="utf-8")
    os.chmod(path, 0o600)
    return path


def clear_config() -> None:
    path = config_path()
    if path.exists():
        path.unlink()
