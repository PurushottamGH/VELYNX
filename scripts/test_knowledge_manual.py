import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from knowledge.knowledge_engine import cross_query

result = cross_query("I keep failing at this and I'm starting to doubt myself")
print("Soul concepts:", result["soul_result"]["concepts"])
print("Domain concepts:", result["domain_concepts"])
print("Bridge connections:", result["bridge_connections"])
print("Domain arc:", result["domain_arc"])
print("Unified arc:", result["unified_arc"])
print("Cross domain:", result["cross_domain"])
