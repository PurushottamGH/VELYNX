"""VELYNX database diagnostic — READ-ONLY.

Walks the backend tree for all SQLite DBs, prints schemas and recent rows
for the tables relevant to context bleed and Phase 61 narrative tests:
  * episodes / episode_links / episode_effects
  * relationships / concepts
  * working_memory (if present)

Never modifies any file. Exits with a summary.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent
SEARCH_ROOTS = (
    BACKEND_ROOT / "data",
    BACKEND_ROOT / "velynx_data",
    BACKEND_ROOT,  # for stray velynx_state.db, velynx_identity.db
)

EPISODIC_TABLES = ("episodes", "episode_links", "episode_effects")
KG_TABLES = ("relationships", "concepts")
WORKING_TABLES = ("working_memory",)


def _iter_dbs() -> list[Path]:
    seen: set[Path] = set()
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.db"):
            if path.is_file():
                seen.add(path.resolve())
    return sorted(seen)


def _safe_connect(path: Path) -> sqlite3.Connection | None:
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as exc:
        print(f"  [skip] cannot open readonly: {exc}")
        return None


def _list_tables(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    return [r[0] for r in cur.fetchall()]


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def _row_count(conn: sqlite3.Connection, table: str) -> int:
    cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
    return int(cur.fetchone()[0])


def _print_recent(conn: sqlite3.Connection, table: str, columns: list[str], limit: int = 5) -> None:
    cur = conn.execute(
        f"SELECT {', '.join(columns)} FROM {table} ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    if not rows:
        print(f"    (empty)")
        return
    widths = [max(len(c), max((len(str(r[i])) for r in rows), default=0)) for i, c in enumerate(columns)]
    header = "  ".join(c.ljust(w) for c, w in zip(columns, widths))
    print(f"    {header}")
    print(f"    {'-' * len(header)}")
    for row in rows:
        cells = [str(row[i])[:60] for i in range(len(columns))]
        print("    " + "  ".join(c.ljust(w) for c, w in zip(cells, widths)))


def _inspect_episodic(conn: sqlite3.Connection) -> None:
    tables = _list_tables(conn)
    if not any(t in tables for t in EPISODIC_TABLES):
        return
    print(f"  EPISODIC TABLES FOUND")
    for table in EPISODIC_TABLES:
        if table not in tables:
            print(f"  [{table}] (not present)")
            continue
        cols = _columns(conn, table)
        count = _row_count(conn, table)
        print(f"  [{table}] count={count} columns={cols}")
        if count > 0 and cols:
            _print_recent(conn, table, cols)


def _inspect_kg(conn: sqlite3.Connection) -> None:
    tables = _list_tables(conn)
    if not any(t in tables for t in KG_TABLES):
        return
    print(f"  KNOWLEDGE GRAPH TABLES FOUND")
    for table in KG_TABLES:
        if table not in tables:
            print(f"  [{table}] (not present)")
            continue
        cols = _columns(conn, table)
        count = _row_count(conn, table)
        print(f"  [{table}] count={count} columns={cols}")
        if count > 0 and cols:
            _print_recent(conn, table, cols)


def _inspect_working(conn: sqlite3.Connection) -> None:
    tables = _list_tables(conn)
    for table in WORKING_TABLES:
        if table in tables:
            cols = _columns(conn, table)
            count = _row_count(conn, table)
            print(f"  [{table}] count={count} columns={cols}")


def run_diagnostic() -> int:
    print("=" * 72)
    print("VELYNX DATABASE DIAGNOSTIC (read-only)")
    print("=" * 72)
    print(f"Backend root: {BACKEND_ROOT}")
    print(f"Searching: {[str(r) for r in SEARCH_ROOTS]}")
    print()

    dbs = _iter_dbs()
    if not dbs:
        print("No SQLite databases found.")
        return 1

    print(f"Discovered {len(dbs)} database(s):")
    for db in dbs:
        print(f"  - {db.relative_to(BACKEND_ROOT.parent) if BACKEND_ROOT.parent in db.parents else db}")
    print()

    for db in dbs:
        print("-" * 72)
        print(f"DB: {db}")
        conn = _safe_connect(db)
        if conn is None:
            continue
        try:
            tables = _list_tables(conn)
            print(f"  All tables ({len(tables)}): {tables}")
            print()
            _inspect_episodic(conn)
            print()
            _inspect_kg(conn)
            print()
            _inspect_working(conn)
        finally:
            conn.close()
        print()

    print("=" * 72)
    print("READ-ONLY diagnostic complete. No files modified.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(run_diagnostic())
