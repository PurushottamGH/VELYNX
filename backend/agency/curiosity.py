"""
VELYNX Phase 59 — Curiosity Engine
==================================

Curiosity, formally, is a *control loop*::

    Gap Detection  ->  Goal Generation

VELYNX already accumulates entities in its Knowledge Graph (concepts + the
relationships that hang off them). What it has lacked is the *drive* to notice
when an entity is impoverished — when we "know of" something but are missing the
fundamental attributes one would expect to know about a thing of that kind — and
to turn that absence into an explicit, actionable :class:`Goal`.

This module implements that loop symbolically (no LLM, no generative model):

* **Ontology / EntityExpectation** — a small, hand-authored map from a *category*
  ("software", "person", "company", …) to the attributes a well-known entity of
  that category is expected to have (e.g. software -> ``creator``,
  ``release_year``). A lightweight, deterministic classifier assigns each KG
  entity a category from its ``domain`` / ``description``.
* **Gap detection** — :func:`scan_for_gaps` walks the most-recently-added KG
  entities, derives each one's expected attributes from the ontology, compares
  them against the relations the entity actually has, and treats every missing
  expected attribute as a *knowledge gap*.
* **Goal generation** — each gap becomes a :class:`Goal` (``status=PENDING``),
  registered in the process-wide :class:`GoalManager` singleton (de-duplicated by
  ``(entity, attribute)``), ready for a later phase to act on (retrieve / learn).

Storage choice
--------------
Goals live in an **in-memory ``GoalManager`` singleton**. They are derived state
— cheaply re-computable from the (persistent) Knowledge Graph by re-running
:func:`scan_for_gaps` — so persisting them to their own SQLite table would add
schema/migration surface for no durability benefit at this phase. The manager is
intentionally tiny and swappable behind a clear API if persistence is wanted
later.
"""
from __future__ import annotations

import logging
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional

logger = logging.getLogger("velynx.curiosity")


# ── Goal schema ───────────────────────────────────────────────────────────────
class GoalStatus(str, Enum):
    """Lifecycle of a curiosity goal."""

    PENDING = "pending"        # generated, not yet acted on
    ACTIVE = "active"          # currently being pursued (e.g. by a retriever)
    SATISFIED = "satisfied"    # the missing attribute has been learned
    BLOCKED = "blocked"        # an attempt failed; eligible for a later retry
    ABANDONED = "abandoned"    # given up on (out of retries / unreachable)


@dataclass
class Goal:
    """A formal intention to learn one missing attribute of one entity.

    Attributes
    ----------
    id:
        Stable unique identifier (uuid hex, 12 chars).
    target_entity:
        The KG entity the gap is about (e.g. ``"blender"``).
    target_attribute:
        The ontological attribute that is missing (e.g. ``"creator"``).
    priority:
        Higher = more important to resolve. Derived from the ontology weight of
        the attribute for the entity's category.
    status:
        See :class:`GoalStatus`.
    """

    target_entity: str
    target_attribute: str
    priority: int = 1
    status: GoalStatus = GoalStatus.PENDING
    category: Optional[str] = None
    attempts: int = 0
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: float = field(default_factory=time.time)

    @property
    def key(self) -> tuple[str, str]:
        """Identity used for de-duplication: one goal per (entity, attribute)."""
        return (self.target_entity.lower().strip(), self.target_attribute.lower().strip())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target_entity": self.target_entity,
            "target_attribute": self.target_attribute,
            "priority": self.priority,
            "status": self.status.value,
            "category": self.category,
            "attempts": self.attempts,
            "created_at": self.created_at,
        }


# ── Ontology / EntityExpectation heuristic ────────────────────────────────────
# A symbolic map: category -> {expected attribute: priority weight}. Higher
# weight = a more fundamental attribute (its absence is a more urgent gap). This
# is deliberately small and hand-authored — the point of Phase 59 is the control
# loop, not ontological coverage.
ONTOLOGY: dict[str, dict[str, int]] = {
    "software":  {"creator": 9, "release_year": 7, "purpose": 5, "license": 3},
    "person":    {"birth_year": 8, "occupation": 6, "nationality": 4},
    "company":   {"founder": 9, "founded_year": 7, "headquarters": 5, "industry": 4},
    "city":      {"country": 8, "population": 6},
    "country":   {"capital": 8, "population": 6, "currency": 4},
    "concept":   {"definition": 7, "domain": 5},
}

# Default expectation for entities we cannot categorise — keep it minimal so we
# do not flood the goal queue with low-value gaps for unknown things.
_DEFAULT_CATEGORY = "concept"

# Keyword cues for the deterministic classifier. Order matters: the first
# category whose cue is found wins. GEOGRAPHIC categories (city/country) are
# checked BEFORE person so a location is never mistaken for a human. Matched
# against the entity name + (cleaned) description + KG domain, all lower-cased.
_CATEGORY_CUES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("software", ("software", "application", "program", "app", "operating system",
                  "tool", "framework", "library", "editor", "engine")),
    ("company",  ("company", "corporation", "corp", "inc", "studio", "startup",
                  "manufacturer", "vendor", "firm")),
    ("city",     ("city", "town", "metropolis", "municipality", "village",
                  "province", "district", "borough", "is a capital")),
    ("country",  ("country", "nation", "republic", "kingdom", "sovereign state")),
    ("person",   ("person", "author", "scientist", "engineer", "founder",
                  "artist", "musician", "writer", "novelist", "philosopher",
                  "politician", "actor", "born in", "born on")),
)

# Small symbolic gazetteer of well-known geographic entities. A name match here
# classifies the entity as a location OUTRIGHT, so a city referenced only via a
# locative relation (whose boilerplate description mentions a "creator"/"author")
# can never be misclassified as a person. Lower-cased for matching.
_CITY_NAMES = frozenset({
    "bengaluru", "bangalore", "mumbai", "bombay", "delhi", "new delhi",
    "chennai", "kolkata", "hyderabad", "pune", "ahmedabad", "jaipur",
    "london", "paris", "berlin", "madrid", "rome", "amsterdam", "vienna",
    "new york", "san francisco", "los angeles", "chicago", "boston", "seattle",
    "tokyo", "osaka", "beijing", "shanghai", "seoul", "hong kong",
    "dubai", "toronto", "vancouver", "sydney", "melbourne", "moscow", "lagos",
})
_COUNTRY_NAMES = frozenset({
    "india", "france", "germany", "spain", "italy", "japan", "china",
    "russia", "brazil", "canada", "australia", "mexico", "egypt", "nigeria",
    "united states", "usa", "america", "united kingdom", "uk", "england",
    "south korea", "singapore",
})

# The consolidator describes an OBJECT concept with cross-reference boilerplate,
# e.g. ``referenced by 'the creator of velynx' via 'lives in'``. That text names
# OTHER entities (the subject + relation), not this one, and must NOT feed the
# classifier — otherwise a city ("Bengaluru") inherits the subject's "creator"
# cue and is misread as a person. We strip it before cue scanning.
_REFERENCE_BOILERPLATE = re.compile(
    r"referenced by\s+'[^']*'\s+via\s+'[^']*'", re.IGNORECASE
)


def classify_entity(name: str, domain: str = "", description: str = "") -> str:
    """Assign a symbolic category to a KG entity (deterministic, no LLM).

    Resolution order:
      1. If the KG ``domain`` is itself a known ontology category, use it.
      2. If the NAME is a known geographic entity (gazetteer), classify it as
         city/country outright — locations must never get human attributes.
      3. Otherwise scan name + (boilerplate-stripped) description + domain for
         category keyword cues, geographic categories first.
      4. Otherwise fall back to the default ("concept").
    """
    dom = (domain or "").strip().lower()
    if dom in ONTOLOGY:
        return dom

    nm = (name or "").strip().lower()
    # 2) Gazetteer — geographic names win outright (prevents birth_year/occupation
    #    being assigned to a city like "Bengaluru").
    if nm in _CITY_NAMES:
        return "city"
    if nm in _COUNTRY_NAMES:
        return "country"

    # 3) Cue scan over the entity's OWN text only (drop cross-reference boilerplate
    #    that names other entities, e.g. a locative object's "referenced by ...").
    clean_desc = _REFERENCE_BOILERPLATE.sub(" ", description or "")
    haystack = " ".join((name or "", clean_desc, domain or "")).lower()
    for category, cues in _CATEGORY_CUES:
        if any(cue in haystack for cue in cues):
            return category
    return _DEFAULT_CATEGORY


def expected_attributes(category: str) -> dict[str, int]:
    """Return the expected ``{attribute: priority}`` map for a category."""
    return ONTOLOGY.get(category, ONTOLOGY[_DEFAULT_CATEGORY])


# ── Goal storage (in-memory singleton) ────────────────────────────────────────
class GoalManager:
    """Process-wide store of curiosity goals, de-duplicated by (entity, attr)."""

    def __init__(self) -> None:
        self._by_id: dict[str, Goal] = {}
        self._by_key: dict[tuple[str, str], str] = {}

    def add(self, goal: Goal) -> bool:
        """Register ``goal``. Returns ``False`` if an equivalent goal exists.

        Equivalence is by ``Goal.key`` ((entity, attribute)). An existing goal is
        never duplicated or downgraded; we simply ignore the new one.
        """
        if goal.key in self._by_key:
            return False
        self._by_id[goal.id] = goal
        self._by_key[goal.key] = goal.id
        return True

    def get(self, goal_id: str) -> Optional[Goal]:
        return self._by_id.get(goal_id)

    def all(self, status: Optional[GoalStatus] = None) -> list[Goal]:
        goals = list(self._by_id.values())
        if status is not None:
            goals = [g for g in goals if g.status == status]
        # Most urgent first, then most recent.
        return sorted(goals, key=lambda g: (-g.priority, -g.created_at))

    def pending(self) -> list[Goal]:
        return self.all(GoalStatus.PENDING)

    def has(self, entity: str, attribute: str) -> bool:
        key = (entity.lower().strip(), attribute.lower().strip())
        return key in self._by_key

    def set_status(self, goal_id: str, status: GoalStatus) -> bool:
        goal = self._by_id.get(goal_id)
        if goal is None:
            return False
        goal.status = status
        return True

    def stats(self) -> dict[str, int]:
        out = {s.value: 0 for s in GoalStatus}
        for g in self._by_id.values():
            out[g.status.value] += 1
        out["total"] = len(self._by_id)
        return out

    def clear(self) -> None:
        self._by_id.clear()
        self._by_key.clear()


# Process-wide singleton.
goal_manager = GoalManager()


# ── Knowledge-Graph access helpers ────────────────────────────────────────────
def _recent_entities(limit: int) -> list[dict]:
    """Return the most-recently-added KG concepts (recency proxied by row id).

    Reads the same ``concepts`` table the :class:`KnowledgeGraph` writes to,
    ordered by ``id DESC`` (the table has no timestamp column, so the
    autoincrement id is our insertion-order proxy). Best-effort: returns an empty
    list if the graph DB is unavailable.
    """
    try:
        from backend.knowledge.knowledge_graph import DB_PATH
        from backend.memory._sqlite import connect as open_connection
    except Exception as exc:  # pragma: no cover - import environment issue
        logger.warning("Curiosity: KG modules unavailable (%s)", exc)
        return []

    try:
        conn = open_connection(str(DB_PATH), row_factory=sqlite3.Row)
    except Exception as exc:
        logger.warning("Curiosity: cannot open KG DB (%s)", exc)
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name, domain, description FROM concepts ORDER BY id DESC LIMIT ?",
            (int(limit),),
        )
        return [
            {"name": r["name"], "domain": r["domain"], "description": r["description"]}
            for r in cur.fetchall()
        ]
    except Exception as exc:
        logger.debug("Curiosity: recent-entity query failed (%s)", exc)
        return []
    finally:
        conn.close()


def _known_attributes(graph, entity: str) -> set[str]:
    """The set of attribute-relations the entity already has (outgoing edges).

    An attribute is modelled as a relationship where ``entity`` is the *source*;
    the relation name is the attribute (normalised to lower-case, spaces->_).
    """
    known: set[str] = set()
    try:
        for rel in graph.get_related(entity):
            if (rel.get("source") or "").lower().strip() == entity.lower().strip():
                relation = (rel.get("relation") or "").lower().strip().replace(" ", "_")
                if relation:
                    known.add(relation)
    except Exception as exc:
        logger.debug("Curiosity: get_related(%r) failed (%s)", entity, exc)
    return known


# ── The curiosity control loop ────────────────────────────────────────────────
def scan_for_gaps(limit: int = 25, *, graph=None, manager: Optional[GoalManager] = None) -> list[Goal]:
    """Detect knowledge gaps in recent KG entities and generate PENDING goals.

    The control loop:
      1. **Scan** — take the ``limit`` most-recently-added KG entities.
      2. **Classify** — assign each a symbolic category (:func:`classify_entity`).
      3. **Compare** — expected attributes (ontology) vs. attributes the entity
         actually has (its outgoing relations).
      4. **Generate** — for every missing expected attribute, create a
         :class:`Goal` (``status=PENDING``) and register it in the
         :class:`GoalManager` (de-duplicated).

    Returns the list of *newly created* goals (existing/duplicate gaps are
    skipped). Never raises — a missing/empty graph yields an empty list.
    """
    mgr = manager or goal_manager
    if graph is None:
        try:
            from backend.knowledge.knowledge_graph import KnowledgeGraph

            graph = KnowledgeGraph()
        except Exception as exc:
            logger.warning("Curiosity: KnowledgeGraph unavailable (%s)", exc)
            return []

    entities = _recent_entities(limit)
    logger.info("Curiosity scan: inspecting %d recent entit(y/ies)", len(entities))

    new_goals: list[Goal] = []
    for ent in entities:
        name = ent["name"]
        category = classify_entity(name, ent.get("domain", ""), ent.get("description", ""))
        expected = expected_attributes(category)
        known = _known_attributes(graph, name)

        missing = {attr: prio for attr, prio in expected.items() if attr not in known}
        if not missing:
            continue

        # Highest-priority gaps first so the queue is naturally ordered.
        for attr, prio in sorted(missing.items(), key=lambda kv: (-kv[1], kv[0])):
            if mgr.has(name, attr):
                continue  # already a goal for this gap
            goal = Goal(
                target_entity=name,
                target_attribute=attr,
                priority=prio,
                category=category,
                status=GoalStatus.PENDING,
            )
            if mgr.add(goal):
                new_goals.append(goal)
                logger.info(
                    "Curiosity goal: learn %r of %r [%s] (priority=%d)",
                    attr, name, category, prio,
                )
                # ── Phase 61: Episodic memory ──────────────────────────
                # Record the birth of this goal as an episode, causally linked
                # (by the manager) to any recent QUERY_FAILURE about the same
                # entity/attribute. Best-effort: a history-logging failure must
                # never break gap detection.
                try:
                    from backend.memory.episodic import episodic_manager

                    episodic_manager.record_goal_created(
                        name, attr, priority=prio, goal_id=goal.id,
                    )
                except Exception as exc:
                    logger.debug("Episodic: goal-created logging failed: %s", exc)

    logger.info(
        "Curiosity scan complete: %d new goal(s); %s",
        len(new_goals), mgr.stats(),
    )
    return new_goals


# ── Goal satisfaction (Phase 61) ──────────────────────────────────────────────
# When a fact is written back to the Knowledge Graph it may *resolve* an
# outstanding curiosity goal. Each ontology attribute maps to the set of relation
# surface-forms (spaCy lemmas / regex verbs) whose presence satisfies a goal
# seeking that attribute — e.g. learning "<X> created <entity>" satisfies the
# entity's ``creator`` gap. Matching is deliberately permissive on the relation
# but strict on the entity (a triple endpoint must be the goal's target entity).
_ATTRIBUTE_RELATION_SYNONYMS: dict[str, set[str]] = {
    "creator": {
        "create", "created", "creates", "creator", "build", "built", "make",
        "made", "design", "designed", "develop", "developed", "developer",
        "write", "wrote", "written", "author", "authored", "invent", "invented",
        "found", "founded", "founder",
    },
    "founder": {
        "found", "founded", "founder", "co_found", "cofounded", "establish",
        "established", "create", "created", "start", "started",
    },
    "founded_year": {"found", "founded", "establish", "established", "founded_year"},
    "release_year": {"release", "released", "launch", "launched", "release_year"},
    "birth_year": {"bear", "born", "birth", "birth_year"},
    "occupation": {"occupation", "profession", "work_as", "works_as"},
    "nationality": {"nationality", "national"},
    "headquarters": {"headquarter", "headquartered", "based", "headquarters"},
    "industry": {"industry", "sector"},
    "country": {"country", "located_in"},
    "capital": {"capital"},
    "population": {"population"},
    "currency": {"currency"},
    "purpose": {"purpose", "used_for", "use_for"},
    "license": {"license", "licensed", "licence"},
    "definition": {"definition", "define", "defined", "mean", "means"},
    "domain": {"domain", "field"},
}


def _normalize_relation(relation: str) -> str:
    return (relation or "").strip().lower().replace(" ", "_")


def _relation_satisfies_attribute(relation: str, attribute: str) -> bool:
    """True if learning ``relation`` plausibly fills the ``attribute`` gap."""
    rel = _normalize_relation(relation)
    attr = _normalize_relation(attribute)
    if not rel or not attr:
        return False
    if rel == attr:
        return True
    if rel in _ATTRIBUTE_RELATION_SYNONYMS.get(attr, set()):
        return True
    # Loose containment as a last resort ("created" vs "creator", "founded_year").
    return attr in rel or rel in attr


def _entity_matches(goal_entity: str, candidate: str) -> bool:
    a = (goal_entity or "").strip().lower()
    b = (candidate or "").strip().lower()
    if not a or not b:
        return False
    return a == b or a in b or b in a


def mark_goals_satisfied_from_triples(
    triples: Iterable,
    *,
    manager: Optional[GoalManager] = None,
    session_id: Optional[str] = None,
    record_episode: bool = True,
) -> list[Goal]:
    """Resolve PENDING curiosity goals fulfilled by freshly-learned ``triples``.

    For every learned ``(subject, relation, object)`` triple, any PENDING goal
    whose ``target_entity`` is one of the triple's endpoints and whose
    ``target_attribute`` is satisfied by the relation transitions
    ``PENDING -> SATISFIED``. When ``record_episode`` is set, a
    ``KNOWLEDGE_ACQUIRED`` episode is also logged (tagged to the goal's
    entity/attribute) so the Episodic Narrative layer can replay the
    failure -> gap -> acquisition chain. Best-effort; never raises.

    Returns the list of goals that were transitioned to SATISFIED.
    """
    mgr = manager or goal_manager
    pending = list(mgr.all(GoalStatus.PENDING))
    if not pending:
        return []

    satisfied: list[Goal] = []
    for triple in triples:
        try:
            subj, rel, obj = str(triple[0]), str(triple[1]), str(triple[2])
        except Exception:
            continue
        endpoints = (subj, obj)

        for goal in pending:
            if goal.status != GoalStatus.PENDING:
                continue
            if not any(_entity_matches(goal.target_entity, e) for e in endpoints):
                continue
            if not _relation_satisfies_attribute(rel, goal.target_attribute):
                continue

            if not mgr.set_status(goal.id, GoalStatus.SATISFIED):
                continue
            satisfied.append(goal)
            logger.info(
                "Curiosity goal SATISFIED: %r of %r resolved by %r -%s-> %r",
                goal.target_attribute, goal.target_entity, subj, rel, obj,
            )

            if not record_episode:
                continue
            # The learned value is the OTHER endpoint relative to the goal entity.
            value = subj if _entity_matches(goal.target_entity, obj) else obj
            try:
                from backend.memory.episodic import episodic_manager

                episodic_manager.record_knowledge_acquired(
                    goal.target_entity,
                    attribute=goal.target_attribute,
                    value=value,
                    triples=[[subj, rel, obj]],
                    session_id=session_id,
                    source="user",
                )
            except Exception as exc:
                logger.debug("Episodic: acquisition logging failed: %s", exc)

    if satisfied:
        logger.info(
            "Curiosity: %d goal(s) satisfied; %s", len(satisfied), mgr.stats(),
        )
    return satisfied


class CuriosityEngine:
    """Thin object wrapper over the curiosity control loop.

    Provided for callers that prefer an injectable component (e.g. a scheduler /
    runtime supervisor) over the module-level functions. Shares the same
    :data:`goal_manager` singleton unless a manager is supplied.
    """

    def __init__(self, graph=None, manager: Optional[GoalManager] = None) -> None:
        self.graph = graph
        self.manager = manager or goal_manager

    def scan(self, limit: int = 25) -> list[Goal]:
        return scan_for_gaps(limit, graph=self.graph, manager=self.manager)

    def pending_goals(self) -> list[Goal]:
        return self.manager.pending()


__all__ = [
    "GoalStatus",
    "Goal",
    "ONTOLOGY",
    "classify_entity",
    "expected_attributes",
    "GoalManager",
    "goal_manager",
    "scan_for_gaps",
    "mark_goals_satisfied_from_triples",
    "CuriosityEngine",
]
