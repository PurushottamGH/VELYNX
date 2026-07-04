"""
Falsifiable Cognitive Test Suite — Phase 57 (Agency & Planning)
==============================================================

This is the first gate of the Agency Era. Until now VELYNX has run a single-pass,
reactive pipeline: one question in, one retrieval/reasoning sweep, one answer out.
That is sufficient for facts it already holds, but it CANNOT answer a question
whose answer depends on the result of an intermediate lookup — a multi-hop goal.

The canonical case here:

    "What is the population of the city where my favorite coffee shop is located?"

No single retrieval can answer this. The system must first DECOMPOSE it:

    Step 1  — query its OWN Knowledge Graph for the favorite coffee shop and its
              city            (expected: Third Wave Coffee → Bengaluru)
    Step 2  — use an EXTERNAL tool (web search / retrieval mesh) to look up the
              population of that city.

Phase 57 introduces exactly that: an explicit, inspectable PLAN emitted before
execution. This suite proves the plan is generated — not (yet) that it executes
flawlessly. The contract is the *plan*, surfaced in the ``debug`` payload.

As with the Phase 53–56 suites (and the components driven by
``run_cognitive_suite.py``), we drive the EXACT backend entry point the CLI and
the FastAPI ``/query`` route both call — ``app.pipeline.answer_question`` (an
async coroutine) — so the test is immune to terminal rendering and route plumbing.

  TURN 1 — SET KNOWLEDGE
      Feed "My favorite coffee shop is Third Wave Coffee." and assert it is
      committed to memory.

  TURN 2 — THE MULTI-HOP GOAL  (the Phase 57 contract)
      Ask the population question and assert the response carries an explicit,
      multi-step ``plan`` in its debug/metadata: at least two distinct steps, the
      first an internal Knowledge-Graph lookup of the favorite coffee shop / its
      city, the second an external-tool call to find that city's population.

Falsifiability
--------------
Every assertion is concrete and can FAIL. Today the pipeline emits no ``plan`` at
all — TURN 2 is EXPECTED to fail (either no plan key, or a degenerate single-step
"answer directly"). That failure is the signal agentic planning does not yet
exist. A green run is the definition of "done".

Run it either way:

    pytest backend/tests/test_agency.py -v
    python  backend/tests/test_agency.py     # standalone PASS/FAIL report
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Windows consoles default to cp1252; pipeline answers contain Unicode (em-dash,
# etc.). Force UTF-8 with a safe fallback so printing a failure report can never
# itself crash the suite. (Same handling as the run_cognitive_suite.py components.)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

# ── Path bootstrap ───────────────────────────────────────────────────────────
# The pipeline mixes bare imports (``from app.pipeline import ...``) with absolute
# package imports (``from backend.memory._sqlite import ...``), so BOTH the
# ``backend/`` directory and the repo root must be importable. Same convention as
# test_cognition.py / test_semantic_grounding.py.
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[1]          # .../VELYNX/backend
_REPO_ROOT = _HERE.parents[2]            # .../VELYNX
for _p in (str(_BACKEND_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest  # noqa: E402

from backend.app.pipeline import answer_question  # noqa: E402


# ── Test fixtures / constants ─────────────────────────────────────────────────
SESSION_ID = "agency-suite"

# TURN 1 plants the only fact the system natively holds.
TURN1_KNOWLEDGE = "My favorite coffee shop is Third Wave Coffee."
SHOP_VALUE = "Third Wave"

# TURN 2 is the multi-hop goal — unanswerable in a single retrieval.
TURN2_MULTI_HOP_GOAL = (
    "What is the population of the city where my favorite coffee shop is located?"
)

# The deterministic acknowledgement emitted by the Knowledge-Acquisition layer.
COMMIT_MESSAGE = "I have committed that to memory."

# Phase 53.1 consolidation runs on a BACKGROUND thread; give it time so any
# KG-dependent planning sees the committed fact rather than racing the writer.
CONSOLIDATION_WAIT_SECONDS = 4

# Minimum steps a genuine multi-hop plan must contain.
MIN_PLAN_STEPS = 2

# Debug/metadata keys under which an explicit AGENTIC plan may be surfaced. We
# accept any of these so the test enforces the CONTRACT (a multi-step plan exists)
# without dictating one exact implementation field name. Deliberately excludes the
# generic "steps" because that already names the existing post-hoc monologue trace
# (``monologue.steps``) — a plan must live under a dedicated planning key.
PLAN_KEYS = {
    "plan", "plan_steps", "agentic_plan", "reasoning_plan",
    "task_plan", "subgoals", "planner", "agency",
}

# Existing post-hoc reasoning/narration containers. These are NOT agentic plans —
# they are produced AFTER a single-pass answer. We never descend into them, so a
# pre-existing trace can neither falsely satisfy "a plan exists" today nor mask a
# real plan added under a proper planning key tomorrow.
EXCLUDED_TRACE_KEYS = {"monologue", "reasoning_trace", "reflection", "dialogue"}

# Vocabulary that marks an INTERNAL knowledge-graph / memory lookup (step 1).
KG_LOOKUP_TERMS = (
    "knowledge graph", "knowledge-graph", "kg", "memory", "recall",
    "lookup", "look up", "graph", "stored", "internal",
)
# The thing step 1 must look up.
SHOP_TERMS = ("coffee", "favorite", "favourite", "shop", "third wave")

# Vocabulary that marks an EXTERNAL tool call (step 2).
EXTERNAL_TOOL_TERMS = (
    "web search", "websearch", "search", "retrieval mesh", "retrieval-mesh",
    "external", "tool", "internet", "wiki", "browse", "api",
)
# The thing step 2 must find.
POPULATION_TERMS = ("population", "inhabitants", "how many people")


def _run(coro):
    """Drive an async pipeline call to completion from sync test context."""
    return asyncio.run(coro)


def _ask(text: str):
    """Hit the real backend entry point and return the AnswerResponse."""
    return _run(answer_question(text, session_id=SESSION_ID))


async def _teach_wait_then_goal(knowledge: str, goal: str, wait_s: float):
    """
    Plant the knowledge, let the consolidation background thread persist it, then
    pose the multi-hop goal — all in ONE event loop so the await genuinely
    cooperates with the async pipeline.
    """
    commit = await answer_question(knowledge, session_id=SESSION_ID)
    await asyncio.sleep(wait_s)
    goal_resp = await answer_question(goal, session_id=SESSION_ID)
    return commit, goal_resp


def _find_plan_steps(node, _under_plan_key: bool = False):
    """
    Recursively locate the first non-empty list of plan steps in a debug payload.
    A list qualifies if it sits under a plan-ish key (e.g. ``plan``/``steps``).
    Returns the list of steps, or ``None`` if no plan is present.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            key_lc = str(key).lower()
            if key_lc in EXCLUDED_TRACE_KEYS:
                continue  # never treat a post-hoc trace as an agentic plan
            key_is_plan = key_lc in PLAN_KEYS
            if key_is_plan and isinstance(value, list) and value:
                return value
            found = _find_plan_steps(value, key_is_plan or _under_plan_key)
            if found:
                return found
        if _under_plan_key:  # a plan container shaped like {"steps": [...]}
            for inner_key in ("steps", "plan", "plan_steps", "subgoals"):
                inner = node.get(inner_key)
                if isinstance(inner, list) and inner:
                    return inner
    elif isinstance(node, list):
        if _under_plan_key and node:
            return node
        for item in node:
            found = _find_plan_steps(item, _under_plan_key)
            if found:
                return found
    return None


def _step_text(step) -> str:
    """Flatten one plan step (str | dict | list) to a lowercase string for matching."""
    return str(step).lower()


def _any_term(haystack: str, terms) -> bool:
    return any(t in haystack for t in terms)


# ─────────────────────────────────────────────────────────────────────────────
# TURN 1 — SET KNOWLEDGE
# ─────────────────────────────────────────────────────────────────────────────
def test_1_set_knowledge():
    """The coffee-shop fact must be committed to memory before the goal is posed."""
    resp = _ask(TURN1_KNOWLEDGE)

    assert resp.answer.strip() == COMMIT_MESSAGE, (
        f"Expected the commitment message {COMMIT_MESSAGE!r}, got {resp.answer!r}. "
        "The Knowledge-Acquisition layer did not intercept the declarative statement."
    )
    assert resp.confidence == "CERTAIN", (
        f"Commit should be CERTAIN, got confidence={resp.confidence!r}"
    )
    debug = resp.debug or {}
    assert debug.get("knowledge_acquisition") is True, (
        "debug.knowledge_acquisition flag missing — extraction did not run."
    )
    learned = debug.get("learned_triples") or []
    flat = " ".join(str(part) for triple in learned for part in triple).lower()
    assert SHOP_VALUE.lower() in flat, (
        f"The shop {SHOP_VALUE!r} was not captured in any learned triple: {learned!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 2 — THE MULTI-HOP GOAL  (Phase 57 contract)
# ─────────────────────────────────────────────────────────────────────────────
def test_2_multi_hop_plan_generated():
    """
    The population question must yield an explicit, multi-step plan in debug:
    step 1 = internal KG lookup of the favorite shop / its city, step 2 = external
    tool call for that city's population.
    """
    _commit, resp = _run(
        _teach_wait_then_goal(
            TURN1_KNOWLEDGE, TURN2_MULTI_HOP_GOAL, CONSOLIDATION_WAIT_SECONDS
        )
    )
    debug = resp.debug or {}

    # (a) A plan must exist at all.
    steps = _find_plan_steps(debug)
    assert steps is not None, (
        "No agentic plan found: the debug/metadata payload contains no list under any "
        f"plan key {sorted(PLAN_KEYS)}. The pipeline answered the multi-hop goal in a "
        f"single reactive pass. debug keys={list(debug.keys())!r}"
    )

    # (b) It must be genuinely multi-step.
    assert len(steps) >= MIN_PLAN_STEPS, (
        f"Plan is not multi-hop: found {len(steps)} step(s), need >= {MIN_PLAN_STEPS}. "
        f"A single-step plan cannot decompose this goal. steps={steps!r}"
    )

    plan_text = " || ".join(_step_text(s) for s in steps)

    # (c) STEP 1 — an internal Knowledge-Graph lookup of the favorite coffee shop.
    has_kg_lookup = _any_term(plan_text, KG_LOOKUP_TERMS) and _any_term(plan_text, SHOP_TERMS)
    assert has_kg_lookup, (
        "Plan is missing the internal Knowledge-Graph lookup step (expected: query the "
        "KG for the favorite coffee shop / its city, e.g. Third Wave Coffee -> Bengaluru). "
        f"No step combined a KG/memory term with a coffee-shop term. plan={plan_text!r}"
    )

    # (d) STEP 2 — an external tool call to find the city's population.
    has_external_population = (
        _any_term(plan_text, EXTERNAL_TOOL_TERMS) and _any_term(plan_text, POPULATION_TERMS)
    )
    assert has_external_population, (
        "Plan is missing the external-tool step (expected: use Web Search / Retrieval "
        "Mesh to find the population of the resolved city). No step combined an "
        f"external-tool term with 'population'. plan={plan_text!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner — prints a falsifiable PASS/FAIL report and sets exit code.
# ─────────────────────────────────────────────────────────────────────────────
def _main() -> int:
    tests = [
        ("TURN 1 - SET KNOWLEDGE (commit shop)", test_1_set_knowledge),
        ("TURN 2 - MULTI-HOP PLAN (KG lookup -> external population)", test_2_multi_hop_plan_generated),
    ]
    print("=" * 72)
    print("VELYNX Falsifiable Cognitive Test Suite (Phase 57 — Agency & Planning)")
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
        print("Agentic planning NOT present — Phase 57 is not 'done'.")
    else:
        print("Multi-step plan generated for a multi-hop goal. Phase 57 'Done When' satisfied.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
