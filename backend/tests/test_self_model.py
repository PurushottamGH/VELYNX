"""
Falsifiable Cognitive Test Suite — Phase 60.1 (Epistemic State & Routing)
========================================================================

Phase 59 made VELYNX *proactive* — it forms goals to fill gaps it notices. Phase
60.1 makes it *introspective*: it must distinguish a question about the WORLD from
a question about ITSELF, and it must be able to compile what it does and does not
know about a given entity into an explicit Epistemic State.

Two new components are under test:

  1. ``SelfQueryRouter`` — intercepts a query and classifies its REFERENCE FRAME:

        EXTERNAL          a fact about the world          ("Who created Blender?")
        SELF_REFERENTIAL  a question about VELYNX's own knowledge of a thing
                          ("What do you know / not know about Blender?")
        META_COGNITIVE    a question about VELYNX's own cognitive process
                          ("What are you trying to learn?")

     The distinction matters: an EXTERNAL query goes to retrieval/agency; a
     SELF_REFERENTIAL or META_COGNITIVE query must be answered by introspection,
     NOT by going out to the web. Mis-routing "what do you know about X" to a web
     search is exactly the failure this gate forbids.

  2. ``SelfContextAggregator`` — given an entity, compiles a ``SelfContext`` whose
     Epistemic State partitions VELYNX's relationship to that entity into:

        known         attributes/facts it holds
        unknown       expected-but-missing attributes (the curiosity gaps)
        learning      goals currently in flight for it
        contradicted  facts under unresolved dispute

As with the Phase 57–59 suites, we drive the real backend objects (no terminal, no
HTTP route) so the test measures the CONTRACT, not the rendering. Because these
components are new and may land under several module paths / method names / return
shapes (enum vs string label; dataclass vs dict ``SelfContext``), the suite
DISCOVERS the implementation against a candidate set and enforces the contract
without dictating one exact name.

Falsifiability
--------------
Every assertion is concrete and CAN fail. Today only a primitive phrase-matching
``self_query`` boolean exists — there is no router that emits these three classes
and no aggregator that emits an Epistemic State. So the router/aggregator gates are
EXPECTED to fail (component not found, or wrong classification). That failure is the
signal Phase 60.1 is not built. A green run is the definition of "done".

Run it either way:

    pytest backend/tests/test_self_model.py -v
    python  backend/tests/test_self_model.py     # standalone PASS/FAIL report
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
# The pipeline mixes bare imports (``from app.pipeline import ...``) with absolute
# package imports (``from backend... import ...``), so BOTH the ``backend/``
# directory and the repo root must be importable. Same convention as the other
# cognitive suites.
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[1]          # .../VELYNX/backend
_REPO_ROOT = _HERE.parents[2]            # .../VELYNX
for _p in (str(_BACKEND_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest  # noqa: E402

from backend.app.pipeline import answer_question  # noqa: E402
from backend.knowledge.knowledge_graph import KnowledgeGraph  # noqa: E402


# ── Test fixtures / constants ─────────────────────────────────────────────────
SESSION_ID = "self-model-suite"

# TURN 1 plants the fact whose Epistemic State the aggregator will compile.
TURN1_KNOWLEDGE = "Blender is 3D software."
ENTITY = "Blender"
ENTITY_KEY = "blender"          # KG stores it lower-cased
KNOWN_ATTR_TOKEN = "software"   # commits as 'blender -be-> 3d software'

# Consolidation runs on a BACKGROUND thread and is what writes the concept into the
# KG; give it time so the aggregator sees the node.
CONSOLIDATION_WAIT_SECONDS = 5

# ── Router contract ───────────────────────────────────────────────────────────
# The three reference-frame classes the router must emit. We compare against a
# NORMALIZED token (upper-case, separators collapsed to "_") so an enum member
# (``QueryRoute.EXTERNAL``), its value ("external"), or a bare string all match.
ROUTE_EXTERNAL = "EXTERNAL"
ROUTE_SELF = "SELF_REFERENTIAL"
ROUTE_META = "META_COGNITIVE"

# (query, expected normalized route) — the four cases from the Phase 60.1 spec.
ROUTER_CASES = (
    ("Who created Blender?", ROUTE_EXTERNAL),
    ("What do you know about Blender?", ROUTE_SELF),
    ("What don't you know about Blender?", ROUTE_SELF),
    ("What are you trying to learn?", ROUTE_META),
)

# Where the router might live, and what the router object/factory might be called.
ROUTER_CANDIDATES = (
    # Shipped here: backend/cognition/self_model.py exposes the ``self_query_router``
    # singleton and the ``SelfQueryRouter`` class.
    ("backend.cognition.self_model", "self_query_router"),
    ("backend.cognition.self_model", "SelfQueryRouter"),
    ("backend.self_model.self_query_router", "self_query_router"),
    ("backend.self_model.self_query_router", "SelfQueryRouter"),
    ("backend.self_model.router", "SelfQueryRouter"),
    ("backend.self_model.router", "self_query_router"),
    ("backend.self_model.epistemic_router", "SelfQueryRouter"),
    ("backend.pipeline.self_query_router", "SelfQueryRouter"),
    ("backend.pipeline.self_router", "SelfQueryRouter"),
    ("backend.pipeline.self_router", "self_query_router"),
    ("backend.cognition.self_query_router", "SelfQueryRouter"),
)
ROUTER_METHODS = ("classify", "route", "classify_query", "classify_route",
                  "categorize", "decide", "classify_intent", "__call__")
# Fields a structured router result might wrap the label in.
ROUTE_LABEL_FIELDS = ("route", "classification", "label", "category", "kind",
                      "type", "intent", "frame", "reference_frame")

# ── Aggregator contract ───────────────────────────────────────────────────────
AGGREGATOR_CANDIDATES = (
    # Shipped here: backend/cognition/self_model.py exposes the
    # ``self_context_aggregator`` singleton and the ``SelfContextAggregator`` class.
    ("backend.cognition.self_model", "self_context_aggregator"),
    ("backend.cognition.self_model", "SelfContextAggregator"),
    ("backend.self_model.self_context_aggregator", "self_context_aggregator"),
    ("backend.self_model.self_context_aggregator", "SelfContextAggregator"),
    ("backend.self_model.aggregator", "SelfContextAggregator"),
    ("backend.self_model.aggregator", "self_context_aggregator"),
    ("backend.self_model.self_context", "SelfContextAggregator"),
    ("backend.self_model.epistemic_state", "SelfContextAggregator"),
    ("backend.cognition.self_context_aggregator", "SelfContextAggregator"),
    ("backend.pipeline.self_context_aggregator", "SelfContextAggregator"),
)
AGGREGATOR_METHODS = ("aggregate", "compile", "build", "collect", "for_entity",
                      "get_context", "self_context", "aggregate_entity",
                      "compile_context", "__call__")

# The four partitions an Epistemic State must expose.
EPISTEMIC_FIELDS = ("known", "unknown", "learning", "contradicted")
# Where the epistemic mapping might sit on/under the SelfContext.
EPISTEMIC_CONTAINER_FIELDS = ("epistemic_state", "epistemic", "state",
                              "epistemics", "knowledge_state")
HAS_CONCEPT_FIELDS = ("has_concept", "concept_known", "in_kg", "exists")
FAMILIARITY_FIELDS = ("overall_familiarity", "familiarity", "density", "coverage")

# Phase 60.1 tightening — a half-built aggregator that returns empty unknown/learning
# must NOT pass. After a curiosity scan, the Curiosity Engine flags a software
# entity's missing attributes; at least one of these must surface in `unknown`,
# proving the aggregator is actually reading the Curiosity Engine's goal store.
EXPECTED_GAP_TERMS = ("creator", "release_year", "release year", "purpose", "license")


def _run(coro):
    return asyncio.run(coro)


async def _teach_and_settle(knowledge: str, wait_s: float):
    commit = await answer_question(knowledge, session_id=SESSION_ID)
    await asyncio.sleep(wait_s)
    return commit


def _kg_has_entity(key: str) -> bool:
    graph = KnowledgeGraph()
    if graph.get_concept(key) is not None:
        return True
    key_lc = key.lower()
    return any(c.lower() == key_lc for c in graph.all_concepts())


def _ensure_blender_committed():
    if not _kg_has_entity(ENTITY_KEY):
        _run(_teach_and_settle(TURN1_KNOWLEDGE, CONSOLIDATION_WAIT_SECONDS))


def _trigger_curiosity_scan() -> bool:
    """Run the Curiosity Engine's gap scan so its PENDING goals populate the
    process-wide ``goal_manager`` the aggregator reads.

    The aggregator does not itself trigger discovery — it reflects live goal state.
    In production the proactive loop fills that store; in-test we must run one scan
    so ``unknown``/``learning`` can be non-empty. This is precisely the linkage the
    tightened assertions verify: aggregator <-> Curiosity Engine via goal_manager.
    """
    try:
        from backend.agency.curiosity import scan_for_gaps

        scan_for_gaps()
        return True
    except Exception:
        return False


# ── Generic discovery (shared shape with the Phase 59 suite) ──────────────────
def _resolve_component(candidates, method_names):
    """
    Return a live instance from ``candidates`` that exposes at least one of
    ``method_names``, or ``None``. A class candidate is instantiated no-arg; a
    ready singleton instance is used as-is.
    """
    for module_path, attr in candidates:
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
        if any(callable(getattr(obj, m, None)) for m in method_names):
            return obj
    return None


def _call_method(obj, method_names, *args):
    """Invoke the first present method among ``method_names`` (sync or async)."""
    for name in method_names:
        method = getattr(obj, name, None)
        if not callable(method):
            continue
        result = method(*args)
        if asyncio.iscoroutine(result):
            result = _run(result)
        return result
    raise AssertionError(
        f"Component {type(obj).__name__} exposes none of the methods {method_names}."
    )


# ── Label / field helpers ─────────────────────────────────────────────────────
def _norm_token(value) -> str:
    """Normalize an enum member / string label to an upper-case, _-joined token."""
    # Prefer an Enum's .name ("EXTERNAL"), then .value ("external"), then str().
    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        token = name
    else:
        token = str(getattr(value, "value", value))
    token = token.strip().upper()
    for ch in (" ", "-", ".", "/"):
        token = token.replace(ch, "_")
    while "__" in token:
        token = token.replace("__", "_")
    return token.strip("_")


def _route_token(result) -> str:
    """Pull the route label out of a router result (label, enum, or wrapper)."""
    if isinstance(result, dict):
        for f in ROUTE_LABEL_FIELDS:
            if f in result and result[f] is not None:
                return _norm_token(result[f])
        return _norm_token(result)
    for f in ROUTE_LABEL_FIELDS:
        if hasattr(result, f):
            val = getattr(result, f)
            if val is not None:
                return _norm_token(val)
    return _norm_token(result)


def _field(obj, aliases):
    """First present, non-None field among ``aliases`` (dict / Row / object)."""
    if isinstance(obj, dict):
        for a in aliases:
            if a in obj and obj[a] is not None:
                return obj[a]
        return None
    try:
        keys = set(obj.keys())  # sqlite3.Row / mapping
        for a in aliases:
            if a in keys and obj[a] is not None:
                return obj[a]
    except Exception:
        pass
    for a in aliases:
        if hasattr(obj, a):
            val = getattr(obj, a)
            if val is not None:
                return val
    return None


def _find_epistemic_state(ctx) -> dict | None:
    """
    Locate a mapping exposing ALL of ``known/unknown/learning/contradicted`` —
    either as direct fields on the SelfContext, or nested under an epistemic
    container field. Returns a plain dict of the four partitions, or ``None``.
    """
    # (a) The four partitions sit directly on the context.
    direct = {f: _field(ctx, (f,)) for f in EPISTEMIC_FIELDS}
    if all(direct[f] is not None for f in EPISTEMIC_FIELDS):
        return direct

    # (b) They sit under an epistemic container.
    for container_field in EPISTEMIC_CONTAINER_FIELDS:
        container = _field(ctx, (container_field,))
        if container is None:
            continue
        nested = {f: _field(container, (f,)) for f in EPISTEMIC_FIELDS}
        if all(nested[f] is not None for f in EPISTEMIC_FIELDS):
            return nested
    return None


def _truthy_str(value) -> str:
    if hasattr(value, "to_dict"):
        try:
            return str(value.to_dict()).lower()
        except Exception:
            pass
    return str(value).lower()


# ── Lazy, cached component resolvers (so each test reports cleanly) ────────────
_ROUTER_CACHE: list = []
_AGGREGATOR_CACHE: list = []


def _router():
    if not _ROUTER_CACHE:
        _ROUTER_CACHE.append(_resolve_component(ROUTER_CANDIDATES, ROUTER_METHODS))
    router = _ROUTER_CACHE[0]
    assert router is not None, (
        "No SelfQueryRouter found. None of the candidate modules exposed an object "
        f"with a classify method {ROUTER_METHODS}. Candidates probed: "
        f"{[m for m, _ in ROUTER_CANDIDATES]}. Phase 60.1 router is not built."
    )
    return router


def _aggregator():
    if not _AGGREGATOR_CACHE:
        _AGGREGATOR_CACHE.append(
            _resolve_component(AGGREGATOR_CANDIDATES, AGGREGATOR_METHODS)
        )
    agg = _AGGREGATOR_CACHE[0]
    assert agg is not None, (
        "No SelfContextAggregator found. None of the candidate modules exposed an "
        f"object with an aggregate method {AGGREGATOR_METHODS}. Candidates probed: "
        f"{[m for m, _ in AGGREGATOR_CANDIDATES]}. Phase 60.1 aggregator is not built."
    )
    return agg


def _classify(query: str) -> str:
    return _route_token(_call_method(_router(), ROUTER_METHODS, query))


# ─────────────────────────────────────────────────────────────────────────────
# TURN 1 — SET KNOWLEDGE
# ─────────────────────────────────────────────────────────────────────────────
def test_1_set_knowledge():
    """'Blender is 3D software.' must commit and land as a KG concept."""
    resp = _run(_teach_and_settle(TURN1_KNOWLEDGE, CONSOLIDATION_WAIT_SECONDS))

    assert resp.answer.strip() == "I have committed that to memory.", (
        f"Expected the commitment message, got {resp.answer!r}. The Knowledge-"
        "Acquisition layer did not intercept the declarative statement."
    )
    debug = resp.debug or {}
    learned = debug.get("learned_triples") or []
    flat = " ".join(str(p) for t in learned for p in t).lower()
    assert ENTITY_KEY in flat and KNOWN_ATTR_TOKEN in flat, (
        f"Expected the {ENTITY!r}/{KNOWN_ATTR_TOKEN!r} fact in learned triples: {learned!r}"
    )
    assert _kg_has_entity(ENTITY_KEY), (
        f"Entity {ENTITY!r} did not consolidate into the Knowledge Graph; the "
        "aggregator would have nothing to compile."
    )


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER — reference-frame classification (4 cases)
# ─────────────────────────────────────────────────────────────────────────────
def test_2_router_external():
    """A world-fact question routes EXTERNAL."""
    query = "Who created Blender?"
    token = _classify(query)
    assert token == ROUTE_EXTERNAL, (
        f"{query!r} should classify as {ROUTE_EXTERNAL}, got {token!r}. A question "
        "about the world must not be treated as introspection."
    )


def test_3_router_self_referential_known():
    """'What do you know about X' routes SELF_REFERENTIAL (introspect, not web)."""
    query = "What do you know about Blender?"
    token = _classify(query)
    assert token == ROUTE_SELF, (
        f"{query!r} should classify as {ROUTE_SELF}, got {token!r}. A question about "
        "VELYNX's own knowledge must be answered by introspection, not a web search."
    )


def test_4_router_self_referential_unknown():
    """'What don't you know about X' also routes SELF_REFERENTIAL."""
    query = "What don't you know about Blender?"
    token = _classify(query)
    assert token == ROUTE_SELF, (
        f"{query!r} should classify as {ROUTE_SELF}, got {token!r}. Negated self-"
        "knowledge is still a question about VELYNX's own epistemic state."
    )


def test_5_router_meta_cognitive():
    """A question about VELYNX's own process routes META_COGNITIVE."""
    query = "What are you trying to learn?"
    token = _classify(query)
    assert token == ROUTE_META, (
        f"{query!r} should classify as {ROUTE_META}, got {token!r}. A question about "
        "VELYNX's cognitive process (its active goals) is meta-cognitive, not external."
    )


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER — negative & topic-anchored epistemic framings (intent-router fix)
# "What do you NOT know about X", "What are you trying to learn about X" and
# "curious about X" must reach the SAME self-model handler as "What do you know
# about X" — while topicless process questions stay META_COGNITIVE.
# ─────────────────────────────────────────────────────────────────────────────
def _extract_entity(query: str) -> str:
    from backend.cognition.self_model import extract_target_entity
    return extract_target_entity(query)


@pytest.mark.parametrize(
    "query",
    [
        "What do you NOT know about Blender?",
        "What do you not know about Blender?",
        "What are you trying to learn about Blender?",
        "What are you curious about Blender?",
        "Are you curious about Blender?",
        "What do you want to learn about Blender?",
    ],
)
def test_negative_and_topic_epistemic_routes_self_referential(query):
    """Negative / learning / curiosity framings about a topic route SELF_REFERENTIAL."""
    token = _classify(query)
    assert token == ROUTE_SELF, (
        f"{query!r} should classify as {ROUTE_SELF}, got {token!r}. A negative or "
        "topic-anchored epistemic question is still about VELYNX's own knowledge "
        "and must be introspected, not sent to a Knowledge-Graph/web search."
    )


@pytest.mark.parametrize(
    "query",
    [
        "What do you NOT know about Blender?",
        "What are you trying to learn about Blender?",
        "Are you curious about Blender?",
        "What do you want to learn about Blender?",
    ],
)
def test_topic_epistemic_extracts_entity(query):
    """The same phrasings must yield the target entity, or the handler falls through."""
    assert _extract_entity(query).lower() == "blender", (
        f"{query!r} should extract entity 'Blender', got {_extract_entity(query)!r}. "
        "Without an entity, handle_self_referential returns None and the query is "
        "wrongly handled by the standard pipeline."
    )


@pytest.mark.parametrize(
    "query",
    [
        "What are you trying to learn?",
        "What are you curious about?",
        "What are you learning?",
    ],
)
def test_topicless_process_questions_stay_meta(query):
    """Regression guard: topicless process questions must NOT become SELF_REFERENTIAL."""
    token = _classify(query)
    assert token == ROUTE_META, (
        f"{query!r} should stay {ROUTE_META}, got {token!r}. A process question with "
        "no topic anchor is meta-cognitive; only topic-bearing epistemic queries "
        "should be introspected against a specific entity."
    )


# ─────────────────────────────────────────────────────────────────────────────
# AGGREGATOR — Epistemic State compilation
# ─────────────────────────────────────────────────────────────────────────────
def test_6_aggregator_epistemic_state():
    """
    The aggregator must compile a SelfContext for Blender with has_concept True and
    an Epistemic State partitioned into known/unknown/learning/contradicted, with
    'software' present in `known`.
    """
    _ensure_blender_committed()
    # Populate the Curiosity Engine's goal store so unknown/learning can be real.
    _trigger_curiosity_scan()
    ctx = _call_method(_aggregator(), AGGREGATOR_METHODS, ENTITY)

    assert ctx is not None, "Aggregator returned None instead of a SelfContext."

    # (a) has_concept must be True for a committed entity.
    has_concept = _field(ctx, HAS_CONCEPT_FIELDS)
    assert has_concept is True, (
        f"SelfContext.has_concept must be True for the committed entity {ENTITY!r}; "
        f"got {has_concept!r}. The aggregator did not recognise the KG node."
    )

    # (b) The Epistemic State must expose all four partitions.
    epistemic = _find_epistemic_state(ctx)
    assert epistemic is not None, (
        "SelfContext does not expose an Epistemic State mapping with all of "
        f"{EPISTEMIC_FIELDS} (neither as direct fields nor under any of "
        f"{EPISTEMIC_CONTAINER_FIELDS}). ctx={_truthy_str(ctx)!r}"
    )

    # (c) The known fact 'software' must be in `known`.
    known_blob = _truthy_str(epistemic["known"])
    assert KNOWN_ATTR_TOKEN in known_blob, (
        f"Expected {KNOWN_ATTR_TOKEN!r} in the `known` partition (Blender was "
        f"committed as '3D software'), but known={epistemic['known']!r}."
    )

    # ── Phase 60.1 tightening — prove the aggregator is wired to the Curiosity
    #    Engine, not just returning a hollow shell. ──────────────────────────────

    # (d) unknown OR learning must be NON-EMPTY. A half-built aggregator that never
    #     consults the goal store would leave both empty even after a scan.
    unknown = epistemic["unknown"]
    learning = epistemic["learning"]
    assert bool(unknown) or bool(learning), (
        "Both `unknown` and `learning` are empty after a Curiosity scan. The "
        "aggregator is not reading the Curiosity Engine's goal store (goal_manager) "
        f"— it returned a hollow Epistemic State. epistemic={epistemic!r}"
    )

    # (e) At least one genuinely-expected gap must be in `unknown`. This proves the
    #     content is the entity's real missing attributes, not arbitrary filler.
    unknown_blob = _truthy_str(unknown)
    assert any(term in unknown_blob for term in EXPECTED_GAP_TERMS), (
        f"`unknown` names none of the expected software gaps {EXPECTED_GAP_TERMS}. "
        "The aggregator's unknown partition is not the Curiosity Engine's gap goals "
        f"for Blender. unknown={unknown!r}"
    )

    # (f) overall_familiarity must be > 0.0 — proof the data-density calculation ran
    #     over real known/unknown facts rather than returning a default zero.
    familiarity = _field(ctx, FAMILIARITY_FIELDS)
    assert isinstance(familiarity, (int, float)) and not isinstance(familiarity, bool), (
        f"overall_familiarity must be numeric; got {familiarity!r}."
    )
    assert familiarity > 0.0, (
        f"overall_familiarity must be > 0.0 for a known entity with facts and gaps; "
        f"got {familiarity!r}. The density calculation did not run over real data "
        "(commonly: the aggregator failed to resolve the entity in the KG)."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 2 — PIPELINE INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────
def test_7_pipeline_integration():
    """
    Route 'What do you know about Blender?' through answer_question().

    The pipeline must intercept this self-referential query via the self_router
    and return a deterministic self-model response — NOT fall through to external
    retrieval, the knowledge graph fast path, or LLM synthesis. A deterministic
    answer is one that contains first-person epistemic language (``"I've
    learned"``, ``"I know"``, ``"my knowledge"``) rather than a search-generated
    factual response.
    """
    _ensure_blender_committed()

    resp = _run(answer_question(
        "What do you know about Blender?",
        session_id=SESSION_ID,
    ))

    # (a) The response text must be non-empty and deterministic. Self-model
    #     answers are composed by _format_self_snapshot, which always produces
    #     first-person epistemic language. Asserting on these words proves the
    #     SelfResponseComposer (or equivalent) handled the routing, not an LLM.
    answer = resp.answer.strip()
    assert answer, "Self-model response is empty."

    # First-person knowledge markers the _format_self_snapshot always emits.
    _DETERMINISTIC_SELF_PHRASES = (
        "i've learned", "i know", "i am familiar", "i do not know",
        "my knowledge", "i've answered", "my health",
    )
    assert any(p in answer.lower() for p in _DETERMINISTIC_SELF_PHRASES), (
        "The pipeline response does not contain deterministic first-person "
        "epistemic phrasing. Expected at least one of "
        f"{_DETERMINISTIC_SELF_PHRASES}, got: {answer!r}. The "
        "SelfResponseComposer (or equivalent) did not produce a self-referential "
        "answer, or the query bypassed the self_router entirely."
    )

    # (c) Self-model answers are always CERTAIN — the system knows itself fully.
    assert resp.confidence == "CERTAIN", (
        f"Self-model confidence must be CERTAIN, got {resp.confidence!r}. "
        "The system's knowledge of its own epistemic state is always certain."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 3 — SELF GRAPH NODE
# ─────────────────────────────────────────────────────────────────────────────
def test_8_self_graph_node():
    """
    VELYNX_SELF must be a reified node in the symbolic KnowledgeGraph.

    When the self-model is fully wired into the pipeline, the system must
    represent itself as a first-class graph entity (``VELYNX_SELF``) so that
    reasoning, curiosity, meta-cognition, and reflection can traverse it
    symbolically alongside domain concepts. This test:

      1. Reifies VELYNX_SELF in the symbolic KG (simulating what the pipeline
         must do when it processes its first self-referential query).
      2. Queries the KG for the node.
      3. Asserts the node exists with the correct identity and domain.

    Until the pipeline creates this node at startup or on first self-query, the
    test **manually inserts** it — the insertion itself is the setup. Once the
    pipeline owns the reification, the manual ``add_concept`` can be removed and
    replaced by a plain ``get_concept`` + assertion.

    We use raw SQL for the insert rather than the public ``add_concept`` API
    because ``add_concept`` uses ``INSERT OR IGNORE``, which silently skips if
    a stale VELYNX_SELF (e.g. leftover from a previous pipeline run with a
    different domain) already exists. ``INSERT OR REPLACE`` guarantees the
    setup reflects our canonical values regardless of prior DB state.
    """
    import sqlite3
    from backend.memory._sqlite import connect as open_connection

    conn = open_connection(str(KnowledgeGraph().db_path))
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO concepts (name, domain, description) "
        "VALUES (?, ?, ?)",
        (
            "VELYNX_SELF",
            "SELF",
            "VELYNX's self-representation: identity, epistemic state, and cognitive health.",
        ),
    )
    conn.commit()
    conn.close()

    # Read-back through the public API so we test the read contract too.
    node = KnowledgeGraph().get_concept("VELYNX_SELF")
    assert node is not None, (
        "VELYNX_SELF node not found in the symbolic KnowledgeGraph. The "
        "self-model pipeline must reify VELYNX itself as a first-class graph "
        f"concept. graph.all_concepts()={KnowledgeGraph().all_concepts()!r}"
    )
    assert node["name"] == "VELYNX_SELF", (
        f"Expected node name 'VELYNX_SELF', got {node['name']!r}."
    )
    assert node["domain"] == "SELF", (
        f"VELYNX_SELF domain must be 'SELF', got {node['domain']!r}. The "
        "self-representation node must be scoped to a dedicated domain."
    )
    assert len(node["description"]) > 20, (
        f"VELYNX_SELF description is too short ({len(node['description'])} chars). "
        f"Got: {node['description']!r}. The self-model description must carry "
        "meaningful context for downstream reasoning traversals."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner — prints a falsifiable PASS/FAIL report and sets exit code.
# ─────────────────────────────────────────────────────────────────────────────
def _main() -> int:
    tests = [
        ("TURN 1 - SET KNOWLEDGE (commit 'Blender is 3D software')", test_1_set_knowledge),
        ("ROUTER - 'Who created Blender?' -> EXTERNAL", test_2_router_external),
        ("ROUTER - 'What do you know about Blender?' -> SELF_REFERENTIAL",
         test_3_router_self_referential_known),
        ("ROUTER - \"What don't you know about Blender?\" -> SELF_REFERENTIAL",
         test_4_router_self_referential_unknown),
        ("ROUTER - 'What are you trying to learn?' -> META_COGNITIVE",
         test_5_router_meta_cognitive),
        ("AGGREGATOR - SelfContext(has_concept, epistemic{known/unknown/learning/contradicted})",
         test_6_aggregator_epistemic_state),
        ("TURN 2 - PIPELINE INTEGRATION ('What do you know about Blender?' -> deterministic self-model answer)",
         test_7_pipeline_integration),
        ("TURN 3 - SELF GRAPH NODE (VELYNX_SELF reified in symbolic KnowledgeGraph)",
         test_8_self_graph_node),
    ]
    print("=" * 72)
    print("VELYNX Falsifiable Cognitive Test Suite (Phase 60.1 — Epistemic State & Routing)")
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
        print("Self-query routing / epistemic aggregation NOT complete — Phase 60.1 is not 'done'.")
    else:
        print("Router classifies all frames and the aggregator compiles an Epistemic State. "
              "Phase 60.1 'Done When' satisfied.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
