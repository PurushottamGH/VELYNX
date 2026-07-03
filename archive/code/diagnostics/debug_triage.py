"""Debug all failing parse_scenario queries."""
import sys, json
sys.path.insert(0, r"backend")
from unittest.mock import patch
patch("cognition.embed_index.semantic_lookup", return_value=[]).start()
from cognition.scenario_engine import parse_scenario

queries = [
    "I am failing at everything and I doubt myself",
    "I feel like a failure and I do not know who I am anymore",
    "I am useless, a total disappointment, and I lost faith in myself",
    "the deployment failed and the server is down",
    "the pipeline crashed and the api is broken",
    "server failure on the primary node",
    "the database is the bottleneck",
    "I lost everything and felt nothing",
    "I failed at my deployment and I feel like a failure",
    "I doubt myself",
]
for q in queries:
    r = parse_scenario(q)
    print(f"=== QUERY: {q}")
    for k, v in sorted(r.items()):
        print(f"  {k}: {json.dumps(v, default=str)}")
    print()
