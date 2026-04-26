"""Resolve a query (UUID or human name) against a list of {id, title} items."""

from __future__ import annotations

import re
from typing import Sequence

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class ResolveNotFound(Exception):
    pass


class ResolveAmbiguous(Exception):
    def __init__(self, query: str, candidates: list[dict]):
        super().__init__(
            f"{len(candidates)} matches for {query!r}: "
            + ", ".join(c.get("title", c.get("id", "")) for c in candidates)
        )
        self.query = query
        self.candidates = candidates


def resolve(query: str, items: Sequence[dict]) -> dict:
    if UUID_RE.match(query.lower()):
        for it in items:
            if it.get("id") == query:
                return it
        raise ResolveNotFound(query)
    q = query.lower().strip()
    exact = [it for it in items if (it.get("title") or "").lower() == q]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise ResolveAmbiguous(query, exact)
    prefix = [it for it in items if (it.get("title") or "").lower().startswith(q)]
    if len(prefix) == 1:
        return prefix[0]
    if len(prefix) > 1:
        raise ResolveAmbiguous(query, prefix)
    sub = [it for it in items if q in (it.get("title") or "").lower()]
    if len(sub) == 1:
        return sub[0]
    if len(sub) > 1:
        raise ResolveAmbiguous(query, sub)
    raise ResolveNotFound(query)
