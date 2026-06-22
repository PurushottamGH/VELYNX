"""VELYNX database wipe — GUARDED, DESTRUCTIVE.

Clears the KnowledgeGraph and Episodic tables from every SQLite DB found
under the backend tree. Companion to the read-only ``diagnose_db.py``.

Safety model (all of these must be satisfied to delete a single row):
  * Dry-run by default. Without ``--wipe`` the script only reports what it
    *would* clear and exits 0 without touching anything.
  * Timestamped file backups are taken before any DELETE (disable with
    ``--no-backup`` only if you really mean it).
  * Interactive typed confirmation ("WIPE") is required unless ``--yes`` is
    passed for non-interactive use.
  * Only the explicitly listed target tables are cleared. Other tables in a
    DB (and DBs with none of these tables) are left untouched.

Usage:
    python wipe_db.py                # dry-run: show counts, change nothing
    python wipe_db.py --wipe         # back up, confirm, then clear targets
    python wipe_db.py --wipe --yes   # same, no interactive prompt (CI)
    python wipe_db.py --wipe --no-backup --yes   # no safety net (discouraged)
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent
SEARCH_ROOTS = (
    BACKEND_ROOT / "data",
    BACKEND_ROOT / "velynx_data",
    BACKEND_ROOT,  # for stray velynx_state.db, velynx_identity.db
)

# Tables cleared by this script, grouped by subsystem. Anything not listed
# here is never touched.
EPISODIC_TABLES = ("episodes", "episode_links", "episode_effects")
KG_TABLES = ("relationships", "concepts", "triples", "understandings")
TARGET_TABLES = EPISODIC_TABLES + KG_TABLES

CONFIRM_WORD = "WIPE"


def _is_test_db(path: Path) -> bool:
    """True if the DB lives under a ``tests`` directory (a test fixture)."""
    return any(part.lower() == "tests" for part in path.parts)


def _iter_dbs(exclude_tests: bool = False) -> list[Path]:
    seen: set[Path] = set()
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.db"):
            if not path.is_file():
                continue
            resolved = path.resolve()
            if exclude_tests and _is_test_db(resolved):
                continue
            seen.add(resolved)
    return sorted(seen)


def _list_tables(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    return [r[0] for r in cur.fetchall()]


def _row_count(conn: sqlite3.Connection, table: str) -> int:
    cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
    return int(cur.fetchone()[0])


def _target_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Map of present target table -> current row count."""
    present = set(_list_tables(conn))
    return {t: _row_count(conn, t) for t in TARGET_TABLES if t in present}


def _rel(path: Path) -> str:
    parent = BACKEND_ROOT.parent
    return str(path.relative_to(parent)) if parent in path.parents else str(path)


def _backup(path: Path, stamp: str) -> Path:
    backup_path = path.with_name(f"{path.name}.{stamp}.bak")
    shutil.copy2(path, backup_path)
    return backup_path


def _wipe_db(path: Path, tables: dict[str, int], stamp: str, make_backup: bool) -> int:
    """Clear ``tables`` in a single DB. Returns rows deleted. Backup first."""
    if make_backup:
        backup_path = _backup(path, stamp)
        print(f"    backup -> {_rel(backup_path)}")

    deleted = 0
    conn = sqlite3.connect(str(path))
    try:
        with conn:  # transaction: commit on success, rollback on error
            for table in tables:
                cur = conn.execute(f"DELETE FROM {table}")
                deleted += cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
        conn.execute("VACUUM")
    finally:
        conn.close()
    return deleted


def _confirm(skip: bool) -> bool:
    if skip:
        return True
    print()
    print(f"Type '{CONFIRM_WORD}' to permanently clear the tables above: ", end="")
    try:
        answer = input().strip()
    except EOFError:
        print("\n  No input available; aborting (use --yes for non-interactive).")
        return False
    return answer == CONFIRM_WORD


def run(wipe: bool, make_backup: bool, skip_confirm: bool, exclude_tests: bool) -> int:
    print("=" * 72)
    print("VELYNX DATABASE WIPE" + ("" if wipe else " (DRY-RUN)"))
    print("=" * 72)
    print(f"Backend root: {BACKEND_ROOT}")
    print(f"Target tables: {list(TARGET_TABLES)}")
    if exclude_tests:
        print("Excluding test-fixture DBs (paths under tests/).")
    print()

    dbs = _iter_dbs(exclude_tests=exclude_tests)
    if not dbs:
        print("No SQLite databases found.")
        return 1

    # Pass 1: discover which DBs actually hold target tables and how many rows.
    plan: list[tuple[Path, dict[str, int]]] = []
    for db in dbs:
        try:
            conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        except sqlite3.OperationalError as exc:
            print(f"  [skip] cannot open {_rel(db)}: {exc}")
            continue
        try:
            counts = _target_counts(conn)
        finally:
            conn.close()
        if counts:
            plan.append((db, counts))

    if not plan:
        print("No target tables found in any database. Nothing to do.")
        return 0

    total_rows = 0
    print(f"Will clear target tables in {len(plan)} database(s):")
    for db, counts in plan:
        print(f"  - {_rel(db)}")
        for table, count in counts.items():
            print(f"      {table}: {count} rows")
            total_rows += count
    print()
    print(f"Total rows that would be deleted: {total_rows}")

    if not wipe:
        print()
        print("DRY-RUN: no files modified. Re-run with --wipe to apply.")
        return 0

    if not _confirm(skip_confirm):
        print("Aborted. No files modified.")
        return 1

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print()
    print(f"Wiping (backup={'on' if make_backup else 'OFF'}, stamp={stamp}) ...")
    deleted_total = 0
    for db, counts in plan:
        print(f"  {_rel(db)}")
        deleted_total += _wipe_db(db, counts, stamp, make_backup)

    print()
    # Pass 2: verify the target tables are now empty.
    clean = True
    for db, _ in plan:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            remaining = _target_counts(conn)
        finally:
            conn.close()
        leftover = {t: n for t, n in remaining.items() if n > 0}
        if leftover:
            clean = False
            print(f"  [WARN] {_rel(db)} still has rows: {leftover}")

    print("=" * 72)
    if clean:
        print(f"DONE. Cleared {deleted_total} rows. All target tables are empty.")
    else:
        print(f"DONE with WARNINGS. Cleared {deleted_total} rows; see above.")
    print("=" * 72)
    return 0 if clean else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clear VELYNX KnowledgeGraph and Episodic tables (guarded)."
    )
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Actually delete rows. Without this flag the script is a dry-run.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip the timestamped .bak file copies before deleting (discouraged).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive 'WIPE' confirmation (for non-interactive use).",
    )
    parser.add_argument(
        "--exclude-tests",
        action="store_true",
        help="Skip databases under any tests/ directory (preserve test fixtures).",
    )
    args = parser.parse_args()
    return run(
        wipe=args.wipe,
        make_backup=not args.no_backup,
        skip_confirm=args.yes,
        exclude_tests=args.exclude_tests,
    )


if __name__ == "__main__":
    sys.exit(main())
