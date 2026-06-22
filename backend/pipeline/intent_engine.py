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


# A run of capitalised tokens (optionally joined by a connective like "of"/"the"
# inside the span, e.g. "Bank of America") is ONE entity, not several. The
# capture is anchored on a capitalised head token and greedily absorbs adjacent
# capitalised tokens — this is what keeps "Driftwood OS" together instead of
# splitting it into ["Driftwood", "OS"] and letting the trailing token win as the
# "most specific" concept (the Interaction #21 truncation bug, where "Driftwood
# OS" collapsed to the entity "os").
_PROPER_NOUN_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*\b")
# Short connective words allowed to sit *between* two capitalised tokens of one
# named entity without breaking the phrase ("Bank of America", "Game of Thrones").
# A trailing/leading connective is never kept — only one that bridges two
# capitalised tokens.
_PROPER_NOUN_INFIX = frozenset({"of", "the", "and", "for", "de", "van", "von", "da"})


def _group_proper_noun_phrases(text: str) -> list[str]:
    """Group consecutive capitalised tokens into multi-word named entities.

    "Who created Driftwood OS?"        -> ["Driftwood OS"]
    "Where is Bank of America located?" -> ["Bank of America"]
    "Ada Lovelace met Charles Babbage." -> ["Ada Lovelace", "Charles Babbage"]

    Adjacent capitalised tokens (allowing a single lowercase connective like
    "of"/"the" between two of them) are merged. A lone capitalised word still
    comes back as a one-element phrase, so single-entity queries are unchanged.
    The sentence-initial word is intentionally NOT special-cased away here —
    interrogatives ("Who", "What") are stripped downstream by the query
    drop-term filter, and over-keeping them is harmless because they are not
    stored entities.
    """
    matches = list(_PROPER_NOUN_RE.finditer(text))
    phrases: list[str] = []
    current: list[str] = []
    last_end = -1
    for m in matches:
        word = m.group(0)
        gap = text[last_end:m.start()] if last_end >= 0 else ""
        # Continue the current phrase when the previous capitalised token is
        # separated only by whitespace, or by a single allowed connective word.
        bridges = gap.strip().lower()
        if current and (bridges == "" or bridges in _PROPER_NOUN_INFIX):
            if bridges:
                current.append(gap.strip())
            current.append(word)
        else:
            if current:
                phrases.append(" ".join(current))
            current = [word]
        last_end = m.end()
    if current:
        phrases.append(" ".join(current))
    # Trim any phrase that is purely a connective leftover, and de-dup.
    cleaned = [p.strip() for p in phrases if p.strip()]
    return list(dict.fromkeys(cleaned))


def _extract_entities(text: str) -> dict:
    entities: dict = {
        "numbers": [],
        "years": [],
        "proper_nouns": [],
        "proper_noun_phrases": [],
        "quoted": [],
    }

    entities["numbers"] = re.findall(r"\b\d+(?:\.\d+)?\b", text)
    entities["years"] = re.findall(r"\b(18|19|20)\d{2}\b", text)
    entities["quoted"] = re.findall(r"\"([^\"]+)\"", text)

    # Singletons (unchanged — kept for backward compatibility with any consumer
    # that reads proper_nouns directly).
    tokens = re.findall(r"\b[A-Z][a-zA-Z0-9]+\b", text)
    entities["proper_nouns"] = list(dict.fromkeys(tokens))

    # Multi-word grouping — the truncation fix. "Driftwood OS" stays one entity.
    entities["proper_noun_phrases"] = _group_proper_noun_phrases(text)
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
