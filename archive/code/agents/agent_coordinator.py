"""
VELYNX Phase 34 — Multi-Agent Coordination System
===================================================
Wraps existing modules in a coordinator pattern with parallel execution
and quality-based retry.

Agents:
  QueryRouterAgent — decides which agents to activate
  FetchAgent       — retrieval + source scoring
  ReasonAgent      — synthesis + truth filtering
  VisualAgent      — visualization + simulation
  FormatAgent      — rich terminal output
  AuditAgent       — quality check before showing answer
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("velynx.agents")


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class AgentPlan:
    """Which agents to activate for this query."""
    fetch: bool = True
    reason: bool = True
    visual: bool = False
    simulate: bool = False
    format: bool = True
    audit: bool = True
    use_kg_fast_path: bool = True
    rewrite_query: bool = True


@dataclass
class FetchResult:
    """Result from FetchAgent."""
    sources: list[dict]
    rewritten_query: str
    elapsed_ms: float
    source_count: int
    errors: list[str] = field(default_factory=list)


@dataclass
class ReasonResult:
    """Result from ReasonAgent."""
    answer: str
    confidence: str
    domain: str
    source: str  # "knowledge_graph", "reasoning_core", "synthesizer", etc.
    elapsed_ms: float


@dataclass
class VisualResult:
    """Result from VisualAgent."""
    viz_path: Optional[str] = None
    sim_path: Optional[str] = None
    viz_type: str = ""
    elapsed_ms: float = 0.0


@dataclass
class AuditResult:
    """Result from AuditAgent."""
    score: float
    verdict: str
    issues: list[str]
    should_retry: bool
    elapsed_ms: float


@dataclass
class AgentResult:
    """Final result from AgentCoordinator."""
    answer: str
    confidence: str
    domain: str
    source: str
    quality_score: float
    quality_verdict: str
    agents_used: list[str]
    viz_path: Optional[str] = None
    sim_path: Optional[str] = None
    formatted: str = ""
    elapsed_ms: float = 0.0
    retry_count: int = 0

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "domain": self.domain,
            "source": self.source,
            "quality_score": round(self.quality_score, 3),
            "quality_verdict": self.quality_verdict,
            "agents_used": self.agents_used,
            "viz_path": self.viz_path,
            "sim_path": self.sim_path,
            "elapsed_ms": round(self.elapsed_ms, 1),
            "retry_count": self.retry_count,
        }


# ── Query Router Agent ───────────────────────────────────────────────────────

class QueryRouterAgent:
    """Decides which agents to activate based on query content."""

    def plan(self, query: str) -> AgentPlan:
        q = query.lower().strip()
        plan = AgentPlan()

        # Always fetch unless KG hit is likely
        plan.fetch = True

        # Visual triggers
        viz_triggers = {"plot", "graph", "show", "draw", "diagram", "chart", "map"}
        plan.visual = any(w in q for w in viz_triggers)

        # Simulation triggers
        sim_triggers = {"simulate", "simulation", "orbit", "pendulum", "wave", "projectile", "molecule"}
        plan.simulate = any(w in q for w in sim_triggers)

        # Skip audit for simple greetings
        if q in {"hi", "hello", "hey", "thanks", "bye"}:
            plan.audit = False
            plan.fetch = False

        return plan


# ── Fetch Agent ──────────────────────────────────────────────────────────────

class FetchAgent:
    """Retrieval + source scoring."""

    async def run(self, query: str) -> FetchResult:
        t0 = time.time()
        sources = []
        rewritten = query
        errors = []

        # Rewrite query for better search
        try:
            from pipeline.query_rewriter import rewrite
            rewritten = rewrite(query)
        except Exception:
            pass

        # Retrieve from web
        try:
            from retrieval.unified_retriever import unified_retriever
            report = await unified_retriever.retrieve(rewritten)
            sources = report.source_dicts
        except Exception as e:
            errors.append(f"retrieval: {e}")

        # Score and filter sources
        try:
            from pipeline.truth_filter import score_sources
            result = score_sources(sources, query=rewritten)
            if isinstance(result, dict):
                sources = result.get("sources", sources)
        except Exception:
            pass

        return FetchResult(
            sources=sources,
            rewritten_query=rewritten,
            elapsed_ms=(time.time() - t0) * 1000,
            source_count=len(sources),
            errors=errors,
        )


# ── Reason Agent ─────────────────────────────────────────────────────────────

class ReasonAgent:
    """Synthesis + truth filtering. Tries multiple reasoning strategies."""

    async def run(self, query: str, sources: list[dict]) -> ReasonResult:
        t0 = time.time()
        answer = ""
        confidence = "UNKNOWN"
        domain = "general"
        source = "none"

        # Strategy 1: Knowledge graph fast path
        try:
            from memory.knowledge_graph import knowledge_graph
            node = knowledge_graph.lookup(query, threshold=0.65)
            if node and node.effective_confidence > 0.65:
                return ReasonResult(
                    answer=node.summary,
                    confidence="CERTAIN" if node.effective_confidence > 0.85 else "PROBABLE",
                    domain=node.domain,
                    source="knowledge_graph",
                    elapsed_ms=(time.time() - t0) * 1000,
                )
        except Exception:
            pass

        # Strategy 2: Concept engine
        try:
            from memory.concept_engine import concept_engine
            concept = concept_engine.understand(query)
            if concept:
                best = concept.best_answer_for(query)
                if best and len(best) > 30:
                    return ReasonResult(
                        answer=best,
                        confidence="PROBABLE",
                        domain=concept.domain,
                        source="concept_engine",
                        elapsed_ms=(time.time() - t0) * 1000,
                    )
        except Exception:
            pass

        # Strategy 3: Teaching engine
        try:
            from cognition.teaching_engine import teaching_engine
            from memory.concept_engine import concept_engine
            concept = concept_engine.understand(query)
            if concept:
                response = teaching_engine.answer(query, primary_concept=concept)
                if response and len(response.answer) > 30:
                    return ReasonResult(
                        answer=response.answer,
                        confidence=response.confidence,
                        domain=concept.domain,
                        source="teaching_engine",
                        elapsed_ms=(time.time() - t0) * 1000,
                    )
        except Exception:
            pass

        # Strategy 4: LLM reasoning
        try:
            from cognition.reasoning_engine import reason
            result = await reason(query=query, sources=sources)
            if result and hasattr(result, "answer") and len(result.answer) > 30:
                return ReasonResult(
                    answer=result.answer,
                    confidence=getattr(result, "confidence", "PROBABLE"),
                    domain="general",
                    source="llm_reasoning",
                    elapsed_ms=(time.time() - t0) * 1000,
                )
        except Exception:
            pass

        # Strategy 5: Internal reasoning (TF-IDF)
        if sources:
            try:
                from pipeline.reasoning_core import reason
                result = reason(sources, query=query)
                answer = result.get("draft", "") or result.get("answer", "")
                if answer:
                    return ReasonResult(
                        answer=answer,
                        confidence=result.get("confidence", "LOW"),
                        domain="general",
                        source="reasoning_core",
                        elapsed_ms=(time.time() - t0) * 1000,
                    )
            except Exception:
                pass

        # Strategy 6: Synthesizer fallback
        if sources:
            try:
                from pipeline.synthesizer import synthesize
                draft = {"draft": sources[0].get("snippet", "")[:400], "confidence": "LOW"}
                result = synthesize(draft, query=query)
                return ReasonResult(
                    answer=result.get("answer", ""),
                    confidence="LOW",
                    domain="general",
                    source="synthesizer",
                    elapsed_ms=(time.time() - t0) * 1000,
                )
            except Exception:
                pass

        return ReasonResult(
            answer="I could not find information for this query.",
            confidence="UNKNOWN",
            domain="general",
            source="none",
            elapsed_ms=(time.time() - t0) * 1000,
        )


# ── Visual Agent ─────────────────────────────────────────────────────────────

class VisualAgent:
    """Visualization + simulation generation."""

    async def run(self, query: str, answer: str) -> VisualResult:
        t0 = time.time()
        viz_path = None
        sim_path = None
        viz_type = ""

        # Check for visualization
        try:
            from cognition.viz_detector import VizDetector
            from cognition.viz_engine import VizEngine
            detector = VizDetector()
            req = detector.detect(query, answer)
            if req:
                engine = VizEngine()
                result = engine.generate(req)
                if result.file_path:
                    viz_path = result.file_path
                    viz_type = req.type
        except Exception:
            pass

        # Check for simulation
        try:
            from cognition.sim_detector import SimDetector
            from cognition.sim_engine import SimEngine
            sim_detector = SimDetector()
            sim_req = sim_detector.detect(query)
            if sim_req:
                sim_engine = SimEngine()
                sim_path = sim_engine.run(sim_req)
        except Exception:
            pass

        return VisualResult(
            viz_path=viz_path,
            sim_path=sim_path,
            viz_type=viz_type,
            elapsed_ms=(time.time() - t0) * 1000,
        )


# ── Format Agent ─────────────────────────────────────────────────────────────

class FormatAgent:
    """Rich terminal output formatting."""

    def run(self, query: str, answer: str, result: dict) -> str:
        try:
            from cognition.rich_formatter import RichFormatter
            formatter = RichFormatter()
            formatted = formatter.format(query, answer, result)
            return formatted.output
        except Exception:
            return answer


# ── Audit Agent ──────────────────────────────────────────────────────────────

class AuditAgent:
    """Quality check before showing answer."""

    async def check(self, query: str, answer: str, sources: list[dict]) -> AuditResult:
        t0 = time.time()

        try:
            from reflection.advanced_reflection import reflection_engine
            report = await reflection_engine.reflect(
                query=query,
                answer=answer,
                sources=sources,
                confidence="PROBABLE",
            )
            return AuditResult(
                score=report.overall_quality,
                verdict=report.verdict,
                issues=report.issues,
                should_retry=report.should_retry,
                elapsed_ms=(time.time() - t0) * 1000,
            )
        except Exception:
            # Fallback: basic quality check
            score = 0.5
            issues = []
            if len(answer) < 50:
                score -= 0.2
                issues.append("Answer too short")
            if "I could not" in answer:
                score -= 0.3
                issues.append("No information found")
            return AuditResult(
                score=score,
                verdict="UNKNOWN",
                issues=issues,
                should_retry=score < 0.3,
                elapsed_ms=(time.time() - t0) * 1000,
            )


# ── Agent Coordinator ────────────────────────────────────────────────────────

class AgentCoordinator:
    """Multi-agent coordinator with parallel execution and quality-based retry."""

    def __init__(self):
        self.router = QueryRouterAgent()
        self.fetch_agent = FetchAgent()
        self.reason_agent = ReasonAgent()
        self.visual_agent = VisualAgent()
        self.format_agent = FormatAgent()
        self.audit_agent = AuditAgent()

    async def process(self, query: str, max_retries: int = 1) -> AgentResult:
        """Main entry point. Runs agents in coordinated sequence."""
        t0 = time.time()
        agents_used = []

        # Step 1: Route
        plan = self.router.plan(query)
        agents_used.append("router")

        # Step 2: Knowledge graph fast path (skip retrieval if hit)
        kg_answer = None
        if plan.use_kg_fast_path:
            try:
                from memory.knowledge_graph import knowledge_graph
                node = knowledge_graph.lookup(query, threshold=0.65)
                if node and node.effective_confidence > 0.65:
                    kg_answer = ReasonResult(
                        answer=node.summary,
                        confidence="CERTAIN" if node.effective_confidence > 0.85 else "PROBABLE",
                        domain=node.domain,
                        source="knowledge_graph",
                        elapsed_ms=0,
                    )
                    agents_used.append("knowledge_graph")
            except Exception:
                pass

        # Step 3: Fetch (skip if KG hit)
        fetch_result = None
        if not kg_answer and plan.fetch:
            fetch_result = await self.fetch_agent.run(query)
            agents_used.append("fetch")

        sources = fetch_result.sources if fetch_result else []

        # Step 4: Reason
        if kg_answer:
            reason_result = kg_answer
        else:
            reason_result = await self.reason_agent.run(query, sources)
            agents_used.append("reason")

        # Step 5: Visual + Format (parallel)
        visual_result = None
        if plan.visual or plan.simulate:
            visual_result = await self.visual_agent.run(query, reason_result.answer)
            agents_used.append("visual")

        # Step 6: Format
        formatted = ""
        if plan.format:
            result_dict = {
                "answer": reason_result.answer,
                "confidence": reason_result.confidence,
                "sources": sources,
                "concept": {"domain": reason_result.domain, "depth": "", "connects_to": []},
            }
            formatted = self.format_agent.run(query, reason_result.answer, result_dict)
            agents_used.append("format")

        # Step 7: Audit
        quality_score = 0.7
        quality_verdict = "GOOD"
        retry_count = 0

        if plan.audit and not kg_answer:
            audit_result = await self.audit_agent.check(query, reason_result.answer, sources)
            agents_used.append("audit")
            quality_score = audit_result.score
            quality_verdict = audit_result.verdict

            # Retry if quality is poor
            if audit_result.should_retry and retry_count < max_retries:
                retry_count += 1
                # Retry with more sources
                if fetch_result:
                    fetch_result = await self.fetch_agent.run(fetch_result.rewritten_query + " detailed explanation")
                    reason_result = await self.reason_agent.run(query, fetch_result.sources)
                    agents_used.append("retry")

        return AgentResult(
            answer=reason_result.answer,
            confidence=reason_result.confidence,
            domain=reason_result.domain,
            source=reason_result.source,
            quality_score=quality_score,
            quality_verdict=quality_verdict,
            agents_used=agents_used,
            viz_path=visual_result.viz_path if visual_result else None,
            sim_path=visual_result.sim_path if visual_result else None,
            formatted=formatted,
            elapsed_ms=(time.time() - t0) * 1000,
            retry_count=retry_count,
        )


# Module singleton
agent_coordinator = AgentCoordinator()
