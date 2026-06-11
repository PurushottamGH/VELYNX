"""
VELYNX Memory Graph — SQLite persistence layer for cross-session recall.
Logs every pipeline invocation (route type, primary concepts, confidence)
and provides temporal queries for context and recurrence detection.
"""

from __future__ import annotations

import contextlib
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

DB_PATH = Path(__file__).parent.parent.parent / "data" / "memory_graph.db"

HEALING_THRESHOLD = 0.15


class MemoryCore:
    """SQLite-backed experience store for the VELYNX cognitive pipeline.

    Usage::

        mem = MemoryCore()
        mem.log_experience(cognitive_packet, meta_packet)
        recent = mem.retrieve_recent_state(limit=5)
        count = mem.retrieve_concept_history("shame")
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_PATH
        self._init_db()

    # ── Schema management ──────────────────────────────────────────────

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp            TEXT    NOT NULL,
                    route_type           TEXT    NOT NULL,
                    primary_soul_concept TEXT,
                    primary_domain_concept TEXT,
                    confidence_score     REAL   DEFAULT 0.0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_experiences_timestamp
                    ON experiences (timestamp DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_experiences_soul
                    ON experiences (primary_soul_concept)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_experiences_domain
                    ON experiences (primary_domain_concept)
            """)

    # ── Connection management ──────────────────────────────────────────

    @contextlib.contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── Public API ─────────────────────────────────────────────────────

    def log_experience(
        self,
        cognitive_packet: dict[str, Any],
        meta_packet: dict[str, Any],
    ) -> int:
        """Parse the pipeline outputs and persist a single experience row.

        Extracts:
        - ``route_type`` from ``soul_result.domain_route``
        - ``primary_soul_concept`` — the highest-weighted soul concept
        - ``primary_domain_concept`` — first domain hit (structural) or first
          domain concept from ``domain_concepts``
        - ``confidence_score`` from ``meta_packet.meta.confidence``

        Returns the new row id.
        """
        soul_result = cognitive_packet.get("soul_result", {})
        meta = meta_packet.get("meta", {})

        route_type = soul_result.get("domain_route", "none")

        # Highest-weighted soul concept
        scores = soul_result.get("scores", {})
        sorted_soul = sorted(
            scores.items(), key=lambda kv: kv[1], reverse=True
        )
        primary_soul = sorted_soul[0][0] if sorted_soul else None

        # Primary domain concept
        domain_hits = soul_result.get("domain_hits", {})
        if domain_hits:
            sorted_domain = sorted(
                domain_hits.items(), key=lambda kv: kv[1], reverse=True
            )
            primary_domain = sorted_domain[0][0]
        else:
            domain_concepts = cognitive_packet.get("domain_concepts", [])
            primary_domain = domain_concepts[0] if domain_concepts else None

        confidence = meta.get("confidence", 0.0)

        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO experiences
                    (timestamp, route_type, primary_soul_concept,
                     primary_domain_concept, confidence_score)
                VALUES (?, ?, ?, ?, ?)
                """,
                (now, route_type, primary_soul, primary_domain, confidence),
            )
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    def calculate_decay(
        self,
        initial_weight: float,
        timestamp_str: str,
        half_life_hours: float = 12.0,
    ) -> float:
        """Return the exponentially decayed weight of a memory.

        The decay follows::

            w(t) = initial_weight * exp(-lambda * t)

        where ``lambda = 0.693 / half_life_hours`` (0.693 ≈ ln 2, so the
        weight halves every ``half_life_hours``).  ``t`` is the number of
        hours elapsed between ``timestamp_str`` and ``datetime.now()``.

        The timestamp is parsed with :func:`datetime.fromisoformat`, so it
        tolerates the ``...+00:00`` suffix that SQLite stores via
        :func:`datetime.now(timezone.utc).isoformat`.  Naive timestamps are
        assumed to be UTC.

        Parameters
        ----------
        initial_weight:
            The memory's starting intensity — typically the
            ``confidence_score`` of the experience when it was first logged.
        timestamp_str:
            ISO-8601 timestamp stored in the ``experiences`` table.
        half_life_hours:
            How many hours until the weight halves.  Defaults to 12 h,
            which roughly mirrors a waking day.
        """

        moment = datetime.fromisoformat(timestamp_str)
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)

        elapsed = datetime.now(timezone.utc) - moment
        t_hours = max(elapsed.total_seconds() / 3600.0, 0.0)

        if half_life_hours <= 0:
            return float(initial_weight)

        decay_constant = 0.693 / half_life_hours
        return float(initial_weight) * math.exp(-decay_constant * t_hours)

    def retrieve_recent_state(self, limit: int = 3) -> list[dict[str, Any]]:
        """Fetch the most recent recorded experiences, newest first.

        Each row is augmented with a temporally decayed ``current_intensity``
        derived from its ``confidence_score`` and the time elapsed since the
        event was logged.  When ``current_intensity`` falls below
        :data:`HEALING_THRESHOLD` (default 0.15) the row is annotated with
        ``{"status": "healed"}`` so downstream callers can recognise that the
        emotional charge has dissolved.
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, timestamp, route_type,
                       primary_soul_concept, primary_domain_concept,
                       confidence_score
                FROM experiences
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        results: list[dict[str, Any]] = []
        for row in rows:
            entry = dict(row)
            initial = entry.get("confidence_score") or 0.0
            current = self.calculate_decay(initial, entry["timestamp"])
            entry["current_intensity"] = current
            if current < HEALING_THRESHOLD:
                entry["status"] = "healed"
            results.append(entry)
        return results

    def retrieve_concept_history(self, concept_name: str) -> int:
        """Return how many times *concept_name* has appeared as the primary
        soul or domain concept across all logged experiences.

        This detects recurring patterns: a high count for e.g. "loss" or
        "shame" signals a persistent emotional or structural theme."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) AS cnt
                FROM experiences
                WHERE primary_soul_concept = ? OR primary_domain_concept = ?
                """,
                (concept_name, concept_name),
            ).fetchone()
            return row["cnt"] if row else 0

    def get_experience_count(self) -> int:
        """Total rows in the experiences table (convenience for stats)."""
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM experiences").fetchone()
            return row["cnt"] if row else 0

    def get_concept_summary(self) -> list[dict[str, Any]]:
        """Return all distinct concepts that have ever appeared as primary,
        along with their frequency, ordered most-frequent first."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT concept, SUM(cnt) AS total
                FROM (
                    SELECT primary_soul_concept AS concept, COUNT(*) AS cnt
                    FROM experiences
                    WHERE primary_soul_concept IS NOT NULL
                    GROUP BY primary_soul_concept
                    UNION ALL
                    SELECT primary_domain_concept, COUNT(*)
                    FROM experiences
                    WHERE primary_domain_concept IS NOT NULL
                    GROUP BY primary_domain_concept
                )
                GROUP BY concept
                ORDER BY total DESC
                """,
            ).fetchall()
            return [dict(r) for r in rows]


if __name__ == "__main__":
    import json
    from pathlib import Path

    print("=" * 60)
    print("VELYNX Memory Graph — Self-Test")
    print("=" * 60)

    # Use a temp DB so we don't pollute production data.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test_memory.db"
        mem = MemoryCore(db_path)

        # ── Personal demo packet (mimics cross_query + reflect) ──────
        personal_cognitive = {
            "query": "I feel like a failure and I doubt myself",
            "soul_result": {
                "concepts": ["shame", "identity", "trust", "depression"],
                "scores": {"shame": 3.75, "identity": 2.5, "trust": 0.42, "depression": 0.35},
                "domain_route": "personal",
                "domain_hits": {},
                "arc": "Shame leads through identity and arrives at trust",
            },
            "domain_concepts": ["debugging", "technical debt"],
            "bridge_connections": [{"soul": "shame", "domain": "debugging"}],
        }
        personal_meta = {
            "concepts": ["shame", "identity", "trust", "depression"],
            "scores": {"shame": 3.75, "identity": 2.5, "trust": 0.42, "depression": 0.35},
            "domain_route": "personal",
            "meta": {"confidence": 0.91, "status": "strong"},
            "gaps": [],
        }

        # ── Structural demo packet ──────────────────────────────────
        structural_cognitive = {
            "query": "the deployment failed and the server is down",
            "soul_result": {
                "concepts": [],
                "scores": {},
                "domain_route": "structural",
                "domain_hits": {"failure": 1.0, "bottleneck": 0.9, "debugging": 0.5},
                "arc": "",
            },
            "domain_concepts": ["failure", "bottleneck", "debugging"],
            "bridge_connections": [],
        }
        structural_meta = {
            "concepts": [],
            "scores": {},
            "domain_route": "structural",
            "meta": {"confidence": 0.65, "status": "partial"},
            "gaps": [{"type": "missing_concept", "concept": "recovery", "reason": "no signal match"}],
        }

        # ── Log several experiences ─────────────────────────────────
        mem.log_experience(personal_cognitive, personal_meta)
        mem.log_experience(structural_cognitive, structural_meta)
        mem.log_experience(personal_cognitive, personal_meta)
        mem.log_experience(personal_cognitive, personal_meta)
        mem.log_experience(structural_cognitive, structural_meta)

        # ── Verify ──────────────────────────────────────────────────
        total = mem.get_experience_count()
        print(f"\nTotal experiences logged: {total}")
        assert total == 5, f"Expected 5, got {total}"

        recent = mem.retrieve_recent_state(limit=3)
        print(f"Recent states (last {len(recent)}):")
        for r in recent:
            print(f"  {r['timestamp']} | {r['route_type']:>10} | "
                  f"soul={r['primary_soul_concept']} | "
                  f"domain={r['primary_domain_concept']} | "
                  f"conf={r['confidence_score']} | "
                  f"intensity={r['current_intensity']:.4f} | "
                  f"status={r.get('status', 'active')}")

        assert len(recent) == 3
        assert recent[0]["route_type"] == "structural"  # newest first
        assert "current_intensity" in recent[0]

        # ── Temporal decay: half_life_hours = 12h, ~0h elapsed → ≈ 1.0
        intensity_now = mem.calculate_decay(1.0, recent[0]["timestamp"])
        assert 0.99 <= intensity_now <= 1.0, intensity_now
        print(f"\n[decay] Fresh memory intensity: {intensity_now:.4f}")

        # ── Far-past timestamp → should be "healed"
        ancient = "2000-01-01T00:00:00+00:00"
        ancient_intensity = mem.calculate_decay(0.9, ancient)
        print(f"[decay] Year-2000 memory decayed to: {ancient_intensity:.6f}")
        assert ancient_intensity < HEALING_THRESHOLD

        for concept, expected in [("shame", 3), ("failure", 2), ("ineffable_void", 0)]:
            count = mem.retrieve_concept_history(concept)
            assert count == expected, (
                f"'{concept}' expected {expected}, got {count}"
            )
            print(f"  Concept '{concept}' appeared {count}x")

        summary = mem.get_concept_summary()
        print(f"\nConcept summary ({len(summary)} entries):")
        for s in summary[:5]:
            print(f"  {s['concept']:>12}  {s['total']}x")

        print(f"\n[PASS] All MemoryCore assertions passed.")
