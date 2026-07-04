"""Session replay — reconstruct and analyze past cognition sessions."""
from __future__ import annotations

import logging
from typing import Any

from backend.runtime.event_bus import event_bus
from backend.runtime.event_models import Event, EventType

logger = logging.getLogger("uvicorn")


class SessionReplay:
    """Replays and analyzes cognition sessions from event history."""

    async def replay_session(self, correlation_id: str) -> dict[str, Any]:
        """Replay a session by its correlation ID."""
        events = await event_bus.replay(correlation_id)

        if not events:
            return {
                "correlation_id": correlation_id,
                "event_count": 0,
                "error": "No events found for this correlation ID",
            }

        # Parse events
        parsed_events = []
        for event in events:
            if isinstance(event, Event):
                parsed_events.append(event)
            elif isinstance(event, dict):
                try:
                    parsed_events.append(Event(**event))
                except Exception:
                    continue

        # Reconstruct session timeline
        timeline = self._build_timeline(parsed_events)

        # Analyze session
        analysis = self._analyze_session(parsed_events)

        return {
            "correlation_id": correlation_id,
            "event_count": len(parsed_events),
            "timeline": timeline,
            "analysis": analysis,
        }

    def _build_timeline(self, events: list[Event]) -> list[dict[str, Any]]:
        """Build a human-readable timeline from events."""
        timeline = []
        for event in sorted(events, key=lambda e: e.timestamp):
            entry = {
                "timestamp": event.timestamp.isoformat() if event.timestamp else "",
                "type": event.type.value if hasattr(event.type, 'value') else str(event.type),
                "source": event.source,
                "summary": self._summarize_event(event),
            }
            timeline.append(entry)
        return timeline

    def _summarize_event(self, event: Event) -> str:
        """Generate a human-readable summary of an event."""
        payload = event.payload or {}
        match event.type:
            case EventType.QUERY_RECEIVED:
                return f"Query: {payload.get('query', '')[:100]}"
            case EventType.QUERY_DECOMPOSED:
                intent = payload.get("intent", {})
                dims = intent.get("dimensions", {}) if isinstance(intent, dict) else {}
                return f"Decomposed into {len(dims)} dimensions"
            case EventType.SOURCES_RETRIEVED:
                return f"Retrieved {payload.get('source_count', 0)} sources"
            case EventType.SOURCES_FILTERED:
                return f"Filtered to {payload.get('filtered_count', 0)} sources"
            case EventType.CONTRADICTIONS_DETECTED:
                return f"Found {payload.get('conflict_count', 0)} contradictions"
            case EventType.DRAFT_GENERATED:
                return f"Draft confidence: {payload.get('confidence', 'unknown')}"
            case EventType.ANSWER_SYNTHESIZED:
                return f"Answer confidence: {payload.get('confidence', 'unknown')}"
            case EventType.REFLECTION_COMPLETED:
                return f"Reasoning quality: {payload.get('reasoning_quality', 0):.2f}"
            case EventType.EPISODE_STORED:
                return f"Episode stored: {payload.get('confidence', 'unknown')}"
            case EventType.MEMORY_STORED:
                return f"Memory stored with tags: {payload.get('tags', [])}"
            case _:
                return f"{event.type.value}: {str(payload)[:100]}"

    def _analyze_session(self, events: list[Event]) -> dict[str, Any]:
        """Analyze a session's events for quality and issues."""
        event_types = [e.type for e in events]

        # Check pipeline completeness
        has_query = EventType.QUERY_RECEIVED in event_types
        has_sources = EventType.SOURCES_RETRIEVED in event_types
        has_answer = EventType.ANSWER_SYNTHESIZED in event_types
        has_reflection = EventType.REFLECTION_COMPLETED in event_types
        has_episode = EventType.EPISODE_STORED in event_types

        pipeline_complete = all([has_query, has_sources, has_answer, has_reflection])

        # Extract quality metrics
        reflection_events = [e for e in events if e.type == EventType.REFLECTION_COMPLETED]
        reasoning_quality = 0.0
        if reflection_events:
            reasoning_quality = reflection_events[-1].payload.get("reasoning_quality", 0.0)

        # Check for contradictions
        contradiction_events = [e for e in events if e.type == EventType.CONTRADICTIONS_DETECTED]
        contradiction_count = sum(
            e.payload.get("conflict_count", 0) for e in contradiction_events
        )

        # Check for errors
        error_events = [e for e in events if e.type in (EventType.TASK_FAILED,)]

        return {
            "pipeline_complete": pipeline_complete,
            "has_query": has_query,
            "has_sources": has_sources,
            "has_answer": has_answer,
            "has_reflection": has_reflection,
            "has_episode": has_episode,
            "reasoning_quality": reasoning_quality,
            "contradiction_count": contradiction_count,
            "error_count": len(error_events),
            "event_type_distribution": self._count_event_types(events),
        }

    def _count_event_types(self, events: list[Event]) -> dict[str, int]:
        """Count events by type."""
        counts: dict[str, int] = {}
        for event in events:
            key = event.type.value if hasattr(event.type, 'value') else str(event.type)
            counts[key] = counts.get(key, 0) + 1
        return counts

    async def compare_sessions(
        self, correlation_id_1: str, correlation_id_2: str
    ) -> dict[str, Any]:
        """Compare two sessions side by side."""
        session_1 = await self.replay_session(correlation_id_1)
        session_2 = await self.replay_session(correlation_id_2)

        analysis_1 = session_1.get("analysis", {})
        analysis_2 = session_2.get("analysis", {})

        return {
            "session_1": {
                "correlation_id": correlation_id_1,
                "event_count": session_1["event_count"],
                "reasoning_quality": analysis_1.get("reasoning_quality", 0.0),
                "contradiction_count": analysis_1.get("contradiction_count", 0),
                "pipeline_complete": analysis_1.get("pipeline_complete", False),
            },
            "session_2": {
                "correlation_id": correlation_id_2,
                "event_count": session_2["event_count"],
                "reasoning_quality": analysis_2.get("reasoning_quality", 0.0),
                "contradiction_count": analysis_2.get("contradiction_count", 0),
                "pipeline_complete": analysis_2.get("pipeline_complete", False),
            },
            "quality_delta": round(
                analysis_2.get("reasoning_quality", 0.0) - analysis_1.get("reasoning_quality", 0.0), 3
            ),
        }


# Module-level singleton
session_replay = SessionReplay()
