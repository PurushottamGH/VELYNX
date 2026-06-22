"""
VELYNX Cognitive Architecture
Module: velynx/graph/living_edges.py
Description: Sovereign Local Weighted Living Edge System with Bayesian Epistemic Rigor,
             Evidence Audit Trails, and Asymptotic Weighting.
Optimizations: Fixed internal connection nesting and removed redundant schema creation calls.
Hardware Target: Local Processing (GTX 1070 / Windows 11)
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from backend.memory._sqlite import connect as open_connection
from backend.memory._sqlite import canonical_db_path, resolve_db_path

DB_NAME = "brain_stem.db"
DB_PATH = str(resolve_db_path(canonical_db_path(DB_NAME)))

def get_db_connection() -> sqlite3.Connection:
    os.makedirs(Path(DB_PATH).parent, exist_ok=True)
    conn = open_connection(DB_PATH, row_factory=sqlite3.Row)
    return conn

def initialize_schema():
    """Builds the non-negotiable 3-table architecture. Called once at system startup."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # TABLE 1: Concepts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS concepts (
            concept_id TEXT PRIMARY KEY,
            domain TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # TABLE 2: Living Edges (State Derived from Evidence)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS living_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            relation TEXT NOT NULL,
            target TEXT NOT NULL,
            asymptotic_weight REAL DEFAULT 0.7,
            weight_alpha REAL DEFAULT 1.0,  
            weight_beta REAL DEFAULT 1.0,   
            context TEXT DEFAULT 'general',
            status TEXT DEFAULT 'active',   
            confidence TEXT DEFAULT 'UNCERTAIN',
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source, relation, target, context)
        );
    ''')

    # TABLE 3: Edge Evidence (The Immutable Audit Trail)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS edge_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER NOT NULL,
            action TEXT NOT NULL,            
            source_quality REAL DEFAULT 0.5, 
            evidence_context TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(edge_id) REFERENCES living_edges(id)
        );
    ''')

    # TABLE 4: Coactivation Counts (Hebbian Creation Guard)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coactivation_counts (
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            context TEXT DEFAULT 'hebbian_inference',
            count INTEGER DEFAULT 0,
            PRIMARY KEY (source, target, context)
        );
    ''')
    
    conn.commit()
    conn.close()

def _evaluate_bayesian_state(alpha: float, beta: float) -> tuple[float, float, float, float, float]:
    """Calculates Bayesian mean and evidence metrics from continuous inputs."""
    reinforced_count = alpha - 1.0
    challenged_count = beta - 1.0
    evidence_count = reinforced_count + challenged_count
    
    weight_mean = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
    challenge_rate = challenged_count / evidence_count if evidence_count > 0 else 0.0
    
    return weight_mean, evidence_count, reinforced_count, challenged_count, challenge_rate

def _calculate_confidence_and_status(weight_mean: float, evidence_count: float, 
                                     reinforced_count: float, challenged_count: float, 
                                     challenge_rate: float) -> tuple[str, str]:
    """Applies strict epistemic filters to evaluate truth-validity."""
    status = 'active'
    
    if challenged_count >= reinforced_count and evidence_count > 0:
        status = 'contested'

    if weight_mean >= 0.90 and evidence_count >= 20 and challenge_rate <= 0.05:
        confidence = 'CERTAIN'
    elif weight_mean >= 0.70 and evidence_count >= 5:
        confidence = 'PROBABLE'
    elif weight_mean < 0.40 or (challenged_count >= reinforced_count and evidence_count > 0):
        confidence = 'CONTESTED'
    else:
        confidence = 'UNCERTAIN'
        
    return confidence, status

def _ensure_concepts_exist(cursor: sqlite3.Cursor, source: str, target: str):
    """Ensures referential integrity for nodes in the graph."""
    for concept in [source, target]:
        cursor.execute('INSERT OR IGNORE INTO concepts (concept_id) VALUES (?)', (concept,))

def _reinforce_edge_core(cursor: sqlite3.Cursor, source: str, relation: str, target: str, 
                         context: str, source_quality: float, update_lambda: float) -> None:
    """Internal core logic for reinforcement execution using an existing database cursor."""
    cursor.execute('''
        SELECT id, asymptotic_weight, weight_alpha, weight_beta 
        FROM living_edges WHERE source = ? AND relation = ? AND target = ? AND context = ?
    ''', (source, relation, target, context))
    row = cursor.fetchone()
    if not row:
        return
        
    edge_id = row['id']
    
    cursor.execute('''
        INSERT INTO edge_evidence (edge_id, action, source_quality)
        VALUES (?, 'reinforce', ?)
    ''', (edge_id, source_quality))
    
    new_alpha = row['weight_alpha'] + source_quality
    new_beta = row['weight_beta']
    
    weight_mean, ev_count, ref_count, ch_count, ch_rate = _evaluate_bayesian_state(new_alpha, new_beta)
    
    current_w = row['asymptotic_weight']
    new_w = round(current_w + update_lambda * (1.0 - current_w), 4)
    
    confidence, status = _calculate_confidence_and_status(
        weight_mean, ev_count, ref_count, ch_count, ch_rate
    )
    
    cursor.execute('''
        UPDATE living_edges SET
            asymptotic_weight = ?, weight_alpha = ?, weight_beta = ?, status = ?, confidence = ?, last_updated = ?
        WHERE id = ?
    ''', (new_w, new_alpha, new_beta, status, confidence, datetime.now().isoformat(), edge_id))

def add_living_edge(source: str, relation: str, target: str, context: str = 'general', 
                    initial_quality: float = 0.9) -> int:
    """Combined execution pipeline to eliminate connection overhead nesting."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    _ensure_concepts_exist(cursor, source, target)
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT OR IGNORE INTO living_edges 
        (source, relation, target, context, first_seen, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (source, relation, target, context, now, now))
    
    cursor.execute('''
        SELECT id FROM living_edges 
        WHERE source = ? AND relation = ? AND target = ? AND context = ?
    ''', (source, relation, target, context))
    edge_id = cursor.fetchone()['id']
    
    # Executes reinforcement completely inside the safe parent connection block
    _reinforce_edge_core(cursor, source, relation, target, context, initial_quality, update_lambda=0.15)
    
    conn.commit()
    conn.close()
    return edge_id

def reinforce_edge(source: str, relation: str, target: str, context: str = 'general', 
                   source_quality: float = 0.5, update_lambda: float = 0.15) -> Optional[Dict[str, Any]]:
    """Standard dynamic interaction hook for structural reinforcement."""
    conn = get_db_connection()
    cursor = conn.cursor()
    _reinforce_edge_core(cursor, source, relation, target, context, source_quality, update_lambda)
    conn.commit()
    conn.close()
    return get_edge(source, target, context)

def challenge_edge(source: str, relation: str, target: str, context: str = 'general', 
                   source_quality: float = 0.5, update_lambda: float = 0.20) -> Optional[Dict[str, Any]]:
    """Logs contradiction metrics, scales down weights asymptotically, increments beta factors."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, asymptotic_weight, weight_alpha, weight_beta 
        FROM living_edges WHERE source = ? AND relation = ? AND target = ? AND context = ?
    ''', (source, relation, target, context))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    edge_id = row['id']
    
    cursor.execute('''
        INSERT INTO edge_evidence (edge_id, action, source_quality)
        VALUES (?, 'challenge', ?)
    ''', (edge_id, source_quality))
    
    new_alpha = row['weight_alpha']
    new_beta = row['weight_beta'] + source_quality
    
    weight_mean, ev_count, ref_count, ch_count, ch_rate = _evaluate_bayesian_state(new_alpha, new_beta)
    
    current_w = row['asymptotic_weight']
    new_w = round(current_w - update_lambda * current_w, 4)
    
    confidence, status = _calculate_confidence_and_status(
        weight_mean, ev_count, ref_count, ch_count, ch_rate
    )
    
    cursor.execute('''
        UPDATE living_edges SET
            asymptotic_weight = ?, weight_alpha = ?, weight_beta = ?, status = ?, confidence = ?, last_updated = ?
        WHERE id = ?
    ''', (new_w, new_alpha, new_beta, status, confidence, datetime.now().isoformat(), edge_id))
    
    conn.commit()
    conn.close()
    return get_edge(source, target, context)

def get_edge(source: str, target: str, context: str = 'general') -> Optional[Dict[str, Any]]:
    """Extracts internal node connection parameters along with dynamically computed mean values."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM living_edges 
        WHERE source = ? AND target = ? AND context = ?
    ''', (source, target, context))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        data['derived_weight_mean'] = round(data['weight_alpha'] / (data['weight_alpha'] + data['weight_beta']), 4)
        return data
    return None

def migrate_flat_edges(old_db_path: str = "backend/velynx_data/soul_graph/graph.db") -> int:
    """Atomic multi-row migration directly from existing SQLite database to Bayesian schema."""
    import os
    if not os.path.exists(old_db_path):
        raise FileNotFoundError(f"Legacy database not found at: {old_db_path}")

    initialize_schema()
    now = datetime.now().isoformat()
    
    # Pre-compute exact Bayesian priors for high-quality baseline data
    init_alpha = 1.9
    init_beta = 1.0
    init_weight_mean, init_ev_count, init_ref_count, init_ch_count, init_ch_rate = _evaluate_bayesian_state(init_alpha, init_beta)
    init_asymptotic_weight = round(0.7 + 0.15 * (1.0 - 0.7), 4)
    init_confidence, init_status = _calculate_confidence_and_status(
        init_weight_mean, init_ev_count, init_ref_count, init_ch_count, init_ch_rate
    )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION;")
        
        # 1. Attach the legacy database
        cursor.execute(f"ATTACH DATABASE '{old_db_path}' AS old_graph")
        
        # 2. Fetch all raw edges from legacy table
        cursor.execute("SELECT from_concept, to_concept, edge_type, reason FROM old_graph.soul_edges")
        legacy_edges = cursor.fetchall()
        
        concepts = set()
        edge_rows = []
        
        for row in legacy_edges:
            source = str(row['from_concept'])
            target = str(row['to_concept'])
            relation = str(row['edge_type'])
            context = str(row['reason']) if row['reason'] else 'general'
            
            concepts.add(source)
            concepts.add(target)
            
            edge_rows.append((
                source, relation, target, init_asymptotic_weight,
                init_alpha, init_beta, context, init_status, init_confidence, now, now
            ))

        if not edge_rows:
            return 0
            
        # 3. Batch create concept entities
        cursor.executemany(
            'INSERT OR IGNORE INTO concepts (concept_id) VALUES (?)',
            [(c,) for c in concepts]
        )
        
        # 4. Batch construct primary derived records
        cursor.executemany('''
            INSERT OR IGNORE INTO living_edges (
                source, relation, target, asymptotic_weight, 
                weight_alpha, weight_beta, context, status, confidence, first_seen, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', edge_rows)
        
        # 5. Synchronize immutable proof logs for the newly mapped structure IDs
        evidence_rows = []
        for row in edge_rows:
            cursor.execute('''
                SELECT id FROM living_edges 
                WHERE source = ? AND relation = ? AND target = ? AND context = ?
            ''', (row[0], row[1], row[2], row[6]))
            res = cursor.fetchone()
            if res:
                evidence_rows.append((res['id'], 'reinforce', 0.9, now))
        
        # 6. Batch record evidence track paths
        cursor.executemany('''
            INSERT INTO edge_evidence (edge_id, action, source_quality, timestamp)
            VALUES (?, ?, ?, ?)
        ''', evidence_rows)
        
        # 7. Commit first, then detach
        conn.commit()
        cursor.execute("DETACH DATABASE old_graph")
        migrated_count = len(evidence_rows)
        
    except Exception as e:
        conn.rollback()
        try:
            cursor.execute("DETACH DATABASE old_graph")
        except:
            pass
        raise e
    finally:
        conn.close()
        
    return migrated_count
