"""Runtime state manager — orchestrates all persistent state."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_engine, async_session
from database.models import Base
from database.repositories import (
    SessionRepository,
    EpisodeRepository,
    ConceptRepository,
    ReflectionRepository,
    GoalRepository,
    PermanenceRepository,
    SourceTrustRepository,
    FeedbackRepository,
    LearnedRuleRepository,
    ContextSnapshotRepository,
)
from database.redis_cache import redis_cache

logger = logging.getLogger("uvicorn")


class RuntimeStateManager:
    """Unified access to all persistent state."""

    def __init__(self) -> None:
        self._initialized = False

    async def initialize(self) -> None:
        """Create tables if they don't exist (dev convenience)."""
        if self._initialized:
            return
        try:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self._initialized = True
            logger.info("Database tables initialized")
        except Exception as exc:
            logger.warning("Database init failed (will use file fallback): %s", exc)

    def repos(self, session: AsyncSession):
        """Create all repositories for a session."""
        return {
            "session": SessionRepository(session),
            "episode": EpisodeRepository(session),
            "concept": ConceptRepository(session),
            "reflection": ReflectionRepository(session),
            "goal": GoalRepository(session),
            "permanence": PermanenceRepository(session),
            "source_trust": SourceTrustRepository(session),
            "feedback": FeedbackRepository(session),
            "learned_rule": LearnedRuleRepository(session),
            "context_snapshot": ContextSnapshotRepository(session),
        }

    async def checkpoint(self, session_id: str | None = None) -> dict:
        """Snapshot full cognitive state: episodes, reflections, goals, rules, trust, permanence."""
        async with async_session() as session:
            repos = self.repos(session)

            # Gather top episodes (by importance)
            top_episodes = await repos["episode"].get_top(limit=5)
            episode_data = [
                {"id": e.id, "prompt": e.prompt[:100], "confidence": e.confidence, "source": e.source}
                for e in top_episodes
            ]

            # Gather recent reflections
            recent_reflections = await repos["reflection"].get_history(limit=5)
            reflection_data = [
                {"id": r.id, "query": r.query[:100], "reasoning_quality": r.reasoning_quality}
                for r in recent_reflections
            ]

            # Gather active goals
            active_goals = await repos["goal"].get_active()
            goal_data = [
                {"id": g.id, "description": g.description[:100], "priority": g.priority}
                for g in active_goals
            ]

            # Gather active rules
            active_rules = await repos["learned_rule"].get_active()
            rule_data = [
                {"id": r.id, "title": r.title, "risk": r.risk, "status": r.status}
                for r in active_rules
            ]

            # Gather source trust summary
            all_trust = await repos["source_trust"].get_all()
            trust_summary = {t.source_name: t.trust_score for t in all_trust[:10]}

            # Gather permanence summary
            all_permanence = await repos["permanence"].get_all()
            permanence_summary = [
                {"fact": p.fact[:80], "score": p.score} for p in all_permanence[:10]
            ]

            snapshot = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": session_id,
                "episode_count": await repos["episode"].count(),
                "recent_episodes": episode_data,
                "recent_reflections": reflection_data,
                "active_goals": goal_data,
                "active_rules": rule_data,
                "source_trust_summary": trust_summary,
                "permanence_summary": permanence_summary,
                "recent_feedback_count": len(await repos["feedback"].get_recent(limit=10)),
            }

            # Persist to PostgreSQL
            try:
                await repos["context_snapshot"].store(
                    session_id=session_id,
                    snapshot=snapshot,
                )
            except Exception as exc:
                logger.debug("Context snapshot store skipped: %s", exc)

            await redis_cache.set("checkpoint:latest", snapshot, ttl=86400)
            return snapshot

    async def restore(self, checkpoint_id: str = "latest") -> dict | None:
        """Retrieve a checkpoint snapshot (Redis first, then DB fallback)."""
        cached = await redis_cache.get(f"checkpoint:{checkpoint_id}")
        if cached:
            return cached

        # DB fallback
        try:
            async with async_session() as session:
                repos = self.repos(session)
                snapshots = await repos["context_snapshot"].get_recent(limit=1)
                if snapshots:
                    return snapshots[0].snapshot
        except Exception:
            pass
        return None

    async def get_cognitive_summary(self) -> dict:
        """Quick overview of current cognitive state."""
        async with async_session() as session:
            repos = self.repos(session)

            # Get counts
            episode_count = await repos["episode"].count()
            active_goals = await repos["goal"].get_active()
            active_rules = await repos["learned_rule"].get_active()
            recent_reflections = await repos["reflection"].get_history(limit=5)
            recent_feedback = await repos["feedback"].get_recent(limit=5)

            # Get trust summary
            all_trust = await repos["source_trust"].get_all()
            top_trusted = sorted(all_trust, key=lambda t: t.trust_score, reverse=True)[:5]

            return {
                "episode_count": episode_count,
                "active_goal_count": len(active_goals),
                "active_rule_count": len(active_rules),
                "recent_reflection_count": len(recent_reflections),
                "recent_feedback_count": len(recent_feedback),
                "top_trusted_sources": [
                    {"source": t.source_name, "score": t.trust_score}
                    for t in top_trusted
                ],
                "latest_reasoning_quality": (
                    recent_reflections[0].reasoning_quality
                    if recent_reflections else None
                ),
            }


# Module-level singleton
runtime_state = RuntimeStateManager()
