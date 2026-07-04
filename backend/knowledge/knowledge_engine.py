import sys
from pathlib import Path

# Ensure backend/ is on sys.path for scenario_engine imports
_backend_root = str(Path(__file__).parent.parent.resolve())
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from backend.cognition.scenario_engine import parse_scenario
from backend.knowledge.bridge import get_domain_concepts
from backend.knowledge.knowledge_graph import KnowledgeGraph
from backend.soul.soul_graph import get_tensions, load_soul


TENSION_PAIRS = {
    ("grief", "hope"): ("Temporal pull", "Grief looks back; hope looks forward", 0.7),
    ("betrayal", "trust"): ("Trust collapse", "Trust requires reliability; betrayal destroys it", 0.9),
    ("betrayal", "love"): ("Trust collapse", "Love requires trust; betrayal destroys it", 0.9),
    ("courage", "fear"): ("Coexistence paradox", "Courage is not the absence of fear", 0.6),
    ("pride", "regret"): ("Self-evaluation split", "Pride affirms; regret questions the same act", 0.7),
    ("anger", "forgiveness"): ("Release conflict", "Forgiveness cannot begin while anger fully possesses", 0.8),
    ("depression", "hope"): ("Vitality inversion", "Depression starves hope; hope requires forward motion", 0.9),
    ("shame", "pride"): ("Self-worth collapse", "Shame attacks the self; pride affirms it", 0.8),
    ("stagnation", "resilience"): ("Flow inversion", "Stagnation drains; resilience moves forward", 0.7),
    ("trust", "betrayal"): ("Trust collapse", "Trust requires reliability; betrayal destroys it", 0.9),
    ("hope", "depression"): ("Vitality inversion", "Hope requires forward motion; depression starves it", 0.9),
    ("forgiveness", "anger"): ("Release conflict", "Forgiveness cannot begin while anger fully possesses", 0.8),
    ("fear", "courage"): ("Coexistence paradox", "Courage is not the absence of fear", 0.6),
    ("regret", "pride"): ("Self-evaluation split", "Regret questions; pride affirms the same act", 0.7),
}


def _detect_dissonance(activated_concepts: list[str]) -> list[tuple[str, str]]:
    """Detect opposing concept pairs among activated soul concepts."""
    dissonance_pairs = []
    seen = set()
    concept_set = {c.lower() for c in activated_concepts}

    for (a, b), (name, desc, severity) in TENSION_PAIRS.items():
        key = tuple(sorted([a, b]))
        if a in concept_set and b in concept_set and key not in seen:
            seen.add(key)
            dissonance_pairs.append(key)

    if not dissonance_pairs:
        try:
            soul = load_soul()
            for concept in activated_concepts:
                tensions = get_tensions(concept)
                for t in tensions:
                    other = t["b"] if t["a"] == concept else t["a"]
                    if other.lower() in concept_set:
                        pair = tuple(sorted([concept.lower(), other.lower()]))
                        if pair not in seen:
                            seen.add(pair)
                            dissonance_pairs.append(pair)
        except Exception:
            pass

    return dissonance_pairs


def _build_domain_arc(domain_concepts: list[str], kg: KnowledgeGraph) -> str:
    if not domain_concepts:
        return ""
    related = []
    seen = set()
    for dc in domain_concepts:
        for rel in kg.get_related(dc):
            if rel["source"] == dc and rel["target"] in domain_concepts:
                key = (dc, rel["relation"], rel["target"])
                if key not in seen:
                    seen.add(key)
                    related.append(f"{dc} {rel['relation']} {rel['target']}")
    return "; ".join(related)


def _build_unified_arc(soul_arc: str, bridge_connections: list[dict], domain_arc: str) -> str:
    parts = []
    if soul_arc:
        parts.append(soul_arc)
    bridges_str = ", ".join(f"{bc['soul']}→{bc['domain']}" for bc in bridge_connections)
    if bridges_str:
        parts.append(f"Bridges: {bridges_str}")
    if domain_arc:
        parts.append(f"Domain: {domain_arc}")
    return " | ".join(parts)


def cross_query(query: str) -> dict:
    kg = KnowledgeGraph()
    kg.build()

    soul_result = parse_scenario(query)

    domain_concepts = []
    bridge_connections = []
    seen_dc = set()

    if soul_result.get("domain_route") == "structural":
        domain_concepts = list(soul_result.get("domain_hits", {}).keys())
        for dc in domain_concepts:
            seen_dc.add(dc)
        bridge_connections = []
    else:
        for sc in soul_result.get("concepts", []):
            dcs = get_domain_concepts(sc)
            for dc in dcs:
                bridge_connections.append({"soul": sc, "domain": dc})
                if dc not in seen_dc:
                    seen_dc.add(dc)
                    domain_concepts.append(dc)

    domain_arc = _build_domain_arc(domain_concepts, kg)
    unified_arc = _build_unified_arc(
        soul_result.get("arc", ""), bridge_connections, domain_arc
    )

    concepts = soul_result.get("concepts", [])
    dissonance_pairs = _detect_dissonance(concepts)
    dissonance = []
    for a, b in dissonance_pairs:
        name, desc, _severity = TENSION_PAIRS.get(
            (a, b), TENSION_PAIRS.get((b, a), (f"{a.title()} vs {b.title()}", f"The mind holds both {a} and {b} simultaneously", 0.5))
        )
        dissonance.append({
            "concept_a": a,
            "concept_b": b,
            "name": name,
            "description": desc,
        })

    return {
        "query": query,
        "soul_result": soul_result,
        "domain_concepts": domain_concepts,
        "bridge_connections": bridge_connections,
        "domain_arc": domain_arc,
        "unified_arc": unified_arc,
        "cross_domain": len(domain_concepts) > 0,
        "dissonance_detected": dissonance if dissonance else None,
    }
