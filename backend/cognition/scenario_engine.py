"""
VELYNX Scenario Engine — parses narrative queries into concept activations + emotional arcs.
Layer 3: No LLM call for scenario parsing. Pure local inference.
"""

import sys
from pathlib import Path

# Ensure backend/ is on sys.path so that `from cognition.xxx` and `from soul.yyy`
# resolve correctly regardless of which entry point calls this module.
_backend_root = str(Path(__file__).parent.parent.resolve())
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from backend.cognition.metacog import reflect


def parse_scenario(query: str) -> dict:
    """
    Phase 40: Resonance-only routing. Legacy cascade removed.

    Parse a narrative query into:
    - activated concepts
    - emotional arc (ordered sequence)
    - query type (direct / relational / scenario)
    - confidence hint
    """
    from soul.soul_graph import resonate
    concepts = resonate(query)

    if concepts and max(concepts.values()) > 0.35:
        return {
            "domain_route": "personal",
            "concepts": list(concepts.keys()),
            "scores": concepts,
            "arc": "",
            "query_type": "scenario",
        }

    return {
        "domain_route": "personal",
        "concepts": [],
        "scores": {},
        "arc": "",
        "query_type": "direct",
    }


from backend.cognition.metacog import reflect  # noqa: E402,F401 — metacognitive wrapper; import at bottom avoids circular dep
