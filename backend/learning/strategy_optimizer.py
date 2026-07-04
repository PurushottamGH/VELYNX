from __future__ import annotations

import re

from backend.learning.permanence import best_strategy, record_strategy


QUERY_TYPES = ['scientific', 'historical', 'philosophical', 'human', 'practical']


def classify_query(query: str) -> str:
    text = query.lower()
    if any(word in text for word in ['study', 'research', 'evidence', 'medicine', 'biology', 'physics', 'science']):
        return 'scientific'
    if any(word in text for word in ['history', 'timeline', 'origin', 'year', 'era']):
        return 'historical'
    if any(word in text for word in ['meaning', 'truth', 'ethics', 'consciousness', 'mind']):
        return 'philosophical'
    if any(word in text for word in ['people', 'behavior', 'community', 'emotion', 'society']):
        return 'human'
    return 'practical'


def detect_strategy(query: str, weights: dict | None = None) -> str:
    text = query.lower()
    if any(word in text for word in ['recent', 'latest', 'current', 'updated', 'today']):
        return 'recent_sources'
    if any(word in text for word in ['compare', 'contradiction', 'why', 'debate', 'conflict']):
        return 'contradiction_first'
    if any(word in text for word in ['how', 'steps', 'build', 'implement', 'workflow']):
        return 'broad_retrieval'
    if weights and weights.get('scientific', 0) > 0.65:
        return 'recent_sources'
    return 'broad_retrieval'


def apply_learned_preferences(query: str, weights: dict, layer: str | None = None) -> tuple[str, dict]:
    query_type = classify_query(query)
    preferred = best_strategy(query_type, layer=layer)
    strategy = preferred or detect_strategy(query, weights)
    adjusted = dict(weights)

    if strategy == 'recent_sources':
        adjusted['scientific'] = round(min(1.0, adjusted.get('scientific', 0.0) + 0.1), 2)
        adjusted['historical'] = round(min(1.0, adjusted.get('historical', 0.0) + 0.08), 2)
    elif strategy == 'contradiction_first':
        adjusted['philosophical'] = round(min(1.0, adjusted.get('philosophical', 0.0) + 0.1), 2)
        adjusted['human'] = round(min(1.0, adjusted.get('human', 0.0) + 0.05), 2)
    else:
        adjusted['practical'] = round(min(1.0, adjusted.get('practical', 0.0) + 0.05), 2)

    return strategy, adjusted


def learn_strategy(query: str, strategy: str, outcome: int, layer: str | None = None) -> tuple[str, float]:
    query_type = classify_query(query)
    delta = 0.05 if outcome > 0 else -0.1
    score = record_strategy(query_type, strategy, delta, layer=layer)
    return query_type, score
