#!/usr/bin/env python3
"""
VELYNX Time Machine CLI — 4D Knowledge Graph diagnostic
========================================================

Standalone, read-only tool that visualises the *4D Knowledge Graph*: it reads
the raw ``(subject, relation, object, valid_from, valid_until)`` 5-tuples from
the ``triples`` table and projects the slice of "Reality" that was active on a
given date.

The temporal cut is performed by DeepSeek's
:func:`backend.knowledge.temporal_filter.filter_triples_by_time` — the *same*
filter the main pipeline is being wired to use — so this tool gives an
independent way to verify time-travel queries without running the NLP stack.

Usage
-----
    python backend/knowledge/time_machine_cli.py --date 2025-06-15
    python backend/knowledge/time_machine_cli.py --date 2025-06-15 --subject Blender

Contract
--------
* **Read-only.** Opens the database with ``PRAGMA query_only=ON`` so it can
  never mutate state, and never creates the DB file if it is absent.
* **Zero pipeline dependencies.** Imports only the Python standard library and
  ``backend.knowledge.temporal_filter``. It does NOT import spaCy, aiosqlite,
  ``fact_extractor``, or ``knowledge_graph`` — so it runs even while the
  temporal middleware is still being wired in.
* **Migration-resilient.** If the ``valid_from`` / ``valid_until`` columns have
  not landed yet, every triple is read with unbounded (``NULL``) temporal
  bounds and therefore passes the filter for any date — the table still
  renders, with a note that temporal bounds are not yet present.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Import bootstrap: make ``backend.knowledge.temporal_filter`` importable when
# this file is run directly (``python backend/knowledge/time_machine_cli.py``)
# as well as as a module (``python -m backend.knowledge.time_machine_cli``).
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.knowledge.temporal_filter import filter_triples_by_time  # noqa: E402

# ---------------------------------------------------------------------------
# Database path resolution.
#
# This mirrors the resolution in ``backend.memory.knowledge_graph`` — the exact
# path ``fact_extractor.py`` writes to — WITHOUT importing it, so the
# diagnostic pulls in no pipeline dependencies (aiosqlite / spaCy / ...):
#   * BACKEND_ROOT-anchored (CWD-independent), overridable via VELYNX_DATA_DIR.
#   * Redirected to the throwaway test dir under VELYNX_TEST_MODE, matching
#     ``backend.memory._sqlite.resolve_db_path``, so a diagnostic run reads the
#     same isolated DB the test suite writes.
# ---------------------------------------------------------------------------
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = Path(os.getenv("VELYNX_DATA_DIR", str(_BACKEND_ROOT))) / "velynx_data" / "knowledge_graph"
_TEST_DB_DIR = _BACKEND_ROOT / "tests" / "data" / "_isolated"


def _resolve_db_path(db_path: Path) -> Path:
    """Replicate ``backend.memory._sqlite.resolve_db_path`` in pure stdlib."""
    if os.environ.get("VELYNX_TEST_MODE") != "1":
        return db_path
    raw = str(db_path)
    if raw == ":memory:" or raw.endswith(":memory:"):
        return db_path
    if _TEST_DB_DIR == db_path.parent or _TEST_DB_DIR in db_path.parents:
        return db_path  # already isolated
    parent_name = db_path.parent.name
    isolated_name = (
        f"{parent_name}__{db_path.name}" if parent_name not in ("", ".") else db_path.name
    )
    _TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
    return _TEST_DB_DIR / isolated_name


KG_DB_PATH = _resolve_db_path(_DATA_DIR / "graph.db")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_iso_date(raw: str) -> date:
    """Parse an ISO-8601 date/datetime string to a ``date``.

    Mirrors ``temporal_filter._parse_date`` so an invalid ``--date`` fails fast
    with a clean argparse error instead of crashing inside the filter.
    """
    if "T" in raw:
        return datetime.fromisoformat(raw).date()
    return date.fromisoformat(raw)


def _escape_like(text: str) -> str:
    """Escape ``\\``/``%``/``_`` so a subject filter matches them literally."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row is not None


def _existing_columns(conn: sqlite3.Connection, table: str) -> set:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


# ---------------------------------------------------------------------------
# Read path
# ---------------------------------------------------------------------------
def load_triples(
    db_path: Path, subject_filter: Optional[str]
) -> Tuple[Optional[list], bool]:
    """Read raw 5-tuple records from the ``triples`` table (read-only).

    Returns ``(rows, has_temporal_columns)`` where ``rows`` is a list of dicts
    with keys ``subject``, ``relation``, ``object``, ``valid_from``,
    ``valid_until``. Returns ``(None, False)`` when the ``triples`` table does
    not exist yet.

    If the ``valid_from`` / ``valid_until`` columns have not been migrated yet,
    they are selected as ``NULL`` (unbounded) so the temporal filter treats
    every triple as always-active, and ``has_temporal_columns`` is ``False``.
    """
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA query_only=ON")  # enforce read-only at the engine
        if not _table_exists(conn, "triples"):
            return None, False
        cols = _existing_columns(conn, "triples")
        select_valid_from = "valid_from" if "valid_from" in cols else "NULL AS valid_from"
        select_valid_until = "valid_until" if "valid_until" in cols else "NULL AS valid_until"
        sql = (
            "SELECT subject, relation, object, "
            f"{select_valid_from}, {select_valid_until} "
            "FROM triples"
        )
        params: Tuple[Any, ...] = ()
        if subject_filter:
            sql += " WHERE LOWER(subject) LIKE LOWER(?) ESCAPE '\\'"
            params = (_escape_like(subject_filter),)
        sql += " ORDER BY subject, relation, object"
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    has_temporal = "valid_from" in cols and "valid_until" in cols
    return (
        [
            {
                "subject": r[0],
                "relation": r[1],
                "object": r[2],
                "valid_from": r[3],
                "valid_until": r[4],
            }
            for r in rows
        ],
        has_temporal,
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
_HEADERS = ("Subject", "Relation", "Object", "Valid From", "Valid Until")


def _fmt_bound(value: Any) -> str:
    return "(open)" if value is None else str(value)


def _render_table(triples: Sequence[dict]) -> str:
    rows = [
        (
            t.get("subject") or "",
            t.get("relation") or "",
            t.get("object") or "",
            _fmt_bound(t.get("valid_from")),
            _fmt_bound(t.get("valid_until")),
        )
        for t in triples
    ]
    widths = [
        max(len(h), max((len(r[i]) for r in rows), default=0))
        for i, h in enumerate(_HEADERS)
    ]

    def fmt(row: Tuple[str, ...]) -> str:
        return " | ".join(c.ljust(widths[i]) for i, c in enumerate(row))

    sep = "-+-".join("-" * w for w in widths)
    lines = [fmt(_HEADERS), sep]
    lines.extend(fmt(r) for r in rows)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="time_machine_cli",
        description=(
            "Visualise the VELYNX 4D Knowledge Graph as of a given date "
            "(standalone, read-only)."
        ),
    )
    parser.add_argument(
        "--date",
        required=True,
        metavar="ISO8601",
        help="As-of date in ISO 8601 (e.g. 2025-06-15 or 2025-06-15T14:30:00). "
        "Only triples whose valid_from/valid_until window contains this date "
        "are shown.",
    )
    parser.add_argument(
        "--subject",
        default=None,
        metavar="SUBSTR",
        help="Optional case-insensitive substring filter on the triple subject.",
    )
    args = parser.parse_args(argv)

    # Validate the date up front for a clean error.
    try:
        _parse_iso_date(args.date)
    except ValueError as exc:
        parser.error(f"invalid --date {args.date!r}: {exc}")

    if not KG_DB_PATH.exists():
        print(f"Knowledge-graph database not found: {KG_DB_PATH}", file=sys.stderr)
        return 1

    raw, has_temporal = load_triples(KG_DB_PATH, args.subject)

    # Context header.
    print("VELYNX Time Machine — Reality projection")
    print(f"  DB:      {KG_DB_PATH}")
    print(f"  As-of:   {args.date}")
    print(f"  Subject: {args.subject if args.subject else '(all)'}")
    if not has_temporal and raw is not None:
        print(
            "  Note:    valid_from/valid_until columns not yet present; every "
            "triple is treated as always-active (unbounded)."
        )
    print()

    if raw is None:
        print(
            "The 'triples' table was not found — the pipeline has not written "
            "any facts to this database yet."
        )
        return 0

    if not raw:
        print("(no triples in the 'triples' table match the subject filter)")
        return 0

    # Pass the raw 5-tuples through DeepSeek's temporal filter.
    active = filter_triples_by_time(raw, as_of_date=args.date)

    print(_render_table(active))
    print()
    print(f"{len(active)} triple(s) active for {args.date} (of {len(raw)} read).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
