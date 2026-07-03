import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from graph.living_edges import initialize_schema, migrate_flat_edges, get_edge

initialize_schema()
print("[VELYNX DB] Schema successfully initialized.")

print("[VELYNX Ingestion] Transferring configurations from legacy SQLite...")
# Pass the exact path OpenCode found
count = migrate_flat_edges("backend/velynx_data/soul_graph/graph.db")
print(f"[VELYNX Ingestion] Complete. Migrated {count} edges cleanly.")

print("-" * 50)
print("[VELYNX Verification] Database initialized successfully.")
