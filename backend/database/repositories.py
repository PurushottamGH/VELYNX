"""Repository layer — data access for all VELYNX persistent state."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    EpisodeModel,
    ConceptModel,
    ReflectionModel,
    GoalModel,
    SessionModel,
    ContextSnapshotModel,
    PermanenceModel,
    SourceTrustModel,
    FeedbackModel,
    LearnedRuleModel,
    MetacognitionReportModel,
    EvaluationReportModel,
    TrialReportModel,
)


# ── Context Snapshot Repository ─────────────────────────────────

class ContextSnapshotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def store(self, *, session_id: str | None, snapshot: dict) -> ContextSnapshotModel:
        obj = ContextSnapshotModel(session_id=session_id, snapshot=snapshot)
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_recent(self, session_id: str | None = None, limit: int = 10) -> list[ContextSnapshotModel]:
        query = select(ContextSnapshotModel).order_by(ContextSnapshotModel.created_at.desc())
        if session_id:
            query = query.where(ContextSnapshotModel.session_id == session_id)
        query = query.limit(limit)
        result = await self._s.execute(query)
        return list(result.scalars().all())

logger = logging.getLogger("uvicorn")


# ── Session Repository ───────────────────────────────────────────

class SessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(self, metadata: dict | None = None) -> SessionModel:
        obj = SessionModel(metadata_=metadata or {})
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def end_session(self, session_id: str) -> None:
        await self._s.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(ended_at=datetime.now(timezone.utc))
        )
        await self._s.commit()

    async def get_active(self) -> SessionModel | None:
        result = await self._s.execute(
            select(SessionModel).where(SessionModel.ended_at.is_(None)).order_by(SessionModel.started_at.desc()).limit(1)
        )
        return result.scalars().first()


# ── Episode Repository ───────────────────────────────────────────

class EpisodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def upsert(
        self,
        *,
        prompt: str,
        answer: str,
        confidence: str = "UNKNOWN",
        source: str | None = None,
        tags: list[str] | None = None,
        kind: str = "learned",
        importance: float = 0.5,
        embedding: list[float] | None = None,
    ) -> EpisodeModel:
        # Check for existing episode with same prompt+answer
        existing = await self.get_by_content(prompt, answer)
        if existing:
            existing.importance = min(existing.importance + 0.1, 1.0)
            existing.access_count += 1
            existing.updated_at = datetime.now(timezone.utc)
            await self._s.commit()
            return existing

        obj = EpisodeModel(
            prompt=prompt,
            answer=answer,
            confidence=confidence,
            source=source,
            tags=tags or [],
            kind=kind,
            importance=importance,
            embedding=embedding,
        )
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_by_content(self, prompt: str, answer: str) -> EpisodeModel | None:
        result = await self._s.execute(
            select(EpisodeModel)
            .where(EpisodeModel.prompt == prompt, EpisodeModel.answer == answer)
            .limit(1)
        )
        return result.scalars().first()

    async def get_by_id(self, episode_id: str) -> EpisodeModel | None:
        result = await self._s.execute(
            select(EpisodeModel).where(EpisodeModel.id == episode_id)
        )
        return result.scalars().first()

    async def search_by_text(self, query: str, limit: int = 5) -> list[EpisodeModel]:
        """Simple text search (fallback when no embeddings)."""
        result = await self._s.execute(
            select(EpisodeModel)
            .where(
                EpisodeModel.prompt.ilike(f"%{query}%")
                | EpisodeModel.answer.ilike(f"%{query}%")
            )
            .order_by(EpisodeModel.importance.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_top(self, limit: int = 10) -> list[EpisodeModel]:
        result = await self._s.execute(
            select(EpisodeModel)
            .order_by(EpisodeModel.importance.desc(), EpisodeModel.access_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def decay_old(self, days: int = 30, min_access: int = 3) -> int:
        """Reduce importance of old, low-access episodes."""
        cutoff = datetime.now(timezone.utc)
        result = await self._s.execute(
            update(EpisodeModel)
            .where(
                EpisodeModel.created_at < func.now() - func.make_interval(0, 0, days),
                EpisodeModel.access_count < min_access,
            )
            .values(importance=EpisodeModel.importance * 0.9)
        )
        await self._s.commit()
        return result.rowcount

    async def evict_stale(self, days: int = 90, max_importance: float = 0.1) -> int:
        """Delete very old, very low-importance episodes."""
        result = await self._s.execute(
            delete(EpisodeModel).where(
                EpisodeModel.created_at < func.now() - func.make_interval(0, 0, days),
                EpisodeModel.importance < max_importance,
            )
        )
        await self._s.commit()
        return result.rowcount

    async def count(self) -> int:
        result = await self._s.execute(select(func.count(EpisodeModel.id)))
        return result.scalar() or 0


# ── Concept Repository ───────────────────────────────────────────

class ConceptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def upsert(self, token: str, weight: float, episode_ids: list[str]) -> ConceptModel:
        existing = await self.get_by_token(token)
        if existing:
            existing.weight = weight
            existing.episodes = list(set((existing.episodes or []) + episode_ids))
            existing.last_seen = datetime.now(timezone.utc)
            await self._s.commit()
            return existing

        obj = ConceptModel(token=token, weight=weight, episodes=episode_ids)
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_by_token(self, token: str) -> ConceptModel | None:
        result = await self._s.execute(
            select(ConceptModel).where(ConceptModel.token == token)
        )
        return result.scalars().first()

    async def get_for_episodes(self, episode_ids: list[str]) -> list[ConceptModel]:
        result = await self._s.execute(
            select(ConceptModel).where(ConceptModel.episodes.overlap(episode_ids))
        )
        return list(result.scalars().all())


# ── Reflection Repository ────────────────────────────────────────

class ReflectionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def store(
        self,
        *,
        query: str,
        answer: str,
        reasoning_quality: float,
        hallucination_risk: float,
        audit_issues: list[dict],
        improvements: list[dict],
        confidence_estimate: dict,
    ) -> ReflectionModel:
        obj = ReflectionModel(
            query=query,
            answer=answer,
            reasoning_quality=reasoning_quality,
            hallucination_risk=hallucination_risk,
            audit_issues=audit_issues,
            improvements=improvements,
            confidence_estimate=confidence_estimate,
        )
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_history(self, limit: int = 20) -> list[ReflectionModel]:
        result = await self._s.execute(
            select(ReflectionModel).order_by(ReflectionModel.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_query(self, query: str) -> ReflectionModel | None:
        result = await self._s.execute(
            select(ReflectionModel).where(ReflectionModel.query == query).limit(1)
        )
        return result.scalars().first()


# ── Goal Repository ──────────────────────────────────────────────

class GoalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(self, description: str, priority: int = 5, parent_id: str | None = None) -> GoalModel:
        obj = GoalModel(description=description, priority=priority, parent_id=parent_id)
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def update_status(self, goal_id: str, status: str) -> None:
        values = {"status": status}
        if status == "completed":
            values["completed_at"] = datetime.now(timezone.utc)
        await self._s.execute(
            update(GoalModel).where(GoalModel.id == goal_id).values(**values)
        )
        await self._s.commit()

    async def get_active(self) -> list[GoalModel]:
        result = await self._s.execute(
            select(GoalModel)
            .where(GoalModel.status == "active")
            .order_by(GoalModel.priority.desc())
        )
        return list(result.scalars().all())

    async def get_by_parent(self, parent_id: str) -> list[GoalModel]:
        result = await self._s.execute(
            select(GoalModel).where(GoalModel.parent_id == parent_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, goal_id: str) -> GoalModel | None:
        result = await self._s.execute(
            select(GoalModel).where(GoalModel.id == goal_id)
        )
        return result.scalars().first()

    async def update_description(self, goal_id: str, description: str) -> None:
        await self._s.execute(
            update(GoalModel).where(GoalModel.id == goal_id).values(description=description)
        )
        await self._s.commit()

    async def get_completed(self, limit: int = 20) -> list[GoalModel]:
        result = await self._s.execute(
            select(GoalModel)
            .where(GoalModel.status == "completed")
            .order_by(GoalModel.completed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_abandoned(self, limit: int = 20) -> list[GoalModel]:
        result = await self._s.execute(
            select(GoalModel)
            .where(GoalModel.status == "abandoned")
            .order_by(GoalModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all(self, limit: int = 100) -> list[GoalModel]:
        result = await self._s.execute(
            select(GoalModel).order_by(GoalModel.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())


# ── Permanence Repository ────────────────────────────────────────

class PermanenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get(self, fact: str) -> PermanenceModel | None:
        result = await self._s.execute(
            select(PermanenceModel).where(PermanenceModel.fact == fact)
        )
        return result.scalars().first()

    async def update_score(self, fact: str, score_delta: float, source: str | None = None) -> PermanenceModel:
        existing = await self.get(fact)
        if existing:
            existing.score = max(0.0, min(1.0, existing.score + score_delta))
            existing.updated_at = datetime.now(timezone.utc)
            await self._s.commit()
            return existing

        obj = PermanenceModel(fact=fact, score=max(0.0, min(1.0, 0.5 + score_delta)), source=source)
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_all(self) -> list[PermanenceModel]:
        result = await self._s.execute(select(PermanenceModel))
        return list(result.scalars().all())


# ── Source Trust Repository ──────────────────────────────────────

class SourceTrustRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def get(self, source_name: str) -> SourceTrustModel | None:
        result = await self._s.execute(
            select(SourceTrustModel).where(SourceTrustModel.source_name == source_name)
        )
        return result.scalars().first()

    async def update(self, source_name: str, trust_delta: float) -> SourceTrustModel:
        existing = await self.get(source_name)
        if existing:
            existing.trust_score = max(0.0, existing.trust_score + trust_delta)
            existing.updated_at = datetime.now(timezone.utc)
            await self._s.commit()
            return existing

        obj = SourceTrustModel(source_name=source_name, trust_score=max(0.0, 1.0 + trust_delta))
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_all(self) -> list[SourceTrustModel]:
        result = await self._s.execute(select(SourceTrustModel))
        return list(result.scalars().all())


# ── Feedback Repository ──────────────────────────────────────────

class FeedbackRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def append(self, query: str, answer: str, rating: int, correction: str | None = None) -> FeedbackModel:
        obj = FeedbackModel(query=query, answer=answer, rating=rating, correction=correction)
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_recent(self, limit: int = 50) -> list[FeedbackModel]:
        result = await self._s.execute(
            select(FeedbackModel).order_by(FeedbackModel.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())


# ── Learned Rule Repository ─────────────────────────────────────

class LearnedRuleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def create(
        self,
        *,
        title: str,
        body: str,
        domains: list[str] | None = None,
        risk: str = "low",
        status: str = "active",
        cognitive_layer: str | None = None,
    ) -> LearnedRuleModel:
        obj = LearnedRuleModel(
            title=title,
            body=body,
            domains=domains or [],
            risk=risk,
            status=status,
            cognitive_layer=cognitive_layer,
        )
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_active(self, cognitive_layer: str | None = None) -> list[LearnedRuleModel]:
        query = select(LearnedRuleModel).where(LearnedRuleModel.status == "active")
        if cognitive_layer:
            query = query.where(
                (LearnedRuleModel.cognitive_layer == cognitive_layer)
                | (LearnedRuleModel.cognitive_layer.is_(None))
            )
        result = await self._s.execute(query)
        return list(result.scalars().all())

    async def get_all(self) -> list[LearnedRuleModel]:
        result = await self._s.execute(select(LearnedRuleModel))
        return list(result.scalars().all())


# ── Metacognition Report Repository ─────────────────────────────

class MetacognitionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def store(
        self,
        *,
        window_hours: int,
        overall_health: str,
        health_score: float,
        report: dict,
    ) -> MetacognitionReportModel:
        obj = MetacognitionReportModel(
            window_hours=window_hours,
            overall_health=overall_health,
            health_score=health_score,
            report=report,
        )
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_recent(self, limit: int = 10) -> list[MetacognitionReportModel]:
        result = await self._s.execute(
            select(MetacognitionReportModel)
            .order_by(MetacognitionReportModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_health_trend(self, limit: int = 50) -> list[MetacognitionReportModel]:
        result = await self._s.execute(
            select(MetacognitionReportModel)
            .order_by(MetacognitionReportModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


# ── Evaluation Report Repository ─────────────────────────────────

class EvaluationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def store(
        self,
        *,
        name: str,
        overall_score: float,
        passed: bool,
        stability_score: float,
        report: dict,
    ) -> EvaluationReportModel:
        obj = EvaluationReportModel(
            name=name,
            overall_score=overall_score,
            passed=1 if passed else 0,
            stability_score=stability_score,
            report=report,
        )
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_recent(self, limit: int = 10) -> list[EvaluationReportModel]:
        result = await self._s.execute(
            select(EvaluationReportModel)
            .order_by(EvaluationReportModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_score_trend(self, limit: int = 50) -> list[EvaluationReportModel]:
        result = await self._s.execute(
            select(EvaluationReportModel)
            .order_by(EvaluationReportModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


# ── Trial Report Repository ─────────────────────────────────────

class TrialRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    async def store(
        self,
        *,
        trial_name: str,
        total_queries: int,
        passed: int,
        failed: int,
        pass_rate: float,
        avg_reasoning_quality: float,
        avg_hallucination_risk: float,
        report: dict,
    ) -> TrialReportModel:
        obj = TrialReportModel(
            trial_name=trial_name,
            total_queries=total_queries,
            passed=passed,
            failed=failed,
            pass_rate=pass_rate,
            avg_reasoning_quality=avg_reasoning_quality,
            avg_hallucination_risk=avg_hallucination_risk,
            report=report,
        )
        self._s.add(obj)
        await self._s.commit()
        return obj

    async def get_recent(self, limit: int = 10) -> list[TrialReportModel]:
        result = await self._s.execute(
            select(TrialReportModel)
            .order_by(TrialReportModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
