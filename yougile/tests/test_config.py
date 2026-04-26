import json
import os
import stat
from pathlib import Path

import pytest

from yougile_config import (
    Config,
    DEFAULT_BASE_URL,
    ConfigMissing,
    config_path,
    load_config,
    save_config,
    clear_config,
)


def test_config_path_uses_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("YOUGILE_CONFIG", str(tmp_path / "x.json"))
    assert config_path() == tmp_path / "x.json"


def test_config_path_default(monkeypatch):
    monkeypatch.delenv("YOUGILE_CONFIG", raising=False)
    monkeypatch.setenv("HOME", "/home/test-user")
    assert config_path() == Path("/home/test-user/.config/yougile/config.json")


def test_load_config_missing_raises(tmp_config_path):
    with pytest.raises(ConfigMissing):
        load_config()


def test_save_then_load_roundtrip(tmp_config_path):
    cfg = Config(
        base_url="https://yougile.com",
        api_key="abc",
        company_id="cid",
        company_title="Co",
    )
    save_config(cfg)
    loaded = load_config()
    assert loaded.api_key == "abc"
    assert loaded.company_id == "cid"
    assert loaded.base_url == "https://yougile.com"


def test_save_sets_0600_permissions(tmp_config_path):
    save_config(Config(base_url=DEFAULT_BASE_URL, api_key="k", company_id="c", company_title="t"))
    mode = stat.S_IMODE(os.stat(tmp_config_path).st_mode)
    assert mode == 0o600


def test_save_creates_parent_directory_with_0700(tmp_path, monkeypatch):
    cfg_path = tmp_path / "nested" / "yougile" / "config.json"
    monkeypatch.setenv("YOUGILE_CONFIG", str(cfg_path))
    save_config(Config(base_url=DEFAULT_BASE_URL, api_key="k", company_id="c", company_title="t"))
    assert cfg_path.parent.is_dir()
    mode = stat.S_IMODE(os.stat(cfg_path.parent).st_mode)
    assert mode == 0o700


def test_clear_config_removes_file(written_config):
    assert written_config.exists()
    clear_config()
    assert not written_config.exists()


def test_clear_config_idempotent(tmp_config_path):
    clear_config()
    clear_config()  # no error on missing file


def test_load_preserves_unicode_in_company_title(tmp_config_path):
    tmp_config_path.write_text(json.dumps({
        "baseUrl": "https://yougile.com",
        "apiKey": "k",
        "companyId": "c",
        "companyTitle": "ООО «Производство»",
        "context": None,
        "createdAt": "2026-04-26T00:00:00Z",
    }, ensure_ascii=False), encoding="utf-8")
    cfg = load_config()
    assert cfg.company_title == "ООО «Производство»"
