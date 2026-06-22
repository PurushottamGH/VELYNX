import sqlite3
import sys

# The whole VELYNX pipeline defaults to velynx_state.db (MemoryStore,
# CandidateStore, RecallLogger). Keep this in sync or pass a path explicitly:
#   python verify_recall_topology.py [db_path]
DEFAULT_DB_PATH = "velynx_state.db"


def verify_recall_topology(db_path: str = DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT
        re.id,
        re.timestamp,
        re.retrieved_memory_count,
        re.total_recall_energy,
        re.recall_ratio,
        re.retrieval_density,
        COUNT(DISTINCT rc.id) AS concept_rows,
        COUNT(DISTINCT rm.id) AS memory_rows
    FROM recall_events re
    LEFT JOIN recall_concepts rc ON rc.recall_event_id = re.id
    LEFT JOIN recall_memories rm ON rm.recall_event_id = re.id
    GROUP BY re.id
    ORDER BY re.id DESC
    LIMIT 5;
    """

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='recall_events'"
    )
    if cursor.fetchone() is None:
        print(f"\nDB: {db_path}")
        print(
            "(recall_events table not found — run the cognitive loop at least once "
            "so RecallLogger can create and populate the Phase 52.8 tables)"
        )
        conn.close()
        return

    cursor.execute(query)
    results = cursor.fetchall()

    print(f"\nDB: {db_path}")
    header = (
        f"{'ID':<5} | {'Timestamp':<26} | {'Mem#':<5} | {'Energy':<7} | "
        f"{'Ratio':<6} | {'Density':<8} | {'Concepts':<8} | {'MemRows':<8}"
    )
    print(header)
    print("-" * len(header))

    if not results:
        print("(no recall_events yet — let the cognitive loop run a few interactions)")
        conn.close()
        return

    integrity_ok = True
    for row in results:
        (event_id, ts, mem_count, energy, ratio, density,
         concept_rows, memory_rows) = row
        print(
            f"{event_id:<5} | {ts:<26} | {mem_count:<5} | {energy:<7.2f} | "
            f"{ratio:<6.2f} | {density:<8.3f} | {concept_rows:<8} | {memory_rows:<8}"
        )
        # Structural integrity check: the count column the logger recorded must
        # match the actual child rows it bound. A mismatch means a broken trail.
        if memory_rows != mem_count:
            integrity_ok = False
            print(
                f"      ^ INTEGRITY WARNING: retrieved_memory_count={mem_count} "
                f"but {memory_rows} recall_memories rows are bound"
            )

    print("-" * len(header))
    print("Integrity: OK" if integrity_ok else "Integrity: MISMATCH (see warnings above)")

    conn.close()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_PATH
    verify_recall_topology(path)
