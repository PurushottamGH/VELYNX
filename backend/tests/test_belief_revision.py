"""
Falsifiable Cognitive Test Suite — Phase 56 (Belief Revision)
============================================================

Phase 56 teaches VELYNX to UPDATE a belief when a newer fact contradicts an older
one, instead of blindly keeping both. The canonical case: a user states a favorite
color, then changes their mind. A system without belief revision simply appends the
second triple, leaving two contradictory facts in the Knowledge Graph; on recall it
then returns the stale value, or worse, "blue and red". Revision detects the
conflict on the shared (subject, relation) and supersedes the old object with the
new one.

As with the Phase 53/54/55 suites, we drive the EXACT backend entry point the CLI
and the FastAPI ``/query`` route both call — ``app.pipeline.answer_question`` (an
async coroutine) — so the test is immune to terminal rendering and route plumbing.

  TURN 1 — SET BELIEF
      Feed "My favorite color is blue." and assert it is committed to memory.

  TURN 2 — REVISE BELIEF
      Feed "Actually, my favorite color is red." and assert it is committed too.

  TURN 3 — VERIFY REVISION  (the Phase 56 contract)
      Ask "What is my favorite color?" and assert the answer is RED, sourced from
      the Knowledge Graph. It must NOT be "blue", and must NOT contain BOTH colors
      (no "blue and red"). The old belief must have been superseded, not retained.

Falsifiability
--------------
Every assertion is concrete and can FAIL. Today ``fact_extractor._store_triples``
does a blind INSERT with no conflict handling, so both triples coexist — TURN 3 is
EXPECTED to fail (returning the stale "blue" and/or both colors). That failure is
the signal belief revision does not yet exist. A green run is the definition of
"done".

Run it either way:

    pytest backend/tests/test_belief_revision.py -v
    python  backend/tests/test_belief_revision.py     # standalone PASS/FAIL report
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Windows consoles default to cp1252; pipeline answers contain Unicode (em-dash,
# etc.). Force UTF-8 with a safe fallback so printing a failure report can never
# itself crash the suite.
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

from app.pipeline import answer_question  # noqa: E402


# ── Test fixtures / constants ─────────────────────────────────────────────────
# A unique session keeps conversation-buffer state from other suites from bleeding
# into this run.
SESSION_ID = "belief-revision-suite"

# The OLD belief (set first) ...
TURN1_OLD_BELIEF = "My favorite color is blue."
OLD_VALUE = "blue"

# ... the NEW belief that must SUPERSEDE it.
TURN2_NEW_BELIEF = "Actually, my favorite color is red."
NEW_VALUE = "red"

# The recall question.
TURN3_QUESTION = "What is my favorite color?"

# The deterministic acknowledgement emitted by the Knowledge-Acquisition layer
# (backend/app/pipeline.py) when a declarative statement is extracted into triples.
COMMIT_MESSAGE = "I have committed that to memory."

# Phase 53.1 consolidation (embedding facts + writing vectors to the store and the
# Reasoning Graph) runs on a BACKGROUND thread. The recall must wait for it to
# finish, otherwise the read races the writer. 4s covers cold model load + embed +
# write locally. (Mirrors test_cognition.py.)
CONSOLIDATION_WAIT_SECONDS = 4

# Provenance markers proving an answer came from the graph / knowledge store and
# not from free-form generation. Graph-sourced citations carry the literal "[KG]"
# prefix; the KG fast-path stamps debug with ``kg_hit``.
GRAPH_PROVENANCE_CITATION_MARK = "[KG]"
GRAPH_DEBUG_KEYS = ("kg_hit", "reasoning_trace", "knowledge_acquisition")

# Confidence labels that legitimately indicate a graph/knowledge-backed answer.
GRAPH_CONFIDENCE_LABELS = {"CERTAIN", "PROBABLE", "DEBATED", "LOW"}


def _run(coro):
    """Drive an async pipeline call to completion from sync test context."""
    return asyncio.run(coro)


def _ask(text: str):
    """Hit the real backend entry point and return the AnswerResponse."""
    return _run(answer_question(text, session_id=SESSION_ID))


async def _set_revise_then_recall(old: str, new: str, question: str, wait_s: float):
    """
    Set a belief, revise it, wait for the consolidation background thread, then
    recall — all inside ONE event loop so ``await asyncio.sleep`` cooperates with
    the async pipeline and both writes land before the read.
    """
    commit_old = await answer_question(old, session_id=SESSION_ID)
    commit_new = await answer_question(new, session_id=SESSION_ID)
    await asyncio.sleep(wait_s)  # let consolidator.py embed + persist both turns
    recall = await answer_question(question, session_id=SESSION_ID)
    return commit_old, commit_new, recall


def _assert_committed(resp, label: str) -> None:
    """Shared assertion: a declarative statement was committed to memory."""
    assert resp.answer.strip() == COMMIT_MESSAGE, (
        f"{label}: expected the commitment message {COMMIT_MESSAGE!r}, got "
        f"{resp.answer!r}. The Knowledge-Acquisition layer did not intercept the "
        "declarative statement."
    )
    assert resp.confidence == "CERTAIN", (
        f"{label}: commit should be CERTAIN, got confidence={resp.confidence!r}"
    )
    debug = resp.debug or {}
    assert debug.get("knowledge_acquisition") is True, (
        f"{label}: debug.knowledge_acquisition flag missing — extraction did not run."
    )
    learned = debug.get("learned_triples") or []
    assert learned, f"{label}: no triples learned — nothing was persisted."


def _has_graph_provenance(resp) -> bool:
    """True iff the response is provably sourced from the graph/knowledge store."""
    citations = getattr(resp, "citations", None) or []
    if any(GRAPH_PROVENANCE_CITATION_MARK in str(c) for c in citations):
        return True
    debug = getattr(resp, "debug", None) or {}
    if isinstance(debug, dict) and any(k in debug for k in GRAPH_DEBUG_KEYS):
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# TURN 1 — SET BELIEF
# ─────────────────────────────────────────────────────────────────────────────
def test_1_set_belief():
    """'My favorite color is blue.' must be committed to memory."""
    resp = _ask(TURN1_OLD_BELIEF)
    _assert_committed(resp, "TURN 1 (set belief)")
    flat = " ".join(
        str(part) for triple in (resp.debug or {}).get("learned_triples", []) for part in triple
    ).lower()
    assert OLD_VALUE in flat, (
        f"TURN 1: the value {OLD_VALUE!r} was not captured in any learned triple: "
        f"{(resp.debug or {}).get('learned_triples')!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 2 — REVISE BELIEF
# ─────────────────────────────────────────────────────────────────────────────
def test_2_revise_belief():
    """'Actually, my favorite color is red.' must also be committed to memory."""
    # Re-establish the prior belief in this session, then revise it.
    _ask(TURN1_OLD_BELIEF)
    resp = _ask(TURN2_NEW_BELIEF)
    _assert_committed(resp, "TURN 2 (revise belief)")
    flat = " ".join(
        str(part) for triple in (resp.debug or {}).get("learned_triples", []) for part in triple
    ).lower()
    assert NEW_VALUE in flat, (
        f"TURN 2: the revised value {NEW_VALUE!r} was not captured in any learned "
        f"triple: {(resp.debug or {}).get('learned_triples')!r}. The 'Actually, ...' "
        "phrasing may not be parsed by the extractor."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TURN 3 — VERIFY REVISION  (Phase 56 contract)
# ─────────────────────────────────────────────────────────────────────────────
def test_3_verify_revision():
    """
    After set+revise, recall must return the NEW belief (red), graph-sourced, and
    must NOT return the OLD belief (blue) or BOTH.
    """
    _old, _new, resp = _run(
        _set_revise_then_recall(
            TURN1_OLD_BELIEF, TURN2_NEW_BELIEF, TURN3_QUESTION, CONSOLIDATION_WAIT_SECONDS
        )
    )
    answer_lc = resp.answer.lower()

    # (a) The answer MUST contain the revised value.
    assert NEW_VALUE in answer_lc, (
        f"Belief revision failed: expected the revised value {NEW_VALUE!r} in the "
        f"answer, got {resp.answer!r}. The new belief did not win recall."
    )

    # (b) The answer MUST NOT contain the superseded value. This single assertion
    #     covers both failure modes the spec calls out: answering the stale "blue",
    #     AND answering "blue and red" (which retains the contradiction).
    assert OLD_VALUE not in answer_lc, (
        f"Belief revision failed: the superseded value {OLD_VALUE!r} still appears in "
        f"the answer {resp.answer!r}. The old triple was not retracted — the KG kept "
        "both contradictory beliefs ('blue and red') or returned the stale one."
    )

    # (c) The answer must cite the Knowledge Graph — proving genuine recall of the
    #     stored, revised fact rather than an ungrounded guess that happens to say
    #     'red'.
    assert _has_graph_provenance(resp), (
        "Recall lacks graph provenance: no [KG] citation and no kg/reasoning debug "
        f"marker. citations={resp.citations!r} "
        f"debug_keys={list((resp.debug or {}).keys())!r}. The 'red' may be ungrounded."
    )

    # (d) Confidence must be a real graph-backed grade.
    assert resp.confidence in GRAPH_CONFIDENCE_LABELS, (
        f"Unexpected confidence label for a recalled fact: {resp.confidence!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner — prints a falsifiable PASS/FAIL report and sets exit code.
# ─────────────────────────────────────────────────────────────────────────────
def _main() -> int:
    tests = [
        ("TURN 1 - SET BELIEF (blue)", test_1_set_belief),
        ("TURN 2 - REVISE BELIEF (red)", test_2_revise_belief),
        ("TURN 3 - VERIFY REVISION (red, not blue, not both)", test_3_verify_revision),
    ]
    print("=" * 72)
    print("VELYNX Falsifiable Cognitive Test Suite (Phase 56 — Belief Revision)")
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
        print("Belief revision NOT working — Phase 56 is not 'done'.")
    else:
        print("Contradiction detected and old belief superseded. Phase 56 'Done When' satisfied.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
