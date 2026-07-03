import sqlite3
import os
from pathlib import Path

# Resolve the exact path to the main knowledge graph
BACKEND_ROOT = Path(__file__).resolve().parent / "backend"
DB_PATH = BACKEND_ROOT / "velynx_data" / "knowledge_graph" / "graph.db"

def migrate_temporal_schema():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Run the pipeline once to create it.")
        return

    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(str(DB_PATH))
    
    try:
        # Disable foreign keys temporarily to allow dropping the table safely
        conn.execute("PRAGMA foreign_keys=off;")
        conn.execute("BEGIN TRANSACTION;")

        print("1. Creating triples_new with 4D UNIQUE constraint...")
        # Note: We add valid_from and valid_until if they aren't there, 
        # and lock the UNIQUE constraint to include valid_from.
        conn.execute("""
            CREATE TABLE triples_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                relation TEXT NOT NULL,
                object TEXT NOT NULL,
                valid_from TEXT,
                valid_until TEXT,
                UNIQUE(subject, relation, object, valid_from)
            )
        """)

        print("2. Copying existing Phase 63 data...")
        # Check existing columns to map them safely
        cursor = conn.execute("PRAGMA table_info(triples)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "valid_from" in columns:
            conn.execute("""
                INSERT INTO triples_new (id, subject, relation, object, valid_from, valid_until)
                SELECT id, subject, relation, object, valid_from, valid_until FROM triples;
            """)
        else:
            conn.execute("""
                INSERT INTO triples_new (id, subject, relation, object)
                SELECT id, subject, relation, object FROM triples;
            """)

        print("3. Dropping legacy triples table...")
        conn.execute("DROP TABLE triples;")

        print("4. Renaming triples_new to triples...")
        conn.execute("ALTER TABLE triples_new RENAME TO triples;")

        conn.execute("COMMIT;")
        conn.execute("PRAGMA foreign_keys=on;")
        print("\nSUCCESS: Phase 64 Temporal Migration Complete. The 4D Graph is unlocked!")

    except Exception as e:
        conn.execute("ROLLBACK;")
        print(f"\nMigration FAILED: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_temporal_schema()
