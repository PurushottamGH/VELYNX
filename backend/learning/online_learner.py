from __future__ import annotations

import logging

from learning import feedback_loop, gap_tracker, source_trust
from learning.failure_diagnosis import diagnose_failure
from learning.living_constitution import record_rule
from learning.permanence import confidence, reinforce_fact, weaken_fact
from learning.rule_deriver import derive_rule_from_failure
from learning.strategy_optimizer import classify_query, detect_strategy, learn_strategy
from memory.vector_store import remember_interaction

logger = logging.getLogger("uvicorn")


def _iter_sources(meta: dict) -> list[str]:
    raw_sources = meta.get('sources') or []
    normalized: list[str] = []
    for item in raw_sources:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict):
            source = item.get('source') or item.get('domain')
            if source:
                normalized.append(str(source))
    return normalized


def learn_from_feedback(query: str, rating: int, meta: dict | None = None) -> dict:
    meta = meta or {}
    feedback_loop.record_feedback(query, rating, meta=meta)

    cognitive_layer = meta.get('cognitive_layer') or meta.get('layer')

    if rating < 0:
        gap_tracker.record_gap(query, 'User rated answer negatively')

    sources = _iter_sources(meta)
    for source in sources:
        source_trust.update_source_trust(source, 0.05 if rating > 0 else -0.05)

    query_type = classify_query(query)
    strategy = meta.get('strategy') or detect_strategy(query, meta.get('weights') or {})
    learning_context = {
        'answer': meta.get('answer'),
        'confidence': meta.get('confidence'),
        'source_count': meta.get('source_count'),
        'gap_count': meta.get('gap_count'),
        'contradiction_count': meta.get('contradiction_count'),
        'source_domains': meta.get('source_domains') or [],
        'sources': meta.get('sources') or [],
    }

    if rating > 0:
        reinforce_fact(query, source=sources[0] if sources else None, layer=cognitive_layer)
        remember_interaction(
            query,
            str(meta.get('answer') or query),
            confidence=str(meta.get('confidence') or 'PROBABLE'),
            source=sources[0] if sources else None,
            tags=[query_type, strategy, 'feedback'] + ([str(cognitive_layer)] if cognitive_layer else []),
            weight=0.35,
            kind='feedback',
        )
        strategy_score = learn_strategy(query, strategy, rating, layer=cognitive_layer)
        return {
            'status': 'ok',
            'query_type': query_type,
            'strategy': strategy,
            'strategy_score': strategy_score[1],
            'confidence': confidence(query, layer=cognitive_layer),
            'learning': {
                'learning_context': learning_context,
                'cognitive_layer': cognitive_layer,
            },
            'learning_context': learning_context,
            'cognitive_layer': cognitive_layer,
        }

    weaken_fact(query, source=sources[0] if sources else None, layer=cognitive_layer)
    failure = diagnose_failure(query, rating, meta=meta)
    rule = derive_rule_from_failure(failure, query=query, meta=meta)
    stored_rule = record_rule(rule)
    strategy_score = learn_strategy(query, strategy, rating, layer=cognitive_layer)
    return {
        'status': 'ok',
        'query_type': query_type,
        'strategy': strategy,
        'strategy_score': strategy_score[1],
        'learning': {
            'failure': failure,
            'rule': stored_rule,
            'learning_context': learning_context,
            'cognitive_layer': cognitive_layer,
        },
        'failure': failure,
        'rule': stored_rule,
        'confidence': confidence(query, layer=cognitive_layer),
        'learning_context': learning_context,
        'cognitive_layer': cognitive_layer,
    }


async def persist_learning_to_db(
    query: str,
    rating: int,
    meta: dict,
    result: dict,
) -> None:
    """Persist learning state to PostgreSQL (Phase 4 dual-write).

    Call this after learn_from_feedback() to sync state to the database.
    Wrapped in try/except for graceful degradation.
    """
    try:
        from app.db_bridge import persist_feedback, persist_source_trust, persist_permanence, persist_learned_rule

        # Persist feedback
        await persist_feedback(
            query=query,
            answer=str(meta.get("answer", "")),
            rating=rating,
            correction=meta.get("correction"),
        )

        # Persist source trust updates
        sources = _iter_sources(meta)
        for source in sources:
            await persist_source_trust(source, 0.05 if rating > 0 else -0.05)

        # Persist permanence updates
        cognitive_layer = meta.get("cognitive_layer") or meta.get("layer")
        if rating > 0:
            await persist_permanence(query, 0.05, source=sources[0] if sources else None)
        else:
            await persist_permanence(query, -0.1, source=sources[0] if sources else None)

        # Persist learned rule (if negative feedback produced one)
        if result.get("rule"):
            rule = result["rule"]
            await persist_learned_rule(
                title=rule.get("title", "Unnamed rule"),
                body=rule.get("body", ""),
                domains=rule.get("domains"),
                risk=rule.get("risk", "low"),
                status=rule.get("status", "active"),
                cognitive_layer=rule.get("cognitive_layer"),
            )
    except Exception as exc:
        logger.debug("DB learning persist skipped: %s", exc)
