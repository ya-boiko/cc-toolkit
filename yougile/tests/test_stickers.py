import responses

from yougile_cli import main


def test_stickers_list_string_only(written_config, capsys):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/string-stickers",
                 json={"content": [{"id": "s1", "name": "Priority"}]})
        rc = main(["stickers", "list", "--type", "string"])
    assert rc == 0
    assert "Priority" in capsys.readouterr().out


def test_stickers_list_default_includes_both(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/string-stickers",
                 json={"content": [{"id": "s1", "name": "Priority"}]})
        rsps.get("https://yougile.com/api-v2/sprint-stickers",
                 json={"content": [{"id": "sp1", "name": "Sprint"}]})
        rc = main(["stickers", "list"])
        assert len(rsps.calls) == 2
    assert rc == 0


def test_stickers_states_string(written_config, capsys):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/string-stickers/s1",
                 json={"id": "s1", "name": "Priority",
                       "states": [{"id": "st1", "name": "High"},
                                  {"id": "st2", "name": "Low"}]})
        rc = main(["stickers", "states", "s1", "--type", "string"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "High" in out and "Low" in out
