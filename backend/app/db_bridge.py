"""Database bridge — async helpers for persisting cognitive state to PostgreSQL.

Each function wraps a repository call with graceful degradation.
If the database is unavailable, the call is silently skipped.
"""
from __future__ import annotations

import logging
from typing import Any

from database.runtime_state import runtime_state
from database.engine import async_session

logger = logging.getLogger("uvicorn")


async def persist_episode(
    prompt: str,
    answer: str,
    confidence: str = "UNKNOWN",
    source: str | None = None,
    tags: list[str] | None = None,
    kind: str = "learned",
    importance: float = 0.5,
) -> None:
    """Persist an episode to PostgreSQL."""
    try:
        async with async_session() as session:
            repos = runtime_state.repos(session)
            await repos["episode"].upsert(
                prompt=prompt,
                answer=answer,
                confidence=confidence,
                source=source,
                tags=tags,
                kind=kind,
                importance=importance,
            )
    except Exception as exc:
        logger.warning("DB episode persist skipped: %s", exc)


async def persist_reflection(
    query: str,
    answer: str,
    reflection_result: Any,
) -> None:
    """Persist a reflection result to PostgreSQL."""
    try:
        async with async_session() as session:
            repos = runtime_state.repos(session)
            audit = reflection_result.audit
            conf = reflection_result.confidence_estimate
            await repos["reflection"].store(
                query=query,
                answer=answer,
                reasoning_quality=reflection_result.reasoning_quality,
                hallucination_risk=audit.hallucination_risk,
                audit_issues=[
                    {"category": i.category, "severity": i.severity, "description": i.description}
                    for i in audit.issues
                ],
                improvements=[
                    {"category": s.category, "priority": s.priority, "description": s.description}
                    for s in reflection_result.improvements
                ],
                confidence_estimate={
                    "initial": conf.initial,
                    "calibrated": conf.calibrated,
                    "delta": conf.calibration_delta,
                    "rationale": conf.rationale,
                },
            )
    except Exception as exc:
        logger.warning("DB reflection persist skipped: %s", exc)


async def persist_context_snapshot(
    session_id: str | None,
    snapshot_data: dict,
) -> None:
    """Persist a context snapshot to PostgreSQL."""
    try:
        async with async_session() as session:
            repos = runtime_state.repos(session)
            from database.models import ContextSnapshotModel
            obj = ContextSnapshotModel(
                session_id=session_id,
                snapshot=snapshot_data,
            )
            session.add(obj)
            await session.commit()
    except Exception as exc:
        logger.warning("DB context snapshot persist skipped: %s", exc)


async def persist_feedback(
    query: str,
    answer: str,
    rating: int,
    correction: str | None = None,
) -> None:
    """Persist user feedback to PostgreSQL."""
    try:
        async with async_session() as session:
            repos = runtime_state.repos(session)
            await repos["feedback"].append(
                query=query,
                answer=answer,
                rating=rating,
                correction=correction,
            )
    except Exception as exc:
        logger.warning("DB feedback persist skipped: %s", exc)


async def persist_source_trust(source_name: str, delta: float) -> None:
    """Persist source trust score update to PostgreSQL."""
    try:
        async with async_session() as session:
            repos = runtime_state.repos(session)
            await repos["source_trust"].update(source_name, delta)
    except Exception as exc:
        logger.warning("DB source trust persist skipped: %s", exc)


async def persist_permanence(
    fact: str,
    score_delta: float,
    source: str | None = None,
) -> None:
    """Persist a permanence score update to PostgreSQL."""
    try:
        async with async_session() as session:
            repos = runtime_state.repos(session)
            await repos["permanence"].update_score(fact, score_delta, source)
    except Exception as exc:
        logger.warning("DB permanence persist skipped: %s", exc)


async def persist_learned_rule(
    title: str,
    body: str,
    domains: list[str] | None = None,
    risk: str = "low",
    status: str = "active",
    cognitive_layer: str | None = None,
) -> None:
    """Persist a learned rule to PostgreSQL."""
    try:
        async with async_session() as session:
            repos = runtime_state.repos(session)
            await repos["learned_rule"].create(
                title=title,
                body=body,
                domains=domains,
                risk=risk,
                status=status,
                cognitive_layer=cognitive_layer,
            )
    except Exception as exc:
        logger.warning("DB learned rule persist skipped: %s", exc)


async def persist_goal(
    description: str,
    priority: int = 5,
    parent_id: str | None = None,
) -> str | None:
    """Persist a goal to PostgreSQL. Returns goal ID or None on failure."""
    try:
        async with async_session() as session:
            repos = runtime_state.repos(session)
            goal = await repos["goal"].create(description, priority, parent_id)
            return goal.id
    except Exception as exc:
        logger.warning("DB goal persist skipped: %s", exc)
        return None


async def persist_goal_status(goal_id: str, status: str) -> None:
    """Update a goal's status in PostgreSQL."""
    try:
        async with async_session() as session:
            repos = runtime_state.repos(session)
            await repos["goal"].update_status(goal_id, status)
    except Exception as exc:
        logger.warning("DB goal status update skipped: %s", exc)


async def persist_plan_snapshot(plan_id: str, plan_data: dict) -> None:
    """Persist a plan snapshot to Redis."""
    try:
        from database.redis_cache import redis_cache
        await redis_cache.set(f"plan:{plan_id}", plan_data, ttl=86400)
    except Exception as exc:
        logger.warning("Plan Redis persist skipped: %s", exc)
