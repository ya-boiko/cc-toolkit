import json

import responses

from yougile_cli import main


def _body(call):
    raw = call.request.body
    return json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)


def test_assignee_add_appends_unique(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks/tid",
                 json={"id": "tid", "assigned": ["u1"]})
        rsps.put("https://yougile.com/api-v2/tasks/tid", json={"id": "tid"})
        rc = main(["tasks", "update", "tid", "--assignee-add", "u2"])
        assert _body(rsps.calls[1]) == {"assigned": ["u1", "u2"]}
    assert rc == 0


def test_assignee_add_idempotent(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks/tid",
                 json={"id": "tid", "assigned": ["u1"]})
        rsps.put("https://yougile.com/api-v2/tasks/tid", json={"id": "tid"})
        rc = main(["tasks", "update", "tid", "--assignee-add", "u1"])
        assert _body(rsps.calls[1]) == {"assigned": ["u1"]}
    assert rc == 0


def test_assignee_remove(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks/tid",
                 json={"id": "tid", "assigned": ["u1", "u2"]})
        rsps.put("https://yougile.com/api-v2/tasks/tid", json={"id": "tid"})
        rc = main(["tasks", "update", "tid", "--assignee-remove", "u2"])
        assert _body(rsps.calls[1]) == {"assigned": ["u1"]}
    assert rc == 0


def test_assignee_set_replaces_all(written_config):
    with responses.RequestsMock() as rsps:
        rsps.put("https://yougile.com/api-v2/tasks/tid", json={"id": "tid"})
        rc = main(["tasks", "update", "tid", "--assignee-set", "u1,u2,u3"])
        assert _body(rsps.calls[0]) == {"assigned": ["u1", "u2", "u3"]}
    assert rc == 0


def test_add_subtask(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks/parent",
                 json={"id": "parent", "subtasks": ["s1"]})
        rsps.put("https://yougile.com/api-v2/tasks/parent", json={"id": "parent"})
        rc = main(["tasks", "add-subtask", "parent", "s2"])
        assert _body(rsps.calls[1]) == {"subtasks": ["s1", "s2"]}
    assert rc == 0


def test_remove_subtask(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks/parent",
                 json={"id": "parent", "subtasks": ["s1", "s2"]})
        rsps.put("https://yougile.com/api-v2/tasks/parent", json={"id": "parent"})
        rc = main(["tasks", "remove-subtask", "parent", "s1"])
        assert _body(rsps.calls[1]) == {"subtasks": ["s2"]}
    assert rc == 0
