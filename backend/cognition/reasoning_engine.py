"""
VELYNX Symbolic Reasoning Engine
================================

A *deterministic*, *autonomous* cognitive reasoning core. This module contains
**no** LLM clients, no prompting, and no external/local model inference. All
reasoning is performed natively over:

    * Symbolic logic        (typed predicates over entities)
    * Graph traversal       (pathfinding across Knowledge-Graph triples)
    * Thermodynamic state   (a scalar that tunes how strict vs. exploratory
                             the traversal and inference are)

The engine consumes Knowledge-Graph triples (Subject, Predicate, Object,
Confidence) and the concepts extracted from a user prompt, and emits a purely
*symbolic* ``ReasoningTrace`` describing the exact logical path taken, the
facts that won contradiction resolution, any deductively inferred facts, and a
calibrated confidence score in ``[0.0, 1.0]``.

Crucially, this engine **does not** produce natural language. Translating a
``ReasoningTrace`` into English is the job of a separate Synthesizer module.
"""
from __future__ import annotations

import asyncio
import logging
import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional, Sequence

from backend.knowledge.predicate_resolver import predicate_resolver

logger = logging.getLogger("velynx.reasoning_engine")

# --------------------------------------------------------------------------- #
#  Predicate taxonomy
# --------------------------------------------------------------------------- #
# Predicates that express a *transitive* relation. If (A pred B) and (B pred C)
# hold for the same transitive predicate, then (A pred C) may be deduced.
#
# Both the *surface forms* (what users / NER pipelines may write) and the
# *core forms* (what the consolidator's predicate resolver collapses them to
# — see :mod:`backend.knowledge.predicate_resolver`) are listed so the engine
# stays robust regardless of which path produced the fact.
_TRANSITIVE_PREDICATES = {
    "causes",
    "cause",
    "leads_to",
    "leads to",
    "results_in",
    "results in",
    "is_a",
    "is a",
    "isa",
    "be",
    "subclass_of",
    "subclass of",
    "part_of",
    "part of",
    "precedes",
    "requires",
    "depends_on",
    "depends on",
    "implies",
    "before",
}

# Predicates that assert an *attribute/identity* of a subject. Two such facts
# about the same (subject, predicate) with different objects are a candidate
# contradiction (e.g. "A IS X" vs "A IS Y").
#
# Membership is checked *synonym-aware* (see ``_predicates_match`` /
# :data:`predicate_resolver`), so listing one representative surface form per
# relation is enough — every synonym that resolves to the same core predicate
# is caught. Listing both surface and core forms here is purely for readability.
_FUNCTIONAL_PREDICATES = {
    "is",
    "is_a",
    "is a",
    "isa",
    "be",
    "equals",
    "has_value",
    "has value",
    "located_in",
    "located in",
    "born_in",
    "born in",
    "type_of",
    "type of",
    "color_is",
    "state_is",
    # ── Authorship / creation (single-valued by convention) ─────────────────
    # The consolidator's belief-revision layer already treats "create" as a
    # singular relation and intentionally KEEPS both edges of a third-party
    # creator conflict (e.g. "Blender create Ton" + "Blender create John") so
    # the reasoner can adjudicate it. Without "create" here, the engine filed
    # those two competing edges under the non-functional ``passthrough`` branch
    # and NEVER compared them — so two rival creators coexisted silently and
    # the expected contradiction was never flagged (the "Vanishing John Smith"
    # bug). "create" is the core form every create-family synonym
    # (created/authored/built/founded/...) resolves to, so this single entry
    # makes all of them contradiction-eligible.
    "create",
    "created",
    "authored",
}


def _predicates_match(a: str, b: str) -> bool:
    """True when ``a`` and ``b`` refer to the same relation.

    Delegates to :func:`predicate_resolver.predicates_match` so surface-form
    synonyms ("created" vs "create", "is" vs "be", "authored" vs "create")
    are recognised as the same predicate everywhere the engine compares them.
    Falls back to a case-insensitive equality check so the function remains
    usable even for predicates the resolver has no synonym mapping for.
    """
    try:
        if predicate_resolver.predicates_match(a, b):
            return True
    except Exception:
        pass
    return str(a or "").strip().lower() == str(b or "").strip().lower()

# Predicates considered semantically negating / opposing one another.
_NEGATION_TOKENS = ("not_", "not ", "no_", "anti_", "non_")

# Asymmetric predicates carry a canonical (subject, object) DIRECTION — the same
# assertion extracted in active vs passive voice ("Ton created Blender" vs
# "Blender was created by Ton") yields two direction-inverted rows describing
# ONE fact. Without dedup the reasoner traverses the edge twice and inflates
# path/winning-fact counts. This set MUST stay in sync with
# :data:`backend.knowledge.consolidator._ASYMMETRIC_PREDICATES`; both hold the
# core forms the predicate resolver collapses the create/locative families onto.
_ASYMMETRIC_PREDICATES = frozenset({"create", "located_in"})


# --------------------------------------------------------------------------- #
#  Symbolic data structures
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Fact:
    """A single normalized symbolic assertion (a Knowledge-Graph triple)."""

    subject: str
    predicate: str
    obj: str
    confidence: float = 0.5
    source: str = ""

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.subject, self.predicate, self.obj)

    def __str__(self) -> str:  # purely symbolic, no prose
        return f"({self.subject} -[{self.predicate}]-> {self.obj} | c={self.confidence:.2f})"


@dataclass
class PathStep:
    """One hop in a reasoning path."""

    fact: Fact

    def __str__(self) -> str:
        return str(self.fact)


@dataclass
class ReasoningPath:
    """A logical path linking two query concepts via a chain of facts."""

    start: str
    end: str
    steps: list[PathStep] = field(default_factory=list)
    confidence: float = 0.0

    @property
    def length(self) -> int:
        return len(self.steps)

    @property
    def nodes(self) -> list[str]:
        if not self.steps:
            return [self.start]
        seq = [self.steps[0].fact.subject]
        for s in self.steps:
            seq.append(s.fact.obj)
        return seq

    def __str__(self) -> str:
        chain = " => ".join(str(s) for s in self.steps)
        return f"PATH[{self.start} ~> {self.end}] ({self.confidence:.2f}): {chain}"


@dataclass
class Contradiction:
    """Record of two conflicting facts and the resolution outcome."""

    subject: str
    predicate: str
    winner: Fact
    loser: Fact
    margin: float
    resolved: bool
    rationale: str  # symbolic rationale tag, not prose


@dataclass
class ReasoningTrace:
    """
    The complete, purely-symbolic output of the reasoning engine.

    This object is the contract handed to the downstream Synthesizer. It
    contains *no* natural-language answer — only structured logic.
    """

    query_concepts: list[str] = field(default_factory=list)
    paths: list[ReasoningPath] = field(default_factory=list)
    winning_facts: list[Fact] = field(default_factory=list)
    inferred_facts: list[Fact] = field(default_factory=list)
    contradictions: list[Contradiction] = field(default_factory=list)
    unresolved_concepts: list[str] = field(default_factory=list)
    confidence: float = 0.0
    thermodynamic_state: float = 0.5
    # diagnostic / introspection metadata (symbolic, machine-readable)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_concepts": list(self.query_concepts),
            "paths": [
                {
                    "start": p.start,
                    "end": p.end,
                    "nodes": p.nodes,
                    "steps": [s.fact.as_tuple() for s in p.steps],
                    "confidence": round(p.confidence, 4),
                }
                for p in self.paths
            ],
            "winning_facts": [f.as_tuple() + (round(f.confidence, 4),) for f in self.winning_facts],
            "inferred_facts": [f.as_tuple() + (round(f.confidence, 4),) for f in self.inferred_facts],
            "contradictions": [
                {
                    "subject": c.subject,
                    "predicate": c.predicate,
                    "winner": c.winner.as_tuple(),
                    "loser": c.loser.as_tuple(),
                    "margin": round(c.margin, 4),
                    "resolved": c.resolved,
                    "rationale": c.rationale,
                }
                for c in self.contradictions
            ],
            "unresolved_concepts": list(self.unresolved_concepts),
            "confidence": round(self.confidence, 4),
            "thermodynamic_state": round(self.thermodynamic_state, 4),
            "metadata": self.metadata,
        }


# --------------------------------------------------------------------------- #
#  The engine
# --------------------------------------------------------------------------- #
class ReasoningEngine:
    """
    Native symbolic reasoning engine for VELYNX.

    No language models. Reasoning emerges from graph structure, predicate
    semantics, evidence confidence, and the system's thermodynamic state.

    Parameters
    ----------
    kg : optional
        Knowledge-Graph handle (e.g. ``KnowledgeGraph``). Optional — the engine
        operates purely on the triples passed into :meth:`reason`. Retained for
        API compatibility with ``VelynxBrain`` and to allow on-demand triple
        retrieval when the caller does not pre-fetch.
    vs : optional
        Vector-store handle. Optional and unused for core symbolic logic; kept
        for constructor compatibility and to interpret episodic context.
    """

    # Absolute floor on evidence confidence regardless of thermodynamic state.
    MIN_CONFIDENCE_FLOOR = 0.05

    # Hard ceiling (seconds) on a single build_chain() reasoning pass. Graph
    # traversal is bounded, but a pathological triple set could still be slow;
    # this guarantees the async answer path never blocks indefinitely.
    BUILD_CHAIN_TIMEOUT_S = 10.0

    def __init__(self, kg: Any = None, vs: Any = None) -> None:
        self.kg = kg
        self.vs = vs

    # ------------------------------------------------------------------ #
    #  Public API (the spec contract)
    # ------------------------------------------------------------------ #
    def reason(
        self,
        query_concepts: Sequence[str],
        retrieved_triples: Iterable[Any] | None = None,
        episodic_context: Iterable[Any] | None = None,
        thermodynamic_state: float = 0.5,
        query_predicate: str = "",
        world_model_facts: Iterable[Any] | None = None,
    ) -> ReasoningTrace:
        """
        Perform deterministic symbolic reasoning.

        Parameters
        ----------
        query_concepts:
            Entities/concepts extracted from the user's prompt.
        retrieved_triples:
            KG triples ``(Subject, Predicate, Object, Confidence)``. Accepts
            tuples, dicts, ``Fact``, or any object exposing
            ``subject/predicate(or relation)/obj(or object)/confidence``.
        episodic_context:
            Recent conversation vectors / records. Used only to *bias*
            concept salience; never to generate text.
        thermodynamic_state:
            System energy in ``[0.0, 1.0]``. Low = cold/strict/conservative
            traversal; high = hot/exploratory/creative traversal.
        query_predicate:
            The *core* relation the user actually asked about (e.g. ``create``
            for "Who created Blender?"). When supplied, contradiction detection
            becomes **predicate-aware**: only conflicts on this predicate are
            flagged and allowed to penalize confidence. Conflicting facts on
            *unrelated* predicates (e.g. a "blender —[be]→ X" disagreement when
            the question is about "create") are resolved silently and never
            tank the confidence of the answer-bearing edge. Empty string
            preserves the legacy behavior of flagging every functional conflict.
        world_model_facts:
            Structured ontology triples derived from the World Model registry
            (entity type chains, facet membership, and resolved attribute
            values — see
            :func:`backend.knowledge.world_model_context.world_model_facts_for_concepts`).
            Unlike ``episodic_context`` (a free-text channel that can only nudge
            a scalar salience bias), these are coerced into first-class
            :class:`Fact` objects and merged into the working knowledge base, so
            they participate FULLY in contradiction resolution, deductive
            inference, pathfinding, and concept resolution. This is what lets
            the reasoner connect an entity to an *inherited* attribute it was
            never explicitly taught — e.g. ``Tesla Model 3 —[mobility_type]→
            wheeled`` lets "Does a Tesla Model 3 have wheels?" resolve instead
            of dead-ending at "no connecting evidence". High-confidence by
            construction (the ontology is curated), but still subject to
            contradiction resolution so direct taught evidence can supersede it.

        Returns
        -------
        ReasoningTrace
            A purely symbolic trace. No natural language.
        """
        state = self._clamp01(float(thermodynamic_state))
        concepts = self._normalize_concepts(query_concepts)
        facts = self._normalize_triples(retrieved_triples)

        # World Model structured facts — coerce and merge into the fact pool so
        # ontology-derived edges participate fully in every downstream stage
        # (contradiction resolution, deduction, pathfinding, concept
        # resolution), not merely as a scalar salience bias. Appended AFTER the
        # retrieved triples so that, on an exact (subject, predicate, object)
        # collision, contradiction resolution adjudicates by confidence rather
        # than silently preferring one channel.
        wm_facts = self._normalize_triples(world_model_facts)
        if wm_facts:
            facts = facts + wm_facts

        # Question-Framed Value Bridging ---------------------------------- #
        # The ontology stores an attribute VALUE ("wheeled") that morphologically
        # answers a query concept ("wheels"), but the value is not itself a query
        # node, so no path connects the subject to the asked-about concept. When
        # the query is interrogative, synthesize a bridging edge
        # (subject —[has]→ <query concept>) for each such stem match so the
        # concept resolves and the graph path closes. Guarded so it only fires
        # for genuine value↔concept morphological matches (see _bridge_facts).
        bridge_facts = self._bridge_value_facts(concepts, wm_facts)
        if bridge_facts:
            facts = facts + bridge_facts

        # Thermodynamics → traversal policy ------------------------------- #
        policy = self._derive_policy(state)
        logger.debug(
            "reason(): %d concepts, %d facts, state=%.3f, policy=%s",
            len(concepts), len(facts), state, policy,
        )

        # 1) Contradiction resolution ------------------------------------- #
        # Resolve over the FULL normalized fact set so that weak-but-conflicting
        # evidence is still surfaced and adjudicated. Confidence and the
        # thermodynamic state jointly decide the winner; only afterwards do we
        # apply the state-derived admissibility threshold for traversal.
        resolved_all, contradictions = self._resolve_contradictions(
            facts, state, query_predicate
        )

        # Filter the resolved evidence by the state-derived confidence
        # threshold (cold = strict, hot = permissive) for downstream traversal.
        resolved_facts = [
            f for f in resolved_all if f.confidence >= policy["conf_threshold"]
        ]
        admissible = resolved_facts

        # 2) Deductive inference ------------------------------------------ #
        inferred = self._deduce(resolved_facts, policy)

        # The working knowledge base = resolved evidence + inferred facts.
        working = resolved_facts + inferred

        # 3) Pathfinding between query concepts --------------------------- #
        paths = self._find_paths(concepts, working, policy)

        # 4) Determine which facts actually carried the reasoning --------- #
        winning_facts = self._collect_winning_facts(paths, resolved_facts, concepts)

        # 5) Episodic salience bias (no text, only weighting) ------------- #
        salience = self._episodic_salience(concepts, episodic_context)

        # 6) Unresolved concepts ------------------------------------------ #
        connected: set[str] = set()
        for p in paths:
            connected.update(self._key(n) for n in p.nodes)
        for f in winning_facts:
            connected.add(self._key(f.subject))
            connected.add(self._key(f.obj))
        unresolved = [c for c in concepts if self._key(c) not in connected]

        # 7) Confidence aggregation --------------------------------------- #
        confidence = self._aggregate_confidence(
            concepts=concepts,
            paths=paths,
            winning_facts=winning_facts,
            inferred=inferred,
            contradictions=contradictions,
            unresolved=unresolved,
            salience=salience,
            state=state,
            query_predicate=query_predicate,
        )

        trace = ReasoningTrace(
            query_concepts=concepts,
            paths=paths,
            winning_facts=winning_facts,
            inferred_facts=inferred,
            contradictions=contradictions,
            unresolved_concepts=unresolved,
            confidence=confidence,
            thermodynamic_state=state,
            metadata={
                "policy": policy,
                "n_triples_in": len(facts),
                "n_admissible": len(admissible),
                "n_resolved": len(resolved_facts),
                "n_inferred": len(inferred),
                "n_paths": len(paths),
                "episodic_salience": salience,
                "n_world_model_facts": len(wm_facts),
                "n_bridge_facts": len(bridge_facts),
            },
        )
        return trace

    # ------------------------------------------------------------------ #
    #  Compatibility adapter for VelynxBrain (build_chain)
    # ------------------------------------------------------------------ #
    async def build_chain(
        self,
        query: str,
        vec_results: Any = None,
        context: dict | None = None,
    ) -> ReasoningTrace:
        """
        Adapter so the existing :class:`VelynxBrain` answer path keeps working.

        Extracts concepts from the (already-retrieved) evidence, pulls triples
        either from ``context`` or — if available — the bound knowledge graph,
        then delegates to :meth:`reason`. Returns a :class:`ReasoningTrace`
        whose ``.steps`` attribute exposes the flattened path steps that the
        brain expects.
        """
        context = context or {}
        thermo = self._clamp01(float(context.get("thermodynamic_state", 0.5)))

        # Concepts: prefer explicit, else derive from vec_results / query.
        concepts = context.get("query_concepts")
        if not concepts:
            concepts = self._concepts_from_vec(vec_results) or self._tokenize_query(query)

        # Triples: prefer explicit, else attempt KG retrieval if bound.
        triples = context.get("retrieved_triples")
        if triples is None and self.kg is not None:
            triples = await self._retrieve_from_kg(concepts)

        episodic = context.get("episodic_context", vec_results)

        # World Model structured facts (Phase 62.1): the caller may pre-resolve
        # ontology triples for the query concepts and pass them via context so
        # they join the fact pool as first-class edges (see reason()).
        world_model_facts = context.get("world_model_facts")

        # Predicate grounding: prefer an explicitly-supplied core predicate, else
        # lift the relation verb from the query itself so contradiction flagging
        # is scoped to what the user actually asked (see reason()).
        query_predicate = context.get("query_predicate") or ""
        if not query_predicate and query:
            try:
                from backend.knowledge.predicate_resolver import extract_predicate

                query_predicate = extract_predicate(query)
            except Exception:
                query_predicate = ""

        # Run the synchronous, CPU-bound reasoning off the event loop and cap it
        # with a hard timeout so the async answer path can never hang.
        try:
            trace = await asyncio.wait_for(
                asyncio.to_thread(
                    self.reason,
                    concepts,
                    triples or [],
                    episodic,
                    thermo,
                    query_predicate,
                    world_model_facts,
                ),
                timeout=self.BUILD_CHAIN_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "build_chain reasoning timed out after %.1fs; returning empty trace",
                self.BUILD_CHAIN_TIMEOUT_S,
            )
            trace = ReasoningTrace(
                query_concepts=concepts,
                thermodynamic_state=thermo,
                metadata={"timed_out": True},
            )
        # Expose a flat .steps view (brain reads chain.steps).
        flat_steps = [str(s) for p in trace.paths for s in p.steps]
        # Attach dynamically without breaking the dataclass contract.
        setattr(trace, "steps", flat_steps)
        return trace

    # ================================================================== #
    #  Normalization helpers
    # ================================================================== #
    @staticmethod
    def _clamp01(x: float) -> float:
        if math.isnan(x):
            return 0.5
        return max(0.0, min(1.0, x))

    @staticmethod
    def _key(s: str) -> str:
        """Canonical comparison key for an entity label."""
        return str(s).strip().lower()

    def _normalize_concepts(self, query_concepts: Sequence[str] | None) -> list[str]:
        if not query_concepts:
            return []
        seen: set[str] = set()
        out: list[str] = []
        for c in query_concepts:
            if c is None:
                continue
            label = str(c).strip()
            if not label:
                continue
            k = self._key(label)
            if k not in seen:
                seen.add(k)
                out.append(label)
        return out

    def _normalize_triples(self, triples: Iterable[Any] | None) -> list[Fact]:
        if not triples:
            return []
        facts: list[Fact] = []
        for t in triples:
            fact = self._coerce_fact(t)
            if fact is not None:
                facts.append(fact)
        return facts

    def _coerce_fact(self, t: Any) -> Optional[Fact]:
        """Coerce a heterogeneous triple representation into a :class:`Fact`."""
        try:
            if isinstance(t, Fact):
                return self._clean_fact(t.subject, t.predicate, t.obj, t.confidence, t.source)

            if isinstance(t, dict):
                subj = t.get("subject") or t.get("subj") or t.get("s")
                pred = (
                    t.get("predicate")
                    or t.get("relation")
                    or t.get("rel")
                    or t.get("p")
                )
                obj = t.get("object") or t.get("obj") or t.get("o")
                conf = t.get("confidence", t.get("conf", 0.5))
                src = t.get("source", t.get("src", ""))
                if subj is None or pred is None or obj is None:
                    return None
                return self._clean_fact(subj, pred, obj, conf, src)

            if isinstance(t, (tuple, list)):
                if len(t) >= 4:
                    subj, pred, obj, conf = t[0], t[1], t[2], t[3]
                    src = t[4] if len(t) >= 5 else ""
                elif len(t) == 3:
                    subj, pred, obj = t
                    conf, src = 0.5, ""
                else:
                    return None
                return self._clean_fact(subj, pred, obj, conf, src)

            # Generic object with attributes (e.g. ConceptTriple uses .obj).
            subj = getattr(t, "subject", None)
            pred = getattr(t, "predicate", None) or getattr(t, "relation", None)
            obj = getattr(t, "obj", None)
            if obj is None:
                obj = getattr(t, "object", None)
            conf = getattr(t, "confidence", 0.5)
            src = getattr(t, "source", "")
            if subj is None or pred is None or obj is None:
                return None
            return self._clean_fact(subj, pred, obj, conf, src)
        except Exception:  # pragma: no cover - defensive
            logger.debug("Could not coerce triple: %r", t, exc_info=True)
            return None

    def _clean_fact(
        self, subj: Any, pred: Any, obj: Any, conf: Any, src: Any
    ) -> Optional[Fact]:
        subject = str(subj).strip()
        predicate = self._norm_predicate(pred)
        obj_s = str(obj).strip()
        if not subject or not predicate or not obj_s:
            return None
        try:
            confidence = float(conf)
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = self._clamp01(confidence)
        source = str(src).strip() if src is not None else ""
        return Fact(subject=subject, predicate=predicate, obj=obj_s,
                    confidence=confidence, source=source)

    @staticmethod
    def _norm_predicate(pred: Any) -> str:
        """Canonicalise a predicate to its core form.

        The consolidator already routes stored predicates through
        :func:`predicate_resolver.resolve` on the write path, so a fact
        taught as "created" arrives here as "create". We re-resolve here
        too so any fact that bypassed the consolidator (raw KG inserts,
        legacy data, direct API calls) still collapses onto the same
        core predicate the read path is comparing against.
        """
        raw = str(pred).strip().lower().replace("-", "_")
        try:
            return predicate_resolver.resolve(raw) or raw
        except Exception:
            return raw

    # ================================================================== #
    #  Question-Framed Value Bridging
    # ================================================================== #
    # The ontology answers many questions with an attribute *value* rather than
    # an edge to the asked-about noun: a Tesla's wheeledness lives in
    # ``mobility_type=wheeled``, not in a ``Tesla —[has]→ wheels`` triple. The
    # value "wheeled" and the query concept "wheels" are the same morpheme, but
    # the graph has no node named "wheels", so BFS between "Tesla Model 3" and
    # "wheels" finds nothing. Bridging closes that gap: when a world-model fact's
    # OBJECT shares a stem with a query CONCEPT, we mint a single
    # ``(subject —[has]→ <concept>)`` edge so the concept resolves and the path
    # connects — without polluting the KG (the edge is request-scoped).

    # Interrogative markers. The bridge only fires for question-framed queries
    # ("does/do/is/are ... wheels?"), so a declarative mention of a value can't
    # silently spawn a spurious "has" edge. Detected via the concept set's
    # provenance is not available here, so the guard is applied by the caller
    # supplying ONLY genuine query concepts; this set is retained for the
    # value-vs-concept morphological gate below.
    _BRIDGE_MIN_STEM = 4  # require a stem of at least this length (avoid "is"/"ed")
    _BRIDGE_PREDICATE = "has"

    @staticmethod
    def _stem(word: str) -> str:
        """Very small, dependency-free morphological stemmer.

        Strips the handful of inflectional suffixes that separate an ontology
        value from its query-concept form (``wheeled``/``wheels`` → ``wheel``).
        Deliberately conservative: it only removes well-known endings and never
        shortens below three characters, so unrelated short tokens don't
        accidentally collapse onto one another.
        """
        w = str(word or "").strip().lower()
        if len(w) <= 3:
            return w
        # Order matters: try longer/more-specific suffixes first.
        for suf in ("ied",):
            if w.endswith(suf) and len(w) - len(suf) + 1 >= 3:
                return w[: -len(suf)] + "y"
        for suf in ("ing", "ed", "es", "s"):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                return w[: -len(suf)]
        return w

    def _bridge_value_facts(
        self, concepts: list[str], world_model_facts: list[Fact]
    ) -> list[Fact]:
        """Synthesize ``(subject —[has]→ concept)`` edges for value↔concept matches.

        For each world-model fact whose OBJECT stem-matches a query CONCEPT that
        is not itself the fact's subject/object, emit one bridging edge so the
        concept becomes a reachable graph node. Examples:

            concept "wheels"  + fact (Tesla, mobility_type, wheeled) → (Tesla, has, wheels)

        The bridge confidence inherits the source fact's confidence (the
        ontology is authoritative). Edges are de-duplicated and request-scoped —
        they never persist to the KG.
        """
        if not concepts or not world_model_facts:
            return []

        # Pre-stem the query concepts once. Skip concepts that already name a
        # fact subject (they're entities, not attribute-value targets).
        subjects = {self._key(f.subject) for f in world_model_facts}
        concept_by_stem: dict[str, str] = {}
        for c in concepts:
            ck = self._key(c)
            if ck in subjects:
                continue  # the entity itself, not a value to bridge to.
            stem = self._stem(c)
            if len(stem) < self._BRIDGE_MIN_STEM:
                continue
            concept_by_stem.setdefault(stem, c)

        if not concept_by_stem:
            return []

        bridges: list[Fact] = []
        seen: set[tuple[str, str, str]] = set()
        for f in world_model_facts:
            obj_stem = self._stem(f.obj)
            if len(obj_stem) < self._BRIDGE_MIN_STEM:
                continue
            concept = concept_by_stem.get(obj_stem)
            if concept is None:
                continue
            # Don't bridge a subject to itself, and don't restate an existing
            # subject→concept identity.
            if self._key(f.subject) == self._key(concept):
                continue
            key = (self._key(f.subject), self._BRIDGE_PREDICATE, self._key(concept))
            if key in seen:
                continue
            seen.add(key)
            bridges.append(
                Fact(
                    subject=f.subject,
                    predicate=self._BRIDGE_PREDICATE,
                    obj=concept,
                    confidence=f.confidence,
                    source="world_model:bridge",
                )
            )
        return bridges

    # ================================================================== #
    #  Thermodynamic policy
    # ================================================================== #
    def _derive_policy(self, state: float) -> dict[str, Any]:
        """
        Map the thermodynamic state to concrete traversal/inference knobs.

        Cold (state→0): strict — high confidence floor, short paths, no
            speculative (cross-predicate) inference, decisive contradiction
            resolution only on clear winners.
        Hot (state→1): exploratory — low confidence floor, long paths,
            speculative inference enabled, narrow-margin contradictions allowed
            to resolve.
        """
        # Confidence threshold: 0.55 when cold → 0.10 when hot.
        conf_threshold = max(
            self.MIN_CONFIDENCE_FLOOR, 0.55 - 0.45 * state
        )
        # Max path depth: 2 hops cold → 6 hops hot.
        max_depth = int(round(2 + 4 * state))
        # Margin required to declare a contradiction winner:
        #   cold demands a clear 0.25 gap; hot accepts near-ties (0.02).
        resolution_margin = 0.25 - 0.23 * state
        # Number of distinct paths to keep per concept pair.
        max_paths_per_pair = 1 + int(round(2 * state))
        # Whether speculative (mixed-predicate) inference is allowed.
        speculative = state >= 0.5
        return {
            "conf_threshold": round(conf_threshold, 4),
            "max_depth": max_depth,
            "resolution_margin": round(resolution_margin, 4),
            "max_paths_per_pair": max_paths_per_pair,
            "speculative_inference": speculative,
        }

    # ================================================================== #
    #  Contradiction resolution
    # ================================================================== #
    def _resolve_contradictions(
        self, facts: list[Fact], state: float, query_predicate: str = ""
    ) -> tuple[list[Fact], list[Contradiction]]:
        """
        Detect and resolve conflicting facts.

        Two facts conflict when they share the same (subject, predicate) under a
        *functional* predicate but assert different objects, or when one is the
        explicit negation of the other.

        Predicate matching is *synonym-aware* — a fact stored as "is" and a
        fact stored as "be" (the core form the consolidator collapses "is"
        onto) are recognised as the same relation, so a "A be X" / "A is Y"
        pair is correctly treated as a candidate contradiction instead of
        silently surviving side by side.

        Predicate-aware flagging: when ``query_predicate`` is supplied, a
        conflict is only *recorded* (and thus only allowed to penalize
        confidence downstream) when it sits on the predicate the user actually
        asked about. A "blender —[be]→ 3d software" / "blender —[be]→ my
        favorite software" disagreement is irrelevant to "Who *created*
        Blender?", so it is still de-duplicated to a single winner for
        traversal but is *not* surfaced as a contradiction — the answer-bearing
        ``create`` edge keeps its full confidence. When no query predicate is
        known, every functional conflict is flagged (legacy behavior).

        Resolution: the higher-confidence fact wins. The *required* margin to
        declare a decisive winner shrinks as thermodynamic state rises (a hot
        system tolerates ambiguity and commits; a cold system stays
        conservative and keeps both only when truly tied). On an undecidable
        tie, the deterministic tie-break is lexicographic on the object so the
        outcome is reproducible.
        """
        policy_margin = self._derive_policy(state)["resolution_margin"]
        groups: dict[tuple[str, str], list[Fact]] = defaultdict(list)
        passthrough: list[Fact] = []

        for f in facts:
            # Synonym-aware membership: "is" / "be" / "isa" all map to the
            # same functional relation. We check the predicate against the
            # canonical (core) form of every entry in _FUNCTIONAL_PREDICATES
            # so the consolidator's resolved predicates ("be") are caught
            # even though "be" is not a literal member of the set.
            is_functional = any(
                _predicates_match(f.predicate, fp) for fp in _FUNCTIONAL_PREDICATES
            )
            if is_functional:
                # Group by the predicate's *core form* so facts stored under
                # different surface forms of the same relation land in the
                # same contradiction group.
                groups[(self._key(f.subject), f.predicate)].append(f)
            else:
                passthrough.append(f)

        resolved: list[Fact] = list(passthrough)
        contradictions: list[Contradiction] = []

        # Predicate-aware gate: when the user's relation is known, a conflict is
        # only relevant — and only allowed to penalize confidence — if it sits
        # on that same predicate. Synonym-aware so "create"/"created"/"authored"
        # all count as the query's predicate.
        scope_to_query = bool(query_predicate)

        for (subj_key, pred), members in groups.items():
            relevant = (
                not scope_to_query
                or _predicates_match(pred, query_predicate)
            )
            # Collapse exact-duplicate objects, keeping the strongest.
            best_by_obj: dict[str, Fact] = {}
            for f in members:
                k = self._key(f.obj)
                if k not in best_by_obj or f.confidence > best_by_obj[k].confidence:
                    best_by_obj[k] = f
            distinct = list(best_by_obj.values())

            if len(distinct) <= 1:
                resolved.extend(distinct)
                continue

            # Rank candidates: confidence desc, then lexicographic object asc.
            ranked = sorted(
                distinct,
                key=lambda f: (-f.confidence, self._key(f.obj)),
            )
            winner, runner_up = ranked[0], ranked[1]
            margin = winner.confidence - runner_up.confidence

            resolved_flag: bool
            decisive = margin >= policy_margin or margin == 0.0
            if margin == 0.0:
                # True tie → deterministic lexicographic winner, flagged
                # unresolved (the evidence itself cannot decide).
                rationale = "tie:lexicographic"
                resolved_flag = False
            elif decisive:
                rationale = "confidence:decisive"
                resolved_flag = True
            else:
                # Narrow margin, below the cold threshold → keep winner but
                # mark the conflict as unresolved for the synthesizer.
                rationale = "confidence:narrow"
                resolved_flag = False

            # Which facts carry forward into the working set?
            #   * Irrelevant-predicate conflict → de-dup to a single winner so
            #     an unrelated "[be]" disagreement can't tank the confidence of
            #     the "[create]" edge the user asked about.
            #   * Relevant + DECISIVE → belief revision keeps only the survivor
            #     (a clearly higher-confidence fact supersedes the rest).
            #   * Relevant + UNDECIDABLE (tie / narrow margin) → keep ALL rival
            #     facts. This is the "Vanishing John Smith" fix: two equally-
            #     confident creators of Blender are a genuine, unresolved
            #     conflict; collapsing them to one survivor here would silently
            #     drop the loser from winning_facts (it only re-surfaced before
            #     by accident, via a reverse edge). Keeping both guarantees both
            #     competing values reach the synthesizer under the SAME predicate
            #     and direction, so the contradiction is actually visible.
            if not relevant or resolved_flag:
                resolved.append(winner)
            else:
                resolved.extend(distinct)

            # Irrelevant-predicate conflict: don't RECORD it — an unrelated
            # "[be]" disagreement must not surface as a contradiction.
            if not relevant:
                continue

            for loser in ranked[1:]:
                contradictions.append(
                    Contradiction(
                        subject=winner.subject,
                        predicate=pred,
                        winner=winner,
                        loser=loser,
                        margin=margin if loser is runner_up else winner.confidence - loser.confidence,
                        resolved=resolved_flag,
                        rationale=rationale,
                    )
                )
        return resolved, contradictions

    # ================================================================== #
    #  Deductive inference
    # ================================================================== #
    def _deduce(self, facts: list[Fact], policy: dict[str, Any]) -> list[Fact]:
        """
        Forward-chain simple deductive rules.

        Core rule — transitivity over transitive predicates:
            (A pred B) ∧ (B pred C)  ⊢  (A pred C)        [same predicate]

        Speculative rule (only when thermodynamic state is hot enough):
            (A causes B) ∧ (B is_a C) ⊢ (A causes C)      [type lifting]

        Inferred facts get a confidence equal to the product of their premises
        (with a small decay), capping below 1.0, so deductions are always
        weaker than direct evidence.
        """
        if not facts:
            return []

        # Index by subject for fast chaining.
        by_subject_pred: dict[tuple[str, str], list[Fact]] = defaultdict(list)
        for f in facts:
            by_subject_pred[(self._key(f.subject), f.predicate)].append(f)

        existing: set[tuple[str, str, str]] = {
            (self._key(f.subject), f.predicate, self._key(f.obj)) for f in facts
        }
        inferred: list[Fact] = []
        inferred_keys: set[tuple[str, str, str]] = set()

        max_depth = policy["max_depth"]
        speculative = policy["speculative_inference"]
        decay = 0.9

        # --- Transitive closure over a single transitive predicate -------- #
        # Collect the unique transitive predicates present in the working set,
        # but dedup by *core form* so "is_a" and "isa" (the same relation)
        # don't both spawn their own BFS.
        transitive_cores: set[str] = set()
        for f in facts:
            if not any(
                _predicates_match(f.predicate, tp) for tp in _TRANSITIVE_PREDICATES
            ):
                continue
            transitive_cores.add(f.predicate)

        for pred in transitive_cores:
            # BFS transitive closure from each subject up to max_depth hops.
            edges: dict[str, list[Fact]] = defaultdict(list)
            for f in facts:
                if _predicates_match(f.predicate, pred):
                    edges[self._key(f.subject)].append(f)

            for start_fact in [f for f in facts if _predicates_match(f.predicate, pred)]:
                start = start_fact.subject
                # frontier holds (current_node, accumulated_conf, depth, target_obj)
                frontier = deque()
                for nxt in edges.get(self._key(start), []):
                    frontier.append((nxt.obj, nxt.confidence, 1))
                # Guard against circular re-expansion (e.g. A->B->A cycles):
                # each node is expanded at most once per start traversal.
                seen_nodes: set[str] = {self._key(start)}
                while frontier:
                    node, acc_conf, depth = frontier.popleft()
                    node_key = self._key(node)
                    if node_key in seen_nodes:
                        continue
                    seen_nodes.add(node_key)
                    if depth >= max_depth:
                        continue
                    for nxt in edges.get(node_key, []):
                        new_conf = acc_conf * nxt.confidence * decay
                        key = (self._key(start), pred, self._key(nxt.obj))
                        if self._key(start) == self._key(nxt.obj):
                            continue  # no self-loops
                        if key not in existing and key not in inferred_keys:
                            inferred_keys.add(key)
                            inferred.append(
                                Fact(
                                    subject=start,
                                    predicate=pred,
                                    obj=nxt.obj,
                                    confidence=self._clamp01(new_conf),
                                    source="deduced:transitive",
                                )
                            )
                        frontier.append((nxt.obj, new_conf, depth + 1))

        # --- Speculative type-lifting (hot states only) ------------------- #
        if speculative:
            causal = [
                f for f in facts
                if any(_predicates_match(f.predicate, p) for p in ("causes", "cause", "leads_to"))
            ]
            isa = [
                f for f in facts
                if any(_predicates_match(f.predicate, p) for p in ("is_a", "isa", "be", "type_of", "subclass_of"))
            ]
            isa_by_subj: dict[str, list[Fact]] = defaultdict(list)
            for f in isa:
                isa_by_subj[self._key(f.subject)].append(f)
            for c in causal:
                for lift in isa_by_subj.get(self._key(c.obj), []):
                    key = (self._key(c.subject), c.predicate, self._key(lift.obj))
                    if (
                        key not in existing
                        and key not in inferred_keys
                        and self._key(c.subject) != self._key(lift.obj)
                    ):
                        inferred_keys.add(key)
                        inferred.append(
                            Fact(
                                subject=c.subject,
                                predicate=c.predicate,
                                obj=lift.obj,
                                confidence=self._clamp01(c.confidence * lift.confidence * decay * 0.9),
                                source="deduced:type_lift",
                            )
                        )
        return inferred

    # ================================================================== #
    #  Pathfinding
    # ================================================================== #
    def _build_graph(self, facts: list[Fact]) -> dict[str, list[tuple[str, Fact]]]:
        """Directed adjacency: node → list of (neighbor, fact).

        Direction-inverted duplicates are collapsed for asymmetric predicates
        (``create``, ``located_in``, ...). Legacy data and pre-Phase-57
        extractions stored both ``(A, create, B)`` and ``(B, create, A)`` for a
        single assertion, which this adjacency build would otherwise materialise
        as two parallel hops and let the BFS walk the same fact twice. The first
        occurrence wins (deterministic, stable across runs); the duplicate's
        reverse arc is dropped so it can't spawn a second path or a second
        winning fact. Symmetric predicates (``requires``, ``related_to``, ...)
        are order-invariant and are left as-is.
        """
        # Canonical dedup key per asymmetric predicate: unordered pair of
        # endpoints. Two facts sharing the same predicate + endpoint set (in
        # either order) are the same underlying assertion.
        seen_pairs: set[tuple[str, str, str]] = set()
        adj: dict[str, list[tuple[str, Fact]]] = defaultdict(list)
        for f in facts:
            is_asym = f.predicate in _ASYMMETRIC_PREDICATES or any(
                _predicates_match(f.predicate, p) for p in _ASYMMETRIC_PREDICATES
            )
            if is_asym:
                # frozenset-style endpoint pair keyed under the predicate.
                lo, hi = sorted((self._key(f.subject), self._key(f.obj)))
                pair_key = (f.predicate, lo, hi)
                if pair_key in seen_pairs:
                    # Already added the canonical arc for this assertion; skip
                    # the inverted duplicate rather than adding a second hop.
                    continue
                seen_pairs.add(pair_key)
            adj[self._key(f.subject)].append((self._key(f.obj), f))
            # Treat the graph as semantically directed but allow reverse hops
            # for connectivity; reverse traversal is weakened during scoring.
            adj[self._key(f.obj)].append((self._key(f.subject), f))
        return adj

    def _find_paths(
        self, concepts: list[str], facts: list[Fact], policy: dict[str, Any]
    ) -> list[ReasoningPath]:
        """
        Find logical links between each ordered pair of query concepts via BFS
        over the triple graph, e.g. asking about A and C surfaces A → B → C.
        """
        if len(concepts) < 2 or not facts:
            return []

        adj = self._build_graph(facts)
        max_depth = policy["max_depth"]
        max_paths = policy["max_paths_per_pair"]
        results: list[ReasoningPath] = []

        for i in range(len(concepts)):
            for j in range(len(concepts)):
                if i == j:
                    continue
                start, goal = concepts[i], concepts[j]
                found = self._bfs_paths(
                    self._key(start), self._key(goal), adj, max_depth, max_paths
                )
                for fact_chain in found:
                    path = ReasoningPath(start=start, end=goal)
                    for fact in fact_chain:
                        path.steps.append(PathStep(fact=fact))
                    path.confidence = self._path_confidence(fact_chain)
                    results.append(path)

        # Strongest paths first.
        results.sort(key=lambda p: (-p.confidence, p.length))
        return results

    def _bfs_paths(
        self,
        start_key: str,
        goal_key: str,
        adj: dict[str, list[tuple[str, Fact]]],
        max_depth: int,
        max_paths: int,
    ) -> list[list[Fact]]:
        """Breadth-first search returning up to ``max_paths`` fact-chains."""
        if start_key == goal_key:
            return []
        paths: list[list[Fact]] = []
        # Queue holds (node, fact_chain, visited_nodes).
        queue: deque[tuple[str, list[Fact], frozenset[str]]] = deque()
        queue.append((start_key, [], frozenset({start_key})))

        while queue and len(paths) < max_paths:
            node, chain, visited = queue.popleft()
            if len(chain) >= max_depth:
                continue
            for neighbor, fact in adj.get(node, []):
                if neighbor in visited:
                    continue
                new_chain = chain + [fact]
                if neighbor == goal_key:
                    paths.append(new_chain)
                    if len(paths) >= max_paths:
                        break
                else:
                    queue.append((neighbor, new_chain, visited | {neighbor}))
        return paths

    @staticmethod
    def _path_confidence(chain: list[Fact]) -> float:
        """A path is only as strong as the product of its links (with length penalty)."""
        if not chain:
            return 0.0
        conf = 1.0
        for f in chain:
            conf *= max(0.01, f.confidence)
        # Mild length penalty so shorter explanations are preferred.
        length_penalty = 0.97 ** (len(chain) - 1)
        return max(0.0, min(1.0, conf * length_penalty))

    # ================================================================== #
    #  Winning fact collection
    # ================================================================== #
    def _collect_winning_facts(
        self,
        paths: list[ReasoningPath],
        resolved_facts: list[Fact],
        concepts: list[str],
    ) -> list[Fact]:
        """
        The "winning facts" are those that actually carried the reasoning:
        every fact appearing on a discovered path, plus the best direct fact
        touching any query concept when no path used it.
        """
        winners: list[Fact] = []
        seen: set[tuple[str, str, str]] = set()

        def _add(f: Fact) -> None:
            k = (self._key(f.subject), f.predicate, self._key(f.obj))
            if k not in seen:
                seen.add(k)
                winners.append(f)

        for p in paths:
            for s in p.steps:
                _add(s.fact)

        concept_keys = {self._key(c) for c in concepts}
        # Best direct fact per concept that wasn't already captured.
        direct = [
            f
            for f in resolved_facts
            if self._key(f.subject) in concept_keys or self._key(f.obj) in concept_keys
        ]
        direct.sort(key=lambda f: -f.confidence)
        for f in direct:
            _add(f)
        return winners

    # ================================================================== #
    #  Episodic salience (no text generation — weighting only)
    # ================================================================== #
    def _episodic_salience(
        self, concepts: list[str], episodic_context: Iterable[Any] | None
    ) -> float:
        """
        Estimate how strongly the recent episodic context references the query
        concepts. Returns a scalar in ``[0, 1]`` used purely as a confidence
        bias. We do not read or emit any natural language meaning here — only
        token presence is checked against concept labels.
        """
        if not episodic_context or not concepts:
            return 0.0
        concept_keys = {self._key(c) for c in concepts}
        hits = 0
        total = 0
        for item in episodic_context:
            total += 1
            text = self._episodic_to_text(item).lower()
            if not text:
                continue
            if any(ck in text for ck in concept_keys):
                hits += 1
        if total == 0:
            return 0.0
        return self._clamp01(hits / total)

    @staticmethod
    def _episodic_to_text(item: Any) -> str:
        if item is None:
            return ""
        if isinstance(item, str):
            return item
        if isinstance(item, dict):
            for key in ("text", "content", "summary", "snippet", "query", "answer"):
                v = item.get(key)
                if isinstance(v, str):
                    return v
            return " ".join(str(v) for v in item.values() if isinstance(v, str))
        for attr in ("text", "content", "summary", "snippet"):
            v = getattr(item, attr, None)
            if isinstance(v, str):
                return v
        return ""

    # ================================================================== #
    #  Confidence aggregation
    # ================================================================== #
    def _aggregate_confidence(
        self,
        *,
        concepts: list[str],
        paths: list[ReasoningPath],
        winning_facts: list[Fact],
        inferred: list[Fact],
        contradictions: list[Contradiction],
        unresolved: list[str],
        salience: float,
        state: float,
        query_predicate: str = "",
    ) -> float:
        """
        Compute a single scalar confidence in ``[0.0, 1.0]`` from the strength
        of the symbolic evidence:

          + strongest discovered path(s)
          + average strength of the winning direct facts
          + episodic salience (small bonus)
          - penalty for unresolved query concepts
          - penalty for unresolved contradictions
          - penalty for over-reliance on speculative deductions

        Confidence dilution guard: when a ``query_predicate`` is supplied and
        the winning evidence contains at least one fact on that predicate, the
        FINAL score is anchored directly on the strongest such fact —
        ``max(f.confidence for f in matching_facts)``. This short-circuits the
        rest of the aggregation, which would otherwise drag a confident target
        edge (e.g. 0.95) down toward the mean of the surrounding background
        facts (~0.32) through evidence averaging, coverage scaling, and
        thermodynamic dampening. The averaging pipeline below runs ONLY as the
        fallback, when no query predicate is targeted or none of the winners
        match it.
        """
        if not concepts:
            return 0.0
        if not winning_facts and not paths:
            return 0.0

        # Predicate-targeted anchor (confidence-dilution guard).
        #
        # When the user asked about a specific relation (e.g. "create"),
        # anchor the FINAL confidence on the single strongest winning fact that
        # actually answers *that* relation. We must return here, not just
        # reweight an intermediate component — otherwise the downstream
        # path/coverage/thermodynamic blending still dilutes the 0.95 target
        # edge. Synonym-aware via _predicates_match, so "create" matches
        # "created"/"authored"/etc. Falls through to the averaging pipeline
        # only when no predicate is targeted or no winner matches it.
        if query_predicate:
            matching_facts = [
                f for f in winning_facts
                if _predicates_match(f.predicate, query_predicate)
            ]
            if matching_facts:
                return round(
                    self._clamp01(max(f.confidence for f in matching_facts)), 4
                )

        # Path component: best path dominates, secondary paths reinforce.
        if paths:
            best = paths[0].confidence
            support = sum(p.confidence for p in paths[1:]) / max(1, len(paths) - 1) if len(paths) > 1 else 0.0
            path_component = self._clamp01(best * 0.8 + support * 0.2)
        else:
            path_component = 0.0

        # Direct evidence component (fallback: average the full winning set).
        if winning_facts:
            evidence_component = sum(f.confidence for f in winning_facts) / len(winning_facts)
        else:
            evidence_component = 0.0

        base = max(path_component, 0.0) * 0.6 + evidence_component * 0.4

        # Coverage: fraction of concepts that participated.
        coverage = 1.0 - (len(unresolved) / len(concepts))
        base *= 0.4 + 0.6 * coverage  # never zero out entirely on partial coverage

        # Episodic salience bonus (bounded).
        base += 0.05 * salience

        # Contradiction penalty (unresolved ones hurt most).
        unresolved_conflicts = sum(1 for c in contradictions if not c.resolved)
        if contradictions:
            base -= 0.08 * unresolved_conflicts
            base -= 0.02 * (len(contradictions) - unresolved_conflicts)

        # Speculation penalty: deductions are weaker evidence.
        spec = sum(1 for f in inferred if f.source.startswith("deduced"))
        if winning_facts:
            spec_ratio = sum(
                1 for f in winning_facts if f.source.startswith("deduced")
            ) / len(winning_facts)
            base -= 0.10 * spec_ratio

        # A hot system is intrinsically less certain about its leaps; a cold
        # system that still produced an answer is, if anything, more trustworthy.
        base *= 1.0 - 0.10 * state

        return round(self._clamp01(base), 4)

    # ================================================================== #
    #  build_chain support helpers
    # ================================================================== #
    def _concepts_from_vec(self, vec_results: Any) -> list[str]:
        if not vec_results:
            return []
        concepts: list[str] = []
        try:
            for r in vec_results:
                if isinstance(r, dict):
                    label = r.get("title") or r.get("concept") or r.get("topic")
                    if label:
                        concepts.append(str(label))
        except TypeError:
            return []
        return concepts

    @staticmethod
    def _tokenize_query(query: str) -> list[str]:
        """Very small stopword-filtered tokenizer (no NLP model)."""
        if not query:
            return []
        stop = {
            "the", "a", "an", "is", "are", "was", "were", "of", "to", "in",
            "on", "for", "and", "or", "what", "why", "how", "does", "do",
            "did", "with", "about", "between", "that", "this", "it", "as",
        }
        tokens = [
            w.strip(".,?!;:'\"()").lower()
            for w in str(query).split()
        ]
        return [w for w in tokens if w and w not in stop and len(w) > 2]

    async def _retrieve_from_kg(self, concepts: list[str]) -> list[dict]:
        """
        Best-effort triple retrieval from a bound knowledge graph. Tries a few
        conventional method names; returns an empty list if none are available.
        Never raises — the engine remains usable without a KG.
        """
        kg = self.kg
        if kg is None:
            return []
        for method_name in ("find_connected", "lookup", "fast_query"):
            method = getattr(kg, method_name, None)
            if method is None:
                continue
            try:
                results: list[dict] = []
                for c in concepts:
                    out = method(c)
                    if hasattr(out, "__await__"):
                        out = await out
                    if out:
                        if isinstance(out, list):
                            results.extend(out)
                        else:
                            results.append(out)
                if results:
                    return results
            except Exception:
                logger.debug("KG retrieval via %s failed", method_name, exc_info=True)
                continue
        return []


__all__ = [
    "Fact",
    "PathStep",
    "ReasoningPath",
    "Contradiction",
    "ReasoningTrace",
    "ReasoningEngine",
]
