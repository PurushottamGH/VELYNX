#!/usr/bin/env python3
"""
VELYNX Chronicle CLI — chronological biography of an entity
============================================================

Standalone, read-only sister tool to ``time_machine_cli.py``. Where the Time
Machine projects a *slice of Reality* active on a single date, the Chronicle
reads every triple about one entity and lays them out as a **vertical ASCII
timeline** — a chronological biography of that subject in VELYNX's memory.

It reads the raw ``(subject, relation, object, valid_from, valid_until)``
5-tuples straight from the same ``triples`` table the Time Machine reads, sorts
them chronologically by ``valid_from`` (treating ``NULL`` as the absolute
beginning of time), and renders one line per triple.

Usage
-----
    python backend/knowledge/chronicle_cli.py --subject "Sam Altman"
    python backend/knowledge/chronicle_cli.py --subject openai

Contract
--------
* **Read-only.** Opens the database with ``PRAGMA query_only=ON`` so it can
  never mutate state, and never creates the DB file if it is absent.
* **Zero pipeline dependencies.** Imports only the Python standard library —
  not spaCy, aiosqlite, ``fact_extractor``, ``knowledge_graph``, or even
  ``temporal_filter``. A chronicle needs no date-slice, only sorting, so the
  whole tool runs cold with nothing but the stdlib.
* **Migration-resilient.** If the ``valid_from`` / ``valid_until`` columns have
  not landed yet, every triple is read with unbounded (``NULL``) temporal
  bounds — they still render, sorted to the beginning of time, with a note that
  temporal bounds are not yet present.
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
# Database path resolution.
#
# This is the *exact same* resolution the Time Machine CLI uses, mirroring
# ``backend.memory.knowledge_graph`` — the path ``fact_extractor.py`` writes to
# — WITHOUT importing it, so the Chronicle pulls in no pipeline dependencies:
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
def _parse_iso_date(raw: str) -> Optional[date]:
    """Parse an ISO-8601 date/datetime string to a ``date``, or ``None``.

    ``None`` / empty input means "unbounded" and yields ``None``. A bad value
    yields ``None`` too — a malformed temporal bound should not crash a
    read-only biography, it just sorts among the unsortable (which land just
    after the dated records and render with their raw text).
    """
    if raw is None or raw == "":
        return None
    try:
        if "T" in str(raw):
            return datetime.fromisoformat(str(raw)).date()
        return date.fromisoformat(str(raw))
    except ValueError:
        return None


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
    db_path: Path, subject_filter: str
) -> Tuple[Optional[list], bool]:
    """Read every triple whose subject matches (case-insensitive, exact).

    Returns ``(rows, has_temporal_columns)`` where ``rows`` is a list of dicts
    with keys ``subject``, ``relation``, ``object``, ``valid_from``,
    ``valid_until``. Returns ``(None, False)`` when the ``triples`` table does
    not exist yet.

    Matching is case-insensitive *equality* on the subject (``Sam Altman`` ==
    ``sam altman`` == ``SAM ALTMAN``), mirroring how the Time Machine subjects
    are normalised — not a substring match, since the Chronicle tells the story
    of one specific entity.

    If the ``valid_from`` / ``valid_until`` columns have not been migrated yet,
    they are selected as ``NULL`` (unbounded) so every record sorts to the
    beginning of time, and ``has_temporal_columns`` is ``False``.
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
            "FROM triples WHERE LOWER(subject) = LOWER(?)"
        )
        rows = conn.execute(sql, (subject_filter,)).fetchall()
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
# Chronological sort
# ---------------------------------------------------------------------------
def sort_chronologically(triples: Sequence[dict]) -> list:
    """Sort triples by ``valid_from`` ascending, ``NULL`` first.

    ``NULL`` / unparseable ``valid_from`` is treated as the absolute beginning
    of time and sorts ahead of any dated record. Among records with the same
    ``valid_from``, ties are broken by ``relation`` then ``object`` so the
    output is deterministic and stable across runs / platforms.

    The sort key is a ``(rank, value)`` tuple so ``date`` objects are never
    compared against strings (which would raise ``TypeError`` on Python 3):

      * rank 0 — unbounded (NULL / unparseable), value ``""``
      * rank 1 — a real date, value the ``date`` itself
      * rank 2 — anything else (raw, unparseable text), value the string
    """
    def sort_key(t: dict) -> Tuple[int, Any]:
        parsed = _parse_iso_date(t.get("valid_from"))
        if parsed is not None:
            return (1, parsed)
        raw = t.get("valid_from")
        if raw is None or raw == "":
            return (0, "")
        return (2, str(raw))

    return sorted(
        triples,
        key=lambda t: (sort_key(t), str(t.get("relation") or ""), str(t.get("object") or "")),
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
_BEGINNING_TOKEN = "[Beginning of Time]"


def _render_timeline(triples: Sequence[dict]) -> str:
    """Render triples as a vertical ASCII timeline.

    Each column's width is the natural maximum of the bracketed tokens
    actually present in it (a column with no unbounded bound never widens to
    fit ``[Beginning of Time]``), so the ``->`` separators form a clean
    vertical spine and the prose (``: Sam Altman was CEO of OpenAI``) reads as
    a sentence:

        [Beginning of Time] -> [2019-01-01] : Sam Altman was CEO of OpenAI
        [2019-01-01]        -> [2023-11-17] : Sam Altman was CEO of OpenAI
    """
    from_tokens = [
        _BEGINNING_TOKEN if t.get("valid_from") is None else f"[{t.get('valid_from')}]"
        for t in triples
    ]
    until_tokens = [
        _BEGINNING_TOKEN if t.get("valid_until") is None else f"[{t.get('valid_until')}]"
        for t in triples
    ]
    from_width = max((len(tok) for tok in from_tokens), default=0)
    until_width = max((len(tok) for tok in until_tokens), default=0)

    lines = []
    for t, ftok, utok in zip(triples, from_tokens, until_tokens):
        frm = ftok.ljust(from_width)
        until = utok.ljust(until_width)
        sentence = f"{t.get('subject') or ''} {t.get('relation') or ''} {t.get('object') or ''}".strip()
        lines.append(f"{frm} -> {until} : {sentence}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="chronicle_cli",
        description=(
            "Render the chronological biography of one entity from the VELYNX "
            "4D Knowledge Graph (standalone, read-only)."
        ),
    )
    parser.add_argument(
        "--subject",
        required=True,
        metavar="SUBJECT",
        help="Exact entity name to chronicle (matched case-insensitively). "
        "e.g. 'Sam Altman', 'openai', or 'Blender'.",
    )
    args = parser.parse_args(argv)

    if not KG_DB_PATH.exists():
        print(f"Knowledge-graph database not found: {KG_DB_PATH}", file=sys.stderr)
        return 1

    raw, has_temporal = load_triples(KG_DB_PATH, args.subject)

    # Context header.
    print("VELYNX Chronicle — chronological biography")
    print(f"  DB:      {KG_DB_PATH}")
    print(f"  Subject: {args.subject}")
    if not has_temporal and raw is not None:
        print(
            "  Note:    valid_from/valid_until columns not yet present; every "
            "record is treated as beginning-of-time."
        )
    print()

    if raw is None:
        print(
            "The 'triples' table was not found — the pipeline has not written "
            "any facts to this database yet."
        )
        return 0

    if not raw:
        print(f"(no triples about {args.subject!r} in the 'triples' table)")
        return 0

    ordered = sort_chronologically(raw)
    print(_render_timeline(ordered))
    print()
    print(f"{len(ordered)} record(s) chronicling {args.subject!r}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
