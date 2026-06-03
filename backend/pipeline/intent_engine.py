from __future__ import annotations

import re

from pipeline.constitution_loader import load_constitution
from learning.curriculum import detect_cognitive_layer
from learning.strategy_optimizer import apply_learned_preferences

DIMENSIONS = ["scientific", "historical", "philosophical", "human", "practical"]
DOMAIN_KEYWORDS = {
    "science": [
        "study",
        "research",
        "evidence",
        "data",
        "experiment",
        "biology",
        "physics",
        "chemistry",
        "medicine",
        "neuroscience",
        "climate",
        "genetics",
        "astronomy",
    ],
    "history": [
        "history",
        "origin",
        "evolution",
        "timeline",
        "ancient",
        "year",
        "era",
        "century",
        "war",
        "empire",
        "revolution",
    ],
    "philosophy": [
        "meaning",
        "ethics",
        "existence",
        "truth",
        "consciousness",
        "mind",
        "identity",
        "free will",
        "morality",
    ],
    "human": [
        "people",
        "behavior",
        "motivation",
        "society",
        "culture",
        "psychology",
        "emotion",
        "community",
        "policy",
    ],
    "practical": [
        "how",
        "use",
        "apply",
        "steps",
        "guide",
        "best way",
        "workflow",
        "tips",
        "implementation",
    ],
}


_STOP_WORDS = frozenset({
    "what", "is", "are", "was", "were", "the", "a", "an", "and", "or", "but",
    "how", "does", "do", "did", "will", "would", "could", "should", "can",
    "this", "that", "these", "those", "with", "from", "about", "into",
    "tell", "explain", "describe", "help", "please", "your", "you", "me",
})


def _keywords(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [t for t in tokens if len(t) > 2 and t not in _STOP_WORDS]


def _classify_domains(tokens: list[str]) -> list[str]:
    matches: list[str] = []
    token_set = set(tokens)
    for domain, words in DOMAIN_KEYWORDS.items():
        if any(word in token_set for word in words):
            matches.append(domain)
    return matches


def _extract_entities(text: str) -> dict:
    entities: dict = {"numbers": [], "years": [], "proper_nouns": [], "quoted": []}

    entities["numbers"] = re.findall(r"\b\d+(?:\.\d+)?\b", text)
    entities["years"] = re.findall(r"\b(18|19|20)\d{2}\b", text)
    entities["quoted"] = re.findall(r"\"([^\"]+)\"", text)

    tokens = re.findall(r"\b[A-Z][a-zA-Z0-9]+\b", text)
    entities["proper_nouns"] = list(dict.fromkeys(tokens))
    return entities


def _build_dimension_queries(query: str, tokens: list[str]) -> dict:
    focus = " ".join(tokens[:8]) if tokens else query
    return {
        "scientific": f"Scientific evidence and data about {focus}",
        "historical": f"Historical background and timeline of {focus}",
        "philosophical": f"Philosophical meaning and implications of {focus}",
        "human": f"Human motivation and societal context of {focus}",
        "practical": f"Practical steps and applications for {focus}",
    }


def _score_dimensions(tokens: list[str], domains: list[str]) -> dict:
    scores = {dimension: 0.3 for dimension in DIMENSIONS}
    for domain in domains:
        if domain == "science":
            scores["scientific"] += 0.4
        if domain == "history":
            scores["historical"] += 0.4
        if domain == "philosophy":
            scores["philosophical"] += 0.4
        if domain == "human":
            scores["human"] += 0.4
        if domain == "practical":
            scores["practical"] += 0.4

    if any(token in {"how", "steps", "guide", "build"} for token in tokens):
        scores["practical"] += 0.2
    if any(token in {"why", "meaning", "ethics"} for token in tokens):
        scores["philosophical"] += 0.2
    if any(token in {"when", "history", "timeline"} for token in tokens):
        scores["historical"] += 0.2

    return {key: round(min(value, 1.0), 2) for key, value in scores.items()}


def decompose_query(query: str) -> dict:
    """Decompose a query into multiple dimensions using deterministic rules."""
    cognitive_layer = detect_cognitive_layer(query)
    constitution = load_constitution(cognitive_layer=cognitive_layer)
    tokens = _keywords(query)
    domains = _classify_domains(tokens)
    dimensions = _build_dimension_queries(query, tokens)
    entities = _extract_entities(query)
    weights = _score_dimensions(tokens, domains)
    strategy, weights = apply_learned_preferences(query, weights, layer=cognitive_layer)
    return {
        "query": query,
        "constitution": constitution,
        "dimensions": dimensions,
        "domains": domains,
        "entities": entities,
        "weights": weights,
        "strategy": strategy,
        "cognitive_layer": cognitive_layer,
    }
