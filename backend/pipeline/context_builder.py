"""Context builder — assembles LLM prompt context from sources, memory, and constitution."""
from __future__ import annotations

from pydantic import BaseModel, Field

_MAX_SOURCE_CHARS = 6000
_MAX_MEMORY_CHARS = 1500


class ContextBundle(BaseModel):
    """Structured context for LLM reasoning."""
    evidence: str = ""
    memory_context: str = ""
    constitution: str = ""
    query: str = ""
    source_count: int = 0
    memory_count: int = 0
    conversation_context: str = ""
    beliefs: str = ""


def build_context(
    query: str,
    sources: list[dict],
    memory_hits: list[dict] | None = None,
    constitution: str | None = None,
    conversation_context: str | None = None,
    beliefs: str | None = None,
) -> ContextBundle:
    """Assemble context bundle for LLM reasoning."""
    evidence = _format_sources(sources)
    memory_ctx = _format_memory(memory_hits or [])

    return ContextBundle(
        evidence=evidence,
        memory_context=memory_ctx,
        constitution=constitution or "",
        query=query,
        source_count=len(sources),
        memory_count=len(memory_hits or []),
        conversation_context=conversation_context or "",
        beliefs=beliefs or "",
    )


def _format_sources(sources: list[dict]) -> str:
    if not sources:
        return "No sources available."

    parts: list[str] = []
    total = 0
    for i, s in enumerate(sources, 1):
        title = s.get("title") or s.get("url") or f"Source {i}"
        snippet = (s.get("snippet") or "")[:500]
        url = s.get("url", "")
        score = s.get("score", 0)
        block = f"[{i}] {title} (relevance: {score:.2f})\n{snippet}\nSource: {url}"
        if total + len(block) > _MAX_SOURCE_CHARS:
            break
        parts.append(block)
        total += len(block)

    return "\n\n".join(parts)


def _format_memory(hits: list[dict]) -> str:
    if not hits:
        return ""

    parts: list[str] = []
    total = 0
    for h in hits:
        prompt = h.get("prompt", "")
        answer = h.get("answer", "")[:300]
        score = h.get("score", 0)
        block = f"Prior Q: {prompt}\nPrior A: {answer} (confidence: {score:.2f})"
        if total + len(block) > _MAX_MEMORY_CHARS:
            break
        parts.append(block)
        total += len(block)

    return "\n---\n".join(parts)
