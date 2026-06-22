"""Self-model routing — 'what do you know', 'describe yourself' queries."""
from __future__ import annotations

import logging

from backend.models.answer import AnswerResponse

logger = logging.getLogger("uvicorn")

_SELF_QUERY_PHRASES = [
    "what do you know", "describe yourself", "what are you",
    "how are you", "who are you", "what can you do",
    "what do you remember", "are you healthy",
]


def self_query(text: str) -> bool:
    lowered = text.lower()
    return any(p in lowered for p in _SELF_QUERY_PHRASES)


def _format_self_snapshot(snap: dict) -> str:
    k = snap["knowledge"]
    l = snap["learning"]
    lines = [
        f"I've learned {k['total_learned']} concepts across {len(k['top_domains'])} domains.",
        f"My knowledge graph has {k['triples']} relationships connecting what I know.",
        f"I've answered {l['total_queries']} questions so far (avg confidence: {l['avg_confidence']:.0%}).",
    ]
    if snap["soul"]:
        lines.append(f"Purushottam has taught me about: {', '.join(snap['soul'])}.")
    if k["weak_topics"]:
        lines.append(f"Areas I'm uncertain about: {', '.join(k['weak_topics'][:5])}.")
    lines.append(f"My health is {snap['health']}, uptime {snap['uptime_sec']:.0f}s.")
    return " ".join(lines)


async def handle_self_query(text: str) -> AnswerResponse | None:
    """Check for self-model query and return a snapshot if matched."""
    if not self_query(text):
        return None
    try:
        from cognition.self_model import self_model

        snap = await self_model.snapshot()
        answer = _format_self_snapshot(snap)
        return AnswerResponse(
            query=text,
            answer=answer,
            confidence="CERTAIN",
            source="self_model",
            sources=[],
            contradictions=[],
            gaps=[],
            citations=[],
            tone="direct",
        )
    except Exception as exc:
        logger.debug("self_model skipped: %s", exc)
    return None
