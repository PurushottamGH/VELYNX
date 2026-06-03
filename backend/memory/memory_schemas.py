"""Pydantic models for the semantic memory system."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


class MemoryEntry(BaseModel):
    """Base memory entry — shared across all memory kinds."""
    id: str = Field(default_factory=_new_id)
    text: str
    kind: str  # "episodic", "semantic", "working"
    source: str | None = None
    tags: list[str] = Field(default_factory=list)
    confidence: str = "UNKNOWN"
    importance: float = 0.5
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    access_count: int = 0
    last_accessed: datetime = Field(default_factory=_now)
    ttl_seconds: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EpisodicMemory(BaseModel):
    """An episode: a prompt-answer pair with context."""
    entry: MemoryEntry
    prompt: str
    answer: str
    context_snapshot: dict[str, Any] = Field(default_factory=dict)


class SemanticMemory(BaseModel):
    """A semantic concept with relationships."""
    entry: MemoryEntry
    concept: str
    relationships: list[str] = Field(default_factory=list)


class WorkingMemory(BaseModel):
    """Short-lived, high-priority memory for active reasoning."""
    entry: MemoryEntry
    priority: int = 5  # 1-10, higher = more important


class RetrievalResult(BaseModel):
    """A scored memory hit from retrieval."""
    entry: MemoryEntry
    score: float
    rank: int
    match_reason: str = ""


class MemoryStats(BaseModel):
    """Aggregate statistics across all memory."""
    total_entries: int = 0
    by_kind: dict[str, int] = Field(default_factory=dict)
    avg_importance: float = 0.0
    oldest: datetime | None = None
    newest: datetime | None = None
