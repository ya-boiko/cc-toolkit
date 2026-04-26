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
