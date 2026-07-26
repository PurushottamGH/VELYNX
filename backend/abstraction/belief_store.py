import sqlite3
import json
from typing import List, Optional
from contextlib import contextmanager

from backend.memory._sqlite import connect as open_connection
from backend.abstraction.belief_models import CandidateBelief, CoreBelief

class BeliefStore:
    def __init__(self, db_path: str = "velynx_state.db"):
        self.db_path = db_path
        self._initialize_schema()

    @contextmanager
    def _conn(self):
        conn = open_connection(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_schema(self):
        with self._conn() as conn:
            cursor = conn.cursor()
            # Candidate beliefs table with batch_id for isolation
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidate_beliefs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT NOT NULL,
                batch_id TEXT NOT NULL,
                belief_text TEXT NOT NULL,
                belief_hash TEXT NOT NULL,
                support_count INTEGER NOT NULL DEFAULT 1,
                belief_confidence REAL NOT NULL,
                mean_effect REAL NOT NULL,
                promotion_score REAL NOT NULL,
                promoted INTEGER NOT NULL DEFAULT 0,
                reason TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(concept, batch_id, belief_hash)
            )
            """)
            # Core beliefs table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS core_beliefs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT NOT NULL,
                belief_text TEXT NOT NULL,
                belief_hash TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_turn INTEGER NOT NULL,
                updated_turn INTEGER NOT NULL,
                UNIQUE(concept, belief_hash)
            )
            """)
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_candidate_concept_batch
            ON candidate_beliefs(concept, batch_id)
            """)
            conn.commit()

    def inspect_candidates(self, concept: str, batch_id: Optional[str] = None) -> List[CandidateBelief]:
        """Retrieve candidate beliefs for a concept, optionally filtered by batch."""
        with self._conn() as conn:
            cursor = conn.cursor()
            if batch_id:
                cursor.execute("""
                    SELECT belief_text, belief_hash, support_count, belief_confidence,
                           mean_effect, promotion_score, promoted, reason
                    FROM candidate_beliefs
                    WHERE concept = ? AND batch_id = ?
                    ORDER BY promotion_score DESC
                """, (concept, batch_id))
            else:
                cursor.execute("""
                    SELECT belief_text, belief_hash, support_count, belief_confidence,
                           mean_effect, promotion_score, promoted, reason
                    FROM candidate_beliefs
                    WHERE concept = ?
                    ORDER BY promotion_score DESC
                """, (concept,))
            return [CandidateBelief.from_row(row) for row in cursor.fetchall()]

    def upsert_candidate(self, concept: str, batch_id: str, candidate: CandidateBelief):
        """Insert or update a candidate belief."""
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO candidate_beliefs 
                (concept, batch_id, belief_text, belief_hash, support_count, belief_confidence,
                 mean_effect, promotion_score, promoted, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(concept, batch_id, belief_hash) DO UPDATE SET
                    support_count = excluded.support_count,
                    belief_confidence = excluded.belief_confidence,
                    mean_effect = excluded.mean_effect,
                    promotion_score = excluded.promotion_score,
                    promoted = excluded.promoted,
                    reason = excluded.reason
            """, (
                concept, batch_id, candidate.belief_text, candidate.belief_hash,
                candidate.support_count, candidate.belief_confidence,
                candidate.mean_effect, candidate.promotion_score,
                int(candidate.promoted), candidate.reason
            ))
            conn.commit()

    def promote_to_core(self, concept: str, candidate: CandidateBelief, turn: int):
        """Promote a candidate belief to core belief."""
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO core_beliefs 
                (concept, belief_text, belief_hash, confidence, created_turn, updated_turn)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(concept, belief_hash) DO UPDATE SET
                    confidence = excluded.confidence,
                    updated_turn = excluded.updated_turn
            """, (concept, candidate.belief_text, candidate.belief_hash,
                  candidate.belief_confidence, turn, turn))
            conn.commit()

    def get_core_beliefs(self, concept: str) -> List[CoreBelief]:
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT concept, belief_text, belief_hash, confidence, created_turn, updated_turn
                FROM core_beliefs
                WHERE concept = ?
                ORDER BY confidence DESC
            """, (concept,))
            return [CoreBelief(*row) for row in cursor.fetchall()]