import json
import os
import stat

import pytest
import responses

from yougile_cli import main


def _setup_companies(rsps, companies):
    rsps.post("https://yougile.com/api-v2/auth/companies",
              json={"content": companies, "paging": {"next": False}})


def _setup_keys_list(rsps, keys):
    rsps.post("https://yougile.com/api-v2/auth/keys/get", json=keys)


def _setup_keys_create(rsps, key):
    rsps.post("https://yougile.com/api-v2/auth/keys",
              json={"key": key}, status=201)


def test_bootstrap_one_company_creates_new_key(tmp_config_path, monkeypatch):
    monkeypatch.setenv("YOUGILE_PASSWORD", "secret")
    with responses.RequestsMock() as rsps:
        _setup_companies(rsps, [{"id": "co-1", "name": "Test Co"}])
        _setup_keys_list(rsps, [])
        _setup_keys_create(rsps, "new-key-xyz")
        rc = main(["bootstrap", "--login", "u@example.com"])
    assert rc == 0
    cfg = json.loads(tmp_config_path.read_text())
    assert cfg["apiKey"] == "new-key-xyz"
    assert cfg["companyId"] == "co-1"
    assert cfg["companyTitle"] == "Test Co"
    assert stat.S_IMODE(os.stat(tmp_config_path).st_mode) == 0o600


def test_bootstrap_reuses_existing_key(tmp_config_path, monkeypatch):
    monkeypatch.setenv("YOUGILE_PASSWORD", "secret")
    with responses.RequestsMock() as rsps:
        _setup_companies(rsps, [{"id": "co-1", "name": "Test Co"}])
        _setup_keys_list(rsps, [{"key": "existing-key"}])
        rc = main(["bootstrap", "--login", "u@example.com"])
    assert rc == 0
    cfg = json.loads(tmp_config_path.read_text())
    assert cfg["apiKey"] == "existing-key"


def test_bootstrap_zero_companies_fails(tmp_config_path, monkeypatch):
    monkeypatch.setenv("YOUGILE_PASSWORD", "secret")
    with responses.RequestsMock() as rsps:
        _setup_companies(rsps, [])
        rc = main(["bootstrap", "--login", "u@example.com"])
    assert rc != 0
    assert not tmp_config_path.exists()


def test_bootstrap_multi_company_with_explicit_company_arg(tmp_config_path, monkeypatch):
    monkeypatch.setenv("YOUGILE_PASSWORD", "secret")
    with responses.RequestsMock() as rsps:
        _setup_companies(rsps, [
            {"id": "co-1", "name": "First"},
            {"id": "co-2", "name": "Second"},
        ])
        _setup_keys_list(rsps, [])
        _setup_keys_create(rsps, "key-2")
        rc = main(["bootstrap", "--login", "u@example.com", "--company", "co-2"])
    assert rc == 0
    cfg = json.loads(tmp_config_path.read_text())
    assert cfg["companyId"] == "co-2"
    assert cfg["companyTitle"] == "Second"


def test_bootstrap_multi_company_without_arg_fails_in_non_interactive(tmp_config_path, monkeypatch):
    monkeypatch.setenv("YOUGILE_PASSWORD", "secret")
    with responses.RequestsMock() as rsps:
        _setup_companies(rsps, [
            {"id": "co-1", "name": "First"},
            {"id": "co-2", "name": "Second"},
        ])
        rc = main(["bootstrap", "--login", "u@example.com"])
    assert rc != 0
    assert not tmp_config_path.exists()


def test_bootstrap_no_password_env_fails(tmp_config_path, monkeypatch):
    monkeypatch.delenv("YOUGILE_PASSWORD", raising=False)
    rc = main(["bootstrap", "--login", "u@example.com"])
    assert rc != 0


def test_auth_status_prints_company(written_config, capsys):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/companies/00000000-0000-0000-0000-000000000001",
                 json={"id": "00000000-0000-0000-0000-000000000001", "title": "Test Co"})
        rc = main(["auth", "status"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Test Co" in captured.out


def test_auth_status_401_returns_3(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/companies/00000000-0000-0000-0000-000000000001",
                 json={"error": "unauthorized", "code": 401, "message": "bad"},
                 status=401)
        rc = main(["auth", "status"])
    assert rc == 3


def test_auth_reset_with_yes_deletes_config(written_config, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    rc = main(["auth", "reset"])
    assert rc == 0
    assert not written_config.exists()


def test_auth_reset_with_no_keeps_config(written_config, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    rc = main(["auth", "reset"])
    assert rc == 0
    assert written_config.exists()
