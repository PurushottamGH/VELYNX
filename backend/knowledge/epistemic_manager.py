"""
VELYNX Epistemic Scaffolding & Explainability API
===================================================

Architectural note (pivot)
--------------------------
Following the design review we are building **Observability before Autonomy**.
This module is the read/audit spine of the Epistemic Engine and is deliberately
*MUTE* about belief dynamics:

* There is **no** automatic confidence recalculation.
* There is **no** posterior / Bayesian math.
* Calling ``add_support`` or ``add_challenge`` does **not** move
  ``current_confidence`` by even one tick — it only appends a row of evidence.
* The only routine that changes ``current_confidence`` is ``record_revision``,
  and it records *exactly* the value the caller hands it, plus a human reason,
  into an append-only audit table. It performs zero computation.

Future autonomy layers may sit *on top* of this scaffold; they may never reach
*inside* it to mutate state silently. Everything an autonomous agent would do
must be expressible here as an explicit, observable, auditable call.

Schema
------
Four tables, all keyed on ``belief_id``:

* ``beliefs``            — the claim triple + its live confidence + status.
* ``belief_sources``     — *origin* provenance: where the belief first came from.
* ``belief_evidence``    — supporting / challenging evidence rows (weighted).
* ``belief_revisions``   — append-only audit log of every confidence change.

Standard library only.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.memory._sqlite import resolve_db_path
from backend.memory._sqlite import connect as open_connection

# ── DB path (mirrors the sibling knowledge_graph.py resolution) ──────────────
# Anchored to the project-root ``data/`` dir so it is CWD-independent; wrapped
# in ``resolve_db_path`` so it is redirected under VELYNX_TEST_MODE and never
# pollutes live data during a test run.
DB_PATH = resolve_db_path(
    Path(__file__).resolve().parent.parent.parent / "data" / "epistemic.db"
)

# Allowed stances in belief_evidence. Kept as a module constant so callers and
# the explainability reader agree on the exact vocabulary.
_STANCE_SUPPORTS = "SUPPORTS"
_STANCE_CHALLENGES = "CHALLENGES"
_VALID_STANCES = (_STANCE_SUPPORTS, _STANCE_CHALLENGES)


def _now_iso() -> str:
    """UTC timestamp in ISO-8601. Single source for every ``*_at``/``timestamp``."""
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    """Open a WAL-enabled connection, ensure the schema exists, return it.

    The caller owns the connection lifecycle (close it when done). Schema
    creation is idempotent (``CREATE TABLE IF NOT EXISTS``), so this is cheap
    to call per-operation — matching the rest of the VELYNX memory stack's
    fresh-connection-per-op style.
    """
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = open_connection(str(DB_PATH), row_factory=sqlite3.Row)
    _initialize_epistemic_schema(conn)
    return conn


# ── 1. Schema ────────────────────────────────────────────────────────────────
def _initialize_epistemic_schema(conn: sqlite3.Connection) -> None:
    """Create the four epistemic tables on ``conn`` if they don't yet exist.

    Idempotent. Split out from the public :func:`initialize_epistemic_schema`
    so internal callers that already hold a connection can bootstrap without
    opening a second one.
    """
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS beliefs (
            belief_id           TEXT PRIMARY KEY,
            subject             TEXT NOT NULL,
            relation            TEXT NOT NULL,
            object              TEXT NOT NULL,
            current_confidence  REAL NOT NULL,
            status              TEXT NOT NULL,
            created_at          TEXT NOT NULL,
            updated_at          TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS belief_sources (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            belief_id   TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_ref  TEXT NOT NULL,
            FOREIGN KEY (belief_id) REFERENCES beliefs(belief_id)
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS belief_evidence (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            belief_id    TEXT NOT NULL,
            stance       TEXT NOT NULL CHECK (stance IN ('SUPPORTS', 'CHALLENGES')),
            evidence_ref TEXT NOT NULL,
            weight       REAL NOT NULL,
            FOREIGN KEY (belief_id) REFERENCES beliefs(belief_id)
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS belief_revisions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            belief_id       TEXT NOT NULL,
            old_confidence  REAL,
            new_confidence  REAL NOT NULL,
            reason          TEXT,
            timestamp       TEXT NOT NULL,
            FOREIGN KEY (belief_id) REFERENCES beliefs(belief_id)
        )
        """
    )
    conn.commit()


def initialize_epistemic_schema(db_path: Any = None) -> None:
    """Public one-shot schema bootstrap.

    Opens its own connection (resolved through the standard VELYNX path logic),
    creates the four tables if absent, and closes. Safe to call repeatedly.

    Pass ``db_path`` to target a non-default location (e.g. ``":memory:"`` in a
    unit test); defaults to the module-level :data:`DB_PATH`.
    """
    path = resolve_db_path(db_path) if db_path is not None else DB_PATH
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = open_connection(str(path), row_factory=sqlite3.Row)
    try:
        _initialize_epistemic_schema(conn)
    finally:
        conn.close()


# ── 2. Pure CRUD (insertion / retrieval — NO automatic mutations) ────────────
def register_belief(
    subject: str,
    relation: str,
    object: str,
    initial_confidence: float,
    status: str = "UNVERIFIED",
) -> str:
    """Insert a new belief row and return its ``belief_id``.

    Pure insertion. ``initial_confidence`` is stored verbatim — it is never
    derived, clamped, or blended. No evidence, source, or revision rows are
    created; those are separate, explicit calls. ``updated_at`` starts equal to
    ``created_at`` and only advances when :func:`record_revision` runs.

    ``belief_id`` is a UTC timestamp + counter suffix so it is globally unique
    and human-sortable without depending on rowid internals.
    """
    belief_id = f"blf-{_now_iso()}"
    ts = _now_iso()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO beliefs
                (belief_id, subject, relation, object,
                 current_confidence, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                belief_id,
                subject,
                relation,
                object,
                float(initial_confidence),
                status,
                ts,
                ts,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return belief_id


def add_source(belief_id: str, source_type: str, source_ref: str) -> int:
    """Record an *origin* source for a belief (the ``belief_sources`` table).

    Pure insertion. Distinct from evidence: a source answers "where did this
    belief come from?", while evidence answers "what backs / undermines it?".
    Returns the new row id.
    """
    conn = _connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO belief_sources (belief_id, source_type, source_ref)
            VALUES (?, ?, ?)
            """,
            (belief_id, source_type, source_ref),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def _add_evidence(stance: str, belief_id: str, evidence_ref: str, weight: float) -> int:
    """Shared inserter for SUPPORTS / CHALLENGES rows.

    NOTE: this is the crux of the "no automatic mutations" contract. It touches
    *only* ``belief_evidence``. It deliberately does **not** read
    ``current_confidence``, recompute it, or write it back. Evidence accrues as
    an observable record; nothing about the belief's headline number changes.
    """
    if stance not in _VALID_STANCES:
        raise ValueError(f"stance must be one of {_VALID_STANCES}, got {stance!r}")
    conn = _connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO belief_evidence (belief_id, stance, evidence_ref, weight)
            VALUES (?, ?, ?, ?)
            """,
            (belief_id, stance, evidence_ref, float(weight)),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def add_support(belief_id: str, evidence_ref: str, weight: float = 1.0) -> int:
    """Append a SUPPORTING evidence row for ``belief_id``. Pure insertion.

    ``evidence_ref`` is an opaque pointer (a triple id, a log line, a citation)
    and ``weight`` is a caller-supplied scalar stored verbatim. The belief's
    ``current_confidence`` is **not** touched.
    """
    return _add_evidence(_STANCE_SUPPORTS, belief_id, evidence_ref, weight)


def add_challenge(belief_id: str, evidence_ref: str, weight: float = 1.0) -> int:
    """Append a CHALLENGING evidence row for ``belief_id``. Pure insertion.

    Same contract as :func:`add_support`: records the challenge, does not move
    confidence. A future autonomy layer will *read* these rows and *then*
    decide — but that decision is not made here.
    """
    return _add_evidence(_STANCE_CHALLENGES, belief_id, evidence_ref, weight)


def record_revision(
    belief_id: str,
    new_confidence: float,
    reason: str,
) -> int:
    """Deliberately set a new confidence and audit-log the change.

    This is the **only** function that updates ``beliefs.current_confidence``,
    and it is intentionally non-automatic:

    * It performs **no** calculation. ``new_confidence`` is written exactly as
      given — there is no clamp, no blend, no posterior.
    * It requires a human-readable ``reason`` so every confidence movement is
      accountable in the audit trail.
    * It snapshots the prior value into ``belief_revisions`` (append-only) and
      advances ``updated_at``.

    Returns the new revision row id.
    """
    ts = _now_iso()
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT current_confidence FROM beliefs WHERE belief_id = ?",
            (belief_id,),
        ).fetchone()
        old_confidence = row["current_confidence"] if row else None
        conn.execute(
            "UPDATE beliefs SET current_confidence = ?, updated_at = ? WHERE belief_id = ?",
            (float(new_confidence), ts, belief_id),
        )
        cur = conn.execute(
            """
            INSERT INTO belief_revisions
                (belief_id, old_confidence, new_confidence, reason, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (belief_id, old_confidence, float(new_confidence), reason, ts),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


# ── 3. Explainability API ───────────────────────────────────────────────────
def get_belief_explainability(belief_id: str) -> dict[str, Any]:
    """Join the epistemic tables for ``belief_id`` and return a structured readout.

    Answers, in one object:
      * **What is the belief?**        — subject / relation / object / status.
      * **Current confidence?**        — the live number + when it last moved.
      * **What supports it?**          — weighted SUPPORTS evidence rows.
      * **What challenges it?**        — weighted CHALLENGES evidence rows.
      * **Where did it come from?**    — origin sources.
      * **When was it last revised?**  — the most recent audit entry (if any),
        plus the full revision history.

    Pure read: no writes, no side effects. Returns ``None`` if the belief does
    not exist (so callers can distinguish "unknown belief" from a belief with
    no evidence).
    """
    conn = _connect()
    try:
        belief = conn.execute(
            """
            SELECT belief_id, subject, relation, object,
                   current_confidence, status, created_at, updated_at
              FROM beliefs
             WHERE belief_id = ?
            """,
            (belief_id,),
        ).fetchone()
        if belief is None:
            return None

        sources = conn.execute(
            "SELECT source_type, source_ref FROM belief_sources WHERE belief_id = ?",
            (belief_id,),
        ).fetchall()

        supports = conn.execute(
            "SELECT evidence_ref, weight FROM belief_evidence "
            "WHERE belief_id = ? AND stance = 'SUPPORTS' ORDER BY weight DESC",
            (belief_id,),
        ).fetchall()

        challenges = conn.execute(
            "SELECT evidence_ref, weight FROM belief_evidence "
            "WHERE belief_id = ? AND stance = 'CHALLENGES' ORDER BY weight DESC",
            (belief_id,),
        ).fetchall()

        revisions = conn.execute(
            "SELECT old_confidence, new_confidence, reason, timestamp "
            "FROM belief_revisions WHERE belief_id = ? ORDER BY id DESC",
            (belief_id,),
        ).fetchall()
    finally:
        conn.close()

    # Connection is closed above; the dict is built from the row snapshots.
    return {
            "belief": {
                "belief_id": belief["belief_id"],
                "subject": belief["subject"],
                "relation": belief["relation"],
                "object": belief["object"],
                "status": belief["status"],
            },
            "current_confidence": belief["current_confidence"],
            "confidence_set_at": belief["updated_at"],
            "created_at": belief["created_at"],
            "sources": [
                {"source_type": s["source_type"], "source_ref": s["source_ref"]}
                for s in sources
            ],
            "supports": [
                {"evidence_ref": e["evidence_ref"], "weight": e["weight"]}
                for e in supports
            ],
            "challenges": [
                {"evidence_ref": e["evidence_ref"], "weight": e["weight"]}
                for e in challenges
            ],
            "last_revised_at": revisions[0]["timestamp"] if revisions else None,
            "revision_history": [
                {
                    "old_confidence": r["old_confidence"],
                    "new_confidence": r["new_confidence"],
                    "reason": r["reason"],
                    "timestamp": r["timestamp"],
                }
                for r in revisions
            ],
        }


def print_explainability(belief_id: str) -> None:
    """Render :func:`get_belief_explainability` as an ASCII readout to stdout.

    Convenience for debugging / the operator console. Pure read.
    """
    exp = get_belief_explainability(belief_id)
    if exp is None:
        print(f"[epistemic] no belief with id {belief_id!r}")
        return

    bar = "─" * 64
    b = exp["belief"]
    print(bar)
    print(f"BELIEF  {b['subject']}  —[{b['relation']}]->  {b['object']}")
    print(f"  id={b['belief_id']}   status={b['status']}")
    print(bar)
    print(f"current confidence : {exp['current_confidence']}")
    print(f"  set at           : {exp['confidence_set_at']}")
    print(f"  created at       : {exp['created_at']}")
    print(f"  last revised at  : {exp['last_revised_at']}")
    print(bar)
    print("ORIGIN SOURCES")
    if exp["sources"]:
        for s in exp["sources"]:
            print(f"  [{s['source_type']}] {s['source_ref']}")
    else:
        print("  (none)")
    print(bar)
    print("SUPPORTING EVIDENCE")
    if exp["supports"]:
        for e in exp["supports"]:
            print(f"  + (w={e['weight']}) {e['evidence_ref']}")
    else:
        print("  (none)")
    print(bar)
    print("CHALLENGING EVIDENCE")
    if exp["challenges"]:
        for e in exp["challenges"]:
            print(f"  - (w={e['weight']}) {e['evidence_ref']}")
    else:
        print("  (none)")
    print(bar)
    print("REVISION HISTORY (most recent first)")
    if exp["revision_history"]:
        for r in exp["revision_history"]:
            print(f"  {r['old_confidence']} -> {r['new_confidence']}   "
                  f"{r['timestamp']}\n      reason: {r['reason']}")
    else:
        print("  (no revisions recorded)")
    print(bar)


# ── Demo / smoke test ───────────────────────────────────────────────────────
if __name__ == "__main__":
    # Standalone self-contained exercise of the scaffold. Uses a private
    # in-memory DB so it never touches the on-disk store.
    import os
    import tempfile

    # Redirect the module's DB_PATH to a throwaway temp file for this run only.
    _tmp = Path(tempfile.gettempdir()) / "velynx_epistemic_demo.db"
    if _tmp.exists():
        _tmp.unlink()
    globals()["DB_PATH"] = resolve_db_path(_tmp)

    bid = register_belief("sky", "has_color", "blue", initial_confidence=0.8)
    add_source(bid, "observation", "morning_walk_2026-06-24")
    add_support(bid, "wavelength_scattering", weight=0.9)
    add_support(bid, "human_consensus", weight=0.5)
    add_challenge(bid, "sunset_photography", weight=0.3)

    print("\n=== Before any explicit revision ===")
    print_explainability(bid)

    # The ONLY way confidence moves: an explicit, reasoned, audited call.
    record_revision(bid, 0.72, reason="operator reviewed sunset counter-evidence")

    print("\n=== After explicit revision ===")
    print_explainability(bid)
