"""
Falsifiable Cognitive Test Suite — Phase 58 (Symbolic Dynamic Agency)
=====================================================================

Phase 57 proved VELYNX can emit an explicit multi-step PLAN for a multi-hop goal.
But that planner was a *fixed* heuristic: it hardcoded the domain ("coffee shop"),
the resolved entities ("Third Wave -> Bengaluru"), and a closed list of attributes
("population", "area", ...). It could only ever decompose the ONE goal it was
written for.

Phase 58 raises the bar to genuine **dynamic agency**: given a goal it has NEVER
seen — in a domain with NO hardcoded vocabulary — the system must construct the
plan *purely from the grammar of the query*. No LLM. No keyword tables. The plan's
targets must be the noun chunks the query's own dependency structure yields.

The canonical Phase 58 case is a NOVEL multi-hop goal in a fresh domain:

    TURN 1 — SET KNOWLEDGE
        "My favorite 3D software is Blender."     (assert it commits)

    TURN 2 — THE NOVEL MULTI-HOP GOAL
        "What year was the original creator of my favorite 3D software born?"

This is unanswerable in a single retrieval. A grammar-driven planner must:

    Step 1 — resolve the DEEPEST noun chunk, the innermost referent the rest of
             the sentence hangs off of:   "favorite 3D software"
    Step 2 — resolve the PARENT chunk that depends on step 1's result:
             "original creator"           (then its birth year)

The contract is the *plan*, surfaced in the ``debug`` payload — exactly as in the
Phase 57 suite, and driven through the same real backend entry point
``app.pipeline.answer_question`` (the coroutine the CLI and the FastAPI ``/query``
route both call), so the test is immune to terminal rendering and route plumbing.

The decisive assertion — what makes this a Phase 58 test and not a Phase 57 one —
is NEGATIVE:

    The plan MUST NOT contain "coffee", "population", "Blender", or "Ton".

    * "coffee" / "population"  — proves the plan is not the hardcoded Phase 57
      template firing on a new query.
    * "Blender" / "Ton"        — proves the plan is built from the query's GRAMMAR,
      not from the *resolved answer* (Blender's creator is Ton Roosendaal). A plan
      that already names the answer it is supposed to go and find has not planned;
      it has cheated.

Falsifiability
--------------
Every assertion is concrete and CAN fail. Today the Phase 57 gate
(``agentic_controller.should_plan``) does not even fire for this query (no
"where/located" nesting clause), so TURN 2 is EXPECTED to fail with *no plan at
all*. Were that gate widened to fire, the Phase 57 ``formulate_plan`` would emit
a "coffee"/"population"/"Third Wave" plan — which this suite REJECTS by name. The
only way to go green is to build a real grammar-driven planner. A green run is the
definition of "Phase 58 done".

Run it either way:

    pytest backend/tests/test_dynamic_agency.py -v
    python  backend/tests/test_dynamic_agency.py     # standalone PASS/FAIL report
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Windows consoles default to cp1252; pipeline answers/plans contain Unicode
# (em-dash, etc.). Force UTF-8 with a safe fallback so printing a failure report
# can never itself crash the suite. (Same handling as the other cognitive suites.)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

# ── Path bootstrap ───────────────────────────────────────────────────────────
# The pipeline mixes bare imports (``from app.pipeline import ...``) with absolute
# package imports (``from backend.memory._sqlite import ...``), so BOTH the
# ``backend/`` directory and the repo root must be importable. Same convention as
# test_agency.py / test_cognition.py.
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[1]          # .../VELYNX/backend
_REPO_ROOT = _HERE.parents[2]            # .../VELYNX
for _p in (str(_BACKEND_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest  # noqa: E402

from app.pipeline import answer_question  # noqa: E402


# ── Test fixtures / constants ─────────────────────────────────────────────────
SESSION_ID = "dynamic-agency-suite"

# TURN 1 plants the only fact the system natively holds — in a domain the Phase 57
# planner knows NOTHING about (no "3D software" / "Blender" in its vocabulary).
TURN1_KNOWLEDGE = "My favorite 3D software is Blender."
SOFTWARE_VALUE = "Blender"

# TURN 2 is the NOVEL multi-hop goal — unanswerable in a single retrieval, and in
# a domain with zero hardcoded support.
TURN2_MULTI_HOP_GOAL = (
    "What year was the original creator of my favorite 3D software born?"
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

# ── The grammar the plan MUST be built from ───────────────────────────────────
# Step 1 must target the DEEPEST noun chunk — the innermost referent the sentence
# defers to. Step 2 must target its PARENT chunk. These are the chunks a
# dependency parse of TURN 2 yields; the planner must derive them, not us.
DEEPEST_CHUNK_TOKENS = ("favorite", "3d software")   # "favorite 3D software"
PARENT_CHUNK_TOKENS = ("original", "creator")        # "original creator"

# ── The decisive NEGATIVE contract ────────────────────────────────────────────
# A grammar-driven plan for THIS query can contain none of these:
#   * "coffee"/"population" — the Phase 57 hardcoded template's fingerprints.
#   * "blender"/"ton"       — the RESOLVED answer (Blender, by Ton Roosendaal).
#                             A plan that already names what it is sent to find has
#                             not planned from grammar; it has leaked the answer.
FORBIDDEN_PLAN_STRINGS = ("coffee", "population", "blender", "ton")


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


# Fields that hold EXECUTION artifacts (what a step resolved), not the plan's
# grammar-derived formulation. We strip these before checking the plan's text so
# the negative assertion tests the PLAN, not the answer it later fetched. (A plan
# is "based on the query's grammar, not resolved answers" — so resolved answers
# must not be what we measure the plan by.)
_RESULT_FIELDS = {"result", "results", "output", "answer", "snippet", "evidence",
                  "web_result", "city", "value", "resolved"}


def _step_formulation_text(step) -> str:
    """
    Flatten ONE plan step to its grammar-derived text (description + params +
    action), deliberately EXCLUDING any resolved-result fields, lowercased for
    matching. Accepts a str, dict, or nested structure.
    """
    if isinstance(step, dict):
        kept = {k: v for k, v in step.items() if str(k).lower() not in _RESULT_FIELDS}
        return json.dumps(kept, ensure_ascii=False, default=str).lower()
    return str(step).lower()


def _all_tokens(haystack: str, tokens) -> bool:
    return all(t in haystack for t in tokens)


# ─────────────────────────────────────────────────────────────────────────────
# TURN 1 — SET KNOWLEDGE
# ─────────────────────────────────────────────────────────────────────────────
def test_1_set_knowledge():
    """The 3D-software fact must be committed to memory before the goal is posed."""
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
    assert SOFTWARE_VALUE.lower() in flat, (
        f"The value {SOFTWARE_VALUE!r} was not captured in any learned triple: {learned!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 2 — THE NOVEL MULTI-HOP GOAL  (Phase 58 contract)
# ─────────────────────────────────────────────────────────────────────────────
def test_2_dynamic_plan_from_grammar():
    """
    The novel goal must yield a dynamically generated, multi-step plan whose
    targets are the query's own noun chunks:

      step 1 -> the DEEPEST chunk  "favorite 3D software"
      step 2 -> the PARENT chunk   "original creator"

    and which contains NONE of the hardcoded-template or resolved-answer strings.
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
        f"plan key {sorted(PLAN_KEYS)}. The pipeline answered the novel multi-hop goal "
        f"in a single reactive pass (or its planner gate never fired). "
        f"debug keys={list(debug.keys())!r}"
    )

    # (b) It must be genuinely multi-step.
    assert len(steps) >= MIN_PLAN_STEPS, (
        f"Plan is not multi-hop: found {len(steps)} step(s), need >= {MIN_PLAN_STEPS}. "
        f"A single-step plan cannot decompose this goal. steps={steps!r}"
    )

    # Grammar-derived text of each step (excludes resolved-result fields) and of
    # the whole plan (used for the negative assertion).
    step_texts = [_step_formulation_text(s) for s in steps]
    plan_text = " || ".join(step_texts)

    # (c) STEP 1 — must target the DEEPEST noun chunk: "favorite 3D software".
    has_deepest = any(_all_tokens(t, DEEPEST_CHUNK_TOKENS) for t in step_texts)
    assert has_deepest, (
        "Plan step 1 does not target the deepest noun chunk 'favorite 3D software'. "
        "A grammar-driven planner must resolve the innermost referent first. "
        f"No single step contained all of {DEEPEST_CHUNK_TOKENS}. plan={plan_text!r}"
    )

    # (d) STEP 2 — must target the PARENT chunk: "original creator".
    has_parent = any(_all_tokens(t, PARENT_CHUNK_TOKENS) for t in step_texts)
    assert has_parent, (
        "Plan step 2 does not target the parent noun chunk 'original creator'. "
        "A grammar-driven planner must derive the dependent outer chunk. "
        f"No single step contained all of {PARENT_CHUNK_TOKENS}. plan={plan_text!r}"
    )

    # (e) THE DECISIVE NEGATIVE CONTRACT — pure grammar, no hardcoding, no leaked
    #     answer. The plan must name none of these.
    leaked = sorted({s for s in FORBIDDEN_PLAN_STRINGS if s in plan_text})
    assert not leaked, (
        f"Plan is contaminated with forbidden string(s) {leaked}. "
        "'coffee'/'population' mean the Phase 57 hardcoded template fired instead of "
        "grammar-driven planning; 'blender'/'ton' mean the plan leaked the RESOLVED "
        "answer (Blender, created by Ton Roosendaal) rather than planning from the "
        f"query's grammar. plan={plan_text!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner — prints a falsifiable PASS/FAIL report and sets exit code.
# ─────────────────────────────────────────────────────────────────────────────
def _main() -> int:
    tests = [
        ("TURN 1 - SET KNOWLEDGE (commit 3D software)", test_1_set_knowledge),
        ("TURN 2 - DYNAMIC PLAN FROM GRAMMAR (deepest chunk -> parent chunk, no leakage)",
         test_2_dynamic_plan_from_grammar),
    ]
    print("=" * 72)
    print("VELYNX Falsifiable Cognitive Test Suite (Phase 58 — Symbolic Dynamic Agency)")
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
        print("Dynamic grammar-driven planning NOT present — Phase 58 is not 'done'.")
    else:
        print("Dynamic plan generated purely from query grammar. Phase 58 'Done When' satisfied.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
