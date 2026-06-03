"""SQLAlchemy ORM models for VELYNX persistent state."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


class Base(DeclarativeBase):
    pass


# ── Memory ───────────────────────────────────────────────────────

class EpisodeModel(Base):
    """A stored prompt-answer episode."""
    __tablename__ = "episodes"

    id = Column(String(16), primary_key=True, default=_new_id)
    prompt = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    confidence = Column(String(16), default="UNKNOWN")
    source = Column(String(64))
    tags = Column(JSONB, default=list)
    kind = Column(String(32), default="learned")
    importance = Column(Float, default=0.5)
    embedding = Column(JSONB)  # list[float] — pgvector can be added later
    access_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class ConceptModel(Base):
    """A concept token with weight and episode links."""
    __tablename__ = "concepts"

    id = Column(String(16), primary_key=True, default=_new_id)
    token = Column(String(128), unique=True, nullable=False, index=True)
    weight = Column(Float, default=0.0)
    episodes = Column(JSONB, default=list)
    last_seen = Column(DateTime(timezone=True), default=_now)


# ── Reflection ───────────────────────────────────────────────────

class ReflectionModel(Base):
    """A stored reflection result."""
    __tablename__ = "reflections"

    id = Column(String(16), primary_key=True, default=_new_id)
    query = Column(Text, nullable=False)
    answer = Column(Text)
    reasoning_quality = Column(Float)
    hallucination_risk = Column(Float)
    audit_issues = Column(JSONB, default=list)
    improvements = Column(JSONB, default=list)
    confidence_estimate = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=_now)


# ── Goals ────────────────────────────────────────────────────────

class GoalModel(Base):
    """An active or completed goal."""
    __tablename__ = "goals"

    id = Column(String(16), primary_key=True, default=_new_id)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=5)
    status = Column(String(16), default="active")  # active, completed, abandoned
    parent_id = Column(String(16), ForeignKey("goals.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    children = relationship("GoalModel", backref="parent", remote_side=[id])


# ── Session ──────────────────────────────────────────────────────

class SessionModel(Base):
    """A runtime session."""
    __tablename__ = "sessions"

    id = Column(String(16), primary_key=True, default=_new_id)
    started_at = Column(DateTime(timezone=True), default=_now)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)


class ContextSnapshotModel(Base):
    """A point-in-time snapshot of cognitive context."""
    __tablename__ = "context_snapshots"

    id = Column(String(16), primary_key=True, default=_new_id)
    session_id = Column(String(16), ForeignKey("sessions.id"), nullable=True)
    snapshot = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)


# ── Learning ─────────────────────────────────────────────────────

class PermanenceModel(Base):
    """A belief with a confidence score."""
    __tablename__ = "permanence"

    id = Column(String(16), primary_key=True, default=_new_id)
    fact = Column(Text, nullable=False)
    score = Column(Float, default=0.5)
    source = Column(String(64))
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class SourceTrustModel(Base):
    """Trust score for a retrieval source."""
    __tablename__ = "source_trust"

    source_name = Column(String(64), primary_key=True)
    trust_score = Column(Float, default=1.0)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class FeedbackModel(Base):
    """A user feedback record."""
    __tablename__ = "feedback"

    id = Column(String(16), primary_key=True, default=_new_id)
    query = Column(Text, nullable=False)
    answer = Column(Text)
    rating = Column(Integer)  # 1=accurate, 0=wrong, -1=incomplete
    correction = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_now)


class LearnedRuleModel(Base):
    """A constitution rule learned from feedback."""
    __tablename__ = "learned_rules"

    id = Column(String(16), primary_key=True, default=_new_id)
    title = Column(String(256), nullable=False)
    body = Column(Text, nullable=False)
    domains = Column(JSONB, default=list)
    risk = Column(String(16), default="low")
    status = Column(String(16), default="active")  # active, pending
    cognitive_layer = Column(String(32))
    created_at = Column(DateTime(timezone=True), default=_now)


# ── Metacognition Report Model ───────────────────────────────────

class MetacognitionReportModel(Base):
    """A persisted metacognition analysis report."""
    __tablename__ = "metacognition_reports"

    id = Column(String(16), primary_key=True, default=_new_id)
    window_hours = Column(Integer, default=24)
    overall_health = Column(String(16))
    health_score = Column(Float)
    report = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)


# ── Evaluation Report Model ─────────────────────────────────────

class EvaluationReportModel(Base):
    """A persisted evaluation/benchmark report."""
    __tablename__ = "evaluation_reports"

    id = Column(String(16), primary_key=True, default=_new_id)
    name = Column(String(128))
    overall_score = Column(Float)
    passed = Column(Integer, default=0)  # boolean as int
    stability_score = Column(Float)
    report = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)


# ── Trial Report Model ──────────────────────────────────────────

class TrialReportModel(Base):
    """A persisted cognition trial report."""
    __tablename__ = "trial_reports"

    id = Column(String(16), primary_key=True, default=_new_id)
    trial_name = Column(String(128))
    total_queries = Column(Integer)
    passed = Column(Integer)
    failed = Column(Integer)
    pass_rate = Column(Float)
    avg_reasoning_quality = Column(Float)
    avg_hallucination_risk = Column(Float)
    report = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)
