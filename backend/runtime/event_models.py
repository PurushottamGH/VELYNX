"""Typed event models for the cognitive runtime event bus."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class EventPriority(int, Enum):
    CRITICAL = 9
    HIGH = 7
    NORMAL = 5
    LOW = 3


class EventType(str, Enum):
    # Query lifecycle
    QUERY_RECEIVED = "query_received"
    QUERY_DECOMPOSED = "query_decomposed"
    SOURCES_RETRIEVED = "sources_retrieved"
    SOURCES_FILTERED = "sources_filtered"
    CONTRADICTIONS_DETECTED = "contradictions_detected"
    DRAFT_GENERATED = "draft_generated"
    ANSWER_SYNTHESIZED = "answer_synthesized"
    REFLECTION_COMPLETED = "reflection_completed"
    EPISODE_STORED = "episode_stored"

    # Feedback
    FEEDBACK_RECEIVED = "feedback_received"
    FEEDBACK_POSITIVE = "feedback_positive"
    FEEDBACK_NEGATIVE = "feedback_negative"
    FAILURE_DIAGNOSED = "failure_diagnosed"
    RULE_DERIVED = "rule_derived"
    RULE_RECORDED = "rule_recorded"

    # Goals
    GOAL_CREATED = "goal_created"
    GOAL_DECOMPOSED = "goal_decomposed"
    GOAL_COMPLETED = "goal_completed"
    GOAL_ABANDONED = "goal_abandoned"
    GOAL_PARENT_AUTO_COMPLETED = "goal_parent_auto_completed"

    # Plans
    PLAN_CREATED = "plan_created"
    PLAN_STARTED = "plan_started"
    PLAN_COMPLETED = "plan_completed"
    PLAN_REPLANNED = "plan_replanned"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_SKIPPED = "task_skipped"
    FAILURE_PROPAGATED = "failure_propagated"

    # Session
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    CONTEXT_SNAPSHOT_CREATED = "context_snapshot_created"

    # Memory
    MEMORY_STORED = "memory_stored"
    MEMORY_DECAYED = "memory_decayed"
    MEMORY_EVICTED = "memory_evicted"
    MEMORY_REINFORCED = "memory_reinforced"

    # Strategy
    STRATEGY_SELECTED = "strategy_selected"
    STRATEGY_ADJUSTED = "strategy_adjusted"
    STRATEGY_LEARNED = "strategy_learned"

    # Cognition
    CONFIDENCE_CALIBRATED = "confidence_calibrated"
    REASONING_AUDITED = "reasoning_audited"

    # Metacognition
    METACOGNITION_ANALYZED = "metacognition_analyzed"
    PATTERN_DETECTED = "pattern_detected"
    HEALTH_CHECK_COMPLETED = "health_check_completed"
    RECOMMENDATION_GENERATED = "recommendation_generated"

    # Operations
    CIRCUIT_BREAKER_TRIPPED = "circuit_breaker_tripped"
    LOAD_SHED_TRIGGERED = "load_shed_triggered"
    RESOURCE_PRESSURE = "resource_pressure"
    TOKEN_BUDGET_EXCEEDED = "token_budget_exceeded"

    # Conversation (Phase 11)
    CONVERSATION_TURN_RECORDED = "conversation_turn_recorded"
    CONVERSATION_CONTEXT_INJECTED = "conversation_context_injected"
    CONVERSATION_COMPRESSED = "conversation_compressed"
    INNER_MONOLOGUE_STARTED = "inner_monologue_started"
    INNER_MONOLOGUE_STEP = "inner_monologue_step"
    INNER_MONOLOGUE_COMPLETED = "inner_monologue_completed"
    BELIEF_FORMED = "belief_formed"
    BELIEF_UPDATED = "belief_updated"
    BELIEF_CONTRADICTED = "belief_contradicted"
    BELIEF_ABANDONED = "belief_abandoned"
    DIALOGUE_ACT_CLASSIFIED = "dialogue_act_classified"
    CLARIFICATION_REQUESTED = "clarification_requested"
    TOPIC_TRANSITION = "topic_transition"
    FOLLOW_UP_DETECTED = "follow_up_detected"
    REASONING_MODE_SELECTED = "reasoning_mode_selected"
    STREAM_STARTED = "stream_started"
    STREAM_STAGE = "stream_stage"
    STREAM_TOKEN = "stream_token"
    STREAM_COMPLETED = "stream_completed"


class Event(BaseModel):
    """A typed runtime event with tracing metadata."""
    id: str = Field(default_factory=_new_id)
    type: EventType
    correlation_id: str = Field(default_factory=_new_id)
    priority: int = Field(default=EventPriority.NORMAL)
    timestamp: datetime = Field(default_factory=_now)
    source: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventEnvelope(BaseModel):
    """Wire format for Redis pub/sub transport."""
    channel: str = "velynx:events"
    event: Event


class HandlerResult(BaseModel):
    """Result of handling a single event by one handler."""
    handler_name: str
    event_id: str
    success: bool = True
    error: str | None = None
    duration_ms: float = 0.0
