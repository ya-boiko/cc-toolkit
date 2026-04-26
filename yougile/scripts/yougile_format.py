"""Compact table formatting for CLI output. UTF-8, fixed-width columns."""

from __future__ import annotations

from typing import Sequence


def short_id(uuid: str | None, n: int = 8) -> str:
    if not uuid:
        return ""
    return uuid[:n]


def render_table(rows: Sequence[dict], columns: Sequence[tuple[str, str]]) -> str:
    """columns: list of (header, dict_key)."""
    if not rows:
        return "(пусто)"
    widths = []
    for header, key in columns:
        col_max = max((len(str(r.get(key, ""))) for r in rows), default=0)
        widths.append(max(len(header), col_max))
    sep = "  "
    out = [sep.join(h.ljust(w) for (h, _), w in zip(columns, widths))]
    out.append(sep.join("-" * w for w in widths))
    for r in rows:
        out.append(sep.join(str(r.get(key, "")).ljust(w) for (_, key), w in zip(columns, widths)))
    return "\n".join(out)
