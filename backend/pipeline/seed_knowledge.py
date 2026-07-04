from __future__ import annotations

import hashlib
from dataclasses import dataclass

from backend.learning.curriculum import resolve_foundation_seed_answer


@dataclass(frozen=True)
class SeedKnowledge:
    key: str
    answer: str
    tone: str = "human"


SEED_KNOWLEDGE: dict[str, SeedKnowledge] = {
    "abcb": SeedKnowledge(
        key="abcb",
        answer="ABCB is VELYNX's bootstrap loop: Ask, Build, Check, Backfill.",
    ),
    "123": SeedKnowledge(
        key="123",
        answer="123 is VELYNX's starter sequence: 1) understand, 2) verify, 3) respond.",
    ),
}


# Domain ontology constraints to prevent cross-domain contamination
def _domain_matches(query: str, answer: str) -> bool:
    """Reject answers where the domain clearly conflicts with the query."""
    q = query.lower()
    a = answer.lower()

    # Geographical terms vs mathematical terms
    geo_words = {"france", "paris", "country", "capital", "continent", "europe", "spain", "germany"}
    math_words = {"pi", "circle", "ratio", "equation", "angle", "degree", "radian", "mathematical"}
    if any(w in q for w in geo_words) and any(w in a for w in math_words):
        return False
    if any(w in q for w in math_words) and any(w in a for w in geo_words):
        return False

    # Chemistry vs Computer Science
    chem_words = {"ice", "water", "molecule", "chemical", "acid", "bond", "react", "temperature"}
    cs_words = {"o(n)", "algorithm", "runtime", "complexity", "big o", "linear time"}
    if any(w in q for w in chem_words) and any(w in a for w in cs_words):
        return False

    # CS vs Biology
    cs_query = {"algorithm", "code", "program", "sort", "search", "runtime"}
    bio_words = {"cell", "dna", "protein", "organism"}
    if any(w in q for w in cs_query) and any(w in a for w in bio_words):
        return False

    return True


def resolve_seed_answer(text: str) -> dict | None:
    foundation = resolve_foundation_seed_answer(text)
    if foundation is not None:
        if not _domain_matches(text, foundation.get("answer", "")):
            return None
        return foundation

    # Match any query that contains a seed key as a word or phrase
    lowered = text.lower().strip()
    matches = [seed for key, seed in SEED_KNOWLEDGE.items() if key in lowered]
    if not matches:
        return None

    answer = " ".join(seed.answer for seed in matches)
    if not _domain_matches(text, answer):
        return None

    return {
        "answer": answer,
        "confidence": "CERTAIN",
        "citations": [],
        "gaps": [],
        "tone": matches[0].tone,
        "seed_keys": [seed.key for seed in matches],
    }


def seed_id_for_topic(topic: str) -> str:
    """Generate a collision-resistant seed ID for a topic using SHA256."""
    return hashlib.sha256(topic.strip().lower().encode()).hexdigest()[:16]
