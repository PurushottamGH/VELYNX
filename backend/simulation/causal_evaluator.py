"""
VELYNX Phase 63 — CounterfactualEvaluator
=========================================

Compares a baseline reasoning trace against a counterfactual one to compute
the **Causal Delta** — what facts changed, what reasoning paths broke, and
whether the final answer flipped.

Design
------
The evaluator drives two passes of the black-box ``reasoning_engine.reason()``:

1. **Baseline pass** — normal triples from the Knowledge Graph.
2. **Simulated pass** — wrapped in a ``SimulationMemoryContext`` that merges
   the real KG with counterfactual triples injected via ``fork_entity``,
   ``extend_schema``, and ``record_triple``.

It then diffs the two ``ReasoningTrace`` objects structurally: fact sets, path
graphs, contradictions, and confidence. No natural-language synthesis is
attempted — the delta is purely symbolic and can be fed to a synthesizer
separately.

Usage
-----
::

    from backend.simulation.causal_evaluator import CounterfactualEvaluator
    from backend.cognition.reasoning_engine import ReasoningEngine
    from backend.pipeline.reasoning_wiring import (
        extract_query_concepts, retrieve_triples,
    )

    evaluator = CounterfactualEvaluator(
        reason_fn=_reasoning_engine.reason,
        triple_retriever=retrieve_triples,
        concept_extractor=extract_query_concepts,
        kg_read_func=triples_read_func,     # see simulation_memory_context.py
    )

    delta = evaluator.evaluate(
        query="Does my Tesla have wheels?",
        premise={"Tesla Model 3": {"mobility_type": "hover", "wheel_count": 0}},
    )

    if delta.answer_flipped:
        print(f"Answer flipped! Confidence dropped {delta.confidence_delta:.2f}")
        print(f"Facts lost: {[f.as_tuple() for f in delta.facts_lost]}")
        print(f"Facts gained: {[f.as_tuple() for f in delta.facts_gained]}")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from backend.cognition.reasoning_engine import (
    Contradiction,
    Fact,
    ReasoningPath,
    ReasoningTrace,
)
from backend.simulation.simulation_memory_context import SimulationMemoryContext

__all__ = [
    "CausalDelta",
    "CounterfactualEvaluator",
]

logger = logging.getLogger("velynx.simulation.causal_evaluator")

# ── Re-export the pipeline's Triple shape ─────────────────────────────────────
Triple = Tuple[str, str, str]


# ══════════════════════════════════════════════════════════════════════════════
# CausalDelta — the result type
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class CausalDelta:
    """The structural diff between baseline and counterfactual reasoning.

    Every field is purely symbolic — no natural-language strings. The caller
    (e.g. a synthesizer) can render a human-readable explanation from these
    fields, or the delta can be fed into a higher-level decision gate (e.g.
    "should I alert the user that the answer changed?")
    """

    # ── Overall verdict ──────────────────────────────────────────────────────

    answer_flipped: bool
    """True when the evaluator's heuristic detects a substantive answer change.

    Heuristic triggers:
    1. Any winning fact involving a query concept was lost or gained.
    2. Baseline confidence >= 0.5 and simulated confidence dropped by >= 0.3.
    3. Every path connecting any pair of query concepts was broken.
    """

    confidence_delta: float
    """simulated.confidence - baseline.confidence. Negative means the
    counterfactual eroded the engine's certainty."""

    # ── Fact changes ─────────────────────────────────────────────────────────

    facts_lost: list[Fact] = field(default_factory=list)
    """winning_facts + inferred_facts present in baseline but absent in
    simulation."""

    facts_gained: list[Fact] = field(default_factory=list)
    """winning_facts + inferred_facts present in simulation but absent in
    baseline."""

    facts_shared: list[Fact] = field(default_factory=list)
    """Facts present in both traces (same subject, predicate, object)."""

    # ── Path changes ─────────────────────────────────────────────────────────

    paths_lost: list[Tuple[str, str]] = field(default_factory=list)
    """``(start, end)`` signatures of reasoning paths that existed in baseline
    but collapsed in simulation."""

    paths_gained: list[Tuple[str, str]] = field(default_factory=list)
    """``(start, end)`` signatures of reasoning paths that only emerged in
    simulation."""

    path_count_delta: int = 0
    """simulated.path_count - baseline.path_count."""

    # ── Contradiction changes ────────────────────────────────────────────────

    contradictions_introduced: list[Contradiction] = field(default_factory=list)
    """Contradictions present in simulation but not in baseline."""

    contradictions_resolved: list[Contradiction] = field(default_factory=list)
    """Contradictions present in baseline but absent in simulation."""

    # ── Full traces (for deep inspection by callers) ──────────────────────────

    baseline_trace: Optional[ReasoningTrace] = None
    simulated_trace: Optional[ReasoningTrace] = None

    # ── Context (for traceability / logging) ─────────────────────────────────

    query: str = ""
    premise: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # ── Public helpers ───────────────────────────────────────────────────────

    def summary(self) -> Dict[str, Any]:
        """Compact, human-readable snapshot of what changed."""
        return {
            "query": self.query,
            "answer_flipped": self.answer_flipped,
            "confidence_delta": round(self.confidence_delta, 4),
            "baseline_confidence": (
                round(self.baseline_trace.confidence, 4)
                if self.baseline_trace
                else None
            ),
            "simulated_confidence": (
                round(self.simulated_trace.confidence, 4)
                if self.simulated_trace
                else None
            ),
            "facts_lost": len(self.facts_lost),
            "facts_gained": len(self.facts_gained),
            "paths_lost": len(self.paths_lost),
            "paths_gained": len(self.paths_gained),
            "path_count_delta": self.path_count_delta,
            "contradictions_introduced": len(self.contradictions_introduced),
            "contradictions_resolved": len(self.contradictions_resolved),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Full serialization for debugging / logging."""
        return {
            "answer_flipped": self.answer_flipped,
            "confidence_delta": round(self.confidence_delta, 4),
            "facts_lost": [f.as_tuple() for f in self.facts_lost],
            "facts_gained": [f.as_tuple() for f in self.facts_gained],
            "facts_shared": [f.as_tuple() for f in self.facts_shared],
            "paths_lost": self.paths_lost,
            "paths_gained": self.paths_gained,
            "path_count_delta": self.path_count_delta,
            "contradictions_introduced": [
                {
                    "subject": c.subject,
                    "predicate": c.predicate,
                    "winner": c.winner.as_tuple(),
                    "loser": c.loser.as_tuple(),
                    "margin": round(c.margin, 4),
                    "resolved": c.resolved,
                    "rationale": c.rationale,
                }
                for c in self.contradictions_introduced
            ],
            "contradictions_resolved": [
                {
                    "subject": c.subject,
                    "predicate": c.predicate,
                    "winner": c.winner.as_tuple(),
                    "loser": c.loser.as_tuple(),
                    "margin": round(c.margin, 4),
                    "resolved": c.resolved,
                    "rationale": c.rationale,
                }
                for c in self.contradictions_resolved
            ],
            "query": self.query,
            "premise": dict(self.premise),
        }


# ══════════════════════════════════════════════════════════════════════════════
# CounterfactualEvaluator
# ══════════════════════════════════════════════════════════════════════════════


class CounterfactualEvaluator:
    """Compares baseline reasoning against a counterfactual ``premise``.

    Parameters
    ----------
    reason_fn
        Black-box callable matching
        ``reason(query_concepts, retrieved_triples, **kwargs) -> ReasoningTrace``.
        Typically ``reasoning_engine.reason``.
    triple_retriever
        Callable that returns KG triples relevant to a set of concepts.
        Signature: ``(concepts: list[str]) -> list[Triple]``.
        Typically ``pipeline.reasoning_wiring.retrieve_triples``.
    concept_extractor
        Callable that extracts symbolic concepts from a raw user query.
        Signature: ``(query: str) -> list[str]``.
        Typically ``pipeline.reasoning_wiring.extract_query_concepts``.
    kg_read_func
        Callable for reading the live KG during simulation. Passed directly
        to ``SimulationMemoryContext``. Signature:
        ``(subject=None, relation=None, obj=None) -> list[Triple]``.
    """

    def __init__(
        self,
        reason_fn: Callable[..., ReasoningTrace],
        triple_retriever: Callable[[List[str]], List[Triple]],
        concept_extractor: Callable[[str], List[str]],
        kg_read_func: Optional[Callable[..., List[Triple]]] = None,
    ) -> None:
        self._reason_fn = reason_fn
        self._triple_retriever = triple_retriever
        self._concept_extractor = concept_extractor
        self._kg_read_func = kg_read_func

        self._logger = logger

    # ── Public entry point ───────────────────────────────────────────────────

    def evaluate(
        self,
        query: str,
        premise: Dict[str, Dict[str, Any]],
        **reason_kwargs: Any,
    ) -> CausalDelta:
        """Run the baseline and counterfactual reasoning passes and diff them.

        Parameters
        ----------
        query
            The user's question, e.g. ``"Does my Tesla have wheels?"``.
        premise
            Counterfactual world state. Shape::

                {"EntityName": {"attribute_key": value, ...}, ...}

            Example::

                {"Tesla Model 3": {"mobility_type": "hover", "wheel_count": 0}}

        **reason_kwargs
            Additional keyword arguments forwarded to ``reason_fn`` on both
            passes (e.g. ``thermodynamic_state``, ``query_predicate``,
            ``episodic_context``).

        Returns
        -------
        CausalDelta
            The structural diff between the two traces.
        """
        # 1. Extract concepts from the query (shared by both passes).
        try:
            concepts = self._concept_extractor(query)
        except Exception as exc:
            self._logger.warning(
                "Concept extraction failed for %r: %s — falling back to empty list.",
                query, exc,
            )
            concepts = []
        self._logger.info(
            "Counterfactual evaluation — query=%r concepts=%s",
            query, concepts,
        )

        # 2. Baseline pass.
        baseline_trace, baseline_triples = self._run_baseline(
            concepts, **reason_kwargs,
        )

        # 3. Simulated pass.
        sim_trace, _ = self._run_simulated(
            concepts, premise, **reason_kwargs,
        )

        # 4. Compute the delta.
        delta = self._compute_delta(
            baseline_trace=baseline_trace,
            simulated_trace=sim_trace,
            concepts=concepts,
            query=query,
            premise=premise,
        )

        self._logger.info(
            "CausalDelta — flipped=%s conf_delta=%.4f "
            "facts_lost=%d facts_gained=%d "
            "paths_lost=%d paths_gained=%d",
            delta.answer_flipped,
            delta.confidence_delta,
            len(delta.facts_lost), len(delta.facts_gained),
            len(delta.paths_lost), len(delta.paths_gained),
        )

        return delta

    # ── Internal: baseline pass ──────────────────────────────────────────────

    def _run_baseline(
        self,
        concepts: List[str],
        **reason_kwargs: Any,
    ) -> Tuple[ReasoningTrace, List[Triple]]:
        """Execute the normal reasoning pass (KG only, no simulation)."""
        triples = self._triple_retriever(concepts) if concepts else []
        trace = self._reason_fn(concepts, triples, **reason_kwargs)
        return trace, triples

    # ── Internal: simulated pass ─────────────────────────────────────────────

    def _run_simulated(
        self,
        concepts: List[str],
        premise: Dict[str, Dict[str, Any]],
        **reason_kwargs: Any,
    ) -> Tuple[ReasoningTrace, List[Triple]]:
        """Execute reasoning inside a ``SimulationMemoryContext`` window.

        The premise is applied before retrieving triples, so the merged view
        (real KG + counterfactual delta) is what the engine sees.
        """
        with SimulationMemoryContext(read_func=self._kg_read_func) as ctx:
            self._apply_premise(ctx, premise)
            sim_triples = self._collect_merged_triples(ctx, concepts)
            trace = self._reason_fn(concepts, sim_triples, **reason_kwargs)

        # trace is captured before context exit — we hold it.
        return trace, sim_triples

    # ── Internal: premise application ────────────────────────────────────────

    # Lazy-loaded predicate map (attribute_key -> predicate label), shared
    # across all evaluator instances.
    _PREDICATE_CACHE: Dict[str, str] = {}

    @classmethod
    def _load_predicate_map(cls) -> Dict[str, str]:
        """Load the inverse of the schema gatekeeper's predicate map.

        Returns a ``{attribute_key: predicate_label}`` mapping.
        """
        if cls._PREDICATE_CACHE:
            return cls._PREDICATE_CACHE
        try:
            # The gatekeeper's _PREDICATE_MAP is ``{predicate: attribute_key}``.
            # Invert it so we can derive predicate labels from attribute keys.
            from backend.knowledge.schema_gatekeeper import _PREDICATE_MAP

            inverted: Dict[str, str] = {}
            for pred, attr in _PREDICATE_MAP.items():
                if attr not in inverted:
                    inverted[attr] = pred
            cls._PREDICATE_CACHE = inverted
        except Exception:
            cls._PREDICATE_CACHE = {}
        return cls._PREDICATE_CACHE

    def _infer_datatype(self, value: Any) -> type:
        """Infer a Python type from a value for schema extension."""
        if isinstance(value, bool):
            return bool
        if isinstance(value, int):
            return int
        if isinstance(value, float):
            return float
        return str

    def _apply_premise(
        self,
        ctx: SimulationMemoryContext,
        premise: Dict[str, Dict[str, Any]],
    ) -> None:
        """Apply the counterfactual premise to the simulation context.

        For each entity in the premise:
        1. Extend the schema for any attribute that doesn't natively exist.
        2. Fork the entity with the specified attribute overrides.
        3. Inject counterfactual triples into the delta layer.

        The order matters: schema extension must happen before fact injection
        because the relaxed gatekeeper only accepts attributes that have been
        explicitly extended.
        """
        if not premise:
            self._logger.warning("Empty premise — no counterfactual applied.")
            return

        pred_map = self._load_predicate_map()

        for entity_name, overrides in premise.items():
            if not overrides:
                continue

            # Phase A — extend schema for novel attributes.
            for attr_key in overrides:
                ctx.extend_schema(
                    entity_name,
                    attr_key,
                    datatype=self._infer_datatype(overrides[attr_key]),
                )

            # Phase B — fork the entity with the overrides.
            ctx.fork_entity(entity_name, attribute_overrides=dict(overrides))

            # Phase C — inject each override as a counterfactual triple.
            for attr_key, value in overrides.items():
                # Derive the predicate label from the predicate map, or fall
                # back to a sensible default based on the attribute key.
                predicate = pred_map.get(attr_key, attr_key)
                ctx.record_triple(entity_name, predicate, str(value))

            self._logger.info(
                "Applied premise: %r — %d overrides",
                entity_name, len(overrides),
            )

    # ── Internal: merged-triple collection ───────────────────────────────────

    def _collect_merged_triples(
        self,
        ctx: SimulationMemoryContext,
        concepts: List[str],
    ) -> List[Triple]:
        """Collect the merged triple view (real KG + delta) for all concepts.

        Gathers triples where any concept appears as either the subject or the
        object, giving the reasoning engine the same contextual neighbourhood
        it would see from the baseline ``triple_retriever``.
        """
        gathered: List[Triple] = []
        seen: set[Triple] = set()

        for concept in concepts:
            for triple in ctx.get_triples(subject=concept):
                if triple not in seen:
                    seen.add(triple)
                    gathered.append(triple)
            for triple in ctx.get_triples(obj=concept):
                if triple not in seen:
                    seen.add(triple)
                    gathered.append(triple)

        self._logger.debug("Collected %d merged triples for %d concepts", len(gathered), len(concepts))
        return gathered

    # ── Internal: delta computation ──────────────────────────────────────────

    def _fact_signature(self, f: Fact) -> Tuple[str, str, str]:
        """Canonical triple signature for dedup / diff."""
        return (f.subject, f.predicate, f.obj)

    def _path_signature(self, p: ReasoningPath) -> Tuple[str, str]:
        """The (start, end) pair that identifies a reasoning connection."""
        return (p.start, p.end)

    def _compute_delta(
        self,
        baseline_trace: ReasoningTrace,
        simulated_trace: ReasoningTrace,
        concepts: List[str],
        query: str,
        premise: Dict[str, Dict[str, Any]],
    ) -> CausalDelta:
        """Diff the two traces and produce the CausalDelta."""

        # ── Fact diff ────────────────────────────────────────────────────────
        base_facts: List[Fact] = baseline_trace.winning_facts + baseline_trace.inferred_facts
        sim_facts: List[Fact] = simulated_trace.winning_facts + simulated_trace.inferred_facts

        base_sigs: set[Tuple[str, str, str]] = {self._fact_signature(f) for f in base_facts}
        sim_sigs: set[Tuple[str, str, str]] = {self._fact_signature(f) for f in sim_facts}

        lost_sigs = base_sigs - sim_sigs
        gained_sigs = sim_sigs - base_sigs
        shared_sigs = base_sigs & sim_sigs

        # Rehydrate Fact objects.
        sig_to_fact = {self._fact_signature(f): f for f in base_facts + sim_facts}
        facts_lost = [sig_to_fact[s] for s in lost_sigs]
        facts_gained = [sig_to_fact[s] for s in gained_sigs]
        facts_shared = [sig_to_fact[s] for s in shared_sigs]

        # ── Path diff ────────────────────────────────────────────────────────
        base_path_sigs: set[Tuple[str, str]] = {
            self._path_signature(p) for p in baseline_trace.paths
        }
        sim_path_sigs: set[Tuple[str, str]] = {
            self._path_signature(p) for p in simulated_trace.paths
        }
        paths_lost = sorted(base_path_sigs - sim_path_sigs)
        paths_gained = sorted(sim_path_sigs - base_path_sigs)

        # ── Contradiction diff ──────────────────────────────────────────────
        base_contra_sigs: set[Tuple[str, str, str, str]] = {
            (c.subject, c.predicate, c.winner.as_tuple(), c.loser.as_tuple())
            for c in baseline_trace.contradictions
        }
        sim_contra_sigs: set[Tuple[str, str, str, str]] = {
            (c.subject, c.predicate, c.winner.as_tuple(), c.loser.as_tuple())
            for c in simulated_trace.contradictions
        }

        sig_to_contra = {(
            c.subject, c.predicate, c.winner.as_tuple(), c.loser.as_tuple()
        ): c for c in baseline_trace.contradictions + simulated_trace.contradictions}

        contradictions_introduced = [
            sig_to_contra[s] for s in (sim_contra_sigs - base_contra_sigs)
        ]
        contradictions_resolved = [
            sig_to_contra[s] for s in (base_contra_sigs - sim_contra_sigs)
        ]

        # ── Confidence delta ─────────────────────────────────────────────────
        confidence_delta = simulated_trace.confidence - baseline_trace.confidence

        # ── Answer-flipped heuristic ─────────────────────────────────────────
        concept_set = set(concepts)

        def _fact_involves_concept(f: Fact) -> bool:
            return f.subject in concept_set or f.obj in concept_set

        lost_query_facts = [f for f in facts_lost if _fact_involves_concept(f)]
        gained_query_facts = [f for f in facts_gained if _fact_involves_concept(f)]

        answer_flipped = (
            # Heuristic 1: a query-relevant fact was lost or gained.
            bool(lost_query_facts or gained_query_facts)
            or
            # Heuristic 2: confidence collapsed from a meaningful baseline.
            (
                baseline_trace.confidence >= 0.5
                and confidence_delta <= -0.3
            )
            or
            # Heuristic 3: all query-concept paths broke.
            (
                len(baseline_trace.paths) > 0
                and len(simulated_trace.paths) == 0
            )
        )

        # ── Assemble ─────────────────────────────────────────────────────────
        return CausalDelta(
            answer_flipped=answer_flipped,
            confidence_delta=confidence_delta,
            facts_lost=facts_lost,
            facts_gained=facts_gained,
            facts_shared=facts_shared,
            paths_lost=paths_lost,
            paths_gained=paths_gained,
            path_count_delta=len(simulated_trace.paths) - len(baseline_trace.paths),
            contradictions_introduced=contradictions_introduced,
            contradictions_resolved=contradictions_resolved,
            baseline_trace=baseline_trace,
            simulated_trace=simulated_trace,
            query=query,
            premise=premise,
        )
