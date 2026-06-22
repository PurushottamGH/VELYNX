"""Self-model — VELYNX knows itself in real time."""
from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("uvicorn")

BACKEND_ROOT = Path(__file__).parent.parent
SOUL_PATH = BACKEND_ROOT / "soul" / "concepts.json"
LEARNING_PATH = BACKEND_ROOT / "velynx_data" / "learning" / "learning_stats.json"


class SelfModel:

    async def snapshot(self) -> dict:
        kg = self._kg_stats()
        return {
            "knowledge": {
                "total_learned": kg["total"],
                "triples": kg["triples"],
                "top_domains": kg["top"][:8],
                "weak_topics": kg["weak"],
            },
            "learning": self._learning(),
            "soul": self.soul_concepts(),
            "health": await self._health(),
            "uptime_sec": self._uptime(),
        }

    def what_i_know(self) -> list[str]:
        return [t for t, _ in self._ranked(0.7, True)]

    def what_i_dont_know(self) -> list[str]:
        return [t for t, _ in self._ranked(0.5)]

    def last_learned(self) -> str | None:
        rows = self._ranked(0.0, True)
        return rows[0][0] if rows else None

    def soul_concepts(self) -> list[str]:
        d = self._read(SOUL_PATH)
        return sorted(d.keys()) if d else []

    # ── internal ─────────────────────────────────────────────

    def _kg_stats(self) -> dict:
        try:
            import sqlite3
            from memory.knowledge_graph import KnowledgeGraph
            from backend.memory._sqlite import connect as open_connection
            db = open_connection(str(KnowledgeGraph().db_path))
            total = db.execute("SELECT COUNT(*) FROM understandings").fetchone()[0]
            triples = db.execute("SELECT COUNT(*) FROM triples").fetchone()[0]
            weak = [r[0] for r in db.execute(
                "SELECT topic FROM understandings WHERE confidence<0.5 ORDER BY confidence LIMIT 20"
            ).fetchall()]
            doms: dict[str, int] = {}
            for t, _ in db.execute("SELECT topic,confidence FROM understandings ORDER BY confidence DESC"):
                k = t.split()[0].rstrip(",:;") if t.split() else "general"
                doms[k] = doms.get(k, 0) + 1
            db.close()
            return {"total": total, "triples": triples, "weak": weak, "top": sorted(doms.items(), key=lambda x: -x[1])[:10]}
        except Exception:
            return {"total": 0, "triples": 0, "weak": [], "top": []}

    def _ranked(self, threshold: float, desc: bool = False) -> list[tuple[str, float]]:
        try:
            import sqlite3
            from memory.knowledge_graph import KnowledgeGraph
            from backend.memory._sqlite import connect as open_connection
            db = open_connection(str(KnowledgeGraph().db_path))
            op, order = (">=", "DESC") if desc else ("<", "ASC")
            rows = db.execute(
                f"SELECT topic,confidence FROM understandings WHERE confidence{op}? ORDER BY confidence {order}",
                (threshold,)
            ).fetchall()
            db.close()
            return [(r[0], r[1]) for r in rows]
        except Exception:
            return []

    def _learning(self) -> dict:
        s = self._read(LEARNING_PATH)
        return {
            "total_queries": s.get("total_queries", 0),
            "concepts": s.get("total_concepts_learned", 0),
            "avg_confidence": s.get("avg_confidence", 0),
            "domains": s.get("domains_covered", {}),
        }

    async def _health(self) -> str:
        try:
            from ops.health_monitor import health_monitor
            if health_monitor.is_alive() and health_monitor.is_ready():
                return "healthy"
            return "degraded"
        except Exception:
            return "unknown"

    def _uptime(self) -> float:
        try:
            from ops.health_monitor import health_monitor
            return round(time.time() - health_monitor._start_time, 1)
        except Exception:
            return 0

    def _read(self, path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}


self_model = SelfModel()


def get_snapshot() -> dict:
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(self_model.snapshot())
    if loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(lambda: asyncio.run(self_model.snapshot()))
            return future.result(timeout=5)
    return loop.run_until_complete(self_model.snapshot())



# ══════════════════════════════════════════════════════════════════════════════
# Phase 60.1 — Self-Model Routing & Epistemic Aggregation
# ══════════════════════════════════════════════════════════════════════════════
# Standalone, LLM-free components that (a) classify how *self-referential* a query
# is, and (b) aggregate VELYNX's scattered knowledge about an entity into one
# explicit epistemic snapshot (Known / Unknown / Learning / Contradicted).
#
# NOTE: these are intentionally NOT wired into the request pipeline yet — they are
# self-contained building blocks for a later routing phase.


# ── Query classification ──────────────────────────────────────────────────────
class QueryType(str, Enum):
    """How a query relates to VELYNX itself vs. the outside world."""

    EXTERNAL = "EXTERNAL"               # about the world ("capital of France")
    SELF_REFERENTIAL = "SELF_REFERENTIAL"  # explicitly about VELYNX's own knowledge of a topic
    META_COGNITIVE = "META_COGNITIVE"   # about VELYNX's knowledge/cognition state
    SELF_IDENTITY = "SELF_IDENTITY"     # about who/what VELYNX is


class EpistemicState(str, Enum):
    """The four epistemic buckets an entity's knowledge can fall into."""

    KNOWN = "known"
    UNKNOWN = "unknown"
    LEARNING = "learning"
    CONTRADICTED = "contradicted"


# Pronoun / reference vocabularies (grammatical heuristic).
_ASSISTANT_REFS = {"you", "your", "yours", "yourself", "yourselves"}
_USER_REFS = {"i", "me", "my", "mine", "myself"}

# Identity nouns: when asked about *your <noun>* / *velynx's <noun>*.
_IDENTITY_NOUNS = {
    "name", "creator", "maker", "author", "developer", "purpose", "origin",
    "identity", "nature", "version", "model", "architecture",
}
# Cognition / knowledge-state vocabulary -> META_COGNITIVE.
# Cognition / knowledge-state vocabulary used only as a narrow META fallback.
# NOTE: "know/understand/remember" are deliberately EXCLUDED here — a question
# about VELYNX's knowledge OF A TOPIC ("what do you know about X") is
# SELF_REFERENTIAL, not meta-cognitive. META is reserved for the cognitive
# *process / state* (goals, learning activity, confidence).
_META_TOKENS = {
    "learning", "curious", "curiosity", "confident", "confidence",
    "goals", "beliefs",
}

# Specific identity phrasings (regex).
_IDENTITY_PATTERNS = (
    re.compile(r"\b(who|what)\s+(are|is)\s+(you|velynx)\b(?!\s+\w)"),
    re.compile(r"\babout\s+yoursel(f|ves)\b"),
    re.compile(r"\bwho\s+(made|created|built|designed)\s+(you|velynx)\b"),
    re.compile(r"\byour\s+(name|creator|maker|purpose|origin|identity|nature|version)\b"),
    re.compile(r"\bwhat'?s\s+your\s+name\b"),
)

# Self-referential phrasings: questions about VELYNX's KNOWLEDGE OF A TOPIC.
# ("what do you know / don't you know / do you NOT know about X", "what can you
# tell me about X", "what are you trying to learn about X", "curious about X").
# Both positive AND negative epistemic framings route here so they reach the
# same self-model introspection handler.
_SELF_REF_PATTERNS = (
    # Positive + negative interrogatives: "what do you know", "what don't you
    # know", "what do you NOT know" (the negation may sit before OR after "you").
    re.compile(r"\bwhat\s+do(?:n['’]?t|\s+n['’]?t)?\s+you\s+(?:not\s+|never\s+)?know\b"),
    re.compile(r"\bdo\s*n['’]?t?\s+you\s+know\s+(about|of)\b"),
    re.compile(r"\byou\s+(?:do\s+not\s+|do\s*n['’]?t\s+|not\s+|never\s+)?know\s+(about|of)\b"),
    re.compile(r"\bwhat\s+do(?:n['’]?t|\s+n['’]?t)?\s+you\s+(?:not\s+|never\s+)?(understand|remember)\b"),
    re.compile(r"\bwhat\s+can\s+you\s+tell\s+me\s+about\b"),
    re.compile(r"\bhave\s+you\s+(heard|learned)\s+(of|about)\b"),
    # Topic-anchored epistemic intent — "(what are) you trying to learn about X",
    # "you're curious about X", "you want to learn about X". The trailing \w
    # requires a real topic, so topicless PROCESS questions ("what are you trying
    # to learn?", "what are you curious about?") still fall through to META below.
    re.compile(r"\byou(?:['’]re|\s+are)?\s+(?:trying\s+to\s+learn|learning|studying|exploring|researching)\s+(?:about|of)\s+\w"),
    re.compile(r"\byou(?:['’]re|\s+are)?\s+curious\s+(?:about|of)\s+\w"),
    re.compile(r"\byou\s+(?:want|wanting)\s+to\s+(?:know|learn)\s+(?:about|of)\s+\w"),
)

# Meta-cognitive phrasings: questions about VELYNX's cognitive PROCESS / STATE
# (its active goals, what it is learning, how confident it is) — NOT tied to a
# specific external topic.
_META_PATTERNS = (
    re.compile(r"\bwhat\s+are\s+you\s+(trying\s+to\s+learn|learning|curious|working|thinking|doing|studying|exploring)\b"),
    re.compile(r"\bwhat\s+do\s+you\s+want\s+to\s+(know|learn)\b"),
    re.compile(r"\bare\s+you\s+(sure|certain|confident|aware)\b"),
    re.compile(r"\bhow\s+(confident|sure|certain)\s+are\s+you\b"),
    re.compile(r"\bwhat\s+are\s+your\s+(goals|beliefs|plans|thoughts|curiosities)\b"),
)


class SelfQueryRouter:
    """Classify a query as EXTERNAL / SELF_REFERENTIAL / META_COGNITIVE / SELF_IDENTITY.

    Pure grammatical + regex heuristics (no LLM). Precedence is deliberate:

      1. SELF_IDENTITY   — asks who/what VELYNX *is* (its name, creator, purpose).
      2. SELF_REFERENTIAL— EXPLICITLY interrogates VELYNX's own knowledge of a
                           topic ("what do/don't you know about X", "have you
                           heard of X"). Matched only by the strict
                           ``_SELF_REF_PATTERNS`` — a bare preposition ("of",
                           "about") or first-person word ("my", "I") is NOT
                           enough.
      3. META_COGNITIVE  — asks about VELYNX's *knowledge / cognition* state.
      4. EXTERNAL        — default: a question about the outside world. This
                           includes first-person framings like "the creator of MY
                           favorite 3D software", which are world-facts (and may
                           need agentic planning), NOT introspection.

    Reserving SELF_REFERENTIAL for explicit self-knowledge questions prevents the
    Phase 57/58 regression where "What year was the creator of my favorite 3D
    software born?" was hijacked away from the AgenticController.
    """

    def classify(self, query: str) -> str:
        if not query or not query.strip():
            return QueryType.EXTERNAL.value

        q = query.strip().lower()
        tokens = set(re.findall(r"[a-z']+", q))
        has_assistant = bool(tokens & _ASSISTANT_REFS) or "velynx" in q

        # 1) SELF_IDENTITY — who/what VELYNX *is*.
        if any(p.search(q) for p in _IDENTITY_PATTERNS):
            return QueryType.SELF_IDENTITY.value
        if has_assistant and (tokens & _IDENTITY_NOUNS):
            return QueryType.SELF_IDENTITY.value

        # 2) SELF_REFERENTIAL — VELYNX's KNOWLEDGE OF A TOPIC ("what do you know
        #    about X", "what don't you know about X"). Checked before META so a
        #    topic-knowledge question is introspected, not treated as a process
        #    question.
        if any(p.search(q) for p in _SELF_REF_PATTERNS):
            return QueryType.SELF_REFERENTIAL.value

        # 3) META_COGNITIVE — VELYNX's cognitive PROCESS / STATE (goals, learning
        #    activity, confidence).
        if any(p.search(q) for p in _META_PATTERNS):
            return QueryType.META_COGNITIVE.value
        if has_assistant and (tokens & _META_TOKENS):
            return QueryType.META_COGNITIVE.value

        # 4) EXTERNAL — default. A first-person reference ("my ...", "I ...") does
        #    NOT by itself make a query introspective: "the creator of MY favorite
        #    3D software" is still a question about the WORLD (and may need agentic
        #    planning). SELF_REFERENTIAL is reserved exclusively for queries that
        #    explicitly interrogate VELYNX's own knowledge (handled in step 2 via
        #    the strict ``_SELF_REF_PATTERNS``). This prevents the Phase 57/58
        #    regression where a multi-hop external query was hijacked here.
        return QueryType.EXTERNAL.value


# ── Epistemic aggregation ─────────────────────────────────────────────────────
def _empty_epistemic_state() -> dict[str, list]:
    """The canonical empty epistemic-state structure."""
    return {
        EpistemicState.KNOWN.value: [],
        EpistemicState.UNKNOWN.value: [],
        EpistemicState.LEARNING.value: [],
        EpistemicState.CONTRADICTED.value: [],
    }


@dataclass
class SelfContext:
    """An aggregated epistemic snapshot of what VELYNX knows about one entity."""

    target_entity: str
    has_concept: bool = False
    triples: list[dict] = field(default_factory=list)
    beliefs: list[str] = field(default_factory=list)
    epistemic_state: dict[str, list] = field(default_factory=_empty_epistemic_state)
    overall_familiarity: float = 0.0

    def to_dict(self) -> dict:
        return {
            "target_entity": self.target_entity,
            "has_concept": self.has_concept,
            "triples": self.triples,
            "beliefs": self.beliefs,
            "epistemic_state": self.epistemic_state,
            "overall_familiarity": round(self.overall_familiarity, 3),
        }


class SelfContextAggregator:
    """Aggregate KG facts, curiosity goals and beliefs into a :class:`SelfContext`.

    Sources (all best-effort; a missing subsystem degrades gracefully):
      * **known**       — outgoing relationships of the entity in the Knowledge
                          Graph (the attributes it actually has).
      * **unknown**     — attributes the Curiosity Engine has flagged as PENDING
                          goals for this entity (gaps not yet pursued).
      * **learning**    — attributes currently being pursued (ACTIVE goals).
      * **contradicted**— functional attributes that hold two or more *distinct*
                          values (a symbolic conflict), augmented by any core
                          beliefs flagged as conflicting.
    """

    def __init__(self, graph=None, manager=None, belief_store=None) -> None:
        self._graph = graph                # injectable KnowledgeGraph
        self._manager = manager            # injectable GoalManager
        self._belief_store = belief_store  # injectable BeliefStore

    # ── lazy deps ─────────────────────────────────────────────────────────
    def _get_graph(self):
        if self._graph is not None:
            return self._graph
        from backend.knowledge.knowledge_graph import KnowledgeGraph

        self._graph = KnowledgeGraph()
        return self._graph

    def _get_manager(self):
        if self._manager is not None:
            return self._manager
        from backend.agency.curiosity import goal_manager

        self._manager = goal_manager
        return self._manager

    def _get_belief_store(self):
        if self._belief_store is not None:
            return self._belief_store
        try:
            from backend.abstraction.belief_store import BeliefStore

            self._belief_store = BeliefStore()
        except Exception as exc:
            logger.debug("SelfContext: belief store unavailable: %s", exc)
            self._belief_store = None
        return self._belief_store

    # ── main entry ────────────────────────────────────────────────────────
    def aggregate(self, entity: str) -> SelfContext:
        entity = (entity or "").strip()
        ctx = SelfContext(target_entity=entity)
        if not entity:
            return ctx

        state = _empty_epistemic_state()

        # 1) KNOWN — KG concept + its outgoing relationships. Resolve the entity
        #    case-insensitively: the KG stores concept names normalised (commonly
        #    lower-cased), so a query for "Blender" must still find "blender".
        graph = self._get_graph()
        lookup_name = entity
        try:
            if graph.get_concept(entity) is not None:
                lookup_name = entity
                ctx.has_concept = True
            elif graph.get_concept(entity.lower()) is not None:
                lookup_name = entity.lower()
                ctx.has_concept = True
            else:
                ent_lc = entity.lower()
                for name in graph.all_concepts():
                    if name.lower() == ent_lc:
                        lookup_name = name
                        ctx.has_concept = True
                        break
        except Exception as exc:
            logger.debug("SelfContext: concept resolution for %r failed: %s", entity, exc)

        triples: list[dict] = []
        try:
            look_lc = lookup_name.lower()
            for rel in graph.get_related(lookup_name):
                triples.append(rel)
                if (rel.get("source") or "").lower() == look_lc:
                    relation = (rel.get("relation") or "").strip()
                    target = (rel.get("target") or "").strip()
                    if relation:
                        state[EpistemicState.KNOWN.value].append(
                            {"attribute": relation, "value": target}
                        )
        except Exception as exc:
            logger.debug("SelfContext: get_related(%r) failed: %s", lookup_name, exc)
        ctx.triples = triples

        # 2/3) UNKNOWN + LEARNING — curiosity goals targeting this entity.
        manager = self._get_manager()
        try:
            from backend.agency.curiosity import GoalStatus

            ent_lc = entity.lower()
            for goal in manager.all(GoalStatus.PENDING):
                if goal.target_entity.lower() == ent_lc:
                    state[EpistemicState.UNKNOWN.value].append(goal.target_attribute)
            for goal in manager.all(GoalStatus.ACTIVE):
                if goal.target_entity.lower() == ent_lc:
                    state[EpistemicState.LEARNING.value].append(goal.target_attribute)
        except Exception as exc:
            logger.debug("SelfContext: goal aggregation failed for %r: %s", entity, exc)

        # 4) CONTRADICTED — functional attributes with >1 distinct value, plus
        #    any conflicting core beliefs.
        ctx.beliefs = self._collect_beliefs(entity)
        state[EpistemicState.CONTRADICTED.value] = self._detect_contradictions(
            state[EpistemicState.KNOWN.value]
        )

        ctx.epistemic_state = state
        ctx.overall_familiarity = self._familiarity(ctx)
        return ctx

    # ── helpers ───────────────────────────────────────────────────────────
    def _collect_beliefs(self, entity: str) -> list[str]:
        store = self._get_belief_store()
        if store is None:
            return []
        try:
            return [b.belief_text for b in store.get_core_beliefs(entity)]
        except Exception as exc:
            logger.debug("SelfContext: get_core_beliefs(%r) failed: %s", entity, exc)
            return []

    @staticmethod
    def _detect_contradictions(known: list[dict]) -> list[dict]:
        """Flag attributes that hold two or more *distinct* values (a conflict).

        Pure symbolic detection: group known ``{attribute, value}`` facts by
        attribute; any attribute with >= 2 distinct values is contradicted. This
        catches functional facts that ended up with competing targets without
        needing any external belief metadata.
        """
        by_attr: dict[str, set] = {}
        for fact in known:
            attr = str(fact.get("attribute", "")).lower().strip()
            val = str(fact.get("value", "")).strip()
            if not attr or not val:
                continue
            by_attr.setdefault(attr, set()).add(val)
        contradicted = []
        for attr, values in by_attr.items():
            if len(values) >= 2:
                contradicted.append({"attribute": attr, "values": sorted(values)})
        return contradicted

    @staticmethod
    def _familiarity(ctx: SelfContext) -> float:
        """A 0..1 score of how well VELYNX knows the entity (data density).

        Combines:
          * a small base for merely having a concept node,
          * *coverage*: known facts vs. (known + unknown) expected attributes,
          * *density*: raw count of known facts, saturating at 5,
          * *beliefs*: a small bonus for having abstracted core beliefs,
        and penalises contradictions. An entirely unheard-of entity scores 0.0.
        """
        state = ctx.epistemic_state
        known_n = len(state[EpistemicState.KNOWN.value])
        unknown_n = len(state[EpistemicState.UNKNOWN.value])
        learning_n = len(state[EpistemicState.LEARNING.value])
        contra_n = len(state[EpistemicState.CONTRADICTED.value])

        # Never heard of it: no concept, no facts, no goals.
        if not ctx.has_concept and known_n == 0 and unknown_n == 0 and learning_n == 0:
            return 0.0

        denom = known_n + unknown_n
        coverage = (known_n / denom) if denom else (1.0 if ctx.has_concept else 0.0)
        density = min(known_n / 5.0, 1.0)
        belief_bonus = min(len(ctx.beliefs) * 0.05, 0.1)

        score = 0.15 * (1.0 if ctx.has_concept else 0.0)
        score += 0.50 * coverage
        score += 0.25 * density
        score += belief_bonus
        score -= 0.15 * contra_n  # competing values erode familiarity
        return max(0.0, min(1.0, score))


# Standalone singletons (NOT wired into the pipeline — Phase 60.1 scope).
self_query_router = SelfQueryRouter()
self_context_aggregator = SelfContextAggregator()


# ══════════════════════════════════════════════════════════════════════════════
# Phase 60.2 — Self-Referential Graph (Component 4) & Response Composer (Component 5)
# ══════════════════════════════════════════════════════════════════════════════
# Component 4 maintains VELYNX's canonical *self* node in the Knowledge Graph so
# that introspective relationships ("VELYNX knows_about X") have a stable anchor.
# Component 5 is a deterministic, LLM-free template engine that renders a
# :class:`SelfContext` (produced by the Phase 60.1 aggregator) into a natural-
# language answer for a SELF_REFERENTIAL query.
#
# Together with the Phase 60.1 router + aggregator these let the request pipeline
# answer "what do you / don't you know about X" by INTROSPECTION — bypassing the
# standard semantic-search / synthesis path entirely.


# ── Canonical self node ────────────────────────────────────────────────────────
VELYNX_SELF = "VELYNX_SELF"


class SelfReferentialGraph:
    """Component 4 — maintain VELYNX's canonical ``VELYNX_SELF`` node in the KG.

    The self node is the anchor for introspective edges. ``ensure_self_node`` is
    idempotent (safe to call on every self-referential turn); ``sync_knows_about``
    is an optional convenience that records a ``VELYNX_SELF -knows_about-> entity``
    edge once VELYNX actually holds a concept for ``entity``.
    """

    SELF_NODE = VELYNX_SELF
    SELF_DOMAIN = "SELF"
    SELF_DESCRIPTION = (
        "VELYNX's self-representation: identity, epistemic state, and cognitive health."
    )
    KNOWS_ABOUT = "knows_about"

    def __init__(self, graph=None) -> None:
        self._graph = graph  # injectable KnowledgeGraph

    # ── lazy dep ──────────────────────────────────────────────────────────
    def _get_graph(self):
        if self._graph is not None:
            return self._graph
        from backend.knowledge.knowledge_graph import KnowledgeGraph

        self._graph = KnowledgeGraph()
        return self._graph

    # ── canonical node ────────────────────────────────────────────────────
    def ensure_self_node(self) -> bool:
        """Idempotently ensure the ``VELYNX_SELF`` concept exists in the KG.

        Returns ``True`` if the node is present after the call (created or
        already existed), ``False`` if the graph was unavailable.
        """
        graph = self._get_graph()
        try:
            if graph.get_concept(self.SELF_NODE) is not None:
                return True
            # KnowledgeGraph.add_concept uses INSERT OR IGNORE — safe to repeat.
            graph.add_concept(self.SELF_NODE, self.SELF_DOMAIN, self.SELF_DESCRIPTION)
            return graph.get_concept(self.SELF_NODE) is not None
        except Exception as exc:
            logger.debug("SelfReferentialGraph.ensure_self_node failed: %s", exc)
            return False

    # ── optional edge sync ────────────────────────────────────────────────
    def sync_knows_about(self, entity: str, *, relation: str | None = None) -> bool:
        """Record ``VELYNX_SELF -knows_about-> entity`` (best-effort, idempotent).

        Optional for now (Phase 60.2 scope): callers may use this to materialise
        VELYNX's self-knowledge as explicit graph edges. ``add_relationship`` is
        ``INSERT OR IGNORE`` so repeated calls do not duplicate the edge.
        """
        entity = (entity or "").strip()
        if not entity:
            return False
        graph = self._get_graph()
        rel = (relation or self.KNOWS_ABOUT).strip() or self.KNOWS_ABOUT
        try:
            self.ensure_self_node()
            graph.add_relationship(self.SELF_NODE, rel, entity)
            return True
        except Exception as exc:
            logger.debug("SelfReferentialGraph.sync_knows_about(%r) failed: %s", entity, exc)
            return False


# ── Familiarity banding ────────────────────────────────────────────────────────
class FamiliarityLevel(str, Enum):
    """A qualitative band over :attr:`SelfContext.overall_familiarity` (0..1)."""

    UNKNOWN = "UNKNOWN"               # never heard of it
    KNOWS_OF = "KNOWS_OF"             # aware of it, very little detail
    KNOWS_SOMEWHAT = "KNOWS_SOMEWHAT"  # a moderate amount of detail
    KNOWS_WELL = "KNOWS_WELL"         # rich, dense knowledge

    @classmethod
    def from_score(cls, score: float, has_concept: bool = False) -> "FamiliarityLevel":
        try:
            s = float(score)
        except (TypeError, ValueError):
            s = 0.0
        if s <= 0.0 and not has_concept:
            return cls.UNKNOWN
        if s < 0.35:
            return cls.KNOWS_OF
        if s < 0.70:
            return cls.KNOWS_SOMEWHAT
        return cls.KNOWS_WELL


# Relations that read as a copula ("X is <value>") rather than "its <attr> is …".
_BE_RELATIONS = {"be", "is", "are", "was", "were", "isa", "is_a", "be_a", "is a"}

_FAMILIARITY_PHRASES = {
    FamiliarityLevel.UNKNOWN: "I'm not yet familiar with {entity}",
    FamiliarityLevel.KNOWS_OF: "I know of {entity}",
    FamiliarityLevel.KNOWS_SOMEWHAT: "I am somewhat familiar with {entity}",
    FamiliarityLevel.KNOWS_WELL: "I am quite familiar with {entity}",
}


def _join_clauses(items: list[str]) -> str:
    """Join clauses into an English list ("a", "a and b", "a, b and c")."""
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f" and {items[-1]}"


class SelfResponseComposer:
    """Component 5 — deterministic ``SelfContext`` -> natural-language renderer.

    Pure templates (no LLM). The output is a short paragraph that reflects each
    epistemic partition in turn:

      * **familiarity** — a qualitative opening derived from
        ``overall_familiarity`` (:class:`FamiliarityLevel`).
      * **known**       — the facts VELYNX holds ("I know it is 3D software").
      * **learning/unknown** — the gaps it is pursuing ("I am currently trying to
        learn its creator").
      * **contradicted** — any attribute under unresolved dispute.
    """

    def compose(self, ctx: SelfContext, is_negative_query: bool = False) -> str:
        """Render a :class:`SelfContext` into a natural-language paragraph.

        ``is_negative_query`` inverts the summary for "what do you NOT know
        about X" framings: instead of leading with the knowns, the paragraph
        opens with the entity's gaps (unknowns, conflicts, pending/active
        goals) and relegates the knowns to a brief tail. Positive framings
        ("what do you know about X") keep the original knowns-first order.
        """
        entity = (getattr(ctx, "target_entity", "") or "").strip() or "that"
        state = getattr(ctx, "epistemic_state", None) or _empty_epistemic_state()
        known = state.get(EpistemicState.KNOWN.value, []) or []
        unknown = state.get(EpistemicState.UNKNOWN.value, []) or []
        learning = state.get(EpistemicState.LEARNING.value, []) or []
        contradicted = state.get(EpistemicState.CONTRADICTED.value, []) or []

        level = FamiliarityLevel.from_score(
            getattr(ctx, "overall_familiarity", 0.0), getattr(ctx, "has_concept", False)
        )

        # Never heard of it: a single honest sentence, optionally noting
        # curiosity. The positive and negative framings collapse to the same
        # admission here — there are no knowns to invert.
        if level == FamiliarityLevel.UNKNOWN and not known and not learning:
            if unknown:
                gaps = self._pretty_gaps(unknown)
                return (
                    f"I'm not familiar with {entity} yet, but I'm curious to learn "
                    f"its {_join_clauses(gaps)}."
                )
            return f"I'm not familiar with {entity} yet; I haven't learned anything about it."

        if is_negative_query:
            return self._compose_negative(entity, level, known, unknown, learning, contradicted)
        return self._compose_positive(entity, level, known, unknown, learning, contradicted)

    # ── composition paths ──────────────────────────────────────────────────
    def _compose_positive(
        self, entity, level, known, unknown, learning, contradicted
    ) -> str:
        """Knowns-first rendering (the original 'what do you know about X' order).

        familiarity -> known -> gaps/learning -> contradictions
        """
        parts: list[str] = [self._familiarity_sentence(level, entity)]

        known_sentence = self._known_sentence(known)
        if known_sentence:
            parts.append(known_sentence)

        gap_sentence = self._gap_sentence(learning, unknown)
        if gap_sentence:
            parts.append(gap_sentence)

        contradiction_sentence = self._contradiction_sentence(contradicted)
        if contradiction_sentence:
            parts.append(contradiction_sentence)

        return " ".join(parts)

    def _compose_negative(
        self, entity, level, known, unknown, learning, contradicted
    ) -> str:
        """Gaps-first rendering for 'what do you NOT know about X' queries.

        Inverts the positive order so the answer leads with what is missing:

          opening (names entity) -> unknowns -> contradictions ->
            active learning -> brief knowns tail (count only, omitted if empty)

        The opener names the entity so the subsequent ``its`` clauses resolve.
        If there are no recorded gaps at all, emit an honest "no gaps" sentence
        instead of a misleading gaps-framed opener.
        """
        gap_sentences: list[str] = []

        # 1) UNKNOWN — pending gaps the Curiosity Engine has flagged but not
        #    yet pursued. The heart of a "what don't you know" question.
        unknown_sentence = self._unknowns_sentence(unknown)
        if unknown_sentence:
            gap_sentences.append(unknown_sentence)

        # 2) CONTRADICTED — unresolved conflicts are themselves a form of
        #    not-knowing, so they belong in the gaps block.
        contradiction_sentence = self._contradiction_sentence(contradicted)
        if contradiction_sentence:
            gap_sentences.append(contradiction_sentence)

        # 3) LEARNING — goals currently being actively pursued.
        learning_sentence = self._learning_sentence(learning)
        if learning_sentence:
            gap_sentences.append(learning_sentence)

        # No gaps on record: say so honestly instead of framing non-existent
        # unknowns. Still surface a brief knowns count for context.
        if not gap_sentences:
            tail = self._knowns_tail(known, entity)
            if tail:
                return f"I have no recorded gaps about {entity}. {tail}"
            return f"I have no recorded gaps about {entity}."

        parts: list[str] = [self._negative_opening(entity, level)]
        parts.extend(gap_sentences)

        # 4) KNOWN — a brief one-line tail (a count, not a re-listing) so the
        #    user still has a sense of what IS established. Omitted when empty.
        tail = self._knowns_tail(known, entity)
        if tail:
            parts.append(tail)

        return " ".join(parts)

    # ── sentence builders ──────────────────────────────────────────────────
    @staticmethod
    def _familiarity_sentence(level: FamiliarityLevel, entity: str) -> str:
        phrase = _FAMILIARITY_PHRASES.get(level, _FAMILIARITY_PHRASES[FamiliarityLevel.KNOWS_OF])
        return phrase.format(entity=entity) + "."

    @staticmethod
    def _negative_opening(entity: str, level: FamiliarityLevel) -> str:
        """Opener for a negative query — names the entity so the following
        ``its`` clauses resolve, and frames the paragraph as a gaps report."""
        if level == FamiliarityLevel.KNOWS_WELL:
            return f"Even about {entity}, what I don't yet know includes:"
        if level == FamiliarityLevel.KNOWS_SOMEWHAT:
            return f"Here is what I don't yet know about {entity}:"
        return f"About {entity}, the gaps in my knowledge are:"

    def _unknowns_sentence(self, unknown: list) -> str:
        """Pending gaps flagged by the Curiosity Engine but not yet pursued."""
        gaps = self._pretty_gaps(unknown)
        if not gaps:
            return ""
        return "I don't yet know its " + _join_clauses(gaps) + "."

    def _learning_sentence(self, learning: list) -> str:
        """Attributes currently being actively pursued (ACTIVE goals)."""
        gaps = self._pretty_gaps(learning)
        if not gaps:
            return ""
        return "I am currently trying to learn its " + _join_clauses(gaps) + "."

    @staticmethod
    def _knowns_tail(known: list, entity: str) -> str:
        """A brief one-line summary of established facts (used only as a tail
        on negative queries). Lists a *count*, not the facts themselves, so the
        paragraph stays gaps-focused. ``known`` may hold dicts or bare strings."""
        n = sum(1 for f in known if (f.get("value", "") if isinstance(f, dict) else str(f).strip()))
        if n <= 0:
            return ""
        if n == 1:
            return f"For reference, I do hold one established fact about {entity}."
        return f"For reference, I do hold {n} established facts about {entity}."

    @staticmethod
    def _known_sentence(known: list) -> str:
        if not known:
            return ""
        copula_values: list[str] = []
        attr_clauses: list[str] = []
        for fact in known:
            if not isinstance(fact, dict):
                # tolerate a bare string fact
                val = str(fact).strip()
                if val:
                    copula_values.append(val)
                continue
            attr = str(fact.get("attribute", "")).strip()
            val = str(fact.get("value", "")).strip()
            if not val:
                continue
            if not attr or attr.lower() in _BE_RELATIONS:
                copula_values.append(val)
            else:
                attr_clauses.append(f"its {attr.replace('_', ' ')} is {val}")
        segments: list[str] = []
        if copula_values:
            segments.append("it is " + _join_clauses(copula_values))
        segments.extend(attr_clauses)
        if not segments:
            return ""
        return "I know " + _join_clauses(segments) + "."

    def _gap_sentence(self, learning: list, unknown: list) -> str:
        gaps = self._pretty_gaps(list(learning) + list(unknown))
        if not gaps:
            return ""
        return "I am currently trying to learn its " + _join_clauses(gaps) + "."

    @staticmethod
    def _contradiction_sentence(contradicted: list) -> str:
        if not contradicted:
            return ""
        bits: list[str] = []
        for conflict in contradicted:
            if not isinstance(conflict, dict):
                continue
            attr = str(conflict.get("attribute", "")).replace("_", " ").strip()
            values = [str(v) for v in (conflict.get("values") or []) if str(v).strip()]
            if attr and len(values) >= 2:
                bits.append(f"its {attr} ({' vs '.join(values)})")
            elif attr:
                bits.append(f"its {attr}")
        if not bits:
            return ""
        return "I have conflicting information about " + _join_clauses(bits) + "."

    @staticmethod
    def _pretty_gaps(attributes: list) -> list[str]:
        """De-duplicate (preserving order) and prettify gap attribute names."""
        seen: set[str] = set()
        pretty: list[str] = []
        for attr in attributes:
            name = str(attr).strip()
            key = name.lower()
            if not name or key in seen:
                continue
            seen.add(key)
            pretty.append(name.replace("_", " "))
        return pretty


# ── Entity extraction for SELF_REFERENTIAL queries ─────────────────────────────
# Pull the target entity out of an introspective query so the aggregator knows
# WHICH entity's epistemic state to compile. The capture is ANCHORED to an
# explicit self-knowledge construct ("you know …", "you tell me about …", "you
# heard of …", "your knowledge of …"): a bare preposition ("of"/"about") in an
# ordinary question ("the creator of Blender") must NOT yield an entity, or a
# world-fact query would be wrongly diverted into introspection (the Phase 57/58
# regression). Deterministic regex, no LLM. Order matters: preposition-bearing
# variants are tried first so "you know about X" captures "X", not "about X".
_ENTITY_PATTERNS = (
    # "(what do) you [not] know/think/understand/remember about|of X" — the
    # optional negation lets "what do you NOT know about X" / "what don't you
    # know about X" yield the same entity as the positive form.
    re.compile(
        r"\byou\s+(?:do\s+not\s+|do\s*n['’]?t\s+|not\s+|never\s+)?(?:know|think|understand|remember)\s+(?:about|of)\s+(?P<ent>.+)$",
        re.IGNORECASE,
    ),
    # "what can you tell me about|of X"
    re.compile(r"\byou\s+tell\s+me\s+(?:about|of)\s+(?P<ent>.+)$", re.IGNORECASE),
    # "have you heard/learned of|about X"
    re.compile(r"\byou\s+(?:heard|learned)\s+(?:of|about)\s+(?P<ent>.+)$", re.IGNORECASE),
    # "your knowledge/understanding of|about X"
    re.compile(
        r"\byour\s+(?:knowledge|understanding)\s+(?:of|about)\s+(?P<ent>.+)$",
        re.IGNORECASE,
    ),
    # "(what are) you trying to learn / learning / studying about X"
    re.compile(
        r"\byou(?:['’]re|\s+are)?\s+(?:trying\s+to\s+learn|learning|studying|exploring|researching)\s+(?:about|of)\s+(?P<ent>.+)$",
        re.IGNORECASE,
    ),
    # "(are) you curious about X"
    re.compile(r"\byou(?:['’]re|\s+are)?\s+curious\s+(?:about|of)\s+(?P<ent>.+)$", re.IGNORECASE),
    # "(what do) you want to know/learn about X"
    re.compile(r"\byou\s+(?:want|wanting)\s+to\s+(?:know|learn)\s+(?:about|of)\s+(?P<ent>.+)$", re.IGNORECASE),
    # "do you know X" / "you understand X" (no preposition) — tried last so the
    # preposition-bearing forms above win when present.
    re.compile(r"\byou\s+(?:know|understand|remember)\s+(?P<ent>.+)$", re.IGNORECASE),
)
# Leading determiners/quotes to strip from the captured phrase.
_LEADING_DET = re.compile(r"^(?:the|a|an)\s+", re.IGNORECASE)


def extract_target_entity(query: str) -> str:
    """Extract the entity an EXPLICIT self-knowledge query is asking about.

    Handles only the supported introspective phrasings, e.g. "what do you know
    about *Blender*", "what don't you know about *Blender*", "what can you tell
    me about *Blender*", "have you heard of *Blender*", "your knowledge of
    *Blender*".

    Returns ``""`` when the query does not explicitly interrogate VELYNX's
    knowledge — including ordinary world-fact questions that merely contain a
    preposition ("What year was the creator **of** Blender born?") or a first-
    person word ("**my** favorite 3D software"). An empty return signals the
    pipeline to fall through to its standard (external / agentic) path.
    """
    if not query or not query.strip():
        return ""
    q = query.strip()
    match = None
    for pattern in _ENTITY_PATTERNS:
        match = pattern.search(q)
        if match:
            break
    if not match:
        return ""
    entity = match.group("ent").strip()
    entity = entity.strip().rstrip("?.!").strip()
    entity = entity.strip("\"'").strip()
    entity = _LEADING_DET.sub("", entity).strip()
    return entity


# ── Negative-epistemic detection ──────────────────────────────────────────────
# "What do you / don't you / NOT know about X" all route SELF_REFERENTIAL (the
# intent-router fix), but the *negative* framings must be rendered differently
# (gaps-first). This detector flags them so the composer can invert its summary.
# The negation grammar mirrors the optional negation block already accepted in
# ``_SELF_REF_PATTERNS`` / ``_ENTITY_PATTERNS`` (the intent-router accepts the
# negation either before OR after "you").
_NEGATIVE_EPISTEMIC_PATTERNS = (
    # "what don't you know about X" / "what do you not know about X"
    re.compile(
        r"\bwhat\s+do(?:n['’]?t|\s+n['’]?t)\s+you\s+(?:know|understand|remember)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bwhat\s+do\s+you\s+(?:not\s+|never\s+)(?:know|understand|remember)\b",
        re.IGNORECASE,
    ),
    # "don't you know about X" / "do you not know about X"
    re.compile(
        r"\bdo\s*n['’]?t?\s+you\s+know\b|\bdo\s+you\s+not\s+know\b",
        re.IGNORECASE,
    ),
)


def is_negative_epistemic_query(query: str) -> bool:
    """Return ``True`` for a negated self-knowledge query.

    Matches "what do you NOT know about X", "what don't you know about X" and
    "don't you know about X" — the same negative framings the intent router
    routes to SELF_REFERENTIAL, but that must be rendered gaps-first by the
    :class:`SelfResponseComposer`. Pure regex heuristic, no LLM.
    """
    if not query or not query.strip():
        return False
    q = query.strip()
    return any(p.search(q) for p in _NEGATIVE_EPISTEMIC_PATTERNS)


# Phase 60.2 singletons.
self_referential_graph = SelfReferentialGraph()
self_response_composer = SelfResponseComposer()
