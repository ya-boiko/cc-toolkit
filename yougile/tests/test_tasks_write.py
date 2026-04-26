import json
from datetime import datetime, timezone

import responses

from yougile_cli import main


def _captured_body(call):
    raw = call.request.body
    return json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)


def test_tasks_create_minimal(written_config):
    with responses.RequestsMock() as rsps:
        rsps.post("https://yougile.com/api-v2/tasks",
                  json={"id": "new-id"}, status=201)
        rc = main(["tasks", "create", "--title", "Привет", "--column", "col-1"])
        body = _captured_body(rsps.calls[0])
    assert rc == 0
    assert body == {"title": "Привет", "columnId": "col-1"}


def test_tasks_create_full(written_config):
    with responses.RequestsMock() as rsps:
        rsps.post("https://yougile.com/api-v2/tasks",
                  json={"id": "new-id"}, status=201)
        rc = main([
            "tasks", "create",
            "--title", "T",
            "--column", "col-1",
            "--description", "d",
            "--assignee", "u1", "--assignee", "u2",
            "--deadline", "2026-05-01",
        ])
        body = _captured_body(rsps.calls[0])
    assert rc == 0
    assert body["title"] == "T"
    assert body["assigned"] == ["u1", "u2"]
    assert body["deadline"]["withTime"] is False
    expected_ms = int(datetime(2026, 5, 1, tzinfo=timezone.utc).timestamp() * 1000)
    assert body["deadline"]["deadline"] == expected_ms


def test_tasks_create_with_datetime_deadline(written_config):
    with responses.RequestsMock() as rsps:
        rsps.post("https://yougile.com/api-v2/tasks", json={"id": "x"}, status=201)
        rc = main(["tasks", "create", "--title", "T", "--column", "c",
                   "--deadline", "2026-05-01T18:30"])
        body = _captured_body(rsps.calls[0])
    assert rc == 0
    assert body["deadline"]["withTime"] is True


def test_tasks_update_change_column(written_config):
    with responses.RequestsMock() as rsps:
        rsps.put("https://yougile.com/api-v2/tasks/tid",
                 json={"id": "tid"})
        rc = main(["tasks", "update", "tid", "--column", "col-2"])
        body = _captured_body(rsps.calls[0])
    assert rc == 0
    assert body == {"columnId": "col-2"}


def test_tasks_update_remove_from_column(written_config):
    with responses.RequestsMock() as rsps:
        rsps.put("https://yougile.com/api-v2/tasks/tid", json={"id": "tid"})
        rc = main(["tasks", "update", "tid", "--column", "-"])
        body = _captured_body(rsps.calls[0])
    assert rc == 0
    assert body["columnId"] == "-"


def test_tasks_update_no_deadline(written_config):
    with responses.RequestsMock() as rsps:
        rsps.put("https://yougile.com/api-v2/tasks/tid", json={"id": "tid"})
        rc = main(["tasks", "update", "tid", "--no-deadline"])
        body = _captured_body(rsps.calls[0])
    assert rc == 0
    assert body["deadline"] == {"deleted": True}


def test_tasks_update_completed_archived_flags(written_config):
    with responses.RequestsMock() as rsps:
        rsps.put("https://yougile.com/api-v2/tasks/tid", json={"id": "tid"})
        rc = main(["tasks", "update", "tid", "--completed", "true", "--archived", "false"])
        body = _captured_body(rsps.calls[0])
    assert rc == 0
    assert body == {"completed": True, "archived": False}


def test_tasks_move_shortcut(written_config):
    with responses.RequestsMock() as rsps:
        rsps.put("https://yougile.com/api-v2/tasks/tid", json={"id": "tid"})
        rc = main(["tasks", "move", "tid", "--column", "col-9"])
        body = _captured_body(rsps.calls[0])
    assert rc == 0
    assert body == {"columnId": "col-9"}


def test_tasks_done_shortcut(written_config):
    with responses.RequestsMock() as rsps:
        rsps.put("https://yougile.com/api-v2/tasks/tid", json={"id": "tid"})
        rc = main(["tasks", "done", "tid"])
        body = _captured_body(rsps.calls[0])
    assert rc == 0
    assert body == {"completed": True}
