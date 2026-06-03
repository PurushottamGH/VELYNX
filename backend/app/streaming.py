"""SSE streaming endpoint — streams pipeline stages, monologue steps, and tokens to frontend."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import AsyncGenerator

from fastapi import Request
from fastapi.responses import StreamingResponse

from conversation.working_memory import conversation_buffer, ConversationTurn
from conversation.monologue import inner_monologue
from conversation.beliefs import belief_store
from conversation.dialogue_manager import dialogue_manager
from conversation.reasoning_modes import select_reasoning_mode, get_mode_config
from models.llm_client import llm_client, LLMMessage
from models.source import Source

logger = logging.getLogger("uvicorn")


def _sse(event: str, data: dict) -> str:
    """Format a server-sent event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def stream_query(
    text: str,
    session_id: str | None = None,
) -> StreamingResponse:
    """Stream a query response as SSE events."""
    async def event_generator() -> AsyncGenerator[str, None]:
        start = time.monotonic()
        sid = session_id or "default"

        try:
            yield _sse("pipeline_stage", {"stage": "context", "status": "active"})

            # Phase 11: Get conversation context
            conv_context = conversation_buffer.get_context_window(sid, max_turns=8)
            working_ctx = conversation_buffer.get_working_context(sid)

            yield _sse("pipeline_stage", {"stage": "context", "status": "complete"})

            # Dialogue analysis
            yield _sse("pipeline_stage", {"stage": "dialogue", "status": "active"})
            dialogue_decision = dialogue_manager.analyze_turn(text, working_ctx)
            yield _sse("pipeline_stage", {"stage": "dialogue", "status": "complete"})

            if dialogue_decision.needs_clarification:
                yield _sse("answer", {
                    "answer": dialogue_decision.clarification_prompt,
                    "confidence": "LOW",
                    "sources": [],
                    "dialogue_act": dialogue_decision.act.value,
                    "clarification_needed": True,
                })
                yield _sse("stream_complete", {"duration_ms": (time.monotonic() - start) * 1000})
                return

            # Intent decomposition
            yield _sse("pipeline_stage", {"stage": "intent", "status": "active"})
            from pipeline import intent_engine
            intent = intent_engine.decompose_query(text)
            yield _sse("pipeline_stage", {"stage": "intent", "status": "complete"})

            # Retrieval
            yield _sse("pipeline_stage", {"stage": "retrieval", "status": "active"})
            from pipeline import retrieval_mesh, truth_filter, contradiction
            dimensions = intent.get("dimensions", {})
            weights = intent.get("weights", {})
            ranked = sorted(dimensions.items(), key=lambda item: weights.get(item[0], 0), reverse=True)
            top_queries = [value for _, value in ranked[:3] if value]
            expanded_query = " | ".join(top_queries) if top_queries else text
            sources = await retrieval_mesh.retrieve_all(text)
            yield _sse("pipeline_stage", {"stage": "retrieval", "status": "complete"})

            # Truth filter
            yield _sse("pipeline_stage", {"stage": "truth", "status": "active"})
            filtered_payload = truth_filter.score_sources(sources, query=text)
            filtered = filtered_payload["sources"]
            yield _sse("pipeline_stage", {"stage": "truth", "status": "complete"})

            # Contradiction
            yield _sse("pipeline_stage", {"stage": "contradiction", "status": "active"})
            conflicts = contradiction.find_contradictions(filtered)
            yield _sse("pipeline_stage", {"stage": "contradiction", "status": "complete"})

            # Reasoning mode
            reasoning_mode = select_reasoning_mode(
                text, intent_result=intent, dialogue_act=dialogue_decision.act.value,
            )
            mode_config = get_mode_config(reasoning_mode)
            yield _sse("pipeline_stage", {"stage": "reasoning_mode", "status": "complete",
                                          "mode": reasoning_mode.value})

            # Inner monologue
            yield _sse("pipeline_stage", {"stage": "monologue", "status": "active"})
            monologue_trace = await inner_monologue.generate_monologue(
                text, filtered, conv_context, reasoning_mode.value,
            )
            for step in monologue_trace.steps:
                yield _sse("monologue_step", {
                    "type": step.type,
                    "content": step.content,
                    "confidence": step.confidence,
                })
            yield _sse("pipeline_stage", {"stage": "monologue", "status": "complete"})

            # Reasoning (LLM)
            yield _sse("pipeline_stage", {"stage": "reasoning", "status": "active"})
            cognitive_layer = intent.get("cognitive_layer")

            draft = None
            if llm_client.available:
                try:
                    from pipeline.context_builder import build_context
                    from cognition.reasoning_engine import reason as llm_reason
                    ctx = build_context(
                        text, filtered,
                        constitution=intent.get("constitution"),
                        conversation_context=conv_context if conv_context else None,
                        beliefs=belief_store.get_all_active_summary() or None,
                    )
                    reasoning_result = await llm_reason(
                        text, filtered,
                        constitution=intent.get("constitution"),
                        cognitive_layer=cognitive_layer,
                        memory_context=ctx.memory_context if ctx.memory_context else None,
                        monologue_context=monologue_trace.summary() or None,
                        mode_prompt_addendum=mode_config.system_prompt_addendum,
                        temperature_override=0.3 + mode_config.temperature_adjustment,
                    )
                    if reasoning_result is not None:
                        draft = {
                            "draft": reasoning_result.answer,
                            "confidence": reasoning_result.confidence,
                            "citations": reasoning_result.citations,
                            "gaps": reasoning_result.gaps,
                        }
                except Exception as exc:
                    logger.info("LLM reasoning unavailable in stream, using internal engine: %s", exc)

            if draft is None:
                from pipeline import reasoning_core
                draft = reasoning_core.reason(
                    filtered,
                    query=text,
                    constitution=intent.get("constitution"),
                    cognitive_layer=cognitive_layer,
                )

            yield _sse("pipeline_stage", {"stage": "reasoning", "status": "complete"})

            # Synthesis
            yield _sse("pipeline_stage", {"stage": "synthesis", "status": "active"})
            from pipeline import synthesizer
            final = synthesizer.synthesize(draft)
            yield _sse("pipeline_stage", {"stage": "synthesis", "status": "complete"})

            # Reflection
            yield _sse("pipeline_stage", {"stage": "reflection", "status": "active"})
            from reflection.reflection_engine import reflection_engine
            reasoning_content = draft.get("debug", {}).get("llm", {}).get("reasoning", "")
            reflection_result = await reflection_engine.reflect(
                query=text,
                answer=final.get("answer", ""),
                sources=filtered,
                reasoning_content=reasoning_content,
                confidence=final.get("confidence", "UNKNOWN"),
            )
            yield _sse("pipeline_stage", {"stage": "reflection", "status": "complete"})

            # Record turns
            answer_text = str(final.get("answer", ""))
            answer_confidence = str(final.get("confidence", "UNKNOWN"))
            conversation_buffer.add_turn(sid, ConversationTurn(
                role="user", text=text, intent=intent, dialogue_act=dialogue_decision.act.value,
            ))
            conversation_buffer.add_turn(sid, ConversationTurn(
                role="assistant", text=answer_text[:500], confidence=answer_confidence,
                dialogue_act=dialogue_decision.act.value,
            ))

            # Build sources
            response_sources = [
                {"url": s.get("url", ""), "title": s.get("title"), "source": s.get("source"), "score": s.get("score")}
                for s in (filtered or sources) if s.get("url")
            ]

            # Final answer
            duration_ms = (time.monotonic() - start) * 1000
            yield _sse("answer", {
                "answer": answer_text,
                "confidence": answer_confidence,
                "sources": response_sources,
                "contradictions": [c.get("summary") for c in conflicts.get("conflicts", [])],
                "gaps": final.get("gaps", []),
                "citations": final.get("citations", []),
                "tone": final.get("tone", "scientific"),
                "dialogue_act": dialogue_decision.act.value,
                "reasoning_mode": reasoning_mode.value,
                "duration_ms": duration_ms,
            })

            yield _sse("stream_complete", {"duration_ms": duration_ms})

        except Exception as exc:
            logger.error("Streaming error: %s", exc, exc_info=True)
            yield _sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
