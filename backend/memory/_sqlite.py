"""
Shared SQLite connection helper for the VELYNX memory stack.
============================================================

VELYNX's cognitive loop and memory subsystems open the same SQLite databases
from many places, often concurrently (the loop writes experiences while
retrievers/telemetry read). The default rollback-journal mode serializes those
accesses and surfaces ``sqlite3.OperationalError: database is locked``.

This helper centralizes the durability/concurrency PRAGMAs so every writer in
the stack opens connections consistently:

* ``journal_mode=WAL``  — Write-Ahead Logging lets readers proceed during a
  write, dramatically reducing lock contention.
* ``busy_timeout``      — block (rather than immediately error) for up to
  ``BUSY_TIMEOUT_MS`` when the database is momentarily locked.
* ``synchronous=NORMAL``— safe with WAL and far faster than FULL.

Use :func:`connect` for synchronous ``sqlite3`` access and
:func:`apply_async_pragmas` for ``aiosqlite`` connections.
"""
from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Any

logger = logging.getLogger("velynx.sqlite")

# How long (milliseconds) a connection waits on a locked database before
# raising OperationalError.
#
# Raised from 5000 → 20000 (Dec 2025) for the live-fire test harness:
# 100 rapid consecutive read/write operations across KGs, episodic memory,
# memory-graph, consolidator, and vector backend exhaust the old 5 s window.
# 20 s matches the MAX_BUSY_WAIT ceiling recommended by the SQLite docs for
# interactive workloads.
BUSY_TIMEOUT_MS = 20_000

# Connection-level timeout (seconds) sqlite3 itself uses for lock acquisition.
# NOTE: this parameter is passed to ``sqlite3.connect()`` which internally
# sets ``PRAGMA busy_timeout``.  We then *also* set ``PRAGMA busy_timeout``
# in ``_pragma_statements()`` so the value is correct even if a subclass or
# wrapper bypasses the ``timeout`` kwarg.
DEFAULT_TIMEOUT_S = 20.0


# ── Canonical data root (CWD-drift fix) ───────────────────────────────────────
# Many subsystems historically opened ``.velynx_data/<file>`` as a CWD-RELATIVE
# string. When the process CWD differed between turns (repo root vs backend/),
# the same logical store resolved to two different files — the root cause of the
# live-fire "ghost memory" / RETRIEVAL_FAILURE at Interaction #2.
#
# ``canonical_db_path`` resolves a logical, ``velynx_data``-relative name to a
# single ABSOLUTE location anchored to the project root, independent of CWD.
#
# Canonical location is the DOTTED ``.velynx_data`` directory at the project
# root — this matches both the brain_stem.db already on disk AND the absolute
# path ``soul/soul_graph.py`` already computes, so unifying on it requires no
# data migration. Override the whole data dir with ``VELYNX_DATA_DIR``.
#
# NOTE: this is intentionally NOT named ``resolve_db_path`` — that name is taken
# below by the VELYNX_TEST_MODE isolation redirector, and ``connect()`` depends
# on that behaviour. The two are composed: a caller resolves the canonical
# absolute path here, and ``connect()`` may then redirect it into the test dir.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CANONICAL_DATA_DIRNAME = ".velynx_data"


def canonical_db_path(relative_path: str) -> Path:
    """Resolve a ``velynx_data``-relative DB name to a CWD-independent absolute path.

    Resolution order:
      1. ``VELYNX_DATA_DIR`` env override, if set → ``<env>/<relative_path>``.
      2. Project-root-anchored dotted data dir → ``<root>/.velynx_data/<relative_path>``.

    The returned path is absolute, so it resolves identically regardless of the
    process working directory. Pass logical names like ``"brain_stem.db"`` or
    ``"knowledge_graph/graph.db"``.
    """
    env_dir = os.getenv("VELYNX_DATA_DIR")
    if env_dir:
        return Path(env_dir) / relative_path
    return PROJECT_ROOT / _CANONICAL_DATA_DIRNAME / relative_path


# ── Test isolation ────────────────────────────────────────────────────────────
# Throwaway directory holding redirected databases during a test run. It is a
# real on-disk location rather than ":memory:" on purpose: the memory stack opens
# a FRESH connection per operation (both sync sqlite3 and async aiosqlite), and a
# per-connection in-memory database would lose its schema between calls. Living
# under backend/tests/data/ guarantees a test run can never write into the live
# velynx_data/ stores.
_TEST_DB_DIR = Path(__file__).resolve().parent.parent / "tests" / "data" / "_isolated"


def _test_mode_enabled() -> bool:
    """True when the suite has requested isolated databases."""
    return os.environ.get("VELYNX_TEST_MODE") == "1"


def resolve_db_path(db_path: Any) -> Any:
    """Redirect a database path into the throwaway test dir under VELYNX_TEST_MODE.

    Outside test mode the path is returned unchanged (zero behavioural change for
    production and for direct ``pytest`` runs that do not set the flag). In test
    mode every database is rewritten to
    ``backend/tests/data/_isolated/<dir>__<file>`` so live user data in
    ``velynx_data/`` is never touched. The ``<dir>__`` prefix keeps same-named
    files apart (e.g. knowledge_graph/graph.db vs soul_graph/graph.db).

    Idempotent: a path already inside the test dir — or the special ``:memory:``
    handle — is returned as-is, so layering this at both the source path constant
    and inside :func:`connect` never double-rewrites.
    """
    if not _test_mode_enabled():
        return db_path
    raw = str(db_path)
    if raw == ":memory:" or raw.endswith(":memory:"):
        return db_path
    p = Path(raw)
    if _TEST_DB_DIR == p.parent or _TEST_DB_DIR in p.parents:
        return db_path  # already isolated
    parent_name = p.parent.name
    isolated_name = f"{parent_name}__{p.name}" if parent_name not in ("", ".") else p.name
    _TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
    return _TEST_DB_DIR / isolated_name


def _pragma_statements() -> tuple[str, ...]:
    return (
        "PRAGMA journal_mode=WAL",
        f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}",
        "PRAGMA synchronous=NORMAL",
    )


def verify_wal(conn: sqlite3.Connection, db_path: Any) -> None:
    """Confirm WAL mode was actually set; warn if it silently fell back."""
    try:
        (mode,) = conn.execute("PRAGMA journal_mode").fetchone()
        if mode.upper() != "WAL":
            logger.warning(
                "Journal mode for %s is %s (not WAL); "
                "concurrent access may cause OperationalError.",
                db_path, mode,
            )
    except Exception:
        pass  # best-effort


def connect(
    db_path: Any,
    *,
    row_factory: Any = None,
    timeout: float = DEFAULT_TIMEOUT_S,
) -> sqlite3.Connection:
    """
    Open a synchronous SQLite connection with WAL + busy_timeout enabled.

    Parameters
    ----------
    db_path:
        Path (str or Path) to the database file.
    row_factory:
        Optional ``sqlite3`` row factory (e.g. ``sqlite3.Row``).
    timeout:
        Lock-acquisition timeout in seconds passed to ``sqlite3.connect``.

    Returns
    -------
    sqlite3.Connection
        A configured connection. The caller owns its lifecycle.
    """
    # Catch-all isolation: any sync connection (soul graph, predictive core,
    # memory graph, episodic, KG init …) is redirected under VELYNX_TEST_MODE.
    db_path = resolve_db_path(db_path)
    conn = sqlite3.connect(str(db_path), timeout=timeout)
    for stmt in _pragma_statements():
        try:
            conn.execute(stmt)
        except sqlite3.Error:
            # PRAGMAs are best-effort; never block a connection over a pragma
            # (e.g. WAL is unsupported on some exotic filesystems).
            pass
    verify_wal(conn, db_path)
    if row_factory is not None:
        conn.row_factory = row_factory
    return conn


async def apply_async_pragmas(db: Any) -> None:
    """
    Apply the same WAL + busy_timeout PRAGMAs to an ``aiosqlite`` connection.

    Call immediately after opening an ``aiosqlite`` connection::

        async with aiosqlite.connect(path) as db:
            await apply_async_pragmas(db)
            ...
    """
    for stmt in _pragma_statements():
        try:
            await db.execute(stmt)
        except Exception:
            pass
