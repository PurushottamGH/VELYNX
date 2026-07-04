"""
VELYNX Phase 64 — Temporal Reasoner Middleware Filter
=====================================================

Pure data-filtering module that prunes a list of knowledge-tuple dicts to only
those whose temporal validity window contains a given *as-of* date.

Every incoming triple dict is expected to carry two optional string fields:

    ``valid_from``   — ISO-8601 date (or ``None`` / missing → unbounded past)
    ``valid_until``  — ISO-8601 date (or ``None`` / missing → unbounded future)

The filter is a strict conjunction: a triple passes iff

    valid_from <= as_of_date   (or valid_from IS NULL / absent)
    AND
    valid_until >= as_of_date  (or valid_until IS NULL / absent)

Design
------
* **No database dependency.** Operates purely on in-memory dicts.
* **No imports from any other VELYNX module.**  This is a leaf utility —
  no circular-import risk.
* **``as_of_date=None`` is a no-op.**  Every triple passes.
* **Gracefully handles missing keys** by treating the absence of
  ``valid_from`` / ``valid_until`` as unbounded.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional


def filter_triples_by_time(
    triples: list[dict[str, Any]],
    as_of_date: str | None = None,
) -> list[dict[str, Any]]:
    """Return only triples whose temporal validity window contains *as_of_date*.

    Parameters
    ----------
    triples:
        Raw triple dicts. Each *may* carry ``valid_from`` and ``valid_until``
        keys (ISO-8601 date strings). Missing keys or ``None`` are treated as
        unbounded in the respective direction.
    as_of_date:
        ISO-8601 date string (e.g. ``"2025-06-01"``).  Pass ``None`` to skip
        all filtering — every triple is returned unchanged.

    Returns
    -------
    Filtered list (same order as input, may be shorter).
    """
    if as_of_date is None:
        return list(triples)

    # Parse once, reuse for every triple.
    parsed_as_of: date = _parse_date(as_of_date)

    out: list[dict[str, Any]] = []
    for t in triples:
        if _in_window(t, parsed_as_of):
            out.append(t)
    return out


# ── Internal helpers ─────────────────────────────────────────────────────────

def _parse_date(raw: str) -> date:
    """Parse an ISO-8601 date string to a ``datetime.date``.

    Accepts both ``"YYYY-MM-DD"`` and ISO-8601 with time components
    (e.g. ``"2025-06-01T12:00:00"``).
    """
    if "T" in raw:
        return datetime.fromisoformat(raw).date()
    return date.fromisoformat(raw)


def _in_window(triple: dict[str, Any], ref: date) -> bool:
    """``True`` when the triple's temporal window contains *ref*."""
    raw_from = triple.get("valid_from")
    raw_until = triple.get("valid_until")

    if raw_from is not None:
        # Must not be BEFORE the start (null start = unbounded → skip check).
        valid_from = _parse_date(raw_from)
        if valid_from > ref:
            return False

    if raw_until is not None:
        # Must not be AFTER the end (null end = unbounded → skip check).
        valid_until = _parse_date(raw_until)
        if valid_until < ref:
            return False

    return True
