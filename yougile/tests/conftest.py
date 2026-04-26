import json
import os
from pathlib import Path

import pytest


@pytest.fixture
def tmp_config_path(tmp_path: Path, monkeypatch) -> Path:
    """Provide an isolated config path; YOUGILE_CONFIG env var points to it."""
    cfg = tmp_path / "config.json"
    monkeypatch.setenv("YOUGILE_CONFIG", str(cfg))
    return cfg


@pytest.fixture
def written_config(tmp_config_path: Path) -> Path:
    """Pre-populated config with valid-looking values."""
    tmp_config_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_config_path.write_text(json.dumps({
        "baseUrl": "https://yougile.com",
        "apiKey": "test-key-1234567890",
        "companyId": "00000000-0000-0000-0000-000000000001",
        "companyTitle": "Test Co",
        "context": None,
        "createdAt": "2026-04-26T00:00:00Z",
    }, ensure_ascii=False))
    os.chmod(tmp_config_path, 0o600)
    return tmp_config_path
