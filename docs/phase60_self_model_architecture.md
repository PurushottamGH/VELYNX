# Phase 60 — Persistent Self Model Architecture

## 1. Problem Statement

VELYNX has four distinct internal subsystems that collectively define its
cognitive state:

| Subsystem | Tracks |
|---|---|
| `KnowledgeGraph` (`living_edges`) | What VELYNX knows — concepts, relationships, confidence |
| `WorkingMemory` (per-session buffer) | What VELYNX was just discussing — active concepts per turn |
| `BeliefSystem` (`BeliefStore`) | What VELYNX believes — claims with confidence and evidence |
| `GoalManager` (curiosity engine) | What VELYNX is trying to learn — pending/active goals |

**What VELYNX cannot do today:**

- **Dynamically compose a self-portrait** — there is no single orchestrator that
  queries all four subsystems on demand and fuses their outputs into a unified
  representation of "what VELYNX knows, believes, and wants about topic X".
- **Represent itself as a first-class entity** — `VELYNX_SELF` does not exist as
  a node in the Knowledge Graph. The graph has no edges for self-referential
  relationships (`knows_about`, `believes_that`, `pursuing_goal`).
- **Distinguish self-referential from external queries** — "What do you know
  about Blender?" and "What is Blender?" both hit the same pipeline. The former
  should construct a self-portrait; the latter should retrieve external facts.
  Currently there is no discriminator.
- **Answer meta-cognitive questions** — "How confident are you about X?",
  "What are you unsure about?", "What did you learn recently?" produce generic
  or empty responses because no module queries the graph's own epistemic state.

Phase 60 introduces a **Persistent Self Model**: a symbolic architecture layer
that makes VELYNX's internal state queryable, introspectable, and articulable —
all without external LLM calls for the aggregation logic.

---

## 2. High-Level Architecture

```
                    User Query
                        │
                        ▼
                ┌────────────────────┐
                │  SelfQueryRouter   │  ← NEW
                │  (pattern-match)   │
                └────────┬───────────┘
                         │
            ┌────────────┼────────────┐
            │ self-ref   │ external   │ meta-cog   │
            ▼            ▼            ▼
    ┌──────────────┐  existing    ┌──────────────┐
    │    Self-     │  pipeline    │   Self-      │
    │   Context    │  (unchanged) │  Model       │
    │  Aggregator  │              │ Introspection│
    └──────┬───────┘              └──────┬───────┘
           │                             │
           ▼                             ▼
    ┌──────────────┐            ┌──────────────┐
    │ SelfResponse │            │  Confidence   │
    │  Composer    │            │  Reporter     │
    └──────────────┘            └──────────────┘

ALL subsystems are queried symbolically (no LLM call).
```

The architecture introduces three new components:

1. **`SelfQueryRouter`** — discriminates self-referential vs external vs
   meta-cognitive queries by pattern matching.
2. **`SelfContextAggregator`** — dynamically queries KG, WorkingMemory,
   BeliefSystem, and GoalManager to build a `SelfContext` for a given topic.
3. **`SelfReferentialGraph`** — represents VELYNX as a first-class entity in the
   Knowledge Graph with structured self-referential edges.

Plus two output composers:
4. **`SelfResponseComposer`** — formats `SelfContext` into a natural-language
   answer.
5. **`ConfidenceReporter`** — answers meta-cognitive questions about epistemic
   state.

---

## 3. Self-Context Aggregator

### 3.1 Purpose

Given a query topic (e.g., `"Blender"`), the aggregator queries all four
subsystems in parallel and fuses the results into a single `SelfContext` object.

### 3.2 Data Model

```python
# backend/self_model/self_context.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class KnowledgeSnapshot:
    """What the KG knows about a topic."""
    topic: str
    has_concept: bool                          # node exists in concepts table
    triples: list[dict] = field(default_factory=list)  # [{relation, target, confidence}]
    related_domains: list[str] = field(default_factory=list)
    confidence: str = "UNKNOWN"                # CERTAIN / PROBABLE / UNCERTAIN / UNKNOWN
    coverage_ratio: float = 0.0                # % of expected ontological attributes present


@dataclass
class MemorySnapshot:
    """What WorkingMemory has about a topic."""
    topic: str
    mentioned_recently: bool
    turn_count: int = 0                        # how many recent turns mentioned it
    last_mention_turn: int = -1
    co_mentioned_with: list[str] = field(default_factory=list)  # sibling concepts


@dataclass
class BeliefSnapshot:
    """What the BeliefSystem believes about a topic."""
    topic: str
    has_beliefs: bool
    beliefs: list[dict] = field(default_factory=list)  # [{claim, confidence, status}]
    contradictions: list[dict] = field(default_factory=list)
    resolved_count: int = 0                    # active beliefs
    conflicted_count: int = 0                  # contradicted beliefs


@dataclass
class GoalSnapshot:
    """What the GoalManager is trying to learn about a topic."""
    topic: str
    has_goals: bool
    pending_goals: list[dict] = field(default_factory=list)  # [{attribute, priority}]
    satisfied_goals: list[dict] = field(default_factory=list)
    failed_goals: list[dict] = field(default_factory=list)
    active_goal_count: int = 0


@dataclass
class SelfContext:
    """Unified self-representation for a topic across all subsystems."""
    topic: str
    timestamp: float = field(default_factory=lambda: __import__("time").time())

    # Subsystem snapshots
    knowledge: KnowledgeSnapshot = field(default_factory=lambda: KnowledgeSnapshot(topic=""))
    memory: MemorySnapshot = field(default_factory=lambda: MemorySnapshot(topic=""))
    beliefs: BeliefSnapshot = field(default_factory=lambda: BeliefSnapshot(topic=""))
    goals: GoalSnapshot = field(default_factory=lambda: GoalSnapshot(topic=""))

    # Aggregated epistemic state
    overall_familiarity: str = "UNKNOWN"       # KNOWS_WELL / KNOWS_SOMEWHAT / UNCERTAIN / UNKNOWN
    active_uncertainties: list[str] = field(default_factory=list)
    knowledge_gaps: list[str] = field(default_factory=list)
```

### 3.3 Aggregation Logic

```python
# backend/self_model/self_context_aggregator.py

from __future__ import annotations

import logging
from typing import Optional

from backend.self_model.self_context import (
    SelfContext,
    KnowledgeSnapshot,
    MemorySnapshot,
    BeliefSnapshot,
    GoalSnapshot,
)
from backend.knowledge.knowledge_graph import KnowledgeGraph
from backend.memory.working_memory import working_memory_manager
from backend.conversation.beliefs import belief_store
from backend.agency.curiosity import goal_manager

logger = logging.getLogger("velynx.self_model")


class SelfContextAggregator:
    """Queries all four subsystems to build a unified SelfContext for a topic.

    This is purely symbolic — every method is a SQL query, a dict lookup, or a
    deterministic composition. No external LLM calls.
    """

    def __init__(
        self,
        kg: Optional[KnowledgeGraph] = None,
        session_id: str = "default",
    ) -> None:
        self.kg = kg or KnowledgeGraph()
        self.session_id = session_id

    # ── Subsystem queries ──────────────────────────────────────────────────

    def _query_knowledge(self, topic: str) -> KnowledgeSnapshot:
        """Query the KnowledgeGraph for what we know about *topic*."""
        topic_lower = topic.lower().strip()

        # Check if the concept exists
        concept = self.kg.get_concept(topic_lower)
        has_concept = concept is not None

        triples: list[dict] = []
        related_domains: set[str] = set()
        if has_concept:
            # Get all outgoing edges (what relations does topic have?)
            for rel in self.kg.get_related(topic_lower):
                triple = {
                    "relation": rel.get("relation", ""),
                    "target": rel.get("target", ""),
                    "confidence": rel.get("confidence", "UNCERTAIN"),
                }
                triples.append(triple)
                if "domain" in rel:
                    related_domains.add(rel["domain"])

        # Compute coverage ratio: % of expected ontological attributes present
        from backend.agency.curiosity import classify_entity, expected_attributes
        category = classify_entity(topic)
        expected = expected_attributes(category)
        known = {t["relation"] for t in triples}
        covered = sum(1 for attr in expected if attr in known)
        coverage = covered / max(len(expected), 1)

        # Overall confidence: take the mode of triple confidences, or UNKNOWN
        confidences = [t["confidence"] for t in triples]
        confidence = self._modal_confidence(confidences) if confidences else "UNKNOWN"

        return KnowledgeSnapshot(
            topic=topic,
            has_concept=has_concept,
            triples=triples,
            related_domains=list(related_domains),
            confidence=confidence,
            coverage_ratio=coverage,
        )

    def _query_working_memory(self, topic: str) -> MemorySnapshot:
        """Query WorkingMemory for recent mentions of *topic*."""
        topic_lower = topic.lower().strip()
        active = working_memory_manager.get_active_concepts(self.session_id)

        # Find mentions and co-mentions
        mentioned_indices = [
            i for i, c in enumerate(active) if c.lower().strip() == topic_lower
        ]
        mentioned_recently = len(mentioned_indices) > 0

        # Co-mentioned concepts (siblings in the same turn)
        co_mentioned: list[str] = []
        if mentioned_recently:
            # Get the raw turn data for more context
            buf = getattr(working_memory_manager, "_buffers", {}).get(self.session_id, [])
            for turn in reversed(list(buf)):
                cleaned = [c.lower().strip() for c in turn]
                if topic_lower in cleaned:
                    co_mentioned.extend(
                        c for c in turn
                        if c.lower().strip() != topic_lower
                        and c.lower().strip() not in (x.lower() for x in co_mentioned)
                    )

        return MemorySnapshot(
            topic=topic,
            mentioned_recently=mentioned_recently,
            turn_count=len(mentioned_indices),
            last_mention_turn=max(mentioned_indices) if mentioned_indices else -1,
            co_mentioned_with=co_mentioned[:8],  # cap at 8
        )

    def _query_beliefs(self, topic: str) -> BeliefSnapshot:
        """Query the BeliefSystem for beliefs about *topic*."""
        topic_lower = topic.lower().strip()

        active_beliefs = belief_store.get_beliefs_for_topic(topic_lower)
        all_beliefs = belief_store._beliefs.get(topic_lower, [])

        beliefs_list: list[dict] = []
        contradictions: list[dict] = []
        for b in active_beliefs:
            beliefs_list.append({
                "claim": b.claim,
                "confidence": b.confidence,
                "status": b.status,
            })
        for b in all_beliefs:
            if b.status == "contradicted":
                contradictions.append({
                    "claim": b.claim,
                    "contradicting_evidence": b.contradicting_evidence,
                })

        return BeliefSnapshot(
            topic=topic,
            has_beliefs=len(active_beliefs) > 0,
            beliefs=beliefs_list,
            contradictions=contradictions,
            resolved_count=len(active_beliefs),
            conflicted_count=len(contradictions),
        )

    def _query_goals(self, topic: str) -> GoalSnapshot:
        """Query the GoalManager for goals related to *topic*."""
        topic_lower = topic.lower().strip()

        all_goals = goal_manager.all()
        pending: list[dict] = []
        satisfied: list[dict] = []
        failed: list[dict] = []

        for g in all_goals:
            if g.target_entity.lower().strip() != topic_lower:
                continue
            entry = {
                "attribute": g.target_attribute,
                "priority": g.priority,
                "id": g.id,
            }
            if g.status.value == "pending":
                pending.append(entry)
            elif g.status.value == "satisfied":
                satisfied.append(entry)
            elif g.status.value == "failed":
                failed.append(entry)

        return GoalSnapshot(
            topic=topic,
            has_goals=len(pending) + len(satisfied) + len(failed) > 0,
            pending_goals=pending,
            satisfied_goals=satisfied,
            failed_goals=failed,
            active_goal_count=len(pending),
        )

    # ── Aggregation ────────────────────────────────────────────────────────

    def _modal_confidence(self, confidences: list[str]) -> str:
        """Return the most frequent confidence label."""
        from collections import Counter
        if not confidences:
            return "UNKNOWN"
        order = ["CERTAIN", "PROBABLE", "UNCERTAIN", "CONTESTED"]
        counts = Counter(confidences)
        # Highest count wins; ties broken by order precedence
        best = max(order, key=lambda c: counts.get(c, 0))
        return best if counts.get(best, 0) > 0 else "UNKNOWN"

    def _compute_overall_familiarity(self, context: SelfContext) -> str:
        """Deterministic aggregate of all four subsystem snapshots."""

        # KNOWS_WELL: has a concept, coverage > 50%, no pending goals, no contradictions
        if (context.knowledge.has_concept
                and context.knowledge.coverage_ratio >= 0.5
                and context.goals.active_goal_count == 0
                and context.beliefs.conflicted_count == 0):
            return "KNOWS_WELL"

        # KNOWS_SOMEWHAT: has a concept but gaps or active goals
        if (context.knowledge.has_concept
                and context.knowledge.coverage_ratio >= 0.25):
            return "KNOWS_SOMEWHAT"

        # UNCERTAIN: has a concept with low coverage, or has contradictory beliefs
        if context.knowledge.has_concept or context.beliefs.resolved_count > 0:
            return "UNCERTAIN"

        # UNKNOWN: no concept, no beliefs, no goals
        return "UNKNOWN"

    def aggregate(self, topic: str) -> SelfContext:
        """Build a complete SelfContext by querying all subsystems."""
        topic = topic.strip()
        knowledge = self._query_knowledge(topic)
        memory = self._query_working_memory(topic)
        beliefs = self._query_beliefs(topic)
        goals = self._query_goals(topic)

        context = SelfContext(
            topic=topic,
            knowledge=knowledge,
            memory=memory,
            beliefs=beliefs,
            goals=goals,
        )
        context.overall_familiarity = self._compute_overall_familiarity(context)

        # Gather active uncertainties from contradictions and low-confidence triples
        uncertainties: list[str] = []
        for bc in context.beliefs.contradictions:
            uncertainties.append(bc["claim"])
        for t in context.knowledge.triples:
            if t["confidence"] in ("UNCERTAIN", "CONTESTED"):
                uncertainties.append(f"{t['relation']} → {t['target']}")
        context.active_uncertainties = uncertainties[:10]  # cap

        # Gather knowledge gaps from pending goals
        context.knowledge_gaps = [g["attribute"] for g in goals.pending_goals]

        return context


# Module-level singleton
self_context_aggregator = SelfContextAggregator()
```

**Key design decisions:**

- **All subsystem queries are symbolic.** Every `_query_*` method is a SQL
  query, a dict lookup, or a deterministic traversal. Zero LLM calls.
- **Parallel-friendly.** Each subsystem query is independent. The
  `aggregate()` method could be trivially parallelised with `concurrent.futures`
  or `asyncio.gather` — but even sequential, each query is O(1) table lookup or
  small-scale BFS.
- **Composable.** Each `_query_*` method is independently testable. The
  `SelfContext` dataclass is a pure value object — serializable to JSON for
  logging or transmission.

---

## 4. Self-Referential Graph Nodes

### 4.1 Purpose

VELYNX should represent itself as a first-class entity in the Knowledge Graph.
This enables the graph's own traversal and confidence machinery to answer
self-referential questions ("What do you know?") with the same symbolic
machinery used for external queries ("What is a qubit?").

### 4.2 Core Entity: `VELYNX_SELF`

**Single canonical node** in the `concepts` table:

```sql
INSERT INTO concepts (name, domain, description)
VALUES ('VELYNX_SELF', 'self_model', 'VELYNX persistent self entity');
```

### 4.3 Self-Referential Edge Types

All edges originate from `VELYNX_SELF` and target other concept nodes or
literal values in the graph.

| Edge Relation | Target | Semantics | Example |
|---|---|---|---|
| `knows_about` | concept | VELYNX has a node for this concept in its graph | `VELYNX_SELF --knows_about--> Blender` |
| `learned_recently` | concept | VELYNX added this concept within the last N insertions | `VELYNX_SELF --learned_recently--> Qubit` |
| `believes_that` | concept | VELYNX holds an active belief whose topic is this concept | `VELYNX_SELF --believes_that--> Creativity` |
| `pursuing_goal` | concept | VELYNX has a PENDING or ACTIVE goal about this concept | `VELYNX_SELF --pursuing_goal--> Blender` |
| `is_curious_about` | concept | VELYNX has identified knowledge gaps for this concept | `VELYNX_SELF --is_curious_about--> Blender` |
| `is_uncertain_about` | concept | Knowledge about this concept has low confidence or contradictions | `VELYNX_SELF --is_uncertain_about--> Dark_Energy` |
| `has_confidence_in` | concept | VELYNX's confidence level in its knowledge of this concept | `VELYNX_SELF --has_confidence_in--> Quantum_Computing` |
| `discussed_recently` | concept | This concept appeared in WorkingMemory within the last few turns | `VELYNX_SELF --discussed_recently--> Neural_Networks` |
| `mastered` | concept | Knowledge coverage > 80%, no gaps, no contradictions | `VELYNX_SELF --mastered--> Python` |

### 4.4 Self-Referential Graph Manager

```python
# backend/self_model/self_referential_graph.py

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger("velynx.self_model")

SELF_ENTITY = "VELYNX_SELF"
SELF_DOMAIN = "self_model"

# Edge types that VELYNX_SELF uses (for validation and queries)
SELF_EDGE_TYPES = frozenset({
    "knows_about",
    "learned_recently",
    "believes_that",
    "pursuing_goal",
    "is_curious_about",
    "is_uncertain_about",
    "has_confidence_in",
    "discussed_recently",
    "mastered",
})


class SelfReferentialGraph:
    """Manages VELYNX_SELF as a first-class entity in the Knowledge Graph.

    All methods are symbolic — they add/remove edges in the ``living_edges``
    table (the Bayesian weighted graph) using the same machinery as any other
    knowledge edge. Self-referential edges are distinguished only by their
    source node being the canonical ``VELYNX_SELF`` entity.

    This manager does NOT recompute edges on every tick. Instead, it exposes
    declarative ``sync_*`` methods that are called:
    - After every ``SelfContextAggregator.aggregate()`` call (on-demand)
    - Periodically by a background tick (every N queries, configurable)
    """

    def __init__(self, kg=None) -> None:
        # Use the v2 Bayesian living edges graph when available; fall back to
        # the v1 symbolic KnowledgeGraph.
        self._kg = kg
        self._ensure_self_entity()

    # ── Lifecycle ──────────────────────────────────────────────────────────

    def _ensure_self_entity(self) -> None:
        """Idempotently create the VELYNX_SELF node in the concepts table."""
        try:
            from backend.knowledge.knowledge_graph import KnowledgeGraph
            kg = self._kg or KnowledgeGraph()
            exists = kg.get_concept(SELF_ENTITY)
            if not exists:
                kg.add_concept(SELF_ENTITY, SELF_DOMAIN, "VELYNX persistent self entity")
                logger.info("Created VELYNX_SELF entity in knowledge graph")
        except Exception as exc:
            logger.debug("Cannot ensure VELYNX_SELF entity: %s", exc)

    def _has_relationship(self, source: str, relation: str, target: str) -> bool:
        """Check whether a relationship already exists (for idempotent adds)."""
        try:
            from backend.knowledge.knowledge_graph import KnowledgeGraph
            kg = self._kg or KnowledgeGraph()
            for rel in kg.get_related(source):
                if (rel.get("source") == source
                        and rel.get("relation") == relation
                        and rel.get("target") == target):
                    return True
        except Exception:
            pass
        return False

    # ── Edge management ────────────────────────────────────────────────────

    def _add_edge(
        self,
        relation: str,
        target: str,
        context: str = "self_model",
    ) -> None:
        """Add a self-referential edge VELYNX_SELF --relation--> target.

        Idempotent: if the edge already exists, this is a no-op (the v1 KG
        uses ``INSERT OR IGNORE`` internally).
        """
        if relation not in SELF_EDGE_TYPES:
            logger.warning("Unknown self-edge type: %s", relation)
            return
        if self._has_relationship(SELF_ENTITY, relation, target):
            return
        try:
            from backend.knowledge.knowledge_graph import KnowledgeGraph
            kg = self._kg or KnowledgeGraph()
            kg.add_relationship(SELF_ENTITY, relation, target)
        except Exception as exc:
            logger.debug("Cannot add self-edge %s -> %s: %s", relation, target, exc)

    def get_self_edges(self) -> list[dict]:
        """Return all outgoing edges from VELYNX_SELF."""
        try:
            from backend.knowledge.knowledge_graph import KnowledgeGraph
            kg = self._kg or KnowledgeGraph()
            return list(kg.get_related(SELF_ENTITY))
        except Exception as exc:
            logger.debug("Cannot get self edges: %s", exc)
            return []

    def get_self_edges_of_type(self, relation: str) -> list[dict]:
        """Return self-edges filtered by relation type."""
        return [e for e in self.get_self_edges() if e.get("relation") == relation]

    # ── Synchronisation ────────────────────────────────────────────────────

    def sync_from_context(self, context: SelfContext) -> None:
        """Synchronise self-referential edges from a SelfContext.

        Called after ``SelfContextAggregator.aggregate()``. Idempotent —
        repeated calls with the same context will add duplicate edges; the
        underlying KG's unique constraint on (source, relation, target)
        prevents true duplication, and weight updates are harmless.
        """
        topic = context.topic

        # knows_about — always set if the concept exists
        if context.knowledge.has_concept:
            self._add_edge("knows_about", topic)

        # learned_recently — set if concept was added within the last N
        # (proxied: any concept that exists and has recent WorkingMemory turns)
        if context.memory.mentioned_recently:
            self._add_edge("learned_recently", topic)

        # believes_that
        if context.beliefs.has_beliefs:
            self._add_edge("believes_that", topic)

        # pursuing_goal / is_curious_about
        if context.goals.active_goal_count > 0:
            self._add_edge("pursuing_goal", topic)
            self._add_edge("is_curious_about", topic)

        # is_uncertain_about
        if context.knowledge.confidence in ("UNCERTAIN", "CONTESTED"):
            self._add_edge("is_uncertain_about", topic)
        elif context.active_uncertainties:
            self._add_edge("is_uncertain_about", topic)

        # has_confidence_in
        if context.knowledge.confidence in ("CERTAIN", "PROBABLE"):
            self._add_edge("has_confidence_in", topic)

        # discussed_recently
        if context.memory.mentioned_recently:
            self._add_edge("discussed_recently", topic)

        # mastered
        if context.overall_familiarity == "KNOWS_WELL":
            self._add_edge("mastered", topic)

    def sync_full_state(self, aggregator: SelfContextAggregator) -> None:
        """Do a full sweep: aggregate contexts for ALL known concepts and
        synchronise self-edges.

        Called on demand for "tell me about yourself" queries, or periodically
        as a background refresh.
        """
        try:
            from backend.knowledge.knowledge_graph import KnowledgeGraph
            kg = self._kg or KnowledgeGraph()
            # all_concepts() returns a list of name strings
            all_concept_names = kg.all_concepts() or []
        except Exception as exc:
            logger.debug("Cannot get all concepts: %s", exc)
            return

        for name in all_concept_names:
            if not name or name == SELF_ENTITY:
                continue
            context = aggregator.aggregate(name)
            self.sync_from_context(context)

        logger.info(
            "Self-referential sync complete: %d concepts processed, %d edges active",
            len(all_concepts),
            len(self.get_self_edges()),
        )
```

---

## 5. Self-Query Router

### 5.1 Purpose

The router's job is to pattern-match a user query and classify it into one of
three lanes:

| Lane | Description | Example Queries |
|---|---|---|
| **EXTERNAL** | Question about the world | "Who created Blender?", "What is Python?" |
| **SELF_REFERENTIAL** | Question about what VELYNX knows | "What do you know about Blender?", "Tell me about what you learned" |
| **META_COGNITIVE** | Question about VELYNX's epistemic state | "How confident are you about X?", "What are you unsure about?" |

### 5.2 Router Implementation

```python
# backend/pipeline/self_query_router.py

from __future__ import annotations

import re
from enum import Enum


class QueryLane(Enum):
    EXTERNAL = "external"
    SELF_REFERENTIAL = "self_referential"
    META_COGNITIVE = "meta_cognitive"
    SELF_IDENTITY = "self_identity"  # "who are you", "describe yourself"


class SelfQueryRouter:
    """Deterministic pattern-matcher that classifies queries into self-model lanes.

    Every pattern is a compiled regex or phrase set. No LLM calls.
    """

    # ── Phase-matched patterns ─────────────────────────────────────────────

    # Self-referential: "what do YOU know/think/believe about X"
    _SELF_REF_PATTERNS: tuple[re.Pattern, ...] = (
        re.compile(r"\b(what do you know about|what do you think about|"
                   r"what have you learned about|tell me what you know about|"
                   r"what can you tell me about|what do you remember about"
                   r")\b", re.IGNORECASE),
        re.compile(r"\b(do you know about|do you know anything about|"
                   r"have you heard of)\b", re.IGNORECASE),
        re.compile(r"\b(what do you believe about|what are your beliefs about"
                   r")\b", re.IGNORECASE),
    )

    # Meta-cognitive: "how confident/uncertain/sure are you about X"
    _META_COG_PATTERNS: tuple[re.Pattern, ...] = (
        re.compile(r"\b(how confident|how sure|how certain|are you confident"
                   r"|are you sure|are you certain)\b", re.IGNORECASE),
        re.compile(r"\b(what are you (unsure|uncertain) about|"
                   r"what don't you know about|what are you not sure about"
                   r")\b", re.IGNORECASE),
        re.compile(r"\b(what are your (gaps|weaknesses|limitations)|"
                   r"where are you weak|what don't you know)\b", re.IGNORECASE),
        re.compile(r"\b(what did you learn (recently|today|lately)|"
                   r"what have you learned)\b", re.IGNORECASE),
        re.compile(r"\b(what are you (working on|curious about|trying to learn)"
                   r"|what is your current goal)\b", re.IGNORECASE),
    )

    # Self-identity: "who are you", "describe yourself", "tell me about yourself"
    _SELF_IDENTITY_PATTERNS: tuple[re.Pattern, ...] = (
        re.compile(r"^(who are you|what are you|describe yourself|"
                   r"tell me about yourself|introduce yourself)\s*$", re.IGNORECASE),
        re.compile(r"^(how are you|how do you work|what can you do)\s*$", re.IGNORECASE),
    )

    # ── External-world question markers (negative patterns) ────────────────

    _EXTERNAL_MARKERS: tuple[str, ...] = (
        "who created", "who invented", "who founded", "who wrote",
        "when was", "where is", "what is the capital of",
        "how many", "how much", "what year",
    )

    # ── Routing logic ──────────────────────────────────────────────────────

    def classify(self, query: str) -> tuple[QueryLane, str | None]:
        """Classify a query and extract the target topic (if applicable).

        Returns (lane, topic) where *topic* is the extracted concept name
        or None for identity queries.
        """
        query_stripped = query.strip()
        if not query_stripped:
            return QueryLane.EXTERNAL, None

        # 1. Self-identity check (exact phrase match, highest priority)
        for pat in self._SELF_IDENTITY_PATTERNS:
            if pat.match(query_stripped):
                return QueryLane.SELF_IDENTITY, None

        # 2. Meta-cognitive check
        for pat in self._META_COG_PATTERNS:
            m = pat.search(query_stripped)
            if m:
                topic = self._extract_topic_after_marker(query_stripped, m)
                return QueryLane.META_COGNITIVE, topic

        # 3. Self-referential check
        for pat in self._SELF_REF_PATTERNS:
            m = pat.search(query_stripped)
            if m:
                topic = self._extract_topic_after_marker(query_stripped, m)
                return QueryLane.SELF_REFERENTIAL, topic

        # 4. Explicit external-world check (questions starting with
        #    "who/what/when/where" that are NOT self-referential)
        lowered = query_stripped.lower()
        for marker in self._EXTERNAL_MARKERS:
            if lowered.startswith(marker):
                return QueryLane.EXTERNAL, self._extract_topic_from_question(
                    query_stripped, marker
                )

        # 5. Default: EXTERNAL (the existing pipeline handles this)
        return QueryLane.EXTERNAL, None

    # ── Topic extraction ───────────────────────────────────────────────────

    @staticmethod
    def _extract_topic_after_marker(query: str, match: re.Match) -> str | None:
        """Extract the noun phrase immediately after the matched pattern.

        E.g., "What do you know about Blender?" → "Blender"
        """
        remainder = query[match.end():].strip().rstrip("?.!")
        # Remove trailing prepositions/articles
        remainder = re.sub(r"\b(about|of|on|in|the|a|an)\s*$", "", remainder, flags=re.IGNORECASE).strip()
        if not remainder:
            return None
        # Take the first significant word or phrase (up to 3 words)
        words = remainder.split()
        return " ".join(words[:3]).strip().rstrip("?")

    @staticmethod
    def _extract_topic_from_question(query: str, marker: str) -> str | None:
        """Extract the topic from a factual question.

        E.g., "Who created Blender?" → "Blender"
        """
        remainder = query[len(marker):].strip().rstrip("?!.")
        return remainder if remainder else None
```

---

## 6. Response Composers

### 6.1 Self-Response Composer

Formats a `SelfContext` into a readable answer string. Uses deterministic
templates — no LLM call.

```python
# backend/self_model/self_response_composer.py

from __future__ import annotations

import logging
from typing import Optional

from backend.self_model.self_context import SelfContext

logger = logging.getLogger("velynx.self_model")


class SelfResponseComposer:
    """Deterministically formats a SelfContext into a natural-language answer."""

    # ── Familiarity prefixes ───────────────────────────────────────────────

    _FAMILIARITY_PREFIX = {
        "KNOWS_WELL": "I know a fair amount about",
        "KNOWS_SOMEWHAT": "I know some things about",
        "UNCERTAIN": "I'm not entirely sure about",
        "UNKNOWN": "I don't know much about",
    }

    def compose(self, context: SelfContext) -> str:
        """Build a complete self-referential answer from a SelfContext."""
        topic = context.topic
        parts: list[str] = []

        # 1. Opening statement (familiarity)
        prefix = self._FAMILIARITY_PREFIX.get(
            context.overall_familiarity, "Regarding"
        )
        parts.append(f"{prefix} **{topic}**.")

        # 2. Knowledge triples (what we know)
        if context.knowledge.triples:
            lines = []
            for t in context.knowledge.triples[:5]:  # cap at 5
                conf = t.get("confidence", "UNKNOWN")
                marker = "🟢" if conf == "CERTAIN" else "🟡" if conf == "PROBABLE" else "🟠"
                lines.append(f"  {marker} {t['relation']} → {t['target']} ({conf})")
            if context.knowledge.coverage_ratio < 0.5:
                lines.append(f"  (Knowledge coverage: {context.knowledge.coverage_ratio:.0%})")
            parts.append("**What I know:**\n" + "\n".join(lines))

        # 3. Beliefs
        if context.beliefs.has_beliefs:
            lines = []
            for b in context.beliefs.beliefs[:3]:
                lines.append(f"  • {b['claim']} ({b['confidence']})")
            if context.beliefs.conflicted_count > 0:
                lines.append(f"  ⚠ {context.beliefs.conflicted_count} contradiction(s)")
            parts.append("**What I believe:**\n" + "\n".join(lines))

        # 4. Recent discussion (working memory)
        if context.memory.mentioned_recently:
            if context.memory.co_mentioned_with:
                together = ", ".join(context.memory.co_mentioned_with[:4])
                parts.append(f"**Recently discussed:** in context with {together}.")
            else:
                parts.append("**Recently discussed:** yes, in our current session.")

        # 5. Knowledge gaps (goals)
        if context.knowledge_gaps:
            gaps = ", ".join(context.knowledge_gaps[:5])
            parts.append(f"**What I'm trying to learn:** {gaps}.")

        # 6. Active uncertainties
        if context.active_uncertainties:
            uncertain = "; ".join(context.active_uncertainties[:3])
            parts.append(f"**Areas of uncertainty:** {uncertain}.")

        return "\n\n".join(parts)

    def compose_identity(self) -> str:
        """Short self-identity answer for 'who are you' queries."""
        return (
            "I am VELYNX, a symbolic cognitive system. "
            "I maintain a persistent knowledge graph, hold beliefs about concepts "
            "I've encountered, track my own curiosity goals, and keep a working "
            "memory of our current conversation. "
            "I can tell you what I know, believe, am learning, or am uncertain about "
            "for any topic I've encountered."
        )

    def compose_compact(self, context: SelfContext) -> str:
        """Single-line summary for space-constrained contexts."""
        topic = context.topic
        k = context.knowledge
        b = context.beliefs
        g = context.goals
        conf = k.confidence
        parts = [
            f"Topic: {topic}",
            f"Familiarity: {context.overall_familiarity}",
            f"Knowledge: {len(k.triples)} triples (confidence: {conf})",
            f"Beliefs: {b.resolved_count} active",
            f"Gaps: {g.active_goal_count} pending",
        ]
        return " | ".join(parts)
```

### 6.2 Confidence Reporter

Answers meta-cognitive questions about VELYNX's epistemic state.

```python
# backend/self_model/confidence_reporter.py

from __future__ import annotations

import logging
from typing import Optional

from backend.self_model.self_context import SelfContext

logger = logging.getLogger("velynx.self_model")


class ConfidenceReporter:
    """Answers questions about VELYNX's confidence in its own knowledge."""

    def report_on_topic(self, context: SelfContext) -> str:
        """How confident is VELYNX about *topic*?"""
        topic = context.topic
        k = context.knowledge

        if not k.has_concept:
            return (
                f"I don't have any knowledge about {topic} in my graph, "
                f"so I can't report confidence."
            )

        triple_details = []
        for t in k.triples:
            triple_details.append(
                f"  {t['relation']} → {t['target']}: {t['confidence']}"
            )

        lines = [
            f"My confidence about **{topic}** is overall **{k.confidence}**.",
            f"Knowledge coverage: {k.coverage_ratio:.0%} of expected attributes.",
            "",
            "**Per-relationship confidence:**",
        ]
        lines.extend(triple_details)

        if context.active_uncertainties:
            lines.append("")
            lines.append(
                f"I have {len(context.active_uncertainties)} active "
                f"uncertainties about this topic."
            )

        if context.knowledge_gaps:
            lines.append("")
            lines.append(
                f"I have {len(context.knowledge_gaps)} identified knowledge "
                f"gaps I'm curious about."
            )

        return "\n".join(lines)

    def report_global_uncertainties(
        self, contexts: list[SelfContext], limit: int = 10
    ) -> str:
        """What are VELYNX's top uncertainties across ALL topics?"""
        uncertain_topics = [
            ctx for ctx in contexts
            if ctx.knowledge.confidence in ("UNCERTAIN", "CONTESTED")
            or ctx.active_uncertainties
        ]
        uncertain_topics.sort(key=lambda ctx: len(ctx.active_uncertainties), reverse=True)
        uncertain_topics = uncertain_topics[:limit]

        if not uncertain_topics:
            return "I don't have any significant uncertainties right now."

        lines = [f"My top {len(uncertain_topics)} areas of uncertainty:"]
        for ctx in uncertain_topics:
            details = "; ".join(ctx.active_uncertainties[:3]) or ctx.knowledge.confidence
            lines.append(f"  • **{ctx.topic}**: {details}")
        return "\n".join(lines)

    def report_recent_learnings(
        self, contexts: list[SelfContext], limit: int = 5
    ) -> str:
        """What has VELYNX learned recently?"""
        known_topics = [
            ctx for ctx in contexts
            if ctx.knowledge.has_concept and ctx.memory.turn_count > 0
        ]
        known_topics.sort(key=lambda ctx: ctx.memory.last_mention_turn, reverse=True)
        known_topics = known_topics[:limit]

        if not known_topics:
            return "I haven't learned anything new recently."

        lines = ["Some things I've encountered recently:"]
        for ctx in known_topics:
            confidence = ctx.knowledge.confidence
            gaps = f" ({len(ctx.knowledge_gaps)} gap(s))" if ctx.knowledge_gaps else ""
            lines.append(f"  • **{ctx.topic}** — {confidence}{gaps}")
        return "\n".join(lines)
```

---

## 7. Pipeline Integration

### 7.1 Interception Point

The `SelfQueryRouter` intercepts queries in `answer_question()` *after* the
reflex check but *before* the existing pipeline cascade:

```
             User Query
                 │
                 ▼
        ┌────────────────┐
        │  reflex check   │
        │  (greeting etc) │
        └────────┬───────┘
                 │ NO
                 ▼
        ┌────────────────────────┐
        │  SelfQueryRouter       │  ← NEW
        │  .classify(query)      │
        └──┬──────┬──────┬──────┘
           │      │      │
      EXTERNAL  SELF_   META_
                 REF    COG
           │      │      │
           ▼      ▼      ▼
      existing   Self-   Confidence
      pipeline   Context  Reporter
      (unchanged) Aggregator
```

### 7.2 Modified Pipeline (backend/app/pipeline.py)

```python
# Inside _answer_question_impl(), add after the reflex block:

from backend.pipeline.self_query_router import SelfQueryRouter, QueryLane
from backend.self_model.self_context_aggregator import SelfContextAggregator
from backend.self_model.self_referential_graph import SelfReferentialGraph
from backend.self_model.self_response_composer import SelfResponseComposer
from backend.self_model.confidence_reporter import ConfidenceReporter

self_query_router = SelfQueryRouter()
self_context_aggregator = SelfContextAggregator()
self_referential_graph = SelfReferentialGraph()
self_response_composer = SelfResponseComposer()
confidence_reporter = ConfidenceReporter()

# ── Step: Self-model routing ─────────────────────────────────────────────
lane, topic = self_query_router.classify(text)

if lane == QueryLane.SELF_IDENTITY:
    answer = self_response_composer.compose_identity()
    return AnswerResponse(
        query=text,
        answer=answer,
        confidence="CERTAIN",
        source="self_model",
        ...
    )

if lane == QueryLane.SELF_REFERENTIAL and topic:
    context = self_context_aggregator.aggregate(topic)
    self_referential_graph.sync_from_context(context)
    answer = self_response_composer.compose(context)
    return AnswerResponse(
        query=text,
        answer=answer,
        confidence=context.knowledge.confidence if context.knowledge.confidence != "UNKNOWN" else "PROBABLE",
        source="self_model",
        debug={"self_context": context},
        ...
    )

if lane == QueryLane.META_COGNITIVE:
    if topic:
        context = self_context_aggregator.aggregate(topic)
        answer = confidence_reporter.report_on_topic(context)
    else:
        # Global meta-cognitive: "what are you unsure about?"
        # Need to aggregate across many topics
        all_contexts = _aggregate_all_known_topics(self_context_aggregator)
        if "unsure" in text.lower() or "uncertain" in text.lower():
            answer = confidence_reporter.report_global_uncertainties(all_contexts)
        elif "learn" in text.lower() or "recent" in text.lower():
            answer = confidence_reporter.report_recent_learnings(all_contexts)
        elif "curious" in text.lower() or "goal" in text.lower():
            answer = _format_global_goals()
        else:
            answer = self_response_composer.compose_identity()
    return AnswerResponse(
        query=text,
        answer=answer,
        confidence="CERTAIN",
        source="self_model",
        ...
    )

# ── Fall through to existing pipeline for EXTERNAL queries ──────────────
```

### 7.3 Helper for Global Aggregation

```python
def _aggregate_all_known_topics(
    aggregator: SelfContextAggregator,
    max_topics: int = 50,
) -> list[SelfContext]:
    """Aggregate SelfContext for all known concepts (capped)."""
    try:
        from backend.knowledge.knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()
        # all_concepts() returns a list of name strings
        all_concept_names = kg.all_concepts() or []
    except Exception:
        return []

    contexts: list[SelfContext] = []
    for name in all_concept_names[:max_topics]:
        if not name or name == "VELYNX_SELF":
            continue
        context = aggregator.aggregate(name)
        contexts.append(context)
    return contexts


def _format_global_goals() -> str:
    """List all pending curiosity goals."""
    from backend.agency.curiosity import goal_manager

    pending = goal_manager.pending()
    if not pending:
        return "I don't have any active learning goals right now."

    lines = [f"I'm curious about {len(pending)} things:"]
    for g in pending[:10]:
        lines.append(f"  • **{g.target_entity}**: learn {g.target_attribute} (priority {g.priority})")
    if len(pending) > 10:
        lines.append(f"  ... and {len(pending) - 10} more.")
    return "\n".join(lines)
```

---

## 8. File Manifest

### 8.1 New Files

| File | Purpose |
|---|---|
| `backend/self_model/self_context.py` | `SelfContext`, `KnowledgeSnapshot`, `MemorySnapshot`, `BeliefSnapshot`, `GoalSnapshot` dataclasses |
| `backend/self_model/self_context_aggregator.py` | `SelfContextAggregator` class — queries all 4 subsystems, composes `SelfContext` |
| `backend/self_model/self_referential_graph.py` | `SelfReferentialGraph` class — manages `VELYNX_SELF` entity and self-edges |
| `backend/self_model/self_response_composer.py` | `SelfResponseComposer` class — formats `SelfContext` into answer text |
| `backend/self_model/confidence_reporter.py` | `ConfidenceReporter` class — meta-cognitive answers about epistemic state |
| `backend/pipeline/self_query_router.py` | `SelfQueryRouter` + `QueryLane` enum — classifies queries into lanes |

### 8.2 Modified Files

| File | Change |
|---|---|
| `backend/app/pipeline.py` | Add self-model routing gate after reflex check; route to `SelfContextAggregator` / `ConfidenceReporter` |
| `backend/self_model/__init__.py` | Export all new self-model classes |
| `backend/pipeline/__init__.py` | Export `SelfQueryRouter`, `QueryLane` |

---

## 9. Edge Cases & Guardrails

### 9.1 Topic Extraction Failures

If the router matches a self-referential pattern but cannot extract a topic:

```python
# In pipeline.py:
if lane == QueryLane.SELF_REFERENTIAL and not topic:
    # No specific topic — return the identity answer instead
    answer = self_response_composer.compose_identity()
```

### 9.2 Empty Knowledge Snapshots

When `_query_knowledge` returns a topic that doesn't exist in the KG:

```python
# The composer gracefully handles this:
context.knowledge.has_concept == False
# → Output: "I don't know much about Blender."
```

### 9.3 Subsystem Unavailability

If a subsystem raises `ImportError` or `ConnectionError`, the aggregator
returns a degraded `SelfContext` with empty/missing fields. The composer
omits sections that are empty:

```python
if context.beliefs.has_beliefs:
    # Only render beliefs section if we have data
```

### 9.4 Graph Sync Race Conditions

The `SelfReferentialGraph.sync_from_context()` is idempotent. If called twice
with the same context, the underlying `UNIQUE(source, relation, target)` on
the `living_edges` table prevents true duplication. Weights are updated, not
duplicated.

### 9.5 Cross-Session Working Memory

WorkingMemory is per-session. If the session is unknown or empty, the
`MemorySnapshot` will show `mentioned_recently=False`. This is correct
behaviour — the system truthfully reports "we haven't discussed this in this
session."

### 9.6 GoalManager with Zero Goals

When `goal_manager` is empty (fresh process), all `GoalSnapshot` values
default to `has_goals=False` and `active_goal_count=0`. The composer
omits the "gaps" section.

### 9.7 Query Ambiguity

Some queries are ambiguous:
- "What do you know?" could be self-identity or self-referential depending
  on context.
- "Do you know about X?" is self-referential (asking about VELYNX's state),
  not external.

The router resolves ambiguity by strict pattern priority:
1. Self-identity patterns (exact phrase match)
2. Meta-cognitive patterns
3. Self-referential patterns (includes "do you know about X")
4. External markers
5. Default = external

---

## 10. Integration with Existing Subsystems

### 10.1 Integration with Phase 57 Agentic Loop

The `SelfContextAggregator` adds a new primitive to the agentic loop's
`PlanAction` enum:

```python
class PlanAction(Enum):
    # ... existing actions ...
    SELF_INTROSPECT = "self_introspect"  # ← NEW
```

A plan step with `action=SELF_INTROSPECT` calls the aggregator, then routes
the result through the composer or confidence reporter depending on the step's
goal.

### 10.2 Integration with Phase 58 Multi-Hop Planning

The self-referential graph edges (`pursuing_goal`, `is_curious_about`) become
first-class graph data that the planner can traverse. A plan that starts with
`"What do you know about X?"` can detect the `pursuing_goal` edge and suggest
filling the gap as a sub-goal.

### 10.3 Integration with Phase 59 Curiosity Engine

The `SelfContextAggregator` already reads from `GoalManager` via
`_query_goals()`. The aggregator's `knowledge_gaps` field is populated
directly from pending goals. This creates a closed loop:

```
Curiosity detects gap → Goal created → Aggregator detects goal
→ Self-edges updated → User asks "what are you curious about?"
→ Aggregator reports gap → User provides information
→ Gap satisfied → Goal status updated → Self-edges refreshed
```

### 10.4 Integration with Existing Self-Model (self_audit / health_monitor)

The existing `CognitiveAuditor` and `CognitiveHealthMonitor` track VELYNX's
health metrics (global_health, saturation, diversity, etc.). The Phase 60
aggregator should include a cognitive health snapshot when constructing a
full self-portrait:

```python
@dataclass
class SelfContext:
    # ... existing fields ...
    cognitive_health: Optional[dict] = None  # ← populated by self_audit

    def populate_health(self) -> None:
        """Attach the latest cognitive health snapshot."""
        try:
            from backend.self_model.identity_store import IdentityStore
            store = IdentityStore("velynx_identity.db")
            health = store.get_latest_health()
            if health:
                self.cognitive_health = {
                    "global_health": health.get("global_health"),
                    "system_state": health.get("system_state"),
                    "confidence_score": health.get("confidence_score"),
                }
        except Exception:
            pass
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

| Module | Test | Assertion |
|---|---|---|
| `SelfQueryRouter.classify()` | "What do you know about Blender?" | `(SELF_REFERENTIAL, "Blender")` |
| `SelfQueryRouter.classify()` | "Who created Blender?" | `(EXTERNAL, "Blender")` |
| `SelfQueryRouter.classify()` | "How confident are you about Blender?" | `(META_COGNITIVE, "Blender")` |
| `SelfQueryRouter.classify()` | "Who are you?" | `(SELF_IDENTITY, None)` |
| `SelfQueryRouter.classify()` | "Tell me about Python" | `(EXTERNAL, None)` |
| `SelfContextAggregator.aggregate()` | Topic not in KG | `has_concept=False`, `overall_familiarity="UNKNOWN"` |
| `SelfContextAggregator.aggregate()` | Topic in KG with triples | `has_concept=True`, triples populated |
| `SelfContextAggregator.aggregate()` | Topic with beliefs | `beliefs.has_beliefs=True` |
| `SelfContextAggregator.aggregate()` | Topic with pending goals | `goals.active_goal_count > 0` |
| `SelfReferentialGraph.sync_from_context()` | `knows_about` edge created | Edge exists in KG |
| `SelfReferentialGraph.get_self_edges()` | After sync | Returns edges of correct types |
| `ConfidenceReporter.report_on_topic()` | Topic with UNCERTAIN confidence | Output contains "uncertain" |
| `SelfResponseComposer.compose()` | `overall_familiarity="KNOWS_WELL"` | Output begins with "I know a fair amount" |

### 11.2 Integration Tests

| Test | Steps |
|---|---|
| Self-referential round trip | `classify("What do you know about Python?")` → `aggregate("Python")` → `compose(context)` → answer contains known triples |
| Meta-cognitive query | `classify("How confident are you about Python?")` → `aggregate("Python")` → `report_on_topic(context)` → output contains confidence level |
| Identity query | `classify("Who are you?")` → `compose_identity()` → output contains "VELYNX" |
| VELYNX_SELF entity | After `sync_full_state()` → `get_self_edges()` returns ≥ 1 edge per concept |
| Pipeline integration | POST `/query` with "What do you know about Blender?" → response `source="self_model"` |

### 11.3 Edge Case Tests

| Test | Expected |
|---|---|
| Empty KG | Aggregator returns `SelfContext` with all `has_* = False` |
| Missing BeliefStore | Belief snapshot returns empty, no crash |
| Empty GoalManager | Goal snapshot returns zero counts |
| Unknown session ID | Working memory returns `mentioned_recently=False` |
| Topic with no triples | Knowledge snapshot has `has_concept=True`, `triples=[]` |
| Very long topic name | Extracted topic is truncated to 3 words |

---

## 12. Summary

Phase 60 adds three new components and two output formatters:

**SelfQueryRouter** — deterministically classifies every query into one of four
lanes (`EXTERNAL`, `SELF_REFERENTIAL`, `META_COGNITIVE`, `SELF_IDENTITY`) using
compiled regex patterns. No LLM call.

**SelfContextAggregator** — queries all four internal subsystems (KnowledgeGraph,
WorkingMemory, BeliefSystem, GoalManager) and fuses their outputs into a single
`SelfContext` dataclass. Every query is a SQL lookup or dict access.

**SelfReferentialGraph** — represents VELYNX as a first-class node
(`VELYNX_SELF`) in the Knowledge Graph with typed edges (`knows_about`,
`believes_that`, `pursuing_goal`, `is_curious_about`, `is_uncertain_about`,
`has_confidence_in`, `discussed_recently`, `mastered`).

**SelfResponseComposer** — formats `SelfContext` into natural-language answers
using deterministic templates.

**ConfidenceReporter** — answers meta-cognitive questions about VELYNX's
epistemic state: confidence levels, uncertainties, recent learnings.

The design is 100% symbolic — every aggregation, classification, and composition
step is a deterministic operation over structured data. VELYNX can now
introspect and articulate its own internal state without delegating the
understanding to an external black box.
