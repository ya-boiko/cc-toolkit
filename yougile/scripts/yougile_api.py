"""Thin HTTP client for the YouGile REST API v2."""

from __future__ import annotations

import json as _json
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests


class YougileError(Exception):
    def __init__(self, status_code: int, code: Optional[int], message: str):
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.code = code
        self.message = message


class AuthError(YougileError):
    pass


class ForbiddenError(YougileError):
    pass


class NotFoundError(YougileError):
    pass


class RateLimitError(YougileError):
    def __init__(self, status_code: int, code: Optional[int], message: str, retry_after: int = 0):
        super().__init__(status_code, code, message)
        self.retry_after = retry_after


class ServerError(YougileError):
    pass


@dataclass
class YougileClient:
    base_url: str
    api_key: str
    timeout: float = 30.0

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, json: Optional[dict] = None,
                 params: Optional[dict] = None) -> Any:
        url = f"{self.base_url.rstrip('/')}{path}"
        body = None
        if json is not None:
            body = _json.dumps(json, ensure_ascii=False).encode("utf-8")
        attempt = 0
        while True:
            attempt += 1
            resp = requests.request(
                method, url,
                headers=self._headers(),
                data=body,
                params=params,
                timeout=self.timeout,
            )
            if 500 <= resp.status_code < 600 and attempt == 1:
                time.sleep(1)
                continue
            return self._handle(resp)

    @staticmethod
    def _handle(resp: requests.Response) -> Any:
        sc = resp.status_code
        if 200 <= sc < 300:
            if not resp.content:
                return None
            try:
                return resp.json()
            except ValueError:
                return resp.text
        try:
            payload = resp.json()
        except ValueError:
            payload = {}
        code = payload.get("code")
        message = (
            payload.get("message")
            or payload.get("error")
            or resp.text
            or f"HTTP {sc}"
        )
        if sc == 401:
            raise AuthError(sc, code, message)
        if sc == 403:
            raise ForbiddenError(sc, code, message)
        if sc == 404:
            raise NotFoundError(sc, code, message)
        if sc == 429:
            retry_after = int(resp.headers.get("Retry-After") or 0)
            raise RateLimitError(sc, code, message, retry_after=retry_after)
        if 500 <= sc < 600:
            raise ServerError(sc, code, message)
        raise YougileError(sc, code, message)

    # ── auth ─────────────────────────────────────────────────────────
    def companies_list(self, login: str, password: str, name: str | None = None) -> list[dict]:
        body: dict = {"login": login, "password": password}
        if name:
            body["name"] = name
        url = f"{self.base_url.rstrip('/')}/api-v2/auth/companies"
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=_json.dumps(body, ensure_ascii=False).encode("utf-8"),
            timeout=self.timeout,
        )
        result = self._handle(resp)
        if isinstance(result, dict):
            return result.get("content", [])
        return result or []

    def keys_list(self, login: str, password: str, company_id: str) -> list[dict]:
        url = f"{self.base_url.rstrip('/')}/api-v2/auth/keys/get"
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=_json.dumps(
                {"login": login, "password": password, "companyId": company_id},
                ensure_ascii=False,
            ).encode("utf-8"),
            timeout=self.timeout,
        )
        return self._handle(resp) or []

    def keys_create(self, login: str, password: str, company_id: str) -> str:
        url = f"{self.base_url.rstrip('/')}/api-v2/auth/keys"
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=_json.dumps(
                {"login": login, "password": password, "companyId": company_id},
                ensure_ascii=False,
            ).encode("utf-8"),
            timeout=self.timeout,
        )
        result = self._handle(resp)
        return result["key"]

    def companies_get(self, company_id: str) -> dict:
        return self._request("GET", f"/api-v2/companies/{company_id}")

    # ── projects/boards/columns (single) ─────────────────────────────
    def projects_get(self, project_id: str) -> dict:
        return self._request("GET", f"/api-v2/projects/{project_id}")

    def boards_get(self, board_id: str) -> dict:
        return self._request("GET", f"/api-v2/boards/{board_id}")

    def columns_get(self, column_id: str) -> dict:
        return self._request("GET", f"/api-v2/columns/{column_id}")

    # ── tasks ────────────────────────────────────────────────────────
    def tasks_list(self, *, limit: int = 50, offset: int = 0,
                   column_id: str | None = None, assigned_to: str | None = None,
                   title: str | None = None, sticker_id: str | None = None,
                   sticker_state_id: str | None = None,
                   include_deleted: bool = False) -> dict:
        params: dict = {"limit": limit, "offset": offset}
        if include_deleted:
            params["includeDeleted"] = "true"
        if column_id:
            params["columnId"] = column_id
        if assigned_to:
            params["assignedTo"] = assigned_to
        if title:
            params["title"] = title
        if sticker_id:
            params["stickerId"] = sticker_id
        if sticker_state_id:
            params["stickerStateId"] = sticker_state_id
        return self._request("GET", "/api-v2/tasks", params=params)

    def tasks_get(self, task_id: str) -> dict:
        return self._request("GET", f"/api-v2/tasks/{task_id}")

    def tasks_create(self, body: dict) -> dict:
        return self._request("POST", "/api-v2/tasks", json=body)

    def tasks_update(self, task_id: str, body: dict) -> dict:
        return self._request("PUT", f"/api-v2/tasks/{task_id}", json=body)

    # ── projects/boards/columns/users (lists) ────────────────────────
    def projects_list(self, *, limit: int = 100, offset: int = 0) -> dict:
        return self._request("GET", "/api-v2/projects",
                             params={"limit": limit, "offset": offset})

    def boards_list(self, *, project_id: str | None = None,
                    limit: int = 100, offset: int = 0) -> dict:
        params: dict = {"limit": limit, "offset": offset}
        if project_id:
            params["projectId"] = project_id
        return self._request("GET", "/api-v2/boards", params=params)

    def columns_list(self, *, board_id: str,
                     limit: int = 100, offset: int = 0) -> dict:
        return self._request("GET", "/api-v2/columns",
                             params={"boardId": board_id, "limit": limit, "offset": offset})

    def users_list(self, *, query: str | None = None,
                   limit: int = 100, offset: int = 0) -> dict:
        params: dict = {"limit": limit, "offset": offset}
        if query:
            params["filterQuery"] = query
        return self._request("GET", "/api-v2/users", params=params)

    # ── chat messages (task comments) ────────────────────────────────
    def messages_list(self, chat_id: str, *, limit: int = 50, offset: int = 0) -> dict:
        return self._request("GET", f"/api-v2/chats/{chat_id}/messages",
                             params={"limit": limit, "offset": offset})

    def messages_create(self, chat_id: str, text: str) -> dict:
        return self._request("POST", f"/api-v2/chats/{chat_id}/messages",
                             json={"text": text})
