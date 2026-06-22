import sqlite3
import json
from contextlib import contextmanager
from typing import Dict, Any

from backend.memory.state_delta import calculate_state_delta
from backend.memory import _sqlite

class MemoryStore:
    def __init__(self, db_path: str = "velynx_state.db"):
        self.db_path = db_path
        self._initialize_schema()
        self.current_turn = self._get_latest_turn()

    @contextmanager
    def _conn(self):
        conn = _sqlite.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _get_latest_turn(self) -> int:
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(turn_index) FROM memory_log")
            result = cursor.fetchone()[0]
            return result if result is not None else 0

    def _initialize_schema(self):
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                turn_index INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                batch_id TEXT,
                memory_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                user_input TEXT NOT NULL,
                activated_concepts_json TEXT NOT NULL,
                dominant_concepts_json TEXT NOT NULL,
                pre_state_json TEXT NOT NULL,
                post_state_json TEXT NOT NULL,
                state_delta_json TEXT NOT NULL,
                prediction_error REAL NOT NULL,
                emotional_energy REAL NOT NULL,
                memory_strength REAL NOT NULL
            )
            """)
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type_strength
            ON memory_log(memory_type, memory_strength DESC)
            """)
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_batch_id
            ON memory_log(batch_id)
            """)
            conn.commit()

    def _determine_memory_type(self, error: float, emotional_energy: float) -> str:
        if error > 0.1 and emotional_energy > 1.0:
            return "episodic"
        elif error <= 0.1 and emotional_energy > 1.0:
            return "reflection"
        return "observation"

    def _determine_priority(self, strength: float) -> str:
        if strength > 0.05:
            return "high"
        elif strength > 0.01:
            return "medium"
        return "low"

    def log_experience(self, user_input: str, sensory_input: Dict[str, float],
                       pre_state: Dict[str, float], post_state: Dict[str, float], error: float,
                       batch_id: str = None):
        """Archives the complete state transition and its delta."""
        self.current_turn += 1

        # Calculate Delta
        state_delta = calculate_state_delta(pre_state, post_state)

        # Calculate Emotional Energy from the top 5 dominant states
        top_states = sorted(post_state.items(), key=lambda item: item[1], reverse=True)[:5]
        emotional_energy = sum(value for _, value in top_states)

        # M = E * (1 + P)
        memory_strength = emotional_energy * (1.0 + error)

        memory_type = self._determine_memory_type(error, emotional_energy)
        priority = self._determine_priority(memory_strength)

        dominant_concepts = {k: v for k, v in top_states}

        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memory_log (
                    turn_index, batch_id, memory_type, priority, user_input, activated_concepts_json,
                    dominant_concepts_json, pre_state_json, post_state_json, state_delta_json,
                    prediction_error, emotional_energy, memory_strength
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_turn,
                batch_id,
                memory_type,
                priority,
                user_input,
                json.dumps(sensory_input),
                json.dumps(dominant_concepts),
                json.dumps(pre_state),
                json.dumps(post_state),
                json.dumps(state_delta),
                float(error),
                float(emotional_energy),
                float(memory_strength)
            ))
            conn.commit()