"""Core query pipeline — the answer_question() orchestrator.

answer_question() imports and delegates to specialised modules under
``backend/pipeline/`` for all concrete work.  This file owns only:
  1. Module-level engine singletons (KG, ReasoningEngine, AnswerSynthesizer).
  2. The request-scoped orchestration flow.
  3. Wiring that is inherently cross-cutting (conversation state, reflection
     dispatch, continuous learning, plasticity, curiosity).
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from backend.cognition.answer_synthesizer import AnswerSynthesizer
from backend.cognition.reasoning_engine import ReasoningEngine
from backend.learning.curriculum import resolve_chat_answer
from backend.learning.knowledge_tutor import resolve_learning_answer
from backend.memory.memory_manager import memory_manager
from backend.models.answer import AnswerResponse
from backend.models.source import Source
# Existing backend/pipeline/* sub-modules (contradiction, intent etc.).
from backend.pipeline import (
    contradiction,
    intent_engine,
    seed_knowledge,
    retrieval_mesh,
    truth_filter,
)
# Newly extracted micro-modules — each owns a single concern.
from backend.pipeline.knowledge_router import handle_kg_fast_path
from backend.pipeline.persistence import persist_local, record_memory_turn
from backend.pipeline.reasoning_wiring import (
    SYNTH_CONFIDENCE_MAP,
    compute_thermodynamic_state,
    contains_unresolved_pronoun,
    extract_query_concepts,
    retrieve_triples,
)
from backend.knowledge.world_model_context import (
    schema_context_for_concepts,
    world_model_facts_for_concepts,
)
from backend.memory.working_memory import working_memory_manager
from backend.knowledge.normalizer import concept_normalizer
from backend.knowledge.predicate_resolver import extract_predicate
from backend.pipeline.agentic_loop import agentic_controller
from backend.pipeline.reflection_router import run_reflection
from backend.pipeline.reflex import is_declarative_statement, reflex_response
from backend.pipeline.resonance import build_resonance_context, fetch_episodic_recall
from backend.pipeline.self_router import handle_self_query
# Phase 61: Episodic Narrative Memory (record history + narrate causal chains).
from backend.memory.episodic import (
    EpisodeKind,
    episodic_manager,
    episodic_narrative_handler,
    extract_learning_subject,
    narrative_compressor,
)
# Phase 60.2: Self-Referential introspection (router + aggregator + composer).
from backend.cognition.self_model import (
    QueryType,
    extract_target_entity,
    is_negative_epistemic_query,
    self_context_aggregator,
    self_query_router,
    self_referential_graph,
    self_response_composer,
)
from backend.pipeline.soul_router import soul_lookup, soul_lookup_legacy
# Phase 11: Conversational Cognition
from backend.conversation.beliefs import belief_store
from backend.conversation.dialogue_manager import dialogue_manager
from backend.conversation.monologue import inner_monologue
from backend.conversation.reasoning_modes import get_mode_config, select_reasoning_mode
from backend.conversation.working_memory import ConversationTurn, conversation_buffer

logger = logging.getLogger("uvicorn")

# ── Native deterministic cognitive engines (no LLMs) ──────────────────────────
# A single ReasoningEngine + AnswerSynthesizer pair is reused across requests.
# The symbolic knowledge graph supplies deterministic (subject, predicate,
# object) triples for graph traversal. All three are LLM-free.
try:
    from backend.knowledge.knowledge_graph import KnowledgeGraph as _SymbolicKnowledgeGraph

    _symbolic_kg = _SymbolicKnowledgeGraph()
    _symbolic_kg.build()  # idempotent: seeds concepts/relationships only if empty
except Exception as _exc:  # pragma: no cover - defensive, never block startup
    logger.warning("Symbolic knowledge graph unavailable: %s", _exc)
    _symbolic_kg = None

_reasoning_engine = ReasoningEngine(_symbolic_kg, None)
_answer_synthesizer = AnswerSynthesizer()

# Phase 62 — install the World Model registry so entity mentions inject their
# inheritance-resolved schema into the reasoning context. Defensive: a failure
# here leaves injection a no-op (schema_context_for_concepts returns []) rather
# than blocking startup.
#
# Phase 62 (foundational ontology): the runtime registry now combines the
# data-driven physical taxonomy (PhysicalObject/Vehicle/Electronics/Person,
# loaded from backend/data/world_ontology.json) with the existing 3D-software
# taxonomy (Software/DesktopApplication/ThreeDModelingApp) into one registry,
# so the two coexist. The combined registry also backs the schema gatekeeper
# that validates TEACH commands. install_combined_registry degrades to
# install_default_registry (software-only) if the ontology file is missing.
try:
    from backend.knowledge.ontology_loader import install_combined_registry

    install_combined_registry()
except Exception as _exc:  # pragma: no cover - never block startup
    logger.warning("Combined ontology unavailable; trying software-only: %s", _exc)
    try:
        from backend.knowledge.world_model_context import install_default_registry

        install_default_registry()
    except Exception as _exc2:  # pragma: no cover - never block startup
        logger.warning("World model registry unavailable: %s", _exc2)

# Phase 45: Per-session curiosity state
_curiosity_session_state: dict = {}


def _format_consolidation_contradictions(raw) -> list[str]:
    """Render ConsolidationReport.contradictions (list[dict]) to list[str].

    ``AnswerResponse.contradictions`` is typed ``list[str]``; the consolidator
    emits a list of dicts shaped like
    ``{"subject", "relation", "old_object", "new_object", "type", "resolution"}``
    (see ``backend.knowledge.consolidator``). We render each into a single
    human-readable line, e.g.::

        "User's favorite movie: 'Interstellar' -> 'Avatar' (overwrite)"

    so the value satisfies the model's type AND gives the live-fire harness a
    non-empty, meaningful ``contradictions`` list to flag. Defensive: tolerates
    missing keys and non-dict entries, and never raises.
    """
    out: list[str] = []
    for c in raw or []:
        if isinstance(c, dict):
            subject = c.get("subject", "?")
            relation = c.get("relation", "")
            old = c.get("old_object", "?")
            new = c.get("new_object", "?")
            resolution = c.get("resolution")
            slot = f"{subject} {relation}".strip()
            line = f"{slot}: {old!r} -> {new!r}"
            if resolution:
                line += f" ({resolution})"
            out.append(line)
        elif c:
            out.append(str(c))
    return out


def _turn_concepts_for_memory(text: str, resp: AnswerResponse, injected: list[str]) -> list[str]:
    """Collect the concepts to remember for this turn, normalized.

    Source priority:
      1. Subjects/objects of any facts just learned (``debug.learned_triples``)
         — the richest, most reliable signal on the knowledge-acquisition path.
      2. Concepts already resolved/injected for this turn (carry referents
         forward so a chain of pronouns keeps its antecedent).
      3. A lightweight keyword extraction from the user's text as a fallback,
         so even a plain question still leaves a topical breadcrumb.
    All values pass through the Phase-54 normalizer so the buffer holds the same
    canonical surface forms the graph and read-path use.
    """
    concepts: list[str] = []

    debug = resp.debug if isinstance(resp.debug, dict) else {}
    for triple in debug.get("learned_triples") or []:
        try:
            subj, _rel, obj = triple[0], triple[1], triple[2]
        except Exception:
            continue
        concepts.append(concept_normalizer.normalize(subj))
        concepts.append(concept_normalizer.normalize(obj))

    concepts.extend(injected or [])

    try:
        for kw in intent_engine._keywords(text) or []:
            concepts.append(concept_normalizer.normalize(kw, preserve_case=True))
    except Exception:
        pass

    return [c for c in concepts if c]


def handle_self_referential(text: str) -> AnswerResponse | None:
    """Phase 60.2 — answer a SELF_REFERENTIAL query by introspection.

    Classifies the query frame; only a SELF_REFERENTIAL query that names an
    explicit target entity ("what do you / don't you know about X") is handled
    here. We compile the entity's Epistemic State via the Phase 60.1 aggregator
    and render it with the deterministic :class:`SelfResponseComposer`, returning
    the string DIRECTLY — bypassing semantic search, retrieval and synthesis.

    Returns ``None`` to fall through to the standard pipeline when the query is
    not self-referential, or is self-referential but names no entity (e.g. a
    purely personal "where is my favourite cafe?" — left to the normal path so
    agentic planning and personal-fact handling are preserved).
    """
    try:
        route = self_query_router.classify(text)
    except Exception as exc:
        logger.debug("Self-query routing failed for %r: %s", text[:40], exc)
        return None

    if route != QueryType.SELF_REFERENTIAL.value:
        return None

    entity = extract_target_entity(text)
    if not entity:
        # Self-referential but no explicit topic entity — defer to the standard
        # pipeline (covers personal "my ..." queries and agentic multi-hop goals).
        return None

    try:
        # Component 4: keep VELYNX's canonical self node present (idempotent).
        self_referential_graph.ensure_self_node()
        # Component 5: aggregate epistemic state and render it deterministically.
        # A negated framing ("what do you NOT know about X") is rendered gaps-
        # first by the composer, so it needs a distinct paragraph from the
        # positive "what do you know about X" framing.
        ctx = self_context_aggregator.aggregate(entity)
        is_negative = is_negative_epistemic_query(text)
        answer = self_response_composer.compose(ctx, is_negative_query=is_negative)
    except Exception as exc:
        logger.warning("Self-referential introspection failed for %r: %s", entity, exc)
        return None

    logger.info(
        "Self-referential introspection: entity=%r route=%s negative=%s",
        entity, route, is_negative,
    )
    return AnswerResponse(
        query=text,
        answer=answer,
        confidence="CERTAIN",
        source="self_referential",
        sources=[],
        contradictions=[],
        gaps=ctx.epistemic_state.get("unknown", []),
        citations=[],
        tone="introspective",
        debug={
            "self_referential": True,
            "route": route,
            "negative_query": is_negative,
            "target_entity": ctx.target_entity,
            "self_context": ctx.to_dict(),
        },
    )


def handle_narrative_query(text: str) -> AnswerResponse | None:
    """Phase 61 — answer "How did you learn about X?" from episodic memory.

    Detects an autobiographical "how did you learn / come to know X" question,
    then asks the :class:`NarrativeCompressor` to traverse the causal episode
    chain (failure -> goal -> knowledge-acquired) and render a deterministic
    story. Returns ``None`` (fall through to the normal pipeline) when the query
    is not an episodic-history question.
    """
    try:
        # Gate on the autobiographical "how did you learn X" shape so normal
        # questions fall straight through to the standard pipeline.
        if not extract_learning_subject(text):
            return None
        answer = episodic_narrative_handler.narrate(text)
    except Exception as exc:
        logger.debug("Episodic narrative failed for %r: %s", text[:40], exc)
        return None

    if not answer:
        return None

    logger.info("Episodic narrative answered: %r", text[:60])
    return AnswerResponse(
        query=text,
        answer=answer,
        confidence="CERTAIN",
        source="episodic_memory",
        sources=[],
        contradictions=[],
        gaps=[],
        citations=[],
        tone="narrative",
        debug={"episodic_narrative": True},
    )


async def answer_question(text: str, session_id: str | None = None) -> AnswerResponse:
    """Public query entry point with Phase 55 working-memory integration.

    Wraps :func:`_answer_question_impl` so short-term memory is handled in ONE
    place regardless of which internal branch answers the turn (reflex,
    knowledge-acquisition commit, learning tutor, KG fast-path, symbolic
    reasoning, ...). Responsibilities:

    * Resolve referential pronouns: if the message contains "it"/"there"/... and
      the session has active concepts, those concepts are the resolved
      antecedent and are exposed as ``debug.working_memory.injected_concepts``.
      (The impl additionally folds them into ``extract_query_concepts`` so the
      reasoning path actually retrieves on them when it is the branch taken.)
    * Record this turn's concepts into the rolling buffer so the NEXT turn has
      an antecedent — done for every turn, every path, fixing the commit-path
      short-circuit where the early return previously skipped the update.
    * Attach a ``working_memory`` debug payload (turn_count, pronoun_detected,
      injected_concepts, active_topics) to the response.

    The user's ``query`` is never rewritten — resolution is an internal
    expansion, not a mutation of the caller's words.
    """
    sid = session_id or "default"

    # Snapshot the buffer state BEFORE this turn so injection reflects prior
    # turns only (the current turn hasn't been recorded yet).
    active_topics = working_memory_manager.get_active_concepts(sid)
    pronoun_detected = contains_unresolved_pronoun(text)
    injected_concepts = list(active_topics) if (pronoun_detected and active_topics) else []

    resp = await _answer_question_impl(text, session_id)

    # Record this turn's concepts so the next turn can resolve back to them.
    working_memory_manager.update(sid, _turn_concepts_for_memory(text, resp, injected_concepts))

    wm_debug = {
        "turn_count": working_memory_manager.turn_count(sid),
        "pronoun_detected": pronoun_detected,
        "injected_concepts": injected_concepts,
        "active_topics": active_topics,
    }
    try:
        if isinstance(resp.debug, dict):
            resp.debug.setdefault("working_memory", wm_debug)
        else:
            resp.debug = {"working_memory": wm_debug}
    except Exception:
        logger.debug("Failed to attach working_memory debug payload", exc_info=True)

    return resp


async def _answer_question_impl(text: str, session_id: str | None = None) -> AnswerResponse:
    """Core query pipeline — processes a question through the full VELYNX stack.

    Wrapped by :func:`answer_question`, which layers Phase 55 working-memory
    bookkeeping (pronoun resolution context + per-turn recording + the
    ``debug.working_memory`` payload) uniformly across every return path.
    """
    sid = session_id or "default"

    # ── Reflex layer — instant, graph-bypassing responses ──────────
    reflex = reflex_response(text)
    if reflex is not None:
        logger.info("Reflex hit (%s) for %r", reflex.debug.get("reflex"), text[:40])
        return reflex

    # ── Knowledge Acquisition layer (Phase 53) ─────────────────────
    if is_declarative_statement(text):
        try:
            from backend.knowledge.fact_extractor import extract_and_store_facts

            learned = extract_and_store_facts(text)
        except Exception as exc:
            logger.warning("Knowledge acquisition failed for %r: %s", text[:40], exc)
            learned = []

        if learned:
            logger.info("Knowledge acquisition: learned %d triple(s) for %r",
                        len(learned), text[:40])

            # ── Phase 53.1: Knowledge Consolidation ────────────────
            # ── Phase 59.1: Curiosity Execution Loop ───────────────
            # Consolidate the freshly-learned triples into the active KG and,
            # once that lands, scan the updated graph for attribute gaps and
            # autonomously pursue them via the Phase 58 planner. Dispatched as a
            # single fire-and-forget task so it never blocks this user turn.
            #
            # In TEST MODE we still consolidate (tests depend on it) but DO NOT
            # run the proactive curiosity loop — it would otherwise wake up mid-
            # test, get curious about freshly-taught entities, and write back
            # into the graph, creating race conditions / pollution.
            # Capture any functional-predicate contradictions the consolidator
            # flags so the TEACH response can surface them (the live-fire harness
            # checks ``resp.contradictions``). Initialized before the dispatch so
            # it is always defined, even if dispatch raises. Rendered to strings
            # because AnswerResponse.contradictions is typed ``list[str]`` while
            # ConsolidationReport.contradictions is a ``list[dict]``; passing the
            # dicts straight through would fail Pydantic validation.
            contradictions_found: list[str] = []
            try:
                import os as _os

                # Consolidate SYNCHRONOUSLY on the TEACH turn (both test and live
                # mode) so the freshly-detected functional-predicate contradiction
                # is attached to THIS teach response. The contradiction is a
                # property of the act of teaching a conflicting value — the
                # subsequent retrieval QUERY ("what is my favorite movie?") never
                # runs consolidation, so it can never carry the signal. The live-
                # fire harness therefore asserts the contradiction on the TEACH
                # turn (see backend/tests/live_fire_harness.py).
                from backend.knowledge.consolidator import consolidate_pending_async

                report = await consolidate_pending_async()
                contradictions_found = _format_consolidation_contradictions(
                    getattr(report, "contradictions", None)
                )

                # In live (non-test) mode, still pursue autonomous curiosity on
                # the now-updated graph — but DON'T re-consolidate (we just did
                # it synchronously above), so dispatch with consolidate=False as
                # a fire-and-forget task that never blocks this user turn.
                if not _os.environ.get("VELYNX_TEST_MODE"):
                    from backend.agency.curiosity_executor import consolidate_and_explore

                    asyncio.create_task(consolidate_and_explore(consolidate=False))
            except Exception as exc:
                logger.warning("Consolidation/curiosity dispatch failed for %r: %s",
                               text[:40], exc)

            # ── Phase 55: Working Memory ───────────────────────────
            # NOTE: the buffer is updated for EVERY turn (including this
            # short-circuiting commit path) by the ``answer_question`` wrapper,
            # which reads ``debug.learned_triples`` below to recover the
            # subject/object concepts just learned. Keeping the bookkeeping in
            # one place guarantees a follow-up like "where is it?" always finds
            # an antecedent, no matter which branch answered the turn.

            # ── Phase 61: Episodic memory ──────────────────────────
            # A user-taught fact is a consequential life event. Record a
            # KNOWLEDGE_ACQUIRED episode; the manager links it (by entity) to any
            # prior GOAL_CREATED episode, so "How did you learn X?" can replay the
            # full goal -> learned chain. Best-effort.
            try:
                subject = str(learned[0][0]) if learned and learned[0] else ""
                if subject:
                    episodic_manager.record_knowledge_acquired(
                        subject,
                        triples=[list(t) for t in learned],
                        summary=f"I was told: {text.strip()}",
                        session_id=sid,
                        source="user",
                    )
            except Exception as exc:
                logger.debug("Episodic: knowledge-acquired logging failed: %s", exc)

            # ── Phase 61: Goal satisfaction ────────────────────────
            # A user-taught fact may resolve an outstanding curiosity goal. Mark
            # any matching PENDING goal SATISFIED (PENDING -> SATISFIED) and let
            # the curiosity layer log a KNOWLEDGE_ACQUIRED episode tagged to the
            # goal's entity/attribute, so "How did you learn X?" can replay the
            # full failure -> gap -> acquisition chain. This runs on the request
            # path (independent of the background curiosity executor, which is
            # suppressed in TEST MODE). Best-effort.
            try:
                from backend.agency.curiosity import mark_goals_satisfied_from_triples

                mark_goals_satisfied_from_triples(
                    [list(t) for t in learned], session_id=sid,
                )
            except Exception as exc:
                logger.debug("Curiosity: goal-satisfaction from triples failed: %s", exc)

            return AnswerResponse(
                query=text,
                answer="I have committed that to memory.",
                confidence="CERTAIN",
                source="knowledge_acquisition",
                sources=[],
                contradictions=contradictions_found,
                gaps=[],
                citations=[],
                tone="friendly",
                debug={
                    "knowledge_acquisition": True,
                    "learned_triples": [list(t) for t in learned],
                },
            )

    # ── Episodic narrative (Phase 61) ──────────────────────────────
    # "How did you learn about X?" is answered from VELYNX's own history by
    # replaying the causal episode chain — before any external retrieval.
    narrative = handle_narrative_query(text)
    if narrative is not None:
        return narrative

    # ── Self-referential introspection (Phase 60.2) ────────────────
    # "What do you / don't you know about X" is a question about VELYNX's OWN
    # knowledge, not the world. Route it through the self-model: compile X's
    # Epistemic State and render it deterministically, bypassing the standard
    # semantic-search / retrieval / synthesis path entirely.
    self_ref = handle_self_referential(text)
    if self_ref is not None:
        return self_ref

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

    # ── Soul concepts — resonance activated ───────────────────────
    soul_answer = soul_lookup(text)  # V2: scenario engine + soul graph
    if not soul_answer:
        soul_answer = soul_lookup_legacy(text)  # Legacy: stem matching + edge synthesis

    resonance_context = ""
    top_concepts: list[str] = []
    resonance_scores: dict[str, float] = {}
    epistemic_states: dict[str, str] = {}
    recalled_memory: dict | None = None

    resonance_context, top_concepts, resonance_scores, epistemic_states = (
        build_resonance_context(soul_answer)
    )

    # --- Phase 47: Episodic Recall ---
    recalled_memory, resonance_context = await fetch_episodic_recall(
        memory_manager, top_concepts, resonance_context
    )

    # ── Self-model ────────────────────────────────────────────────
    self_response = await handle_self_query(text)
    if self_response is not None:
        return self_response

    # ── Agentic planning (Phase 57) ───────────────────────────────
    # Multi-hop goals (e.g. "population of the city where my favorite coffee
    # shop is located") cannot be answered by a single retrieval. When the
    # deterministic gate fires, decompose the goal into an explicit DAG and
    # execute it, bypassing the single-pass reasoning block below. The plan is
    # attached to the debug payload for inspection.
    if agentic_controller.should_plan(text):
        plan = agentic_controller.formulate_plan(text)
        logger.info("Agentic planning engaged for %r: %d-step plan", text[:60], len(plan.steps))
        synthesis = await agentic_controller.execute_plan(plan)
        agentic_answer = {
            "answer": synthesis["answer"],
            "confidence": synthesis["confidence"],
            "citations": synthesis.get("citations", []),
            "gaps": [],
            "tone": "analytical",
            "source": "agentic",
            "debug": {"agentic": True, "plan": plan.to_dict()},
        }
        await record_memory_turn(text, agentic_answer, "agentic", ["agentic", "planning"])
        return AnswerResponse(
            query=text,
            answer=agentic_answer["answer"],
            confidence=agentic_answer["confidence"],
            sources=[],
            contradictions=[],
            gaps=[],
            citations=agentic_answer["citations"],
            tone="analytical",
            debug=agentic_answer["debug"],
        )

    # ── Knowledge Graph fast path ──────────────────────────────────
    kg_response = await handle_kg_fast_path(text, resonance_context)
    if kg_response is not None:
        return kg_response

    # ── Learning tutor / curriculum / seed knowledge ──────────────
    learning = await resolve_learning_answer(text)
    if learning is not None:
        tags = ["deterministic", "terminal"]
        if learning.get("cognitive_layers"):
            tags.extend(learning.get("cognitive_layers"))
        await record_memory_turn(text, learning, "learning_tutor", tags)
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
        await record_memory_turn(text, local, "curriculum", ["curriculum", "terminal"])
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
        await record_memory_turn(text, seeded, "seed_knowledge", ["seeded", "terminal"])
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

    # ── Semantic recall (with hard timeout) ────────────────────────
    semantic_results = []
    try:
        semantic_results = await asyncio.wait_for(
            memory_manager.recall(text, limit=1, kinds=["episodic", "semantic"]),
            timeout=3.0,
        )
    except asyncio.TimeoutError:
        logger.debug("Semantic recall timed out (3s)")
    except Exception as exc:
        logger.debug("Semantic recall failed: %s", exc)

    # Semantic recall — KG provenance tagging (Phase 53.1)
    if semantic_results and semantic_results[0].score >= 0.72:
        hit = semantic_results[0]

        entry_source = getattr(hit.entry, "source", "") or ""
        entry_rels = (hit.entry.metadata or {}).get("relationships") or []
        fact_text = hit.entry.text
        is_kg_fact = (
            entry_source == "consolidation"
            or "->" in fact_text
            or any("->" in str(r) for r in entry_rels)
        )

        if is_kg_fact:
            kg_confidence = "CERTAIN" if hit.score >= 0.9 else "PROBABLE"
            kg_answer = f"{fact_text} [KG]"
            kg_debug = {
                "kg_hit": True,
                "kg": {
                    "fact": fact_text,
                    "relationships": entry_rels,
                    "score": hit.score,
                    "source": entry_source or "knowledge_graph",
                },
                "reasoning_trace": [
                    f"knowledge_graph: {fact_text} (score={hit.score:.3f})"
                ],
                "memory": {
                    "kind": hit.entry.kind,
                    "score": hit.score,
                    "match_reason": hit.match_reason,
                },
            }
            kg_remembered = {
                "answer": kg_answer,
                "confidence": kg_confidence,
                "citations": ["[KG]"],
                "gaps": [],
                "tone": "human",
                "source": "knowledge_graph",
                "debug": kg_debug,
            }
            await record_memory_turn(
                text, kg_remembered, "knowledge_graph", ["knowledge_graph", "kg"]
            )
            return AnswerResponse(
                query=text,
                answer=kg_answer,
                confidence=kg_confidence,
                source="knowledge_graph",
                sources=[],
                contradictions=[],
                gaps=[],
                citations=["[KG]"],
                tone="human",
                debug=kg_debug,
            )

        # ── Non-KG (episodic/associative) hit: fall through ────
        remembered = {
            "answer": hit.entry.metadata.get("answer", hit.entry.text),
            "confidence": hit.entry.confidence,
            "kind": hit.entry.kind,
            "score": hit.score,
        }

    # ── Intent decomposition & retrieval ──────────────────────────
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

    # ── Native symbolic reasoning (no LLMs) ───────────────────────────────
    # Phase 55 — Working Memory injection. Pull this session's recently
    # discussed concepts; extract_query_concepts only folds them in when the
    # message has an unresolved pronoun ("where is it?"), resolving the
    # referent to the previous turn's topic. Buffer bookkeeping + the
    # ``working_memory`` debug payload are handled uniformly by the
    # ``answer_question`` wrapper so EVERY return path is covered.
    wm_concepts = working_memory_manager.get_active_concepts(sid)
    query_concepts = extract_query_concepts(
        text, intent, top_concepts, working_memory_concepts=wm_concepts
    )
    retrieved_triples = retrieve_triples(query_concepts, _symbolic_kg, query=text)
    thermodynamic_state = compute_thermodynamic_state(conflicts, len(filtered))

    # Phase 62 — World Model schema injection. If any extracted concept names a
    # registered Entity (e.g. "Blender"), pull its fully evaluated profile —
    # every own + inherited attribute with defaults filled — rendered to text.
    # These blocks are folded into ``episodic_context`` below so the reasoner
    # and the LLM synthesiser receive the entity's structured attributes
    # (license_model: GPL, vendor: Blender Foundation, ...) instead of the bare
    # token. Lookups are memoised per entity, so this adds no live-loop latency.
    try:
        world_model_context = schema_context_for_concepts(query_concepts)
    except Exception as exc:  # injection must never break the answer path
        world_model_context = []
        logger.debug("World model injection skipped: %s", exc)

    # Phase 62.1 — structured ontology triples for the SAME concepts. Unlike the
    # text blocks above (which only bias scalar salience as episodic_context),
    # these flow into the reasoner's fact pool as first-class edges so inherited
    # attributes (e.g. mobility_type=wheeled) participate in pathfinding and let
    # the engine answer inheritance questions it was never explicitly taught.
    try:
        world_model_facts = world_model_facts_for_concepts(query_concepts)
    except Exception as exc:  # injection must never break the answer path
        world_model_facts = []
        logger.debug("World model fact injection skipped: %s", exc)

    # Predicate grounding for contradiction scoping. Lift the user's relation
    # verb ("Who *created* Blender?" -> "create") so the reasoner only flags —
    # and only penalizes confidence for — conflicts on THAT predicate. Unrelated
    # "[be]" disagreements on the same entity must not tank the answering edge.
    try:
        query_predicate = extract_predicate(text)
    except Exception:
        query_predicate = ""

    # Episodic context = recent recall + any explicitly recalled turn.
    episodic_context: list[str] = []
    # Phase 62 — prepend World Model schema blocks so the entity's structured,
    # inheritance-resolved attributes lead the context the reasoner/synthesiser
    # consume (they are higher-signal than free-form recall for typed entities).
    episodic_context.extend(world_model_context)
    for hit in semantic_results or []:
        try:
            episodic_context.append(hit.entry.metadata.get("answer") or hit.entry.text)
        except Exception:
            continue
    if recalled_memory:
        episodic_context.append(
            f"{recalled_memory.get('prompt', '')} {recalled_memory.get('answer', '')}".strip()
        )

    logger.info(
        "Symbolic reasoning: %d concept(s), %d triple(s), thermo=%.2f",
        len(query_concepts), len(retrieved_triples), thermodynamic_state,
    )

    reasoning_trace = _reasoning_engine.reason(
        query_concepts=query_concepts,
        retrieved_triples=retrieved_triples,
        episodic_context=episodic_context,
        thermodynamic_state=thermodynamic_state,
        query_predicate=query_predicate,
        world_model_facts=world_model_facts,
    )

    # ── Synthesize the symbolic trace into natural language ───────────────
    synth_result = await _answer_synthesizer.synthesize(text, reasoning_trace)

    mapped_confidence = SYNTH_CONFIDENCE_MAP.get(
        synth_result.confidence_label, "UNKNOWN"
    )
    final = {
        "answer": synth_result.text,
        "confidence": mapped_confidence,
        "gaps": list(reasoning_trace.unresolved_concepts),
        "citations": [f"[KG] {s}" for s in synth_result.sources],
        "tone": "scientific",
        "sources": [],
        "debug": {"reasoning_trace": reasoning_trace.to_dict()},
    }

    # Phase 3: Reflection (with timeout)
    reasoning_content = "; ".join(str(p) for p in reasoning_trace.paths[:3])
    reflection_result = await run_reflection(
        query=text,
        answer=final.get("answer", ""),
        sources=filtered,
        reasoning_content=reasoning_content,
        confidence=final.get("confidence", "UNKNOWN"),
    )

    tags = ["retrieval", "terminal"]
    if cognitive_layer:
        tags.append(str(cognitive_layer))
    await record_memory_turn(text, final, "retrieval", tags, concept_tags=top_concepts[:3])

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
    persist_local(text, str(final.get("answer", "")),
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

    # ── Confidence calibration ──
    final_confidence = final.get("confidence", "UNKNOWN")
    if final_confidence == "CERTAIN":
        final_confidence = "LOW"

    # --- Phase 42: Synaptic Plasticity Trigger ---
    if soul_answer and soul_answer.get('concepts') and final_confidence in ("CERTAIN", "PROBABLE"):
        from backend.soul.soul_graph import apply_plasticity

        asyncio.to_thread(apply_plasticity, soul_answer.get('scores', {}), source_quality=0.6)

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

    # --- Phase 48: Metacognitive Penalty Trigger ---
    if soul_answer and soul_answer.get("concepts") and final_confidence in ("LOW", "UNKNOWN"):
        from backend.soul.soul_graph import apply_metacognitive_penalty

        await asyncio.to_thread(apply_metacognitive_penalty, soul_answer["concepts"])

    # --- Phase 61: Episodic memory — record the failure to answer ---
    # Reaching the symbolic terminal path with low/unknown confidence means
    # VELYNX could not satisfactorily answer. Record a QUERY_FAILURE episode so
    # the Curiosity Engine's later GOAL_CREATED (and any eventual
    # KNOWLEDGE_ACQUIRED) can be causally chained back to this moment. We tag it
    # with the most specific query concept as the entity. Best-effort.
    if final_confidence in ("LOW", "UNKNOWN"):
        try:
            fail_entity = query_concepts[-1] if query_concepts else ""
            episodic_manager.record_query_failure(
                text,
                entity=fail_entity,
                session_id=sid,
                confidence=final_confidence,
            )
        except Exception as exc:
            logger.debug("Episodic: query-failure logging failed: %s", exc)

    debug_info = {
        "intent": intent,
        "truth_filter": filtered_payload["report"],
        "contradiction": conflicts,
        "evidence_graph": evidence_graph,
        "cognitive_layer": cognitive_layer,
        "soul_used": False,
        "confidence_clamped": final_confidence != final.get("confidence", "UNKNOWN"),
    }
    if final.get("debug"):
        debug_info["reasoning_trace"] = final["debug"].get("reasoning_trace", {})
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
