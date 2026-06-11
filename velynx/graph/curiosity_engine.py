"""
VELYNX Phase 45: The Curiosity Engine
Part A: Gap Scanner — runs during REM sleep to find cognitive gaps
Part B: Question Selector — picks one relevant question per session
Part C: Writer — queues natural-language questions into curiosity_queue
"""

import sqlite3
import datetime
import os

BRAIN_STEM_DB = ".velynx_data/brain_stem.db"


def get_db_connection() -> sqlite3.Connection:
    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.dirname(os.path.dirname(base_dir))
    target_db = os.path.join(project_root, BRAIN_STEM_DB)
    conn = sqlite3.connect(target_db)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_curiosity_schema():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS curiosity_queue (
                concept TEXT,
                question TEXT,
                priority INTEGER,
                created_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                PRIMARY KEY (concept, question)
            )
        ''')
        conn.commit()


# --- PART A & C: GAP SCANNER & WRITER (Runs during REM Sleep) ---
def run_gap_scanner():
    """
    Scans living_edges for cognitive gaps and generates questions.
    MUST ONLY be called from the idle sleep cycle.
    """
    initialize_curiosity_schema()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Priority 1: Inferred edges with UNCERTAIN confidence
        cursor.execute(
            "SELECT source, target FROM living_edges "
            "WHERE status = 'inferred' AND confidence = 'UNCERTAIN'"
        )
        high_gaps = cursor.fetchall()

        # Priority 2: Edges with low alpha (< 2.0)
        cursor.execute(
            "SELECT source, target FROM living_edges "
            "WHERE status = 'active' AND weight_alpha < 2.0"
        )
        med_gaps = cursor.fetchall()

        # Priority 3: Concepts with < 3 outbound edges
        cursor.execute(
            "SELECT source FROM living_edges "
            "GROUP BY source HAVING COUNT(target) < 3"
        )
        low_gaps = cursor.fetchall()

        queued_count = 0
        now = datetime.datetime.now().isoformat()

        for source, target in high_gaps:
            q = (
                f"what does it actually enable after {target}? "
                f"I have a hypothesis but I'm not certain."
            )
            queued_count += _queue_question(cursor, source, q, 3, now)

        for source, target in med_gaps:
            q = (
                f"I've been connecting {source} and {target}, but I'm not sure if "
                f"that holds. Does {source} always precede {target} for you?"
            )
            queued_count += _queue_question(cursor, source, q, 2, now)

        for row in low_gaps:
            concept = row[0]
            q = (
                f"how does it connect to the rest of your experiences? "
                f"I feel like I'm missing the bigger picture."
            )
            queued_count += _queue_question(cursor, concept, q, 1, now)

        conn.commit()
        return queued_count


def _queue_question(cursor, concept, natural_question, priority, timestamp):
    full_question = f"I've been thinking about {concept} — {natural_question}"
    cursor.execute(
        "SELECT 1 FROM curiosity_queue WHERE concept = ? AND status = 'pending'",
        (concept,),
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO curiosity_queue (concept, question, priority, created_at, status) "
            "VALUES (?, ?, ?, ?, 'pending')",
            (concept, full_question, priority, timestamp),
        )
        return 1
    return 0


# --- PART B: QUESTION SELECTOR (Runs after response) ---
def select_curiosity_question(session_has_asked: bool, resonance_scores: dict) -> str:
    """
    Selects one relevant question per session.
    """
    if session_has_asked:
        return ""

    # Only pull gaps for concepts the user is actively talking about
    active_concepts = [
        concept
        for concept, score in resonance_scores.items()
        if score > 0.3
    ]
    if not active_concepts:
        return ""

    with get_db_connection() as conn:
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in active_concepts)
        query = (
            "SELECT concept, question FROM curiosity_queue "
            "WHERE status = 'pending' AND concept IN ({}) "
            "ORDER BY priority DESC, created_at ASC LIMIT 1"
        ).format(placeholders)
        cursor.execute(query, active_concepts)
        row = cursor.fetchone()

        if row:
            concept, question = row["concept"], row["question"]
            cursor.execute(
                "UPDATE curiosity_queue SET status = 'asked' WHERE concept = ? AND question = ?",
                (concept, question),
            )
            conn.commit()
            return f"\n\n{question}"

    return ""
