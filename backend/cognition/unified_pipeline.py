"""
VELYNX Phases 28-30
====================
Phase 28: Unified Pipeline — web + terminal same brain
Phase 29: Continuous Improvement Loop — smarter every night
Phase 30: Self-Improvement Awareness — VELYNX audits itself
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("velynx.improvement")

_DATA_DIR = Path(os.getenv("VELYNX_DATA_DIR", ".")) / "velynx_data" / "improvement"
_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 28 — UNIFIED PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

class UnifiedPipeline:
    """One brain, two interfaces. Web and terminal use identical pipeline."""

    async def process(self, query: str, session_id: str = "default", mode: str = "auto") -> dict:
        t_start = time.time()
        steps = []

        # Step 1: Self-knowledge check
        try:
            from cognition.advanced_cognition import cognition_coordinator
            from memory.concept_engine import concept_engine
            concept = concept_engine.understand(query)
            assessment = cognition_coordinator.get_honest_answer(query, concept)
            steps.append(f"self_knowledge: {assessment['state']}")
            if assessment["state"] == "deep" and not assessment["should_search"]:
                answer = assessment.get("human_explanation") or (concept.best_answer_for(query) if concept else "")
                if answer and len(answer) > 30:
                    return self._build_response(query=query, answer=answer,
                        confidence=assessment["confidence"], source="concept_engine_deep",
                        elapsed=time.time() - t_start, steps=steps, concept=concept)
        except Exception as e:
            steps.append(f"concept_engine: unavailable ({e})")

        # Step 2: Knowledge graph fast path
        try:
            from memory.knowledge_graph import knowledge_graph
            node = knowledge_graph.lookup(query, threshold=0.65)
            if node and node.effective_confidence > 0.65:
                steps.append(f"knowledge_graph: hit (conf={node.effective_confidence:.0%})")
                return self._build_response(query=query, answer=node.summary,
                    confidence=self._float_to_label(node.effective_confidence),
                    source="knowledge_graph", elapsed=time.time() - t_start, steps=steps)
        except Exception as e:
            steps.append(f"knowledge_graph: {e}")

        # Step 3: Live retrieval
        try:
            from pipeline.query_rewriter import rewrite
            search_query = rewrite(query)
            steps.append(f"query_rewritten: '{search_query}'")
        except Exception:
            search_query = query

        try:
            from retrieval.unified_retriever import unified_retriever
            report = await unified_retriever.retrieve(search_query)
            sources = report.source_dicts
            steps.append(f"retrieval: {len(sources)} sources in {report.elapsed:.1f}s")
        except Exception as e:
            sources = []
            steps.append(f"retrieval: failed ({e})")

        if not sources:
            return self._build_response(query=query,
                answer="I could not retrieve information for this query.",
                confidence="UNKNOWN", source="no_retrieval",
                elapsed=time.time() - t_start, steps=steps)

        # Step 4: Deep learning — extract understanding
        concept_obj = None
        try:
            from memory.concept_engine import concept_engine
            concept_obj = concept_engine.learn(query, sources)
            steps.append(f"concept_learned: depth={concept_obj.depth_label}")
            from cognition.advanced_cognition import cognition_coordinator
            cognition_coordinator.after_learning(query, concept_obj, sources)
        except Exception as e:
            steps.append(f"concept_learning: {e}")

        # Step 5: Teaching mode response
        answer = ""
        confidence = "UNKNOWN"
        try:
            from cognition.teaching_engine import teaching_engine
            if concept_obj:
                response = teaching_engine.answer(query, primary_concept=concept_obj)
                if response and len(response.answer) > 30:
                    answer = response.answer
                    confidence = response.confidence
                    steps.append(f"teaching_engine: {response.intent.value}")
        except Exception as e:
            steps.append(f"teaching_engine: {e}")

        # Step 6: Fallback synthesis
        if not answer or len(answer) < 30:
            try:
                from pipeline.reasoning_core import reason
                result = reason(sources, query=query)
                answer = result.get("answer", "")
                confidence = result.get("confidence", "LOW")
                steps.append("reasoning_core: fallback")
            except Exception as e:
                steps.append(f"reasoning_core: {e}")
                if sources:
                    answer = sources[0].get("snippet", "")[:400]
                    confidence = "LOW"

        # Step 7: Store in knowledge graph
        try:
            from memory.knowledge_graph import knowledge_graph
            knowledge_graph.integrate(query=query, sources=sources, answer=answer, confidence=confidence)
            steps.append("knowledge_graph: stored")
        except Exception:
            pass

        # Step 8: Continuous learning
        try:
            from learning.continuous_learner import continuous_learner
            await continuous_learner.learn_from_query(query=query, sources=sources,
                answer=answer, confidence=confidence)
            steps.append("continuous_learner: recorded")
        except Exception:
            pass

        return self._build_response(query=query, answer=answer, confidence=confidence,
            source="live_retrieval", elapsed=time.time() - t_start, steps=steps,
            sources=sources, concept=concept_obj)

    def _build_response(self, query, answer, confidence, source, elapsed, steps=None,
                        sources=None, concept=None) -> dict:
        response = {"query": query, "answer": answer, "confidence": confidence,
                    "source": source, "elapsed": round(elapsed, 3),
                    "sources": sources or [], "steps": steps or []}
        if concept:
            response["concept"] = {"depth": concept.depth_label, "domain": concept.domain,
                "connects_to": concept.connects_to[:5], "open_questions": concept.open_questions[:2]}
        return response

    def _float_to_label(self, f: float) -> str:
        if f >= 0.85: return "CERTAIN"
        if f >= 0.65: return "PROBABLE"
        if f >= 0.40: return "DEBATED"
        return "LOW"


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 29 — CONTINUOUS IMPROVEMENT LOOP
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ImprovementSession:
    date: str
    concepts_deepened: int = 0
    contradictions_resolved: int = 0
    curiosity_questions_answered: int = 0
    weak_areas_identified: list[str] = field(default_factory=list)
    avg_confidence_before: float = 0.0
    avg_confidence_after: float = 0.0
    duration_seconds: float = 0.0


class ContinuousImprovementLoop:
    """Every night VELYNX improves itself."""

    async def run_nightly_session(self, hours: float = 4.0) -> ImprovementSession:
        from datetime import datetime
        session = ImprovementSession(date=datetime.now().isoformat())
        t_start = time.time()
        deadline = t_start + (hours * 3600)

        logger.info("Nightly improvement session started (%.1f hours)", hours)
        pipeline = UnifiedPipeline()

        # Deepen shallow concepts
        try:
            from memory.concept_engine import concept_engine
            session.avg_confidence_before = self._avg_confidence(concept_engine)
            shallow = [c for c in concept_engine._concepts.values()
                      if c.depth_label in ("SHALLOW", "SURFACE", "PARTIAL")]
            shallow.sort(key=lambda c: c.query_count, reverse=True)
            for concept in shallow[:20]:
                if time.time() > deadline:
                    break
                try:
                    result = await pipeline.process(f"How does {concept.concept} work in depth?", mode="deep")
                    if result.get("answer"):
                        session.concepts_deepened += 1
                    await asyncio.sleep(2)
                except Exception:
                    pass
        except Exception as e:
            logger.warning("Concept deepening failed: %s", e)

        # Answer curiosity questions
        try:
            from cognition.advanced_cognition import curiosity_engine
            for _ in range(10):
                if time.time() > deadline:
                    break
                q = curiosity_engine.get_next()
                if not q:
                    break
                try:
                    result = await pipeline.process(q.question)
                    if result.get("answer"):
                        curiosity_engine.mark_answered(q.question)
                        session.curiosity_questions_answered += 1
                    await asyncio.sleep(2)
                except Exception:
                    pass
        except Exception:
            pass

        # Consolidate knowledge graph
        try:
            from memory.knowledge_graph import knowledge_graph
            knowledge_graph.consolidate()
        except Exception:
            pass

        # Identify weak areas
        try:
            from memory.concept_engine import concept_engine
            session.avg_confidence_after = self._avg_confidence(concept_engine)
            session.weak_areas_identified = [c.concept for c in concept_engine._concepts.values()
                                             if c.confidence < 0.5 and c.query_count > 2][:10]
        except Exception:
            pass

        session.duration_seconds = time.time() - t_start
        self._save_session(session)
        return session

    def _avg_confidence(self, concept_engine) -> float:
        if not concept_engine._concepts:
            return 0.0
        return sum(c.confidence for c in concept_engine._concepts.values()) / len(concept_engine._concepts)

    def _save_session(self, session: ImprovementSession):
        try:
            f = _DATA_DIR / "sessions.json"
            existing = json.loads(f.read_text()) if f.exists() else []
            existing.append(asdict(session))
            f.write_text(json.dumps(existing[-30:], indent=2))
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 30 — SELF-IMPROVEMENT AWARENESS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class SelfAuditReport:
    timestamp: str
    weak_reasoning_examples: list[str]
    shallow_concepts: list[str]
    unanswered_curiosity: list[str]
    unresolved_contradictions: int
    recommended_actions: list[str]
    overall_health: str


class SelfImprovementAwareness:
    def audit(self) -> SelfAuditReport:
        from datetime import datetime
        weak = self._find_weak_reasoning()
        shallow = self._find_shallow_concepts()
        unanswered = self._find_unanswered_curiosity()
        contradictions = self._count_contradictions()
        actions = self._recommend_actions(weak, shallow, unanswered, contradictions)
        health = "EXCELLENT" if len(shallow) + contradictions == 0 else "GOOD" if len(shallow) + contradictions < 5 else "NEEDS_WORK" if len(shallow) + contradictions < 15 else "POOR"

        report = SelfAuditReport(timestamp=datetime.now().isoformat(),
            weak_reasoning_examples=weak, shallow_concepts=shallow,
            unanswered_curiosity=unanswered, unresolved_contradictions=contradictions,
            recommended_actions=actions, overall_health=health)
        self._save_report(report)
        return report

    def _find_weak_reasoning(self) -> list[str]:
        issues = []
        try:
            from memory.concept_engine import concept_engine
            for concept in list(concept_engine._concepts.values())[:50]:
                if concept.why == "" and concept.query_count > 3:
                    issues.append(f"'{concept.concept}' — answers WHAT but not WHY")
                if concept.human_meaning == "" and concept.query_count > 5:
                    issues.append(f"'{concept.concept}' — no human meaning layer")
        except Exception:
            pass
        return issues[:8]

    def _find_shallow_concepts(self) -> list[str]:
        try:
            from memory.concept_engine import concept_engine
            return [f"{c.concept} ({c.domain})" for c in concept_engine._concepts.values()
                    if c.depth_label in ("SHALLOW", "SURFACE") and c.query_count > 1][:10]
        except Exception:
            return []

    def _find_unanswered_curiosity(self) -> list[str]:
        try:
            from cognition.advanced_cognition import curiosity_engine
            return curiosity_engine.get_learning_targets(5)
        except Exception:
            return []

    def _count_contradictions(self) -> int:
        try:
            from cognition.advanced_cognition import contradiction_resolver
            return len(contradiction_resolver.get_unresolved())
        except Exception:
            return 0

    def _recommend_actions(self, weak, shallow, unanswered, contradictions) -> list[str]:
        actions = []
        if shallow:
            actions.append(f"Deepen {len(shallow)} shallow concepts")
        if contradictions > 0:
            actions.append(f"Resolve {contradictions} unresolved contradictions")
        if unanswered:
            actions.append(f"Answer {len(unanswered)} curiosity questions: {', '.join(unanswered[:3])}")
        if weak:
            actions.append(f"Fix {len(weak)} reasoning gaps — add WHY and human meaning layers")
        return actions or ["Knowledge base is healthy — continue normal learning"]

    def _save_report(self, report: SelfAuditReport):
        try:
            (_DATA_DIR / "last_audit.json").write_text(json.dumps(asdict(report), indent=2))
        except Exception:
            pass

    def print_report(self, report: SelfAuditReport):
        print(f"\n  VELYNX Self-Audit Report")
        print(f"  Health: {report.overall_health}")
        print(f"  Unresolved contradictions: {report.unresolved_contradictions}")
        if report.shallow_concepts:
            print(f"\n  Shallow concepts ({len(report.shallow_concepts)}):")
            for c in report.shallow_concepts[:5]:
                print(f"    · {c}")
        if report.weak_reasoning_examples:
            print(f"\n  Weak reasoning ({len(report.weak_reasoning_examples)}):")
            for w in report.weak_reasoning_examples[:5]:
                print(f"    · {w}")
        if report.recommended_actions:
            print(f"\n  Recommended actions:")
            for a in report.recommended_actions:
                print(f"    → {a}")
        print()


unified_pipeline = UnifiedPipeline()
improvement_loop = ContinuousImprovementLoop()
self_improvement = SelfImprovementAwareness()
