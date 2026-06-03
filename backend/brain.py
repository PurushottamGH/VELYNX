"""
VELYNX Brain v2 — single unified reasoning loop.
Replaces: unified_pipeline.py, inference_pipeline.py, reasoning_core.py
"""
import asyncio
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from backend.memory.knowledge_graph import KnowledgeGraph
from backend.memory.vector_store import VectorStore
from backend.learning.deep_learner import DeepLearner
from backend.cognition.reasoning_engine import ReasoningEngine
from backend.cognition.answer_synthesizer import AnswerSynthesizer
from backend.self_coder import SelfCoder
from backend.reflection.reflection_engine import ReflectionEngine


class Intent(Enum):
    ANSWER   = "answer"
    LEARN    = "learn"
    CODE     = "code"
    REFLECT  = "reflect"
    SIMULATE = "simulate"
    IMPROVE  = "improve"   # self-triggered


@dataclass
class BrainResult:
    answer: str = ""
    intent: Intent = Intent.ANSWER
    confidence: float = 0.0
    sources: list = field(default_factory=list)
    reasoning_chain: list = field(default_factory=list)
    latency_ms: float = 0.0
    improved: bool = False
    error: str = ""


class VelynxBrain:
    """
    The single brain. All queries go through think().
    No external orchestration needed — brain handles routing,
    memory, learning, self-coding, and quality gating internally.
    """

    QUALITY_THRESHOLD = 0.70
    MAX_RETRY = 2

    def __init__(self):
        self.kg    = KnowledgeGraph()
        self.vs    = VectorStore()
        self.learn = DeepLearner(self.kg, self.vs)
        self.reason = ReasoningEngine(self.kg, self.vs)
        self.synth  = AnswerSynthesizer(self.kg)
        self.coder  = SelfCoder()
        self.mirror = ReflectionEngine()
        self._ready = False

    async def boot(self):
        """Call once at startup."""
        await self.kg.load()
        await self.vs.load()
        self._ready = True
        print("[VELYNX] Brain online.")

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    async def think(self, query: str, context: dict | None = None) -> BrainResult:
        if not self._ready:
            await self.boot()

        t0 = time.perf_counter()
        result = BrainResult()

        try:
            intent = self._route(query)
            result.intent = intent

            if intent == Intent.LEARN:
                result = await self._do_learn(query)
            elif intent == Intent.CODE:
                result = await self._do_code(query)
            elif intent == Intent.SIMULATE:
                result = await self._do_simulate(query)
            elif intent == Intent.IMPROVE:
                result = await self._do_improve(query)
            else:
                result = await self._do_answer(query, context)

        except Exception as exc:
            result.error = traceback.format_exc()
            result.answer = f"[ERROR] {exc}"
            result.confidence = 0.0

        result.latency_ms = (time.perf_counter() - t0) * 1000
        return result

    # ------------------------------------------------------------------ #
    #  Intent router                                                       #
    # ------------------------------------------------------------------ #

    def _route(self, query: str) -> Intent:
        q = query.lower()
        if any(w in q for w in ["learn about", "study", "read about", "teach yourself"]):
            return Intent.LEARN
        if any(w in q for w in ["write code", "fix bug", "patch yourself", "improve your"]):
            return Intent.CODE
        if any(w in q for w in ["simulate", "orbital", "pendulum", "wave", "molecule"]):
            return Intent.SIMULATE
        if any(w in q for w in ["reflect", "how well", "self-audit", "benchmark"]):
            return Intent.REFLECT
        return Intent.ANSWER

    # ------------------------------------------------------------------ #
    #  Answer path (the main path)                                        #
    # ------------------------------------------------------------------ #

    async def _do_answer(self, query: str, context: dict | None) -> BrainResult:
        result = BrainResult(intent=Intent.ANSWER)

        for attempt in range(self.MAX_RETRY + 1):
            # 1. Fast path: check knowledge graph first
            kg_hit = await self.kg.fast_query(query)
            if kg_hit and kg_hit.confidence >= self.QUALITY_THRESHOLD:
                result.answer      = kg_hit.answer
                result.confidence  = kg_hit.confidence
                result.sources     = kg_hit.sources
                return result

            # 2. Vector similarity search
            vec_results = await self.vs.search(query, top_k=5)

            # 3. Reasoning chain
            chain = await self.reason.build_chain(query, vec_results, context)
            result.reasoning_chain = chain.steps

            # 4. Synthesize
            answer = await self.synth.synthesize(query, chain, vec_results)
            result.answer     = answer.text
            result.confidence = answer.confidence
            result.sources    = answer.sources

            # 5. Quality gate
            if result.confidence >= self.QUALITY_THRESHOLD:
                break

            # 6. Gate failed → learn more, retry
            if attempt < self.MAX_RETRY:
                await self.learn.fill_gap(query)

        # 7. Store good answers back to KG
        if result.confidence >= self.QUALITY_THRESHOLD:
            await self.kg.store_answer(query, result.answer, result.confidence, result.sources)

        return result

    # ------------------------------------------------------------------ #
    #  Learn path                                                          #
    # ------------------------------------------------------------------ #

    async def _do_learn(self, query: str) -> BrainResult:
        topic = query.replace("learn about", "").replace("study", "").strip()
        nodes_added = await self.learn.deep_learn(topic)
        return BrainResult(
            intent=Intent.LEARN,
            answer=f"Learned {nodes_added} new concepts about '{topic}'. Knowledge graph updated.",
            confidence=1.0,
        )

    # ------------------------------------------------------------------ #
    #  Self-coding path                                                    #
    # ------------------------------------------------------------------ #

    async def _do_code(self, query: str) -> BrainResult:
        patch_result = await self.coder.handle(query)
        return BrainResult(
            intent=Intent.CODE,
            answer=patch_result.summary,
            confidence=1.0 if patch_result.success else 0.0,
            improved=patch_result.success,
        )

    # ------------------------------------------------------------------ #
    #  Simulation path                                                     #
    # ------------------------------------------------------------------ #

    async def _do_simulate(self, query: str) -> BrainResult:
        from backend.cognition.sim_engine import SimEngine
        engine = SimEngine()
        html = await engine.run(query)
        return BrainResult(
            intent=Intent.SIMULATE,
            answer=html,
            confidence=1.0,
        )

    # ------------------------------------------------------------------ #
    #  Self-improve path                                                   #
    # ------------------------------------------------------------------ #

    async def _do_improve(self, query: str) -> BrainResult:
        report = await self.mirror.full_audit()
        if report.critical_gaps:
            await self.learn.deep_learn(report.critical_gaps[0])
        if report.broken_modules:
            for mod in report.broken_modules[:2]:
                await self.coder.auto_fix(mod)
        return BrainResult(
            intent=Intent.IMPROVE,
            answer=report.summary,
            confidence=1.0,
            improved=True,
        )