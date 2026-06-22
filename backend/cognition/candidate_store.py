import sqlite3
import datetime
from typing import List, Dict, Any

from backend.memory._sqlite import connect as open_connection
from backend.memory._sqlite import canonical_db_path

class CandidateStore:
    def __init__(self, db_path: str = ""):
        self.db_path = db_path or str(canonical_db_path("velynx_state.db"))
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = open_connection(self.db_path, row_factory=sqlite3.Row)
        return conn

    def _init_db(self):
        """Initializes the Phase 52.7 Observability Tables."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Aggregate Statistics Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidate_concepts (
                concept TEXT PRIMARY KEY,
                frequency_count INTEGER NOT NULL DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                promotion_status TEXT NOT NULL DEFAULT 'candidate',
                confidence REAL NOT NULL DEFAULT 0.0,
                unique_sessions INTEGER NOT NULL DEFAULT 1
            )
        ''')
        
        # Evidence Trail Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidate_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT NOT NULL,
                observed_text TEXT,
                timestamp TEXT NOT NULL,
                source TEXT DEFAULT 'perception',
                session_id TEXT,
                FOREIGN KEY (concept) REFERENCES candidate_concepts(concept)
            )
        ''')
        conn.commit()
        conn.close()

    def log_candidate_observation(self, concept: str, observed_text: str, session_id: str = "default_session"):
        """Logs an unrecognized word and updates aggregate candidate metrics."""
        conn = self._get_conn()
        cursor = conn.cursor()
        now = datetime.datetime.now().isoformat()

        # 1. Log the exact evidence trail
        cursor.execute('''
            INSERT INTO candidate_observations (concept, observed_text, timestamp, source, session_id)
            VALUES (?, ?, ?, 'perception', ?)
        ''', (concept, observed_text, now, session_id))

        # 2. Update or Insert the aggregate concept
        cursor.execute("SELECT frequency_count FROM candidate_concepts WHERE concept = ?", (concept,))
        row = cursor.fetchone()

        if row:
            # Dynamically calculate unique sessions from the observations table to ensure accuracy
            cursor.execute('''
                UPDATE candidate_concepts
                SET frequency_count = frequency_count + 1,
                    last_seen = ?,
                    unique_sessions = (SELECT COUNT(DISTINCT session_id) FROM candidate_observations WHERE concept = ?),
                    confidence = MIN(1.0, (frequency_count + 1.0) / 20.0)
                WHERE concept = ?
            ''', (now, concept, concept))
        else:
            # Base confidence of 0.05 for a first-time appearance (1/20)
            cursor.execute('''
                INSERT INTO candidate_concepts (concept, frequency_count, first_seen, last_seen, promotion_status, confidence, unique_sessions)
                VALUES (?, 1, ?, ?, 'candidate', 0.05, 1)
            ''', (concept, now, now))

        conn.commit()
        conn.close()

    def get_top_candidates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves the highest-confidence candidates for the Phase 52.7 Audit Dashboard."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT concept, frequency_count, unique_sessions, confidence, promotion_status
            FROM candidate_concepts
            WHERE promotion_status = 'candidate'
            ORDER BY frequency_count DESC, confidence DESC
            LIMIT ?
        ''', (limit,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_candidate_details(self, concept: str) -> List[Dict[str, Any]]:
        """Fetches the raw context lines (evidence) for a specific candidate."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT observed_text, timestamp, session_id
            FROM candidate_observations
            WHERE concept = ?
            ORDER BY timestamp DESC
        ''', (concept,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results