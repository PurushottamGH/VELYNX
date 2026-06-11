BRIDGE_NODES: dict[str, list[str]] = {
    "curiosity": ["iteration", "inference", "feedback loop"],
    "shame": ["failure", "debugging", "refactoring"],
    "patience": ["iteration", "testing", "optimization"],
    "resilience": ["recovery", "refactoring", "fallback"],
    "planning": ["architecture", "abstraction", "assumption"],
    "trust": ["verification", "testing", "proof"],
    "pain": ["technical debt", "bottleneck", "debugging"],
    "identity": ["architecture", "abstraction", "verification"],
    "courage": ["deployment", "refactoring"],
    "grief": ["legacy code", "technical debt", "entropy", "depreciation"],
    "anger": ["bottleneck", "technical debt", "friction"],
    "hope": ["recovery", "feedback loop"],
    "depression": ["bottleneck", "feedback loop", "inertia", "illiquidity"],
    "loss": ["legacy code", "deprecation", "failure", "entropy", "depreciation"],
    "understanding": ["inference", "abstraction", "proof"],
    "regret": ["technical debt", "assumption"],
    "forgiveness": ["refactoring", "recovery"],
    "stagnation": ["inertia", "illiquidity"],
    "resistance": ["friction"],
}


def get_domain_concepts(soul_concept: str) -> list[str]:
    return BRIDGE_NODES.get(soul_concept, [])


def get_soul_concepts(domain_concept: str) -> list[str]:
    return [s for s, targets in BRIDGE_NODES.items() if domain_concept in targets]


def bridge_exists(soul_concept: str, domain_concept: str) -> bool:
    return domain_concept in BRIDGE_NODES.get(soul_concept, [])
