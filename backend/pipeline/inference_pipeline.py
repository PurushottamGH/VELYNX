"""Inference pipeline — orchestrates context building → LLM reasoning → structured output."""
from __future__ import annotations

import logging
from typing import Any

from backend.pipeline.context_builder import build_context
from backend.cognition.reasoning_engine import reason, ReasoningResult
from backend.memory.memory_manager import memory_manager

logger = logging.getLogger("uvicorn")


async def run_inference(
    query: str,
    sources: list[dict],
    *,
    constitution: str | None = None,
    cognitive_layer: str | None = None,
) -> dict[str, Any]:
    """Run the full LLM inference pipeline.

    Drop-in replacement for reasoning_core.reason() — returns the same dict shape.
    """
    # 1. Retrieve relevant memory (semantic + legacy fallback)
    memory_dicts: list[dict] = []
    try:
        semantic_hits = await memory_manager.recall(query, limit=3)
        memory_dicts = [
            {"prompt": h.entry.metadata.get("prompt", h.entry.text[:100]),
             "answer": h.entry.metadata.get("answer", h.entry.text[:200]),
             "score": h.score}
            for h in semantic_hits
        ]
    except Exception as exc:
        logger.debug("Semantic recall failed, trying legacy: %s", exc)

    if not memory_dicts:
        # Legacy fallback
        from memory.vector_store import _DEFAULT_VECTOR_STORE
        legacy_hits = _DEFAULT_VECTOR_STORE.recall(query, limit=3)
        memory_dicts = [
            {"prompt": h.prompt, "answer": h.answer, "score": h.score}
            for h in legacy_hits
        ]

    # 2. Build context
    ctx = build_context(query, sources, memory_dicts, constitution)

    # 3. LLM reasoning
    result = await reason(
        query,
        sources,
        constitution=constitution,
        cognitive_layer=cognitive_layer,
        memory_context=ctx.memory_context if ctx.memory_context else None,
    )

    # 4. Return in reasoning_core.reason() compatible format
    return _to_legacy_format(result, sources, cognitive_layer)


def _to_legacy_format(
    result: ReasoningResult,
    sources: list[dict],
    cognitive_layer: str | None,
) -> dict[str, Any]:
    """Convert ReasoningResult to the dict shape expected by synthesizer and main.py."""
    citations = result.citations
    # If citations are just [1], [2] etc, resolve to actual URLs
    if citations and all(c.startswith("[") for c in citations):
        resolved: list[str] = []
        for c in citations:
            try:
                idx = int(c.strip("[]")) - 1
                if 0 <= idx < len(sources):
                    resolved.append(sources[idx].get("url", c))
                else:
                    resolved.append(c)
            except ValueError:
                resolved.append(c)
        citations = resolved

    return {
        "draft": result.answer,
        "confidence": result.confidence,
        "citations": citations[:5],
        "gaps": result.gaps,
        "cognitive_layer": cognitive_layer,
        "debug": {
            "llm": {
                "reasoning": result.reasoning_content,
                "token_usage": result.token_usage,
                "raw": result.raw_response,
            }
        },
    }
