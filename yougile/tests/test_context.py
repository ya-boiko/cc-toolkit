import json

import responses

from yougile_cli import main


def test_context_show_empty(written_config, capsys):
    rc = main(["context", "show"])
    assert rc == 0
    assert "не задан" in capsys.readouterr().out


def test_context_set_project_only(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/projects/proj-1",
                 json={"id": "proj-1", "title": "Main Project"})
        rc = main(["context", "set", "--project", "proj-1"])
    assert rc == 0
    cfg = json.loads(written_config.read_text())
    assert cfg["context"]["projectId"] == "proj-1"
    assert cfg["context"]["projectTitle"] == "Main Project"
    assert cfg["context"]["boardId"] is None


def test_context_set_full_chain(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/projects/p", json={"id": "p", "title": "P"})
        rsps.get("https://yougile.com/api-v2/boards/b", json={"id": "b", "title": "B"})
        rsps.get("https://yougile.com/api-v2/columns/c", json={"id": "c", "title": "C"})
        rc = main(["context", "set", "--project", "p", "--board", "b", "--column", "c"])
    assert rc == 0
    cfg = json.loads(written_config.read_text())
    assert cfg["context"]["columnTitle"] == "C"


def test_context_clear(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/projects/p", json={"id": "p", "title": "P"})
        main(["context", "set", "--project", "p"])
    rc = main(["context", "clear"])
    assert rc == 0
    cfg = json.loads(written_config.read_text())
    assert cfg["context"] is None
