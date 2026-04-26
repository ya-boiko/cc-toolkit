import json

import responses

from yougile_cli import main


def test_comments_list(written_config, capsys):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/chats/tid/messages",
                 json={"content": [
                     {"id": "m1", "text": "Привет", "fromUserId": "u1",
                      "timestamp": 1700000000000},
                 ]})
        rc = main(["comments", "list", "tid"])
    assert rc == 0
    assert "Привет" in capsys.readouterr().out


def test_comments_add(written_config):
    with responses.RequestsMock() as rsps:
        rsps.post("https://yougile.com/api-v2/chats/tid/messages",
                  json={"id": "m1"}, status=201)
        rc = main(["comments", "add", "tid", "--text", "ok"])
        body = json.loads(rsps.calls[0].request.body)
        assert body == {"text": "ok"}
    assert rc == 0
