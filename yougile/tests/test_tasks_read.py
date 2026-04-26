import json

import responses

from yougile_cli import main


def test_tasks_list_default_limit_50(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks",
                 json={"content": [
                     {"id": "tid1", "title": "T1", "columnId": "c1",
                      "assigned": [], "completed": False},
                 ], "paging": {"next": False}})
        rc = main(["tasks", "list"])
        assert "limit=50" in rsps.calls[0].request.url
    assert rc == 0


def test_tasks_list_with_filters(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks",
                 json={"content": [], "paging": {"next": False}})
        rc = main(["tasks", "list", "--column", "col-1",
                   "--assignee", "user-1", "--limit", "10"])
        url = rsps.calls[0].request.url
        assert "columnId=col-1" in url
        assert "assignedTo=user-1" in url
        assert "limit=10" in url
    assert rc == 0


def test_tasks_get_prints_title(written_config, capsys):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks/tid1",
                 json={"id": "tid1", "title": "Hello Привет", "columnId": "c1",
                       "description": "desc", "assigned": [], "completed": False})
        rc = main(["tasks", "get", "tid1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Hello Привет" in out


def test_tasks_get_json_flag(written_config, capsys):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks/tid1",
                 json={"id": "tid1", "title": "X"})
        rc = main(["--json", "tasks", "get", "tid1"])
    assert rc == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["id"] == "tid1"
