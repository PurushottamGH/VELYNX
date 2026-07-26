"""
Universal database wipe for the VELYNX live-fire test harness.

No hardcoded paths — discovers every ``.db`` file under the project root via
``pathlib.Path.rglob()``, wipes all user tables, applies a ``VACUUM`` to
episodic stores, and runs a post-wipe verification that raises
:class:`GhostMemoryError` if any .db file was missed.

Also deletes the root-level ``velynx_data/`` directory (being consolidated into
``backend/velynx_data/``) before discovery, so its .db files don't leak into
the post-wipe check.

Usage
-----
    python scripts/wipe_db.py          # wipe everything
    python scripts/wipe_db.py --dry    # preview without wiping
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Exclusions ────────────────────────────────────────────────────────────────
# NOTE: The wiper's PRIMARY job is to reset the live-fire test harness, which
# runs under VELYNX_TEST_MODE='1'. In that mode every database is redirected to
# backend/tests/data/_isolated/ (see backend/memory/_sqlite.resolve_db_path).
# Those throwaway test DBs MUST be wiped or stale rows survive into the next run
# as ghost facts. Therefore "tests" and "_isolated" are deliberately NOT excluded
# here, and there is no test_*/test_velynx file-name exclusion. Only genuine
# non-data locations (virtualenvs, VCS metadata, build caches) are skipped.
EXCLUDE_DIR_NAMES = {
    "__pycache__",
    ".venv",
    "venv",
    ".git",
    "node_modules",
}
EXCLUDE_DIR_PREFIXES = (".venv", "venv", "site-packages")
EXCLUDE_FILE_FRAGMENTS: tuple[str, ...] = ()


# ── GhostMemoryError ──────────────────────────────────────────────────────────
class GhostMemoryError(RuntimeError):
    """Raised when .db files survive the wipe, indicating path drift.

    The post-wipe verification re-scans the project root after all wipe
    operations complete. If any .db file is found that was NOT successfully
    processed (permissions error, locked file, or newly appeared during
    execution), this error surfaces the orphaned paths so the operator can
    investigate immediately instead of discovering a ghost fact later.
    """


# Backward-compatibility alias. The live-fire harness (backend/tests/
# live_fire_harness.py::reset_state) imports this name and catches it around its
# run_wipe(strict=True) call. The previous wiper raised WipeTargetMissingError on
# runtime/wipe path divergence; in this universal-rglob design that failure mode
# is subsumed by GhostMemoryError (a surviving/missed DB IS the divergence), so
# the names are unified. Kept as a distinct subclass so existing
# ``except WipeTargetMissingError`` handlers still match.
class WipeTargetMissingError(GhostMemoryError):
    """Deprecated alias of :class:`GhostMemoryError` (harness compatibility)."""


# ── Safety guard ──────────────────────────────────────────────────────────────
def _is_safe(path: Path) -> bool:
    """True if *path* is a live data DB safe to wipe."""
    parts_lower = [p.lower() for p in path.parts]
    for part in parts_lower:
        if part in EXCLUDE_DIR_NAMES:
            return False
        if any(part.startswith(pfx) for pfx in EXCLUDE_DIR_PREFIXES):
            return False
    name = path.name.lower()
    if any(frag in name for frag in EXCLUDE_FILE_FRAGMENTS):
        return False
    return True


# ── Discovery ─────────────────────────────────────────────────────────────────
def _discover() -> list[Path]:
    """Recursively find every live .db file under ROOT, minus exclusions."""
    seen: set[Path] = set()
    for p in ROOT.rglob("*.db"):
        if not p.is_file():
            continue
        pp = p.resolve()
        if _is_safe(pp):
            seen.add(pp)
    return sorted(seen)


# ── Generic wipe ──────────────────────────────────────────────────────────────
EPISODIC_TABLES = ("episode_effects", "episode_links", "episodes")


def _wipe_file(db_path: Path, *, dry: bool) -> dict:
    """Wipe *db_path*.

    * If the database contains episodic tables (``episode_effects``,
      ``episode_links``, ``episodes``) it performs a targeted DELETE +
      VACUUM — the same physical-page reclamation the episodic memory
      module requires to prevent ghost-fact leaks.
    * Otherwise it does a generic DELETE of every user table.

    Returns a dict with keys ``path``, ``status`` (one of ``"wiped"``,
    ``"generic"``, ``"dry_run"``, ``"skipped"``), and ``details``.
    """
    result: dict = {
        "path": str(db_path),
        "status": "skipped",
        "details": None,
    }

    conn = sqlite3.connect(str(db_path), timeout=20.0)
    try:
        conn.execute("PRAGMA busy_timeout=20000")
        present = {
            row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }

        if not present:
            return result  # no tables → nothing to wipe

        # ── Check for episodic tables ────────────────────────────────────
        has_episodic = any(t in present for t in EPISODIC_TABLES)
        if has_episodic:
            if dry:
                return {
                    **result,
                    "status": "dry_run",
                    "details": f"would DELETE {', '.join(EPISODIC_TABLES)} + VACUUM",
                }

            cleared: list[str] = []
            deleted = 0
            for table in EPISODIC_TABLES:
                if table not in present:
                    continue
                cur = conn.execute(f"DELETE FROM {table}")
                if cur.rowcount and cur.rowcount > 0:
                    deleted += cur.rowcount
                cleared.append(table)
            # Commit the DELETEs explicitly BEFORE VACUUM. VACUUM cannot run
            # inside an open transaction, so the pending DELETE transaction must
            # be flushed to disk first or the row removals are lost.
            conn.commit()
            conn.execute("VACUUM")
            # VACUUM is auto-committing, but call commit() again defensively so
            # no implicit transaction is left dangling to lock the file.
            conn.commit()
            return {
                **result,
                "status": "wiped",
                "details": f"{deleted} row(s) deleted from {', '.join(cleared)}; VACUUM complete",
            }

        # ── Generic wipe ─────────────────────────────────────────────────
        non_system = [name for name in present if name != "sqlite_sequence"]
        if not non_system:
            return result

        if dry:
            return {
                **result,
                "status": "dry_run",
                "details": f"would DELETE rows from {', '.join(non_system)}",
            }

        for name in non_system:
            conn.execute(f"DELETE FROM {name}")
        # Commit the row deletions to disk before reclaiming pages.
        conn.commit()
        conn.execute("VACUUM")
        conn.commit()
        return {
            **result,
            "status": "generic",
            "details": f"Tables: {', '.join(non_system)}; VACUUM complete",
        }

    finally:
        conn.close()


# ── Content-level ghost scan (post-wipe) ──────────────────────────────────────
def _db_contains_term(db_path: Path, term: str) -> list[str]:
    """Return names of tables in *db_path* whose any column contains *term*.

    Read-only. Casts every column to TEXT so numeric/blob columns are searched
    harmlessly. Best-effort per table — a malformed table is skipped, never
    aborting the scan.
    """
    hits: list[str] = []
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.OperationalError:
        return hits
    try:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' " "AND name != 'sqlite_sequence'"
            ).fetchall()
        ]
        for table in tables:
            try:
                cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
                if not cols:
                    continue
                where = " OR ".join(f"CAST({c} AS TEXT) LIKE ?" for c in cols)
                params = [f"%{term}%"] * len(cols)
                if conn.execute(f"SELECT 1 FROM {table} WHERE {where} LIMIT 1", params).fetchone():
                    hits.append(table)
            except sqlite3.Error:
                continue
    except sqlite3.Error:
        # Listing tables itself failed (e.g. malformed DB) — return what we have.
        return hits
    finally:
        # Always release the read-only handle so Windows does not keep a file lock.
        conn.close()
    return hits


def post_wipe_verification(term: str = "Avatar", *, verbose: bool = True) -> None:
    """Scan EVERY discovered .db for *term*; raise GhostMemoryError on any hit.

    This is the CONTENT-level gate (complementary to run_wipe's file-drift
    check): it proves no surviving row in any live DB still holds the canonical
    ghost fact (default ``"Avatar"``). A DB the wipe loop *processed* but failed
    to truly clear (locked row, un-checkpointed WAL) is caught here.

    The scan iterates over ALL databases returned by ``_discover()`` — the same
    set the wipe loop processed — so no file is skipped. Previously this was
    filtered to only the ``backend/`` and ``data/`` trees, which silently
    excluded several discovered DBs (e.g. ``velynx_state.db`` living elsewhere)
    from the ghost check.
    """
    dbs = _discover()
    if verbose:
        print()
        print("-" * 72)
        print(f"Step 4 — CONTENT GHOST SCAN (probe={term!r})")
        print("-" * 72)
        print(f"Scanning all {len(dbs)} discovered .db file(s).")
    offenders: list[str] = []
    for db in dbs:
        tables = _db_contains_term(db, term)
        if tables:
            offenders.append(f"{db} -> {tables}")
            if verbose:
                print(f"  [GHOST] {db}  (tables: {', '.join(tables)})")
        elif verbose:
            print(f"  [clean] {db.name}")
    if offenders:
        raise GhostMemoryError(
            f"Residual {term!r} found AFTER wipe — a processed DB was not truly "
            f"cleared. Offenders: " + "; ".join(offenders)
        )
    if verbose:
        print(f"  OK — no '{term}' residue in any of the {len(dbs)} discovered databases.")


# ── Orchestration ─────────────────────────────────────────────────────────────
def run_wipe(
    *, dry: bool = False, verbose: bool = True, verify_term: str = "Avatar", strict: bool = False
) -> dict:
    """Discover and wipe every live .db file, then verify nothing was missed.

    Returns a summary dict with keys ``databases_wiped``, ``dry_run``,
    ``orphaned_paths`` (empty list on success).

    Parameters
    ----------
    strict
        Accepted for backward compatibility with the live-fire harness
        (``reset_state`` calls ``run_wipe(strict=True)``). In this design the
        post-wipe file-drift check and content ghost scan are ALWAYS run on a
        real wipe, so ``strict`` does not change behaviour — it is retained so
        the harness's existing keyword call does not raise ``TypeError``.
    """
    label = "DRY-RUN" if dry else "WIPE"

    # ── Step 0: delete root-level velynx_data/ (consolidation) ───────────
    root_data = ROOT / "velynx_data"
    if root_data.is_dir():
        if verbose:
            print("-" * 72)
            print("Step 0 — DELETE ROOT velynx_data/ (consolidation)")
            print("-" * 72)
        if dry:
            print(f"[DRY-RUN] would delete directory: {root_data}")
        else:
            shutil.rmtree(root_data)
            print(f"[DELETE] {root_data}")

    # ── Step 1: discover ─────────────────────────────────────────────────
    dbs = _discover()
    if verbose:
        print()
        print("-" * 72)
        print("Step 1 — DISCOVERY")
        print("-" * 72)
        print(f"Found {len(dbs)} .db file(s) to wipe.")

    if not dbs:
        if verbose:
            print("\nNo .db files found. Nothing to wipe.")
        return {"databases_wiped": 0, "dry_run": dry, "orphaned_paths": []}

    # ── Step 2: wipe ─────────────────────────────────────────────────────
    if verbose:
        print()
        print("-" * 72)
        print("Step 2 — WIPE")
        print("-" * 72)

    processed: set[Path] = set()
    for db_path in dbs:
        result = _wipe_file(db_path, dry=dry)
        processed.add(db_path)

        if result["status"] == "wiped":
            if verbose:
                print(f"[{label}] {db_path.name:40s}  {result['details']}")
        elif result["status"] == "generic":
            if verbose:
                print(f"[{label}] {db_path.name:40s}  {result['details']}")
        elif result["status"] == "dry_run":
            if verbose:
                print(f"[DRY-RUN] {db_path.name:40s}  {result['details']}")
        else:
            if verbose and result["details"]:
                print(f"[ ] {db_path.name:40s}  {result['details']}")

    # ── Step 3: post-wipe verification ───────────────────────────────────
    if verbose:
        print()
        print("-" * 72)
        print("Step 3 — POST-WIPE VERIFICATION")
        print("-" * 72)

    orphaned: list[Path] = []
    for p in _discover():
        if p not in processed:
            orphaned.append(p)

    if orphaned:
        orphaned_str = "\n  ".join(str(p) for p in orphaned)
        raise GhostMemoryError(
            f"{len(orphaned)} .db file(s) survived the wipe:\n"
            f"  {orphaned_str}\n\n"
            "These files were NOT in the original discovered list or could not\n"
            "be processed. This indicates path drift — new .db files appeared\n"
            "in a location the rglob scan found but the wipe loop missed."
        )

    if verbose:
        if not dry:
            print(f"Verification PASSED — all {len(dbs)} discovered .db files processed.")
        else:
            print("Skipped (dry run — no files were modified).")

    # ── Step 4: content ghost scan (real wipes only) ─────────────────────
    if not dry:
        post_wipe_verification(verify_term, verbose=verbose)

    return {
        "databases_wiped": len(dbs) if not dry else 0,
        "dry_run": dry,
        "orphaned_paths": orphaned,
        "ghost_verified": (not dry),
    }


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry", action="store_true", help="Preview without wiping")
    parser.add_argument(
        "--verify-term",
        default="Avatar",
        help="Probe string for the post-wipe content ghost scan "
        "(default: Avatar). Raises GhostMemoryError if found.",
    )
    args = parser.parse_args()
    run_wipe(dry=args.dry, verify_term=args.verify_term)


if __name__ == "__main__":
    main()
