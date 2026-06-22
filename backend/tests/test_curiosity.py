"""
Falsifiable Cognitive Test Suite — Phase 59 (Curiosity Engine & Goal Formation)
===============================================================================

Through Phase 58 VELYNX was *reactive*: it answered, committed, planned — but only
ever in response to a turn the user typed. Phase 59 is the first PROACTIVE gate.

The claim under test: when a new entity enters the Knowledge Graph, VELYNX should
notice — without being asked — that it knows almost nothing about it, and turn that
ignorance into ACTION. Concretely, it must detect the missing attributes of the new
entity and autonomously file structured GOALS to go fill them.

The canonical Phase 59 case:

    TURN 1 — SET KNOWLEDGE
        "My favorite software is Blender."
        Commits to the KG as the concept ``blender`` (domain PERSONAL). At this
        point the graph holds exactly one edge — ``... -be-> blender`` — and NO
        attributes: no creator, no release year, no developer. That void is the
        raw material for curiosity.

    TURN 2 — THE CURIOSITY TRIGGER
        Invoke the curiosity engine's gap scan (e.g. ``scan_for_gaps()``). It must
        inspect the KG, see that ``blender`` is an attribute-poor node, and EMIT at
        least one autonomous goal to enrich it.

    THE ASSERTION
        At least one PENDING goal now exists in VELYNX's internal state, and it is
        structurally sound:
          * a stable ``id``
          * a ``target entity`` that refers to Blender
          * a ``target attribute`` naming the missing fact to discover
            (e.g. creator / release year / developer)
          * ``status == "PENDING"``

As with the Phase 57/58 suites, we drive real backend objects (no terminal, no
route plumbing) so the test measures the CONTRACT, not the rendering. Because the
curiosity engine may legitimately live under several module paths and expose the
goal in several shapes (dataclass, dict, or DB row), the suite DISCOVERS the
implementation against a small candidate set and enforces the contract without
dictating one exact field name or import path.

Falsifiability
--------------
Every assertion is concrete and CAN fail. Today no proactive curiosity engine emits
structured ``Goal`` objects with a target entity/attribute/PENDING status, so TURN 2
is EXPECTED to fail — either the engine/method does not exist, or no goal is
produced. That failure is the signal Phase 59 is not built. A green run is the
definition of "Phase 59 done".

Run it either way:

    pytest backend/tests/test_curiosity.py -v
    python  backend/tests/test_curiosity.py     # standalone PASS/FAIL report
"""

from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path

# Windows consoles default to cp1252; pipeline answers/goals may carry Unicode.
# Force UTF-8 with a safe fallback so printing a failure report can never itself
# crash the suite. (Same handling as the other cognitive suites.)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

# ── Path bootstrap ───────────────────────────────────────────────────────────
# The pipeline mixes bare imports (``from app.pipeline import ...``) with absolute
# package imports (``from backend.knowledge... import ...``), so BOTH the
# ``backend/`` directory and the repo root must be importable. Same convention as
# test_agency.py / test_dynamic_agency.py.
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[1]          # .../VELYNX/backend
_REPO_ROOT = _HERE.parents[2]            # .../VELYNX
for _p in (str(_BACKEND_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest  # noqa: E402

from app.pipeline import answer_question  # noqa: E402
from backend.knowledge.knowledge_graph import KnowledgeGraph  # noqa: E402


# ── Test fixtures / constants ─────────────────────────────────────────────────
SESSION_ID = "curiosity-suite"

# TURN 1 plants the new entity.
TURN1_KNOWLEDGE = "My favorite software is Blender."
ENTITY = "Blender"                 # canonical form as the user typed it
ENTITY_KEY = "blender"             # how the KG normalizes/stores it (lowercased)

# The deterministic acknowledgement emitted by the Knowledge-Acquisition layer.
COMMIT_MESSAGE = "I have committed that to memory."

# Phase 53.1 consolidation runs on a BACKGROUND thread and is what actually writes
# the concept into the KnowledgeGraph; give it time so the gap scan sees the node.
CONSOLIDATION_WAIT_SECONDS = 5

# The status a freshly-formed, not-yet-pursued goal must carry.
PENDING_STATUS = "PENDING"

# Where a proactive curiosity engine might live, and what the engine object/factory
# might be called. We probe each (module, attribute) pair and use the first that
# exposes a gap-scan entry point. This enforces the CONTRACT without locking the
# implementation to one path. Extend this list if the engine lands elsewhere.
CURIOSITY_ENGINE_CANDIDATES = (
    # First Claude shipped the Phase 59 engine here: backend/agency/curiosity.py,
    # exposing the ``CuriosityEngine`` wrapper, a module-level ``scan_for_gaps``
    # function, and the ``goal_manager`` singleton that stores the goals.
    ("backend.agency.curiosity", "CuriosityEngine"),
    ("backend.agency.curiosity", "curiosity_engine"),
    ("backend.agency.curiosity", "goal_manager"),
    ("backend.cognition.curiosity_engine", "curiosity_engine"),
    ("backend.cognition.curiosity_engine", "CuriosityEngine"),
    ("backend.learning.curiosity_engine", "curiosity_engine"),
    ("backend.learning.curiosity_engine", "CuriosityEngine"),
    ("backend.knowledge.curiosity_engine", "curiosity_engine"),
    ("backend.knowledge.curiosity_engine", "CuriosityEngine"),
    ("backend.cognition.curiosity", "curiosity_engine"),
    ("backend.motivation.curiosity_engine", "curiosity_engine"),
    ("backend.agency.curiosity_engine", "curiosity_engine"),
)

# Method names a gap scan might expose.
SCAN_METHOD_NAMES = ("scan_for_gaps", "scan_gaps", "detect_gaps", "form_goals",
                     "generate_goals", "scan", "run_scan")

# Method names that return the current goal set (used if the scan does not itself
# return the goals).
GOAL_GETTER_NAMES = ("get_pending_goals", "pending_goals", "get_goals",
                     "list_goals", "goals", "get_open_goals", "open_goals")

# Field aliases for the four structural properties a sound Goal must expose. We
# accept any alias so the contract is "these properties exist", not "this exact
# attribute name". Pulled from dataclass attrs, dict keys, or sqlite Row columns.
ID_FIELDS = ("id", "goal_id", "uid", "uuid", "pk")
ENTITY_FIELDS = ("target_entity", "entity", "subject", "about", "about_concept",
                 "concept", "target", "node")
ATTRIBUTE_FIELDS = ("target_attribute", "attribute", "attr", "missing_attribute",
                    "predicate", "relation", "slot", "property", "field")
STATUS_FIELDS = ("status", "state")

# An attribute the gap scan should want to discover for a bare software entity.
# Blender's KG node holds only a ``be`` edge — so a genuine gap goal targets one of
# these real, currently-absent attributes (the prompt's own examples:
# "creator of Blender", "release year of Blender"). ``be`` is explicitly NOT here:
# a goal to rediscover the edge that already exists is not curiosity.
MISSING_ATTRIBUTE_TERMS = (
    "creator", "author", "developer", "founder", "maker", "designer",
    "release", "year", "born", "birth", "created", "founded", "origin",
    "company", "publisher", "license", "language", "purpose", "use", "type",
    "first", "version", "history",
)


def _run(coro):
    """Drive an async pipeline call to completion from sync test context."""
    return asyncio.run(coro)


async def _teach_and_settle(knowledge: str, wait_s: float):
    """Plant the knowledge and let the consolidation thread write it to the KG."""
    commit = await answer_question(knowledge, session_id=SESSION_ID)
    await asyncio.sleep(wait_s)
    return commit


def _kg_has_entity(key: str) -> bool:
    """True if the KG holds a concept matching ``key`` (case-insensitive)."""
    graph = KnowledgeGraph()
    if graph.get_concept(key) is not None:
        return True
    key_lc = key.lower()
    return any(c.lower() == key_lc for c in graph.all_concepts())


# ── Implementation discovery ──────────────────────────────────────────────────
def _resolve_curiosity_engine():
    """
    Return a live curiosity-engine instance exposing a gap-scan method, or ``None``
    if no candidate module/attribute provides one. A class candidate is instantiated
    (no-arg); a ready instance is used as-is.
    """
    for module_path, attr in CURIOSITY_ENGINE_CANDIDATES:
        try:
            module = importlib.import_module(module_path)
        except Exception:
            continue
        obj = getattr(module, attr, None)
        if obj is None:
            continue
        # Instantiate a class; accept an already-built singleton instance.
        if isinstance(obj, type):
            try:
                obj = obj()
            except Exception:
                continue
        if any(callable(getattr(obj, m, None)) for m in SCAN_METHOD_NAMES):
            return obj
    return None


def _result_is_nonempty(result) -> bool:
    """True if a scan result actually carries goals."""
    if isinstance(result, (list, tuple)):
        return len(result) > 0
    if isinstance(result, dict):
        return any(
            isinstance(result.get(k), (list, tuple)) and result.get(k)
            for k in ("goals", "pending", "new_goals", "formed")
        )
    return bool(result)


def _invoke_scan(engine):
    """Call the engine's gap-scan method (sync or async) and return its result.

    Implementations differ in signature: some take a numeric ``limit`` (e.g.
    ``scan(limit=25)``), others take the entity to scan (e.g. ``scan_for_gaps(
    "Blender")``). We must not assume one shape — passing the entity where an int
    ``limit`` is expected does NOT raise here, it silently scans nothing. So we try
    the no-arg / keyword forms FIRST, fall back to a positional entity LAST, and
    prefer whichever call actually produced goals. A bad signature never aborts the
    search; only a real error with no working form does.
    """
    last_exc: Exception | None = None
    for name in SCAN_METHOD_NAMES:
        method = getattr(engine, name, None)
        if not callable(method):
            continue
        fallback = None
        any_success = False
        # Order matters: no-arg and keyword forms can't be misread as ``limit``;
        # a bare positional entity (risky — may be taken as ``limit``) goes last.
        for call in (
            lambda: method(),
            lambda: method(entity=ENTITY),
            lambda: method(ENTITY),
            lambda: method(ENTITY_KEY),
        ):
            try:
                result = call()
            except TypeError:
                continue  # signature mismatch — try the next form
            except Exception as exc:
                last_exc = exc  # remember, but a later form may still work
                continue
            if asyncio.iscoroutine(result):
                result = _run(result)
            any_success = True
            if _result_is_nonempty(result):
                return name, result      # a productive call — prefer it
            if fallback is None:
                fallback = result        # remember a clean-but-empty result
        if any_success:
            return name, fallback
    if last_exc is not None:
        raise last_exc
    raise AssertionError(
        f"Curiosity engine exposes none of the expected scan methods {SCAN_METHOD_NAMES}."
    )


def _collect_goals(engine, scan_result) -> list:
    """
    Resolve the current goal collection: prefer a non-empty list returned by the
    scan; otherwise query the engine's goal getters.
    """
    if isinstance(scan_result, (list, tuple)) and scan_result:
        return list(scan_result)
    if isinstance(scan_result, dict):
        for k in ("goals", "pending", "new_goals", "formed"):
            v = scan_result.get(k)
            if isinstance(v, (list, tuple)) and v:
                return list(v)
    for name in GOAL_GETTER_NAMES:
        attr = getattr(engine, name, None)
        try:
            value = attr() if callable(attr) else attr
        except Exception:
            continue
        if asyncio.iscoroutine(value):
            value = _run(value)
        if isinstance(value, (list, tuple)) and value:
            return list(value)
    return []


# ── Goal field access (object | dict | sqlite Row) ────────────────────────────
def _field(goal, aliases):
    """Return the first present, non-empty field value among ``aliases``."""
    # Mapping-like (dict / sqlite3.Row).
    if isinstance(goal, dict):
        for a in aliases:
            if a in goal and goal[a] not in (None, ""):
                return goal[a]
    else:
        try:  # sqlite3.Row supports keys()
            keys = set(goal.keys())  # type: ignore[attr-defined]
            for a in aliases:
                if a in keys and goal[a] not in (None, ""):
                    return goal[a]
        except Exception:
            pass
    # Object attributes.
    for a in aliases:
        if hasattr(goal, a):
            val = getattr(goal, a)
            if val not in (None, ""):
                return val
    return None


def _goal_repr(goal) -> str:
    if isinstance(goal, dict):
        return str(goal)
    if hasattr(goal, "to_dict"):
        try:
            return str(goal.to_dict())
        except Exception:
            pass
    try:
        keys = list(goal.keys())  # type: ignore[attr-defined]
        return str({k: goal[k] for k in keys})
    except Exception:
        return repr(goal)


def _status_str(status) -> str:
    """Normalize a status to an upper-case token.

    Handles a plain string ("pending"/"PENDING") AND an Enum member such as
    ``GoalStatus.PENDING`` whose ``str()`` is ``"GoalStatus.PENDING"`` but whose
    ``.value`` is ``"pending"``. Without unwrapping ``.value`` a perfectly valid
    enum-typed PENDING goal would be silently rejected.
    """
    if status is None:
        return ""
    value = getattr(status, "value", status)  # Enum -> its underlying value
    return str(value).strip().upper()


def _has_entity(value, entity_key: str) -> bool:
    return entity_key.lower() in str(value).lower()


def _names_missing_attribute(*values) -> bool:
    blob = " ".join(str(v).lower() for v in values if v is not None)
    return any(term in blob for term in MISSING_ATTRIBUTE_TERMS)


# ─────────────────────────────────────────────────────────────────────────────
# TURN 1 — SET KNOWLEDGE (commit Blender to the KG)
# ─────────────────────────────────────────────────────────────────────────────
def test_1_set_knowledge_commits_to_kg():
    """The new entity must commit and land as a KG concept before curiosity runs."""
    resp = _run(_teach_and_settle(TURN1_KNOWLEDGE, CONSOLIDATION_WAIT_SECONDS))

    assert resp.answer.strip() == COMMIT_MESSAGE, (
        f"Expected the commitment message {COMMIT_MESSAGE!r}, got {resp.answer!r}. "
        "The Knowledge-Acquisition layer did not intercept the declarative statement."
    )
    assert resp.confidence == "CERTAIN", (
        f"Commit should be CERTAIN, got confidence={resp.confidence!r}"
    )
    debug = resp.debug or {}
    learned = debug.get("learned_triples") or []
    flat = " ".join(str(part) for triple in learned for part in triple).lower()
    assert ENTITY.lower() in flat, (
        f"The entity {ENTITY!r} was not captured in any learned triple: {learned!r}"
    )

    # The decisive precondition for curiosity: the entity is now a KG node.
    assert _kg_has_entity(ENTITY_KEY), (
        f"Entity {ENTITY!r} did not consolidate into the Knowledge Graph as a "
        f"concept (looked for {ENTITY_KEY!r}). The background consolidator has not "
        "written the node; curiosity has nothing to scan."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 2 — THE CURIOSITY TRIGGER (Phase 59 contract)
# ─────────────────────────────────────────────────────────────────────────────
def test_2_curiosity_forms_pending_goal():
    """
    Scanning for gaps must autonomously produce >= 1 structurally-sound PENDING goal
    that targets a missing attribute of Blender.
    """
    # Make sure the entity is in the KG even if this test runs in isolation.
    if not _kg_has_entity(ENTITY_KEY):
        _run(_teach_and_settle(TURN1_KNOWLEDGE, CONSOLIDATION_WAIT_SECONDS))

    engine = _resolve_curiosity_engine()
    assert engine is not None, (
        "No proactive curiosity engine found. None of the candidate modules exposed "
        f"an object with a gap-scan method {SCAN_METHOD_NAMES}. Candidates probed: "
        f"{[m for m, _ in CURIOSITY_ENGINE_CANDIDATES]}. Phase 59 is not built."
    )

    scan_name, scan_result = _invoke_scan(engine)
    goals = _collect_goals(engine, scan_result)

    # (a) Curiosity must have produced at least one goal.
    assert goals, (
        f"The gap scan ({scan_name}) produced no goals. VELYNX did not autonomously "
        "form any goal for the attribute-poor 'blender' node — it is not yet curious."
    )

    # (b) At least one goal must be a sound, PENDING, Blender-targeted attribute goal.
    pending_blender_goals = []
    for goal in goals:
        status = _field(goal, STATUS_FIELDS)
        if _status_str(status) != PENDING_STATUS:
            continue
        entity = _field(goal, ENTITY_FIELDS)
        if entity is None or not _has_entity(entity, ENTITY_KEY):
            continue
        pending_blender_goals.append(goal)

    assert pending_blender_goals, (
        f"No PENDING goal targets {ENTITY!r}. A curiosity goal must carry "
        f"status=={PENDING_STATUS!r} and a target-entity field referencing the new "
        f"node. Goals seen: {[_goal_repr(g) for g in goals]!r}"
    )

    # (c) Structural soundness + a real missing attribute, on at least one of them.
    sound = None
    diagnostics = []
    for goal in pending_blender_goals:
        gid = _field(goal, ID_FIELDS)
        entity = _field(goal, ENTITY_FIELDS)
        attribute = _field(goal, ATTRIBUTE_FIELDS)
        has_id = gid is not None
        has_attr_field = attribute is not None
        # The attribute must name a genuinely-missing fact — accept the dedicated
        # attribute field, or (as a fallback) a description/title that names one.
        descr = _field(goal, ("description", "title", "text", "goal", "objective"))
        names_gap = _names_missing_attribute(attribute, descr)
        if has_id and has_attr_field and names_gap:
            sound = goal
            break
        diagnostics.append(
            f"id={gid!r} attribute={attribute!r} descr={descr!r} "
            f"(has_id={has_id}, has_attribute_field={has_attr_field}, "
            f"names_missing_attribute={names_gap})"
        )

    assert sound is not None, (
        "A PENDING Blender goal exists but none is structurally sound: each must have "
        "an id, a target-attribute field, and that attribute must name a genuinely "
        f"missing fact (one of {MISSING_ATTRIBUTE_TERMS[:6]}...). "
        f"Diagnostics: {diagnostics!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner — prints a falsifiable PASS/FAIL report and sets exit code.
# ─────────────────────────────────────────────────────────────────────────────
def _main() -> int:
    tests = [
        ("TURN 1 - SET KNOWLEDGE (commit Blender to KG)", test_1_set_knowledge_commits_to_kg),
        ("TURN 2 - CURIOSITY TRIGGER (autonomous PENDING goal for missing attribute)",
         test_2_curiosity_forms_pending_goal),
    ]
    print("=" * 72)
    print("VELYNX Falsifiable Cognitive Test Suite (Phase 59 — Curiosity & Goal Formation)")
    print("=" * 72)

    failures = 0
    for label, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failures += 1
            print(f"[FAIL] {label}\n       {exc}")
        except Exception as exc:  # infrastructure / import / runtime error
            failures += 1
            print(f"[ERROR] {label}\n        {type(exc).__name__}: {exc}")
        else:
            print(f"[PASS] {label}")

    print("-" * 72)
    total = len(tests)
    print(f"Result: {total - failures}/{total} passed.")
    if failures:
        print("Proactive curiosity / goal formation NOT present — Phase 59 is not 'done'.")
    else:
        print("Autonomous PENDING goal formed for a missing attribute. Phase 59 'Done When' satisfied.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
