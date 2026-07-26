from backend.memory.memory_retriever import MemoryRetriever

retriever = MemoryRetriever()

active_query = {"confusion": 0.3, "focus": 0.3, "hope": 0.3}

results = retriever.retrieve_by_context(active_query, top_k=3)

print("\n=== TOP K RETRIEVAL RESULTS ===")
for i, res in enumerate(results, start=1):
    print(
        f"Rank {i}: "
        f"ID {res['turn_index']} | "
        f"Trigger: {res['trigger']} | "
        f"Strength: {res['strength']:.4f}"
    )

print("\n=== RAW TELEMETRY CANDIDATE POOL ===")
for entry in retriever.last_raw_candidates:
    print(
        f"ID: {entry['memory_id']} | "
        f"Final: {entry['score']:.4f} | "
        f"Trigger: {entry.get('trigger_cosine', 0.0):.4f} | "
        f"State: {entry.get('state_cosine', 0.0):.4f}"
    )
