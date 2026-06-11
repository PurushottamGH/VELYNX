"""Core query pipeline — the answer_question() function and helpers."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sqlite3
import time
from pathlib import Path

from nltk.stem import PorterStemmer

from backend.learning.curriculum import resolve_chat_answer
from backend.learning.knowledge_tutor import resolve_learning_answer
from backend.memory.memory_manager import memory_manager
from backend.memory.vector_store import recall_answer
from backend.models.answer import AnswerResponse
from backend.models.source import Source
from backend.models.llm_client import llm_client
from backend.pipeline import (
    contradiction,
    intent_engine,
    seed_knowledge,
    reasoning_core,
    retrieval_mesh,
    synthesizer,
    truth_filter,
)
from backend.reflection.reflection_engine import reflection_engine
from backend.soul.soul_graph import apply_plasticity

# Phase 11: Conversational Cognition
from conversation.working_memory import conversation_buffer, ConversationTurn
from conversation.monologue import inner_monologue
from conversation.beliefs import belief_store
from conversation.dialogue_manager import dialogue_manager
from conversation.reasoning_modes import select_reasoning_mode, get_mode_config

logger = logging.getLogger("uvicorn")

SOUL_PATH = Path(__file__).parent.parent / "soul" / "concepts.json"
SOUL_EDGE_PATH = Path(__file__).parent.parent.parent / "data" / "concepts.json"
_STEMMER = PorterStemmer()

# Pre-compute stems for all soul concept names on module load
_SOUL_CONCEPT_STEMS: dict[str, str] = {}
_SOUL_EDGES: list[dict] = []
try:
    if SOUL_PATH.exists():
        raw = json.loads(SOUL_PATH.read_text())
        for name in raw:
            _SOUL_CONCEPT_STEMS[name] = _STEMMER.stem(name)
    if SOUL_EDGE_PATH.exists():
        edge_data = json.loads(SOUL_EDGE_PATH.read_text())
        _SOUL_EDGES = edge_data.get("edges", [])
except Exception:
    pass


def _stem_match(query_word: str, concept_name: str) -> bool:
    """Return True if the query word stems to the same root as the concept."""
    s_q = _STEMMER.stem(query_word.strip(",.!?;:'\"()[]{}"))
    s_c = _SOUL_CONCEPT_STEMS.get(concept_name, "")
    if not s_q or not s_c:
        return False
    return s_q == s_c or (len(s_q) >= 4 and s_q[:4] == s_c[:4])


def _get_edge_synthesis(matched: list[str]) -> str | None:
    """If >1 concept matched, look for edges connecting them and synthesize."""
    if len(matched) < 2:
        return None
    pairs = set()
    for e in _SOUL_EDGES:
        src = e.get("source", "")
        tgt = e.get("target", "")
        if src in matched and tgt in matched:
            pairs.add((src, tgt, e.get("relationship_type", ""), e.get("context", "")))
    if not pairs:
        # No explicit edges — generate a default bridging synthesis
        parts = []
        for i in range(len(matched) - 1):
            parts.append(
                f"{matched[i].capitalize()} and {matched[i+1]} are deeply connected human "
                f"experiences. {matched[i].capitalize()} shapes how we experience "
                f"{matched[i+1]}, and understanding both together gives a fuller "
                f"picture of the human condition than either alone."
            )
        return "\n\n".join(parts)
    # Build from found edges
    lines = []
    for src, tgt, rtype, ctx in pairs:
        lines.append(f"{src.capitalize()} {rtype} {tgt}: {ctx}")
    return "\n\n".join(lines)


def _build_soul_block(concept: str, data: dict) -> str:
    """Build a formatted soul response from a single concept's data."""
    core = data.get("core", "").strip()
    if not core:
        return ""
    parts = [core]
    not_list = data.get("what_it_is_not", [])
    if not_list:
        parts.append("It is not: " + ", ".join(not_list[:3]))
    situations = data.get("real_situations", [])
    if situations:
        s = situations[0]
        parts.append(f"In reality: {s.get('why', '')}")
    taught_by = data.get("taught_by", "")
    if taught_by:
        parts.append(f"(Taught by {taught_by})")
    return "\n\n".join(p for p in parts if p)


# ── VELYNX V2 soul pipeline ──────────────────────────────────────────────────


def _soul_lookup(query: str) -> dict | None:
    """
    V2 soul lookup using scenario engine + soul graph + embedding index.
    Handles direct, relational, and scenario-type queries that the legacy
    _soul_lookup may miss (e.g. "A man forgave someone who never apologized").
    """
    try:
        from cognition.scenario_engine import parse_scenario
        from soul.soul_graph import synthesize, get_edges, get_tensions
    except Exception:
        return None

    result = parse_scenario(query)
    if not result["concepts"]:
        return None

    soul_path = SOUL_PATH
    if not soul_path.exists():
        return None
    soul = json.loads(soul_path.read_text())

    qtype = result["query_type"]

    # Build concept data with edges/tensions
    concept_data = []
    for concept in result["concepts"][:3]:
        entry = soul.get(concept, {})
        concept_data.append({
            "name": concept,
            "entry": entry,
            "edges": get_edges(concept),
            "tensions": get_tensions(concept),
        })

    if qtype == "direct" and len(result["concepts"]) == 1:
        c = concept_data[0]
        entry = c["entry"]
        if isinstance(entry, dict):
            response = entry.get("definition", entry.get("core", str(entry)))
        else:
            response = str(entry)
    elif qtype in ("relational", "scenario"):
        response = result["arc"]
        if not response:
            names = [c["name"] for c in concept_data]
            response = synthesize(names)
            # synthesize() returns a generic stub when no edges exist —
            # fall through to legacy which builds richer formatted blocks
            if response and response.startswith("These concepts are deeply connected"):
                response = ""
    else:
        response = result["arc"] or str(concept_data[0]["entry"])

    if not response:
        return None

    return {
        "answer": response,
        "concepts": result["concepts"],
        "arc": result["arc"],
        "soul_used": True,
        "v2": True,
        "scores": result.get("scores", {}),
    }


def _soul_lookup_legacy(query: str) -> dict | None:
    """
    Legacy soul lookup using Porter stemming on query words and concept names.

    This is the original V1 implementation, preserved as a fallback.
    "forgave"  -> stem "forgiv" matches "forgiveness" -> stem "forgiv".
    Returns a dict with:
      - answer:      str  (combined soul definitions + any edge synthesis)
      - concepts:    list[str]  (all matched concept names)
      - soul_used:   True
    Returns None if nothing matches.
    """
    try:
        if not SOUL_PATH.exists():
            return None

        soul = json.loads(SOUL_PATH.read_text())
        query_words = query.lower().split()

        matched_concepts: list[str] = []
        for concept_name, data in soul.items():
            # 1) exact substring (fast path — keeps old behaviour)
            if concept_name in query.lower():
                matched_concepts.append(concept_name)
                continue
            # 2) stem match on any query word
            for qw in query_words:
                if _stem_match(qw, concept_name):
                    matched_concepts.append(concept_name)
                    break

        if not matched_concepts:
            return None

        # Deduplicate while preserving order
        seen: set[str] = set()
        ordered: list[str] = []
        for c in matched_concepts:
            if c not in seen:
                seen.add(c)
                ordered.append(c)

        # Build answer blocks for each matched concept
        blocks: list[str] = []
        for c in ordered:
            block = _build_soul_block(c, soul[c])
            if block:
                blocks.append(block)

        # If >1 concept matched, add edge synthesis
        synth = _get_edge_synthesis(ordered)
        if synth:
            blocks.append("── Relationship ──")
            blocks.append(synth)

        answer = "\n\n".join(blocks)

        return {
            "answer": answer,
            "concepts": ordered,
            "soul_used": True,
        }

    except Exception:
        return None


async def _record_memory_turn(query: str, response: dict, source: str, tags: list[str] | None = None, concept_tags: list[str] | None = None) -> None:
    confidence = str(response.get("confidence") or "UNKNOWN")
    if confidence == "UNKNOWN":
        return
    try:
        combined_tags = (tags or []) + (concept_tags or [])
        await memory_manager.store_episodic(
            query,
            str(response.get("answer") or ""),
            confidence=confidence,
            source=source,
            tags=combined_tags,
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


def _self_query(text: str) -> bool:
    lowered = text.lower()
    return any(p in lowered for p in [
        "what do you know", "describe yourself", "what are you",
        "how are you", "who are you", "what can you do",
        "what do you remember", "are you healthy",
    ])


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


_KG_DB = Path(__file__).parent.parent / "velynx_data" / "knowledge_graph" / "graph.db"

# Phase 45: Per-session curiosity state
_curiosity_session_state: dict = {}


def _persist_local(query: str, answer: str, confidence: str, session_id: str | None = None) -> None:
    if not _KG_DB.exists():
        return
    try:
        db = sqlite3.connect(str(_KG_DB))
        db.execute("CREATE TABLE IF NOT EXISTS sessions (session_id TEXT, query TEXT, answer TEXT, confidence TEXT, timestamp REAL)")
        ts = time.time()
        db.execute(
            "INSERT OR REPLACE INTO understandings (topic, summary, confidence, query_count, timestamp) "
            "VALUES (?, ?, ?, COALESCE((SELECT query_count FROM understandings WHERE topic=?), 0) + 1, ?)",
            (query[:80], answer[:500], confidence, query[:80], ts),
        )
        db.execute(
            "INSERT OR REPLACE INTO sessions (session_id, query, answer, confidence, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id or "default", query[:200], answer[:500], confidence, ts),
        )
        db.commit()
        db.close()
    except Exception:
        pass


async def answer_question(text: str, session_id: str | None = None) -> AnswerResponse:
    """Core query pipeline — processes a question through the full VELYNX stack."""
    sid = session_id or "default"
    conv_context = conversation_buffer.get_context_window(sid, max_turns=8)
    working_ctx = conversation_buffer.get_working_context(sid)

    # ── Priority classification (informational only) ──────────────
    from cognition.priority_router import classify as get_priority
    _priority = get_priority(text)

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

    # ── Soul concepts — resonance activated ──────────────
    soul_answer = _soul_lookup(text)  # V2: scenario engine + soul graph
    if not soul_answer:
        soul_answer = _soul_lookup_legacy(text)  # Legacy: stem matching + edge synthesis
    resonance_context = ""
    top_concepts: list[str] = []
    resonance_scores: dict[str, float] = {}
    epistemic_states: dict[str, str] = {}
    recalled_memory: dict | None = None
    if soul_answer:
        scores = soul_answer.get("scores", {})
        if scores:
            # --- Phase 46: Epistemic Honesty Injection ---
            from backend.soul.soul_graph import get_epistemic_state
            top_concepts = list(scores.keys())[:5]
            epistemic_states = get_epistemic_state(top_concepts)
            resonance_scores = {c: round(scores[c], 3) for c in top_concepts}

            enriched_scores = []
            for c in top_concepts:
                score = resonance_scores[c]
                state = epistemic_states.get(c, "UNKNOWN")
                enriched_scores.append(f"{c}:{score} ({state})")

            resonance_context = (
                "SYSTEM [RESONANCE FIELD ACTIVE]: The user's query activated "
                "the following deep cognitive concepts: " + ", ".join(enriched_scores)
                + "\nCRITICAL INSTRUCTION: If a concept is marked INFERRED or UNCERTAIN, "
                "you MUST explicitly communicate this doubt to the user "
                "(e.g. 'I am inferring this, but I am not certain...'). "
                "Do not state uncertain concepts as absolute facts."
            )
            # ---------------------------------------------

    # --- Phase 47: Episodic Recall — fetch memory tagged with primary concept ---
    if top_concepts and resonance_context:
        primary_concept = top_concepts[0]
        try:
            past_eps = await asyncio.wait_for(
                memory_manager.recall_by_tag(primary_concept, limit=1),
                timeout=3.0,
            )
            if past_eps:
                past_prompt = past_eps[0].entry.metadata.get("prompt", "")
                past_answer = past_eps[0].entry.metadata.get("answer", "")[:200]
                recalled_memory = {
                    "concept": primary_concept,
                    "prompt": past_prompt,
                    "answer": past_answer,
                }
                episodic_context = (
                    f"\nEPISODIC RECALL: The last time you discussed '{primary_concept}', "
                    f"the user said: '{past_prompt}'. "
                    f"You answered: '{past_answer}'. "
                    f"Use this to contextualize your response."
                )
                resonance_context += episodic_context
        except asyncio.TimeoutError:
            logger.debug("Episodic recall timed out (3s)")
        except Exception as exc:
            logger.debug("Episodic recall failed: %s", exc)
    # -----------------------------------------------------------------

    # ── Self-model — 'what do you know', 'describe yourself' ─
    if _self_query(text):
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

    # ── Knowledge Graph fast path ──────────────
    if not resonance_context:
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

    # Prefer legacy associative memory for definition-like prompts even when the
    # user isn't explicitly asking to "remember/recall".
    # This avoids cases where generic retrieval/LLM answers unrelated "meanings".
    definition_intent = any(
        phrase in text.lower()
        for phrase in [
            "what does",
            "what do ",
            "what is",
            "what's",
            "mean ",
            "meaning",
            "define",
            "definition",
        ]
    )

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

    # If this looks like a definition request and we have a legacy hit, return it.
    # Use a soft threshold based on legacy scoring done in vector_store.
    if remembered is not None and definition_intent:
        mem = (remembered.get("debug") or {}).get("memory") or {}
        legacy_score = float(mem.get("score") or 0.0)
        if legacy_score >= 0.35:
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
                resonance_context=resonance_context or None,
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
                    resonance_context=ctx.resonance_context or None,
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
    await _record_memory_turn(text, final, "retrieval", tags, concept_tags=top_concepts[:3])

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

    # Phase 4: Persist locally
    _persist_local(text, str(final.get("answer", "")),
                   str(final.get("confidence", "UNKNOWN")), session_id)

    # Auto-save every answered query to KG
    conf_label = final.get("confidence", "UNKNOWN")
    if conf_label not in ("LOW", "UNKNOWN"):
        from memory.knowledge_graph import KnowledgeGraph
        knowledge_graph = KnowledgeGraph()
        await knowledge_graph.store_answer(
            query=text,
            answer=str(final.get("answer", ""))[:500],
            confidence=0.7 if conf_label == "CERTAIN" else 0.5,
            sources=final.get("sources", []),
        )

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

    # ── Fix 3: Soul confidence calibration ──
    # If the full pipeline ran (soul wasn't used) and the draft says CERTAIN,
    # clamp to LOW. The pipeline cannot be CERTAIN without soul anchoring.
    final_confidence = final.get("confidence", "UNKNOWN")
    if final_confidence == "CERTAIN":
        final_confidence = "LOW"

    # --- Phase 42: Synaptic Plasticity Trigger ---
    if soul_answer and soul_answer.get('concepts') and final_confidence in ("CERTAIN", "PROBABLE"):
        asyncio.to_thread(apply_plasticity, soul_answer.get('scores', {}), source_quality=0.6)
    # ---------------------------------------------

    # --- Phase 45: Curiosity Engine — inject one question per session ---
    from velynx.graph.curiosity_engine import select_curiosity_question
    _session_state = _curiosity_session_state.setdefault(sid, {"has_asked": False})
    curiosity_q = select_curiosity_question(
        _session_state.get("has_asked", False),
        soul_answer.get("scores", {}) if soul_answer else {},
    )
    if curiosity_q:
        final["answer"] += curiosity_q
        _session_state["has_asked"] = True
    # -----------------------------------------------------------

    # --- Phase 48: Metacognitive Penalty Trigger ---
    if soul_answer and soul_answer.get("concepts") and final_confidence in ("LOW", "UNKNOWN"):
        from backend.soul.soul_graph import apply_metacognitive_penalty
        asyncio.to_thread(apply_metacognitive_penalty, soul_answer["concepts"])
    # -----------------------------------------------

    debug_info = {
        "intent": intent,
        "truth_filter": filtered_payload["report"],
        "contradiction": conflicts,
        "evidence_graph": evidence_graph,
        "cognitive_layer": cognitive_layer,
        "soul_used": False,
        "confidence_clamped": final_confidence != final.get("confidence", "UNKNOWN"),
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
        confidence=final_confidence,
        sources=response_sources,
        contradictions=[c.get("summary") for c in conflicts.get("conflicts", [])],
        gaps=final.get("gaps", []),
        citations=final.get("citations", []),
        tone=final.get("tone", "scientific"),
        debug=debug_info,
        dialogue_act=dialogue_decision.act.value,
        clarification_needed=False,
        resonance_scores=resonance_scores,
        epistemic_states=epistemic_states,
        recalled_memory=recalled_memory,
    )
