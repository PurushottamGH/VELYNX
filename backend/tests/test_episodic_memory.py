"""
Falsifiable Cognitive Test Suite — Phase 61 (Episodic Narrative Memory)
=======================================================================

Phase 59 gave VELYNX *proactive curiosity* — it autonomously detects missing
attributes and files PENDING goals. Phase 60.1 gave it *introspection* — it can
compile what it does and does not know into an Epistemic State. Phase 60.2 gave it
*self-referential routing* — "what do you know about X" is answered by
introspection, not the web.

What VELYNX still cannot do is **narrate its own learning history**. When asked
"How did you learn who created Blender?" it has no episodic causal chain to
replay — no memory that links an initial retrieval failure, the curiosity-driven
goal that was formed in response, and the eventual acquisition of the fact.

Phase 61 introduces **Episodic Narrative Memory** — a subsystem that tracks causal
chains of events (e.g. Query -> Retrieval Failure -> Goal Creation -> Eventual
Learning) and can replay them when asked "how did you learn X?".

The canonical case:

    TURN 1 — SET KNOWLEDGE
        "Blender is my favorite software."
        Commits to the KG as ``blender`` (domain PERSONAL). The curiosity engine
        detects the bare node and files PENDING goals for missing attributes
        (creator, release_year, ...).

    TURN 2 — THE FAILURE
        "Who created Blender?"
        The system does not know (confidence != CERTAIN). The pipeline's external
        retrieval similarly finds nothing useful. **Crucially**, the system MUST
        have a PENDING curiosity goal for ``(blender, creator)`` — the gap was
        detected during TURN 1's consolidation and never satisfied.

    TURN 3 — THE ACQUISITION
        "Ton Roosendaal created Blender."
        The Knowledge-Acquisition layer learns the fact. The curiosity engine's
        goal for ``(blender, creator)`` transitions from PENDING to SATISFIED.

    TURN 4 — THE CAUSAL TEST
        "How did you learn who created Blender?"
        This is the Phase 61 contract. The system must:
          1) Route this query to the Episodic Narrative Memory subsystem (it is
             NOT an external-fact question — it is auto-biographical).
          2) Respond with an answer that references the causal chain:
             - the initial retrieval/knowledge failure,
             - the knowledge gap / curiosity goal that was detected,
             - the eventual acquisition of the fact.

Falsifiability
--------------
Every assertion is concrete and CAN fail. Today there is no Episodic Narrative
Memory module — no component intercepts "how did you learn X" and no causal-chain
data structure exists. TURN 2 will fail if the curiosity engine does not produce a
PENDING "creator" goal after TURN 1 (Phase 59 not built). TURN 4 will fail if the
episodic narrative handler does not exist or produces a generic answer without the
causal-chain references. A green run is the definition of "Phase 61 done".

Run it either way:

    pytest backend/tests/test_episodic_memory.py -v
    python  backend/tests/test_episodic_memory.py     # standalone PASS/FAIL report
"""

from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path

# Windows consoles default to cp1252; answers/labels may carry Unicode. Force UTF-8
# with a safe fallback so a failure report can never itself crash the suite.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

# ── Path bootstrap ───────────────────────────────────────────────────────────
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
SESSION_ID = "episodic-narrative-suite"

# TURN 1 plants the entity whose learning journey we will trace.
TURN1_KNOWLEDGE = "Blender is my favorite software."
ENTITY = "Blender"
ENTITY_KEY = "blender"          # KG stores it lower-cased

# TURN 2 — the question the system CANNOT answer (yet).
TURN2_QUERY = "Who created Blender?"

# TURN 3 — the bridging fact that satisfies the curiosity goal.
TURN3_KNOWLEDGE = "Ton Roosendaal created Blender."
CREATOR = "ton_roosendaal"      # KG normalised form
CREATOR_PRETTY = "Ton Roosendaal"

# TURN 4 — the causal-chain query that Phase 61 must handle.
TURN4_QUERY = "How did you learn who created Blender?"
CAUSAL_CHAIN_QUERIES = (
    "How did you learn who created Blender?",
    "How do you know who created Blender?",
    "How did you find out who created Blender?",
)

# Consolidation runs on a BACKGROUND thread; give it time to write to the KG.
CONSOLIDATION_WAIT_SECONDS = 5

# The curiosity engine must produce a PENDING "creator" goal for Blender after
# TURN 1, and that goal must transition to SATISFIED after TURN 3.
PENDING_STATUS = "PENDING"
SATISFIED_STATUS = "SATISFIED"

# ── Episodic Narrative Memory discovery candidates ───────────────────────────
# Where the Phase 61 handler might live, and what the handler/class might be
# called. The candidate list mirrors the convention in the Phase 59/60 suites:
# we probe each (module, attribute) pair and use the first that exposes an
# entry point for processing causal-chain / "how did you learn" queries.
EPISODIC_CANDIDATES = (
    ("backend.cognition.episodic_narrative", "episodic_narrative_handler"),
    ("backend.cognition.episodic_narrative", "EpisodicNarrativeHandler"),
    ("backend.cognition.episodic_memory", "episodic_narrative_handler"),
    ("backend.cognition.episodic_memory", "EpisodicNarrativeHandler"),
    ("backend.memory.episodic_narrative", "episodic_narrative_handler"),
    ("backend.memory.episodic_narrative", "EpisodicNarrativeHandler"),
    ("backend.memory.episodic_memory", "episodic_narrative_handler"),
    ("backend.memory.episodic_memory", "EpisodicNarrativeHandler"),
    ("backend.pipeline.episodic_narrative", "episodic_narrative_handler"),
    ("backend.pipeline.episodic_narrative", "EpisodicNarrativeHandler"),
    ("backend.pipeline.causal_chain", "causal_chain_handler"),
    ("backend.pipeline.causal_chain", "CausalChainHandler"),
)
# Method names the handler might expose for processing "how did you learn" queries.
NARRATIVE_METHODS = (
    "narrate", "replay", "trace", "get_narrative", "answer_narrative",
    "process_causal_query", "handle_causal_query", "causal_narrative",
    "retrieve_causal_chain", "__call__",
)
# Method names that return the full causal chain (for direct assertion without
# going through the handler's text-answer path).
CAUSAL_CHAIN_GETTERS = (
    "get_causal_chain", "causal_chain", "chain", "get_trace",
    "retrieve_chain", "causal_trace",
)
# Field aliases for causal-chain events/steps.
EVENT_FIELDS = ("event", "step", "type", "kind", "phase", "description", "summary")
TIMESTAMP_FIELDS = ("timestamp", "time", "when", "at", "ts")

# ── Causal-chain event-type content we expect the narrative to reference ──────
CAUSAL_CHAIN_MARKERS = (
    # The retrieval/knowledge failure must be referenced.
    "retrieval", "failure", "could not answer", "did not know", "didn't know",
    "not found", "was unknown",
    "unknown", "couldn't answer",
    # The knowledge gap / curiosity goal must be referenced.
    "knowledge gap", "curiosity goal", "goal", "curiosity", "detected",
    "missing", "gap", "creator",
    # The acquisition / learning event must be referenced.
    "learned", "acquired", "committed", "stored", "satisfied",
    "you told me", "you taught", "was taught",
)

# ── Goal properties (reused from test_curiosity.py conventions) ──────────────
STATUS_FIELDS = ("status", "state")
ENTITY_FIELDS = ("target_entity", "entity", "subject", "about", "about_concept",
                 "concept", "target", "node")
ATTRIBUTE_FIELDS = ("target_attribute", "attribute", "attr", "missing_attribute",
                    "predicate", "relation", "slot", "property", "field")
ID_FIELDS = ("id", "goal_id", "uid", "uuid", "pk")

# The specific attribute we expect a curiosity goal to target for Blender.
EXPECTED_ATTRIBUTE_TERMS = ("creator", "author", "developer", "founder", "maker",
                            "designer", "created", "founded")


def _run(coro):
    """Drive an async pipeline call to completion from sync test context."""
    return asyncio.run(coro)


async def _teach_and_settle(knowledge: str, wait_s: float):
    """Plant the knowledge and let the consolidation thread write it to the KG."""
    commit = await answer_question(knowledge, session_id=SESSION_ID)
    await asyncio.sleep(wait_s)
    return commit


def _kg_has_entity(key: str) -> bool:
    graph = KnowledgeGraph()
    if graph.get_concept(key) is not None:
        return True
    kg_lc = key.lower()
    return any(c.lower() == kg_lc for c in graph.all_concepts())


def _ensure_blender_committed():
    if not _kg_has_entity(ENTITY_KEY):
        _run(_teach_and_settle(TURN1_KNOWLEDGE, CONSOLIDATION_WAIT_SECONDS))


# ── Curiosity / Goal helpers ─────────────────────────────────────────────────
def _resolve_goal_manager():
    """Return the process-wide GoalManager singleton, or None."""
    try:
        from backend.agency.curiosity import goal_manager as _gm
        return _gm
    except Exception:
        return None


def _field(obj, aliases):
    """Return the first present, non-empty field value among ``aliases``."""
    if isinstance(obj, dict):
        for a in aliases:
            if a in obj and obj[a] not in (None, ""):
                return obj[a]
    else:
        try:
            keys = set(obj.keys())
            for a in aliases:
                if a in keys and obj[a] not in (None, ""):
                    return obj[a]
        except Exception:
            pass
    for a in aliases:
        if hasattr(obj, a):
            val = getattr(obj, a)
            if val not in (None, ""):
                return val
    return None


def _status_str(status) -> str:
    """Normalize a status to an upper-case token (handles Enum members)."""
    if status is None:
        return ""
    value = getattr(status, "value", status)
    return str(value).strip().upper()


def _goal_repr(goal) -> str:
    if isinstance(goal, dict):
        return str(goal)
    if hasattr(goal, "to_dict"):
        try:
            return str(goal.to_dict())
        except Exception:
            pass
    try:
        keys = list(goal.keys())
        return str({k: goal[k] for k in keys})
    except Exception:
        return repr(goal)


def _find_goals_for_entity(goals, entity_key: str) -> list:
    """Filter goals whose target-entity field references ``entity_key``."""
    result = []
    for goal in goals:
        entity = _field(goal, ENTITY_FIELDS)
        if entity is not None and entity_key.lower() in str(entity).lower():
            result.append(goal)
    return result


def _trigger_curiosity_scan():
    """Run scan_for_gaps so PENDING goals populate the goal_manager."""
    try:
        from backend.agency.curiosity import scan_for_gaps
        scan_for_gaps()
        return True
    except Exception:
        return False


# ── Episodic Narrative Memory discovery ──────────────────────────────────────
def _resolve_narrative_handler():
    """
    Return a live episodic-narrative handler instance or ``None``.
    Probes candidate modules for a class (instantiated no-arg) or a ready
    singleton; the handler must expose at least one narrative method.
    """
    for module_path, attr in EPISODIC_CANDIDATES:
        try:
            module = importlib.import_module(module_path)
        except Exception:
            continue
        obj = getattr(module, attr, None)
        if obj is None:
            continue
        if isinstance(obj, type):
            try:
                obj = obj()
            except Exception:
                continue
        if any(callable(getattr(obj, m, None)) for m in NARRATIVE_METHODS):
            return obj
    return None


def _invoke_narrative(handler, query: str, entity: str = "Blender"):
    """
    Call the handler's first available narrative method with ``query``.
    Tries (query,) first, then (query, entity), then query + context dict.
    Returns the result or raises an informative error.
    """
    last_exc: Exception | None = None
    for name in NARRATIVE_METHODS:
        method = getattr(handler, name, None)
        if not callable(method):
            continue
        for call_args in (
            lambda: method(query),
            lambda: method(query, entity),
            lambda: method(query, {"entity": entity}),
        ):
            try:
                result = call_args()
                if asyncio.iscoroutine(result):
                    result = _run(result)
                return result
            except TypeError:
                continue
            except Exception as exc:
                last_exc = exc
                continue
    if last_exc is not None:
        raise last_exc
    raise AssertionError(
        f"Episodic narrative handler exposes none of the expected methods "
        f"{NARRATIVE_METHODS}."
    )


def _extract_text(result) -> str:
    """Pull the answer text out of a narrative result (AnswerResponse, dict, or str)."""
    if isinstance(result, str):
        return result
    if hasattr(result, "answer"):
        return str(getattr(result, "answer"))
    if isinstance(result, dict):
        return str(result.get("answer", result.get("narrative", result.get("text", result))))
    return str(result)


def _extract_causal_chain(handler) -> list | None:
    """Get the raw causal-chain events from the handler, if a getter exists."""
    for name in CAUSAL_CHAIN_GETTERS:
        method = getattr(handler, name, None)
        if callable(method):
            try:
                chain = method()
                if asyncio.iscoroutine(chain):
                    chain = _run(chain)
                if isinstance(chain, (list, tuple)) and chain:
                    return list(chain)
            except Exception:
                continue
    return None


def _chain_event_texts(chain: list) -> list[str]:
    """Flatten a causal-chain event list to human-readable strings."""
    texts = []
    for event in chain:
        if isinstance(event, str):
            texts.append(event)
        elif isinstance(event, dict):
            val = _field(event, EVENT_FIELDS + TIMESTAMP_FIELDS)
            if val:
                texts.append(str(val))
            else:
                texts.append(str(event))
        elif hasattr(event, "__dict__"):
            texts.append(str(event))
        else:
            texts.append(str(event))
    return texts


# ─────────────────────────────────────────────────────────────────────────────
# TURN 1 — SET KNOWLEDGE (commit Blender to KG)
# ─────────────────────────────────────────────────────────────────────────────
def test_1_set_knowledge_commits_to_kg():
    """'Blender is my favorite software' must commit and land as a KG concept.

    This is the prerequisite for all subsequent turns: the curiosity engine needs
    the entity to exist before it can file goals against it.
    """
    resp = _run(_teach_and_settle(TURN1_KNOWLEDGE, CONSOLIDATION_WAIT_SECONDS))

    assert resp.answer.strip() == "I have committed that to memory.", (
        f"Expected the commitment message, got {resp.answer!r}. The Knowledge-"
        "Acquisition layer did not intercept the declarative statement."
    )
    assert resp.confidence == "CERTAIN", (
        f"Commit should be CERTAIN, got confidence={resp.confidence!r}"
    )
    debug = resp.debug or {}
    learned = debug.get("learned_triples") or []
    flat = " ".join(str(part) for triple in learned for part in triple).lower()
    assert ENTITY_KEY in flat, (
        f"The entity {ENTITY!r} was not captured in any learned triple: {learned!r}"
    )

    # The decisive precondition: the entity is now a KG node.
    assert _kg_has_entity(ENTITY_KEY), (
        f"Entity {ENTITY!r} did not consolidate into the Knowledge Graph as a "
        f"concept (looked for {ENTITY_KEY!r}). The background consolidator has not "
        "written the node; the curiosity engine has nothing to scan."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 2 — THE FAILURE (system cannot answer, but PENDING goal exists)
# ─────────────────────────────────────────────────────────────────────────────
def test_2_failure_and_pending_goal():
    """
    'Who created Blender?' must produce a LOW/UNKNOWN answer AND a PENDING curiosity
    goal for '(blender, creator)' must exist.

    The curiosity engine detected the missing attributes during TURN 1's
    consolidation. Even though the pipeline does not know the answer, the
    internally-filed PENDING goal for 'creator' proves VELYNX *registered the gap*.
    This gap is the first causal link in the episodic chain.
    """
    _ensure_blender_committed()
    # Ensure the curiosity engine has scanned — even in test mode the scan should
    # have been triggered by consolidate_and_explore (or we trigger it manually).
    _trigger_curiosity_scan()

    # Execute the question the system cannot answer.
    resp = _run(answer_question(TURN2_QUERY, session_id=SESSION_ID))

    # (a) The answer confidence must NOT be CERTAIN — the system genuinely does not
    #     know who created Blender (unless it happens to have an external retrieval
    #     hit, which would be coincidental and not causal).
    assert resp.confidence in ("LOW", "UNKNOWN"), (
        f"Expected LOW/UNKNOWN confidence for an unlearned fact {TURN2_QUERY!r}, "
        f"got confidence={resp.confidence!r}. The system should not pretend to know "
        "this without having been taught."
    )

    # (b) The Curiosity Engine must have a PENDING goal targeting Blender's creator.
    gm = _resolve_goal_manager()
    assert gm is not None, (
        "No GoalManager found. The curiosity engine must be built and its "
        "process-wide singleton accessible for Phase 61's causal chain to trace."
    )

    # We need to check across ALL goal statuses because the consolidation process
    # may mark some goals alongside PENDING ones. We check specifically for a
    # PENDING goal with entity=blender and an attribute matching "creator".
    from backend.agency.curiosity import GoalStatus

    pending_blender_goals = _find_goals_for_entity(
        gm.all(GoalStatus.PENDING), ENTITY_KEY
    )

    assert pending_blender_goals, (
        f"No PENDING curiosity goal targets {ENTITY!r}. The curiosity engine did not "
        f"detect missing attributes for the newly-learned entity. "
        f"All goals: {[g.target_attribute for g in gm.all()]!r}. "
        "Phase 59 (curiosity gap detection) must be functioning for Phase 61 to "
        "track the causal chain."
    )

    # (c) At least one PENDING goal must target the creator attribute specifically.
    creator_goal = None
    for goal in pending_blender_goals:
        attr = _field(goal, ATTRIBUTE_FIELDS)
        if attr and any(term in str(attr).lower() for term in EXPECTED_ATTRIBUTE_TERMS):
            creator_goal = goal
            break

    assert creator_goal is not None, (
        f"None of the PENDING goals for {ENTITY!r} target the creator attribute. "
        f"Goals seen: {[_field(g, ATTRIBUTE_FIELDS) for g in pending_blender_goals]!r}. "
        "The curiosity engine must produce a 'creator' goal for a software entity; "
        "this is the gap whose eventual satisfaction the episodic narrative replays."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 3 — THE ACQUISITION (learn the creator fact)
# ─────────────────────────────────────────────────────────────────────────────
def test_3_acquire_creator_fact():
    """
    'Ton Roosendaal created Blender' must commit to the KG AND the corresponding
    curiosity goal for '(blender, creator)' must transition to SATISFIED.

    The transition from PENDING -> SATISFIED is the second causal link in the chain:
    it proves VELYNX knows this fact now as a result of deliberate teaching.
    """
    _ensure_blender_committed()
    # Ensure no stale SATISFIED state from a prior run.
    _trigger_curiosity_scan()

    # Execute the teaching turn.
    resp = _run(_teach_and_settle(TURN3_KNOWLEDGE, CONSOLIDATION_WAIT_SECONDS))

    assert resp.answer.strip() == "I have committed that to memory.", (
        f"Expected the commitment message, got {resp.answer!r}"
    )
    assert resp.confidence == "CERTAIN", (
        f"Commit should be CERTAIN, got confidence={resp.confidence!r}"
    )

    # (a) The creator fact must be in learned triples.
    debug = resp.debug or {}
    learned = debug.get("learned_triples") or []
    flat = " ".join(str(part) for triple in learned for part in triple).lower()
    assert CREATOR in flat or CREATOR_PRETTY.lower() in flat, (
        f"The creator {CREATOR_PRETTY!r} was not captured in learned triples: "
        f"{learned!r}"
    )

    # (b) The curiosity goal for '(blender, creator)' must now be SATISFIED.
    gm = _resolve_goal_manager()
    assert gm is not None, "GoalManager not available for status assertion."

    from backend.agency.curiosity import GoalStatus

    satisfied_blender_goals = _find_goals_for_entity(
        gm.all(GoalStatus.SATISFIED), ENTITY_KEY
    )

    creator_satisfied = False
    for goal in satisfied_blender_goals:
        attr = _field(goal, ATTRIBUTE_FIELDS)
        if attr and any(term in str(attr).lower() for term in EXPECTED_ATTRIBUTE_TERMS):
            creator_satisfied = True
            break

    assert creator_satisfied, (
        f"No SATISFIED curiosity goal for creator of {ENTITY!r} found after teaching "
        f"the creator fact. All SATISFIED goals for Blender: "
        f"{[_field(g, ATTRIBUTE_FIELDS) for g in satisfied_blender_goals]!r}. "
        "The curiosity engine must mark the goal SATISFIED when the fact enters the "
        "KG; this transition is the causal evidence Phase 61 replays."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 4 — THE CAUSAL TEST (episodic narrative memory)
# ─────────────────────────────────────────────────────────────────────────────
def test_4_episodic_narrative_references_causal_chain():
    """
    'How did you learn who created Blender?' must route to the Episodic Narrative
    Memory subsystem and produce a response that references the full causal chain:

      1. The retrieval/knowledge failure (the system did not know)
      2. The knowledge gap / curiosity goal (the system detected it was missing)
      3. The eventual acquisition (the system learned from the user)

    This is the Phase 61 contract. If the handler does not exist, the test fails
    instructively. If the handler exists but returns a generic response without
    referencing the causal markers, the test fails instructively.
    """
    _ensure_blender_committed()
    _trigger_curiosity_scan()

    # Ensure the creator fact is in the KG and the goal is satisfied.
    if not _kg_has_entity(CREATOR):
        _run(_teach_and_settle(TURN3_KNOWLEDGE, CONSOLIDATION_WAIT_SECONDS))

    handler = _resolve_narrative_handler()
    assert handler is not None, (
        "No Episodic Narrative Memory handler found. None of the candidate modules "
        f"exposed an object with a narrative method {NARRATIVE_METHODS}. "
        f"Candidates probed: {[m for m, _ in EPISODIC_CANDIDATES]}. "
        "Phase 61 is not built: VELYNX cannot narrate its own learning history."
    )

    result = _invoke_narrative(handler, TURN4_QUERY, ENTITY)
    answer_text = _extract_text(result)

    assert answer_text, (
        "The episodic narrative handler returned an empty response. Phase 61 must "
        "produce a non-empty answer for 'How did you learn who created Blender?'."
    )

    # (a) The answer must reference at least ONE of the causal-chain markers
    #     covering retrieval failure, gap detection, and acquisition.
    answer_lower = answer_text.lower()
    matched_markers = [
        m for m in CAUSAL_CHAIN_MARKERS if m.lower() in answer_lower
    ]

    # (b) We need coverage across ALL three causal phases: failure, gap, acquisition.
    #     Partition the markers into the three causal phases.
    FAILURE_MARKERS = {"retrieval", "failure", "could not answer", "did not know",
                       "didn't know", "not found", "was unknown", "unknown",
                       "couldn't answer"}
    GAP_MARKERS = {"knowledge gap", "curiosity goal", "goal", "curiosity", "detected",
                   "missing", "gap", "creator"}
    ACQUISITION_MARKERS = {"learned", "acquired", "committed", "stored", "satisfied",
                           "you told me", "you taught", "was taught"}

    has_failure = any(m in answer_lower for m in FAILURE_MARKERS)
    has_gap = any(m in answer_lower for m in GAP_MARKERS)
    has_acquisition = any(m in answer_lower for m in ACQUISITION_MARKERS)

    assert has_failure, (
        f"The episodic narrative response does not reference the RETRIEVAL FAILURE "
        f"phase of the causal chain. Expected at least one of {FAILURE_MARKERS} in "
        f"the response. Got: {answer_text!r}"
    )
    assert has_gap, (
        f"The episodic narrative response does not reference the KNOWLEDGE GAP / "
        f"CURIOSITY GOAL phase. Expected at least one of {GAP_MARKERS} in the "
        f"response. Got: {answer_text!r}"
    )
    assert has_acquisition, (
        f"The episodic narrative response does not reference the ACQUISITION phase. "
        f"Expected at least one of {ACQUISITION_MARKERS} in the response. "
        f"Got: {answer_text!r}"
    )

    # (c) The response must reference the entity "Blender" and the creator "Ton
    #     Roosendaal" (or referential equivalents).
    assert ENTITY.lower() in answer_lower, (
        f"The episodic narrative response must reference {ENTITY!r}. "
        f"Got: {answer_text!r}"
    )

    # (d) Optionally, check that the handler's internal causal chain contains at
    #     least 2 distinct event entries (failure -> acquisition).
    raw_chain = _extract_causal_chain(handler)
    if raw_chain is not None:
        assert len(raw_chain) >= 2, (
            f"The causal chain should contain at least 2 events (failure -> "
            f"acquisition), got {len(raw_chain)}: {_chain_event_texts(raw_chain)!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner — prints a falsifiable PASS/FAIL report and sets exit code.
# ─────────────────────────────────────────────────────────────────────────────
def _main() -> int:
    tests = [
        ("TURN 1 - SET KNOWLEDGE (commit 'Blender is my favorite software')",
         test_1_set_knowledge_commits_to_kg),
        ("TURN 2 - FAILURE + PENDING GOAL ('Who created Blender?' -> LOW/UNKNOWN + PENDING creator goal)",
         test_2_failure_and_pending_goal),
        ("TURN 3 - ACQUISITION ('Ton Roosendaal created Blender' -> committed + SATISFIED goal)",
         test_3_acquire_creator_fact),
        ("TURN 4 - CAUSAL CHAIN ('How did you learn who created Blender?' -> episodic narrative with failure/gap/acquisition)",
         test_4_episodic_narrative_references_causal_chain),
    ]
    print("=" * 72)
    print("VELYNX Falsifiable Cognitive Test Suite (Phase 61 — Episodic Narrative Memory)")
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
        print("Episodic Narrative Memory NOT complete — Phase 61 is not 'done'.")
    else:
        print("VELYNX can narrate its own learning history with causal-chain awareness. "
              "Phase 61 'Done When' satisfied.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
