import responses

from yougile_cli import main


def test_projects_list_renders_table(written_config, capsys):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/projects",
                 json={"content": [
                     {"id": "p1", "title": "Alpha"},
                     {"id": "p2", "title": "Beta"},
                 ]})
        rc = main(["projects", "list"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Alpha" in out and "Beta" in out


def test_boards_list_with_project_filter(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/boards",
                 json={"content": [{"id": "b1", "title": "Main"}]})
        rc = main(["boards", "list", "--project", "p1"])
        assert "projectId=p1" in rsps.calls[0].request.url
    assert rc == 0


def test_columns_list_requires_board(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/columns",
                 json={"content": [{"id": "c1", "title": "To Do"}]})
        rc = main(["columns", "list", "--board", "b1"])
        assert "boardId=b1" in rsps.calls[0].request.url
    assert rc == 0


def test_users_list_with_query(written_config):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/users",
                 json={"content": [{"id": "u1", "realName": "Иван", "email": "ivan@x.com"}]})
        rc = main(["users", "list", "--query", "иван"])
    assert rc == 0
