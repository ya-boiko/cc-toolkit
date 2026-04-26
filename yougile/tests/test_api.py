import pytest
import responses

from yougile_api import (
    YougileClient,
    YougileError,
    AuthError,
    NotFoundError,
    RateLimitError,
    ServerError,
)


@pytest.fixture
def client():
    return YougileClient(base_url="https://yougile.com", api_key="test-key")


def test_get_sends_bearer_header(client):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/companies/abc",
                 json={"id": "abc", "title": "Co"})
        result = client._request("GET", "/api-v2/companies/abc")
        assert result == {"id": "abc", "title": "Co"}
        assert rsps.calls[0].request.headers["Authorization"] == "Bearer test-key"
        assert rsps.calls[0].request.headers["Content-Type"] == "application/json"


def test_post_sends_unicode_json_body(client):
    with responses.RequestsMock() as rsps:
        rsps.post("https://yougile.com/api-v2/tasks",
                  json={"id": "tid"}, status=201)
        client._request("POST", "/api-v2/tasks", json={"title": "Привет"})
        sent = rsps.calls[0].request.body
        # YougileClient serializes with ensure_ascii=False; 'П' must be raw UTF-8.
        assert b"\xd0\x9f" in sent


def test_401_raises_auth_error(client):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/companies/abc",
                 json={"error": "unauthorized", "code": 401, "message": "Bad key"},
                 status=401)
        with pytest.raises(AuthError) as exc:
            client._request("GET", "/api-v2/companies/abc")
        assert "Bad key" in str(exc.value)


def test_404_raises_not_found(client):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks/xxx",
                 json={"error": "not_found", "code": 404, "message": "no"},
                 status=404)
        with pytest.raises(NotFoundError):
            client._request("GET", "/api-v2/tasks/xxx")


def test_429_raises_rate_limit_with_retry_after(client):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks",
                 json={"error": "rate_limited"},
                 status=429,
                 headers={"Retry-After": "12"})
        with pytest.raises(RateLimitError) as exc:
            client._request("GET", "/api-v2/tasks")
        assert exc.value.retry_after == 12


def test_5xx_retries_once_then_succeeds(client):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks", status=503)
        rsps.get("https://yougile.com/api-v2/tasks", json={"content": []})
        result = client._request("GET", "/api-v2/tasks")
        assert result == {"content": []}
        assert len(rsps.calls) == 2


def test_5xx_retries_once_then_raises(client):
    with responses.RequestsMock() as rsps:
        rsps.get("https://yougile.com/api-v2/tasks", status=503)
        rsps.get("https://yougile.com/api-v2/tasks", status=502)
        with pytest.raises(ServerError):
            client._request("GET", "/api-v2/tasks")
        assert len(rsps.calls) == 2


def test_400_raises_yougile_error_with_message(client):
    with responses.RequestsMock() as rsps:
        rsps.post("https://yougile.com/api-v2/tasks",
                  json={"error": "bad_request", "code": 400, "message": "title required"},
                  status=400)
        with pytest.raises(YougileError) as exc:
            client._request("POST", "/api-v2/tasks", json={})
        assert "title required" in str(exc.value)
        assert exc.value.status_code == 400
