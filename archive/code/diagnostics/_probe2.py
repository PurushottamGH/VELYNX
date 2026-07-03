import os
os.environ.setdefault("VELYNX_TEST_MODE", "1")

from backend.pipeline import intent_engine
from backend.pipeline.reasoning_wiring import extract_query_concepts

q = "Does a Tesla Model 3 have wheels?"
intent = intent_engine.decompose_query(q)
print("intent keys:", list(intent.keys()))
print("entities:", intent.get("entities"))

concepts = extract_query_concepts(q, intent, [])
print("query_concepts:", concepts)
