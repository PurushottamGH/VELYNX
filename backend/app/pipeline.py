"""Core query pipeline — the answer_question() function and helpers."""
from __future__ import annotations

import asyncio
import logging
import os

from learning.curriculum import resolve_chat_answer
from learning.knowledge_tutor import resolve_learning_answer
from memory.memory_manager import memory_manager
from memory.vector_store import recall_answer
from models.answer import AnswerResponse
from models.source import Source
from models.llm_client import llm_client
from pipeline import (
    contradiction,
    intent_engine,
    seed_knowledge,
    reasoning_core,
    retrieval_mesh,
    synthesizer,
    truth_filter,
)
from reflection.reflection_engine import reflection_engine
from app.db_bridge import (
    persist_episode,
    persist_reflection,
    persist_context_snapshot,
)

# Phase 11: Conversational Cognition
from conversation.working_memory import conversation_buffer, ConversationTurn
from conversation.monologue import inner_monologue
from conversation.beliefs import belief_store
from conversation.dialogue_manager import dialogue_manager
from conversation.reasoning_modes import select_reasoning_mode, get_mode_config

logger = logging.getLogger("uvicorn")


async def _record_memory_turn(query: str, response: dict, source: str, tags: list[str] | None = None) -> None:
    confidence = str(response.get("confidence") or "UNKNOWN")
    if confidence == "UNKNOWN":
        return
    try:
        await memory_manager.store_episodic(
            query,
            str(response.get("answer") or ""),
            confidence=confidence,
            source=source,
            tags=tags or [],
            kind=source,
            importance=0.7 if confidence == "CERTAIN" else 0.5,
        )
    except Exception as exc:
        logger.debug("Memory store skipped: %s", exc)


def _looks_like_memory_request(text: str) -> bool:
    lowered = text.lower()
    return any(
        phrase in lowered
        for phrase in [
            "remember",
            "what did you say",
            "as you said",
            "last time",
            "earlier",
            "repeat",
            "recall",
        ]
    )


async def answer_question(text: str, session_id: str | None = None) -> AnswerResponse:
    """Core query pipeline — processes a question through the full VELYNX stack."""
    sid = session_id or "default"
    conv_context = conversation_buffer.get_context_window(sid, max_turns=8)
    working_ctx = conversation_buffer.get_working_context(sid)

    # Phase 11D: Dialogue analysis
    dialogue_decision = dialogue_manager.analyze_turn(text, working_ctx)
    if dialogue_decision.needs_clarification:
        return AnswerResponse(
            query=text,
            answer=dialogue_decision.clarification_prompt,
            confidence="LOW",
            sources=[],
            contradictions=[],
            gaps=[],
            citations=[],
            tone="clarification",
            dialogue_act=dialogue_decision.act.value,
            clarification_needed=True,
        )

    # ── Knowledge Graph fast path ──────────────
    try:
        from memory.knowledge_graph import knowledge_graph
        kg_node = knowledge_graph.lookup(text, threshold=0.3)
        if kg_node and kg_node.effective_confidence >= 0.3:
            import html as _html
            import re as _re
            clean_summary = _html.unescape(kg_node.summary)
            clean_summary = _re.sub(r"\(pronunciation[^)]*\)", "", clean_summary)
            clean_summary = _re.sub(r"\s+", " ", clean_summary).strip()
            conf = "CERTAIN" if kg_node.effective_confidence >= 0.85 else (
                "PROBABLE" if kg_node.effective_confidence >= 0.65 else (
                "DEBATED" if kg_node.effective_confidence >= 0.40 else "LOW"))
            kg_result = {
                "answer": clean_summary,
                "confidence": conf,
                "sources": [],
                "gaps": [],
                "citations": [f"[KG] Learned from {kg_node.source_count} source(s)"],
                "tone": "human",
                "debug": {"kg_hit": True, "concept": kg_node.concept, "domain": kg_node.domain},
            }
            await _record_memory_turn(text, kg_result, "knowledge_graph", ["kg", "terminal"])
            return AnswerResponse(
                query=text,
                answer=clean_summary,
                confidence=conf,
                sources=[],
                contradictions=[],
                gaps=[],
                citations=kg_result["citations"],
                tone="human",
                debug=kg_result["debug"],
            )
    except Exception:
        pass

    learning = await resolve_learning_answer(text)
    if learning is not None:
        tags = ["deterministic", "terminal"]
        if learning.get("cognitive_layers"):
            tags.extend(learning.get("cognitive_layers"))
        await _record_memory_turn(text, learning, "learning_tutor", tags)
        return AnswerResponse(
            query=text,
            answer=learning["answer"],
            confidence=learning["confidence"],
            sources=[
                Source(
                    url=item.get("url", ""),
                    title=item.get("title"),
                    snippet=item.get("snippet"),
                    source=item.get("source"),
                    score=item.get("score"),
                )
                for item in learning.get("sources", [])
                if item.get("url")
            ],
            contradictions=[],
            gaps=learning.get("gaps", []),
            citations=learning.get("citations", []),
            tone=learning.get("tone", "human"),
            debug=learning.get("debug", {}),
        )

    local = resolve_chat_answer(text)
    if local is not None:
        await _record_memory_turn(text, local, "curriculum", ["curriculum", "terminal"])
        return AnswerResponse(
            query=text,
            answer=local["answer"],
            confidence=local["confidence"],
            sources=[],
            contradictions=[],
            gaps=local["gaps"],
            citations=local["citations"],
            tone=local["tone"],
            debug={"seeded": True, "seed_keys": local["seed_keys"]},
        )

    seeded = seed_knowledge.resolve_seed_answer(text)
    if seeded is not None:
        await _record_memory_turn(text, seeded, "seed_knowledge", ["seeded", "terminal"])
        return AnswerResponse(
            query=text,
            answer=seeded["answer"],
            confidence=seeded["confidence"],
            sources=[],
            contradictions=[],
            gaps=seeded["gaps"],
            citations=seeded["citations"],
            tone=seeded["tone"],
            debug={"seeded": True, "seed_keys": seeded["seed_keys"]},
        )

    # Semantic recall (new system) — with hard timeout
    semantic_results = []
    try:
        semantic_results = await asyncio.wait_for(
            memory_manager.recall(text, limit=1, kinds=["episodic"]),
            timeout=3.0,
        )
    except asyncio.TimeoutError:
        logger.debug("Semantic recall timed out (3s)")
    except Exception as exc:
        logger.debug("Semantic recall failed: %s", exc)

    # Legacy recall (backward compat)
    remembered = recall_answer(text)
    memory_debug = (remembered or {}).get("debug") or {}
    memory_meta = memory_debug.get("memory") or {}
    memory_kind = str(memory_meta.get("kind") or "")

    # Prefer semantic hit if it scores high enough
    if semantic_results and semantic_results[0].score >= 0.65:
        hit = semantic_results[0]
        remembered = {
            "answer": f"I remember this: {hit.entry.metadata.get('answer', hit.entry.text)}",
            "confidence": hit.entry.confidence,
            "citations": [],
            "gaps": [],
            "tone": "human",
            "debug": {"memory": {"kind": hit.entry.kind, "score": hit.score, "match_reason": hit.match_reason}},
        }

    if remembered is not None and (_looks_like_memory_request(text) or memory_kind == "feedback"):
        await _record_memory_turn(text, remembered, "memory", ["associative", "terminal"])
        return AnswerResponse(
            query=text,
            answer=remembered["answer"],
            confidence=remembered["confidence"],
            sources=[],
            contradictions=[],
            gaps=remembered.get("gaps", []),
            citations=remembered.get("citations", []),
            tone=remembered.get("tone", "human"),
            debug=remembered.get("debug", {}),
        )

    intent = intent_engine.decompose_query(text)
    dimensions = intent.get("dimensions", {})
    weights = intent.get("weights", {})
    ranked = sorted(dimensions.items(), key=lambda item: weights.get(item[0], 0), reverse=True)
    top_queries = [value for _, value in ranked[:3] if value]
    expanded_query = " | ".join(top_queries) if top_queries else text
    cognitive_layer = intent.get("cognitive_layer")

    try:
        sources = await asyncio.wait_for(retrieval_mesh.retrieve_all(text), timeout=10.0)
    except asyncio.TimeoutError:
        sources = []
        logger.warning("Retrieval timed out (10s), continuing with empty sources")
    filtered_payload = truth_filter.score_sources(sources, query=text)
    filtered = filtered_payload["sources"]
    conflicts = contradiction.find_contradictions(filtered)
    evidence_graph = contradiction.build_evidence_graph(filtered)

    # Phase 11E: Select reasoning mode
    reasoning_mode = select_reasoning_mode(
        text, intent_result=intent, dialogue_act=dialogue_decision.act.value,
    )
    mode_config = get_mode_config(reasoning_mode)

    # Phase 11B: Generate inner monologue (with timeout)
    try:
        monologue_trace = await asyncio.wait_for(
            inner_monologue.generate_monologue(text, filtered, conv_context, reasoning_mode.value),
            timeout=3.0,
        )
    except asyncio.TimeoutError:
        from conversation.monologue import MonologueTrace
        monologue_trace = MonologueTrace(steps=[], summary_value=None, confidence=0.5)
        logger.debug("Monologue timed out (3s)")

    draft = None
    if llm_client.available:
        try:
            from pipeline.context_builder import build_context
            ctx = build_context(
                text, filtered,
                constitution=intent.get("constitution"),
                conversation_context=conv_context if conv_context else None,
                beliefs=belief_store.get_all_active_summary() or None,
            )
            from cognition.reasoning_engine import reason as llm_reason
            reasoning_result = await asyncio.wait_for(
                llm_reason(
                    text,
                    filtered,
                    constitution=intent.get("constitution"),
                    cognitive_layer=cognitive_layer,
                    memory_context=ctx.memory_context if ctx.memory_context else None,
                    monologue_context=monologue_trace.summary() or None,
                    mode_prompt_addendum=mode_config.system_prompt_addendum,
                    temperature_override=0.3 + mode_config.temperature_adjustment,
                ),
                timeout=12.0,
            )
            if reasoning_result is not None:
                draft = {
                    "draft": reasoning_result.answer,
                    "confidence": reasoning_result.confidence,
                    "citations": reasoning_result.citations,
                    "gaps": reasoning_result.gaps,
                    "cognitive_layer": cognitive_layer,
                    "debug": {
                        "llm": {
                            "reasoning": reasoning_result.reasoning_content,
                            "token_usage": reasoning_result.token_usage,
                            "raw": reasoning_result.raw_response,
                        }
                    },
                }
        except Exception as exc:
            logger.info("LLM reasoning unavailable, using internal engine: %s", exc)

    if draft is None:
        draft = reasoning_core.reason(
            filtered,
            query=text,
            constitution=intent.get("constitution"),
            cognitive_layer=cognitive_layer,
        )
    final = synthesizer.synthesize(draft, query=text)

    # Phase 3: Reflection (with timeout)
    reasoning_content = draft.get("debug", {}).get("llm", {}).get("reasoning", "")
    try:
        reflection_result = await asyncio.wait_for(
            reflection_engine.reflect(
                query=text,
                answer=final.get("answer", ""),
                sources=filtered,
                reasoning_content=reasoning_content,
                confidence=final.get("confidence", "UNKNOWN"),
            ),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        from reflection import AuditResult, ConfidenceEstimate
        from reflection.reflection_engine import ReflectionResult
        reflection_result = ReflectionResult(
            audit=AuditResult(issues=[], overall_quality=0.5, hallucination_risk=0.5, reasoning_coherence=0.5),
            confidence_estimate=ConfidenceEstimate(initial=0.5, calibrated=0.5, calibration_delta=0.0, rationale="reflection timed out"),
            improvements=[],
            memory_priority=0.3,
            reasoning_quality=0.5,
        )

    tags = ["retrieval", "terminal"]
    if cognitive_layer:
        tags.append(str(cognitive_layer))
    await _record_memory_turn(text, final, "retrieval", tags)

    # Phase 14: Wire continuous learner
    try:
        from learning.continuous_learner import continuous_learner
        await continuous_learner.learn_from_query(
            query=text,
            sources=filtered if filtered else sources,
            answer=str(final.get("answer", "")),
            confidence=str(final.get("confidence", "UNKNOWN")),
            tags=tags,
        )
    except Exception as exc:
        logger.debug("Continuous learner skipped: %s", exc)

    # Phase 11C: Update belief state
    answer_text = str(final.get("answer", ""))
    answer_confidence = str(final.get("confidence", "UNKNOWN"))
    if answer_confidence in ("CERTAIN", "PROBABLE") and answer_text:
        topic = (intent.get("domains", ["general"])[0] if intent.get("domains") else "general")
        existing = belief_store.get_beliefs_for_topic(topic)
        if not existing:
            belief_store.add_belief(
                topic=topic,
                claim=answer_text[:300],
                confidence=answer_confidence,
                source_turn=sid,
            )

    # Phase 11A: Record conversation turns
    conversation_buffer.add_turn(sid, ConversationTurn(
        role="user",
        text=text,
        intent=intent,
        dialogue_act=dialogue_decision.act.value,
    ))
    conversation_buffer.add_turn(sid, ConversationTurn(
        role="assistant",
        text=answer_text[:500],
        confidence=answer_confidence,
        dialogue_act=dialogue_decision.act.value,
    ))

    # Phase 4: Persist to PostgreSQL
    await persist_episode(
        prompt=text,
        answer=str(final.get("answer", "")),
        confidence=str(final.get("confidence", "UNKNOWN")),
        source="retrieval",
        tags=tags,
        kind="retrieval",
        importance=0.7 if final.get("confidence") == "CERTAIN" else 0.5,
    )
    await persist_reflection(text, str(final.get("answer", "")), reflection_result)
    await persist_context_snapshot(session_id, {
        "intent": intent,
        "sources_count": len(filtered),
        "conflicts": conflicts.get("conflicts", []),
        "cognitive_layer": cognitive_layer,
        "confidence": final.get("confidence"),
        "reasoning_quality": reflection_result.reasoning_quality,
    })

    response_source_items = filtered or sources
    response_sources = [
        Source(
            url=item.get("url", ""),
            title=item.get("title"),
            snippet=item.get("snippet"),
            source=item.get("source"),
            score=item.get("score"),
        )
        for item in response_source_items
        if item.get("url")
    ]

    debug_info = {
        "intent": intent,
        "truth_filter": filtered_payload["report"],
        "contradiction": conflicts,
        "evidence_graph": evidence_graph,
        "cognitive_layer": cognitive_layer,
    }
    if draft.get("debug"):
        debug_info["llm"] = draft["debug"].get("llm", {})
    debug_info["reflection"] = reflection_result.model_dump()
    debug_info["monologue"] = monologue_trace.model_dump()
    debug_info["reasoning_mode"] = reasoning_mode.value
    debug_info["dialogue"] = dialogue_decision.model_dump()
    debug_info["working_memory"] = {
        "turn_count": conversation_buffer.get_turn_count(sid),
        "active_topics": working_ctx.active_topics if working_ctx else [],
    }

    return AnswerResponse(
        query=text,
        answer=final.get("answer", ""),
        confidence=final.get("confidence", "UNKNOWN"),
        sources=response_sources,
        contradictions=[c.get("summary") for c in conflicts.get("conflicts", [])],
        gaps=final.get("gaps", []),
        citations=final.get("citations", []),
        tone=final.get("tone", "scientific"),
        debug=debug_info,
        dialogue_act=dialogue_decision.act.value,
        clarification_needed=False,
    )
