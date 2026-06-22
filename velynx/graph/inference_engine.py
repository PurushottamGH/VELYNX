"""
VELYNX Cognitive Architecture
Module: velynx/graph/inference_engine.py
Description: Phase 44 — Transitive Inference Engine (The Dreaming State).
             Propagates inferences across the Bayesian living graph using
             SQLite self-join transitive closure.
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

from backend.memory._sqlite import connect as open_connection
from backend.memory._sqlite import canonical_db_path, resolve_db_path

DB_NAME = "brain_stem.db"
DB_PATH = str(resolve_db_path(canonical_db_path(DB_NAME)))


def _get_conn() -> sqlite3.Connection:
    os.makedirs(Path(DB_PATH).parent, exist_ok=True)
    conn = open_connection(DB_PATH, row_factory=sqlite3.Row)
    return conn


def propagate_inferences() -> int:
    """
    Find all valid transitive chains (A->B and B->C) where both edges have
    confidence in ('CERTAIN', 'PROBABLE') and status = 'active', then create
    inferred A->C edges.

    Returns the number of new inferred edges created.
    """
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT DISTINCT e1.source AS A, e1.target AS B, e2.target AS C,
               e1.asymptotic_weight AS w1, e2.asymptotic_weight AS w2
        FROM living_edges e1
        JOIN living_edges e2 ON e1.target = e2.source
        WHERE e1.confidence IN ('CERTAIN', 'PROBABLE')
          AND e1.status = 'active'
          AND e2.confidence IN ('CERTAIN', 'PROBABLE')
          AND e2.status = 'active'
          AND e1.source != e2.target
          AND NOT EXISTS (
              SELECT 1 FROM living_edges le
              WHERE le.source = e1.source
                AND le.target = e2.target
          )
    ''')
    candidates = cursor.fetchall()

    now = datetime.now().isoformat()
    created = 0

    for row in candidates:
        A, B, C, w1, w2 = row['A'], row['B'], row['C'], row['w1'], row['w2']
        new_weight = round(w1 * w2 * 0.6, 4)

        cursor.execute('''
            INSERT OR IGNORE INTO concepts (concept_id) VALUES (?)
        ''', (A,))
        cursor.execute('''
            INSERT OR IGNORE INTO concepts (concept_id) VALUES (?)
        ''', (C,))

        cursor.execute('''
            INSERT OR IGNORE INTO living_edges
                (source, relation, target, asymptotic_weight,
                 weight_alpha, weight_beta, context, status, confidence,
                 first_seen, last_updated)
            VALUES (?, 'inferred_transitive', ?, ?,
                    1.2, 1.0, 'background_inference', 'inferred', 'UNCERTAIN',
                    ?, ?)
        ''', (A, C, new_weight, now, now))

        cursor.execute("SELECT changes()")
        if cursor.fetchone()[0]:
            created += 1

    conn.commit()
    conn.close()
    return created
