import json
from backend.memory.memory_retriever import MemoryRetriever

retriever = MemoryRetriever()

# Mimic the perception output
active_query = {"confusion": 0.3, "focus": 0.3, "hope": 0.3}

# Fetch the top 3 matches
results = retriever.retrieve_by_context(active_query, top_k=3)

print("\n=== TOP K RETRIEVAL RESULTS ===")
for i, res in enumerate(results):
    print(
        f"Rank {i+1}: ID {res['turn_index']} | Trigger: '{res['trigger']}' | Strength: {res['strength']}"
    )

print("\n=== RAW TELEMETRY CANDIDATE POOL ===")
for entry in retriever.last_raw_candidates:
    print(f"ID: {entry['memory_id']} | Blended Score: {entry['score']:.4f}")
