import json
import sqlite3
import networkx as nx
import uuid
import os
from datetime import datetime, timezone

from backend.memory._sqlite import connect as open_connection

def ensure_schema(cursor):
    """Ensures the Phase 50 schema exists before seeding."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concept_states (
            concept TEXT PRIMARY KEY,
            activation REAL,
            baseline REAL,
            state_confidence REAL,
            source TEXT,
            evidence_count INTEGER,
            updated_at TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transition_rules (
            rule_id TEXT PRIMARY KEY,
            source_concept TEXT,
            target_concept TEXT,
            effect REAL,
            rule_confidence REAL,
            decay REAL,
            condition TEXT,
            evidence_count INTEGER,
            created_at TIMESTAMP,
            origin_ref TEXT
        )
    """)

def load_curriculum(json_path: str, db_path: str = "velynx_state.db") -> nx.DiGraph:
    print("--- INITIATING DUAL-HEMISPHERE SEED LOADER ---")
    
    if not os.path.exists(json_path):
        print(f"FATAL: Could not find {json_path}. Please create the JSON file.")
        return None

    with open(json_path, 'r') as f:
        curriculum = json.load(f)

    # Initialize Graph & DB
    G = nx.DiGraph()
    conn = open_connection(db_path)
    cursor = conn.cursor()
    ensure_schema(cursor)
    
    now = datetime.now(timezone.utc).isoformat()
    rules_to_insert = []

    for concept in curriculum:
        name = concept["name"]
        
        # 1. Build NetworkX Map
        G.add_node(name, category=concept["cat"], phenomenology=concept["phenomenology"])
        
        # 2. SQLite Baseline Seeding
        cursor.execute("""
            INSERT OR IGNORE INTO concept_states 
            (concept, activation, baseline, state_confidence, source, evidence_count, updated_at)
            VALUES (?, 0.0, 0.0, 1.0, 'curriculum_bootstrap', 1, ?)
        """, (name, now))

        # 3. Process Thermodynamic Effects
        effects = concept.get("effects", {})
        
        # Immediate Effects (Fast Decay)
        for target, weight in effects.get("immediate", {}).items():
            G.add_edge(name, target, weight=weight, type="immediate")
            rules_to_insert.append((
                f"rule_{uuid.uuid4().hex[:8]}", name, target, weight, 
                0.9, 0.05, 'immediate', 1, now, 'curriculum'
            ))

        # Over-Time Effects (Slow Decay)
        for target, weight in effects.get("over_time", {}).items():
            G.add_edge(name, target, weight=weight, type="over_time")
            rules_to_insert.append((
                f"rule_{uuid.uuid4().hex[:8]}", name, target, weight, 
                0.8, 0.005, 'over_time', 1, now, 'curriculum'
            ))

    cursor.executemany("""
        INSERT OR IGNORE INTO transition_rules 
        (rule_id, source_concept, target_concept, effect, rule_confidence, decay, condition, evidence_count, created_at, origin_ref)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rules_to_insert)

    conn.commit()
    conn.close()

    print(f"SUCCESS: Seeded {len(curriculum)} life nodes into the database.")
    print(f"SUCCESS: Mapped {len(rules_to_insert)} transition rules governing their interactions.")
    
    return G

if __name__ == "__main__":
    soul_graph = load_curriculum("backend/cognition/soul_curriculum.json")
