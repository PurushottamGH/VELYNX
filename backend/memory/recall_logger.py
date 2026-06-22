import sqlite3
import json
import datetime
from typing import List, Dict, Any, Union, Iterable

from backend.memory import _sqlite


class RecallLogger:
    """
    Phase 52.8: Recall Observability.

    Non-blocking telemetry for the memory recall subsystem. This class is a pure
    OBSERVER — it never participates in or mutates retrieval logic. Every public
    write is wrapped by the caller in a try/except so a telemetry failure can
    never crash the cognitive loop.
    """

    def __init__(self, db_path: str = "velynx_state.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return _sqlite.connect(self.db_path, row_factory=sqlite3.Row)

    def _init_db(self):
        """Initializes the Phase 52.8 Recall Observability tables."""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Top-level recall event (one row per retrieve_by_context call)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recall_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                trigger_concepts_json TEXT NOT NULL,
                retrieved_memory_count INTEGER NOT NULL,
                total_recall_energy REAL NOT NULL,
                recall_ratio REAL NOT NULL,
                retrieval_density REAL NOT NULL,
                system_error REAL NOT NULL
            )
        ''')

        # The trigger concepts (and their activation) that drove this recall
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recall_concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recall_event_id INTEGER NOT NULL,
                concept TEXT NOT NULL,
                activation REAL NOT NULL,
                FOREIGN KEY (recall_event_id) REFERENCES recall_events(id)
            )
        ''')

        # The individual memories surfaced by this recall
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recall_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recall_event_id INTEGER NOT NULL,
                memory_id INTEGER,
                memory_strength REAL NOT NULL,
                FOREIGN KEY (recall_event_id) REFERENCES recall_events(id)
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_recall_concepts_event
            ON recall_concepts(recall_event_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_recall_memories_event
            ON recall_memories(recall_event_id)
        ''')

        conn.commit()

        # Phase 52.9A: Retrieval Candidate Observability.
        # Additively migrate recall_events to capture the pre-cutoff raw pool
        # (the top-N candidates BEFORE top_k slicing). Stored as JSON arrays so
        # existing rows and readers are unaffected.
        self._migrate_raw_candidates(conn)

        conn.close()

    def _migrate_raw_candidates(self, conn: sqlite3.Connection):
        """
        Idempotently adds raw_candidate_ids / raw_candidate_scores columns to
        recall_events. SQLite has no ADD COLUMN IF NOT EXISTS, so we inspect the
        schema first. New columns default to NULL for legacy rows.
        """
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(recall_events)")
        existing_cols = {row[1] for row in cursor.fetchall()}

        if "raw_candidate_ids" not in existing_cols:
            cursor.execute(
                "ALTER TABLE recall_events ADD COLUMN raw_candidate_ids TEXT"
            )
        if "raw_candidate_scores" not in existing_cols:
            cursor.execute(
                "ALTER TABLE recall_events ADD COLUMN raw_candidate_scores TEXT"
            )

        conn.commit()

    @staticmethod
    def _normalize_concepts(trigger_concepts: Union[Dict[str, float], Iterable[str]]) -> Dict[str, float]:
        """Accepts either a {concept: activation} mapping or a bare list of concepts."""
        if isinstance(trigger_concepts, dict):
            return {str(k): float(v) for k, v in trigger_concepts.items()}
        return {str(c): 0.0 for c in (trigger_concepts or [])}

    @staticmethod
    def _split_raw_candidates(raw_candidates):
        """
        Phase 52.9A: splits the pre-cutoff raw pool into two parallel arrays
        (ids, scores) for storage. Accepts a list of dicts shaped like
        {"memory_id": int, "score": float} (the MemoryRetriever format) and is
        tolerant of legacy/alt keys. Returns (ids: List, scores: List[float]).
        """
        ids: List[Any] = []
        scores: List[float] = []
        for cand in (raw_candidates or []):
            if isinstance(cand, dict):
                cid = cand.get("memory_id", cand.get("turn_index", cand.get("id")))
                cscore = cand.get("score", cand.get("memory_strength", cand.get("strength", 0.0)))
            else:
                # Tolerate a bare (id, score) pair.
                cid, cscore = cand
            ids.append(cid)
            try:
                scores.append(float(cscore))
            except (TypeError, ValueError):
                scores.append(0.0)
        return ids, scores

    def log_recall_event(
        self,
        trigger_concepts: Union[Dict[str, float], Iterable[str]],
        retrieved_memories: List[Dict[str, Any]],
        recall_energy: float,
        recall_ratio: float,
        system_error: float,
        raw_candidates: List[Dict[str, Any]] = None,
    ) -> int:
        """
        Persists a single recall event and its associated concepts and memories.

        Returns the new recall_events.id. Raises on failure — the caller is
        responsible for catching and emitting a [RECALL TELEMETRY WARNING].
        """
        concepts = self._normalize_concepts(trigger_concepts)
        memories = retrieved_memories or []

        retrieved_memory_count = len(memories)
        total_recall_energy = float(recall_energy)
        # Average energy carried by each surfaced memory (guard against /0)
        retrieval_density = total_recall_energy / max(retrieved_memory_count, 1)

        now = datetime.datetime.now().isoformat()

        # Phase 52.9A: serialize the pre-cutoff raw candidate pool.
        raw_ids, raw_scores = self._split_raw_candidates(raw_candidates)

        conn = self._get_conn()
        try:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO recall_events (
                    timestamp, trigger_concepts_json, retrieved_memory_count,
                    total_recall_energy, recall_ratio, retrieval_density, system_error,
                    raw_candidate_ids, raw_candidate_scores
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                now,
                json.dumps(concepts),
                retrieved_memory_count,
                total_recall_energy,
                float(recall_ratio),
                retrieval_density,
                float(system_error),
                json.dumps(raw_ids),
                json.dumps(raw_scores),
            ))
            recall_event_id = cursor.lastrowid

            if concepts:
                cursor.executemany('''
                    INSERT INTO recall_concepts (recall_event_id, concept, activation)
                    VALUES (?, ?, ?)
                ''', [(recall_event_id, c, a) for c, a in concepts.items()])

            if memories:
                cursor.executemany('''
                    INSERT INTO recall_memories (recall_event_id, memory_id, memory_strength)
                    VALUES (?, ?, ?)
                ''', [
                    (
                        recall_event_id,
                        mem.get("memory_id", mem.get("turn_index")),
                        float(mem.get("memory_strength", mem.get("strength", 0.0))),
                    )
                    for mem in memories
                ])

            conn.commit()
            return recall_event_id
        finally:
            conn.close()
