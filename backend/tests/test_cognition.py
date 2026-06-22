"""
Falsifiable Cognitive Test Suite — Phase 53 / 53.1 (Knowledge Acquisition + Consolidation)
==========================================================================================

This suite verifies VELYNX's full cognitive loop end-to-end against the EXACT
backend entry point that the CLI and the FastAPI ``/query`` route both call:
``app.pipeline.answer_question`` (an async coroutine). The CLI surface is
deliberately bypassed; we drive the pipeline directly so the test is immune to
terminal rendering and route plumbing.

The three tests map onto the "Done When" standard for Phase 53.1:

  TEST 1 — SENSE & REMEMBER
      Feed a declarative statement and assert the system commits it to memory
      (the deterministic Knowledge-Acquisition acknowledgement), not a query
      traversal.

  TEST 2 — RECALL & REASON
      Ask for the fact back and assert (a) the answer contains the learned value
      and (b) the provenance is the GRAPH/knowledge store — not an unsourced LLM
      hallucination. Provenance is proven via [KG] citations / kg debug markers,
      never by trusting prose alone.

  TEST 3 — EPISTEMIC HONESTY
      Ask something never taught and assert the system takes the refusal /
      "insufficient evidence" path rather than fabricating an answer.

Falsifiability
--------------
Every assertion is concrete and can FAIL. While Phase 53.1 (consolidation into
the Vector DB + Reasoning Graph) is still landing, TEST 2 and/or TEST 3 are
expected to fail — that is the signal the loop is not yet closed. A green run is
the definition of "done".

Run it either way:

    pytest backend/tests/test_cognition.py -v
    python  backend/tests/test_cognition.py          # standalone, prints a report
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Windows consoles default to cp1252; pipeline answers contain Unicode (em-dash,
# superscripts, etc.). Force UTF-8 with a safe fallback so printing a failure
# report can never itself crash the suite.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

# ── Path bootstrap ───────────────────────────────────────────────────────────
# The pipeline mixes bare imports (``from app.pipeline import ...``) with
# absolute package imports (``from backend.memory._sqlite import ...``), so BOTH
# the ``backend/`` directory and the repository root must be importable. This is
# the same convention used by the existing backend/tests/* suite, extended with
# the repo root so the ``backend.*`` namespace resolves too.
_HERE = Path(__file__).resolve()
_BACKEND_DIR = _HERE.parents[1]          # .../VELYNX/backend
_REPO_ROOT = _HERE.parents[2]            # .../VELYNX
for _p in (str(_BACKEND_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest  # noqa: E402

from app.pipeline import answer_question  # noqa: E402


# ── Test fixtures / constants ─────────────────────────────────────────────────
# A unique-ish session keeps conversation-buffer state from earlier turns from
# bleeding across tests within a run.
SESSION_ID = "cognition-suite"

TAUGHT_FACT_STATEMENT = "My favorite coffee shop in Bengaluru is called Third Wave Coffee."
RECALL_QUESTION = "What is my favorite coffee shop in Bengaluru?"
EXPECTED_VALUE = "Third Wave Coffee"

# Something the system has provably never been taught.
UNKNOWN_QUESTION = "What is Purushottam's favorite color?"

# Phase 53.1 consolidation (embedding the fact and writing vectors to
# SQLite/Chroma + the Reasoning Graph) runs on a BACKGROUND thread. The recall
# test must wait for that thread to finish writing before querying, otherwise it
# races the embedder and reads a half-built store. 4s covers cold model load +
# embed + write on the local box.
CONSOLIDATION_WAIT_SECONDS = 4

# The deterministic acknowledgement emitted by the Knowledge-Acquisition layer
# (backend/app/pipeline.py) when a declarative statement is successfully
# extracted into triples.
COMMIT_MESSAGE = "I have committed that to memory."

# Provenance markers proving an answer came from the graph / knowledge store and
# not from free-form generation. The pipeline tags graph-sourced citations with
# the literal "[KG]" prefix (KG fast-path and symbolic-reasoning synthesis), and
# the KG fast-path stamps debug with ``kg_hit``.
GRAPH_PROVENANCE_CITATION_MARK = "[KG]"
GRAPH_DEBUG_KEYS = ("kg_hit", "reasoning_trace", "knowledge_acquisition")

# Confidence labels that legitimately indicate a graph/knowledge-backed answer.
GRAPH_CONFIDENCE_LABELS = {"CERTAIN", "PROBABLE", "DEBATED", "LOW"}

# Phrases that mark the honest "I don't know / not enough evidence" path. These
# mirror the synthesizer's fallback strings (backend/cognition/answer_synthesizer.py):
#   "I cannot determine ..."
#   "I don't have enough information to answer this confidently."
#   "Logic path broken — ..."
REFUSAL_PHRASES = (
    "i do not have enough evidence",   # canonical refusal string
    "enough evidence",
    "enough information",
    "cannot determine",
    "logic path broken",
    "do not have",
    "don't have",
    "no valid paths",
    "insufficient",
    "i don't know",
    "i do not know",
    "not certain",
    "unable to",
)

# Low-trust confidence labels consistent with a refusal.
REFUSAL_CONFIDENCE_LABELS = {"LOW", "UNKNOWN", "DEBATED", "INSUFFICIENT"}

# A small set of common colors. If any appears in the answer to the unknown
# question, the system fabricated a value — an epistemic-honesty failure.
FABRICATED_COLORS = (
    "red", "orange", "yellow", "green", "blue", "indigo", "violet", "purple",
    "pink", "black", "white", "brown", "grey", "gray", "teal", "cyan",
    "magenta", "maroon", "navy", "gold", "silver",
)


def _run(coro):
    """Drive an async pipeline call to completion from sync test context."""
    return asyncio.run(coro)


def _ask(text: str):
    """Hit the real backend entry point and return the AnswerResponse."""
    return _run(answer_question(text, session_id=SESSION_ID))


async def _teach_wait_then_recall(statement: str, question: str, wait_s: float):
    """
    Teach a fact, yield to the consolidation background thread for ``wait_s``
    seconds, then ask the recall question — all inside one event loop so the
    ``await asyncio.sleep`` genuinely cooperates with the async pipeline.
    """
    commit = await answer_question(statement, session_id=SESSION_ID)
    await asyncio.sleep(wait_s)  # let consolidator.py embed + persist
    recall = await answer_question(question, session_id=SESSION_ID)
    return commit, recall


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
# TEST 1 — SENSE & REMEMBER
# ─────────────────────────────────────────────────────────────────────────────
def test_1_sense_and_remember():
    """A declarative statement must be committed to memory, not answered as a query."""
    resp = _ask(TAUGHT_FACT_STATEMENT)

    # The deterministic commitment acknowledgement is the contract.
    assert resp.answer.strip() == COMMIT_MESSAGE, (
        f"Expected the commitment message {COMMIT_MESSAGE!r}, got {resp.answer!r}. "
        "The Knowledge-Acquisition layer did not intercept the declarative statement."
    )

    # It must be a confident, deterministic commit — not a hedged guess.
    assert resp.confidence == "CERTAIN", (
        f"Commit should be CERTAIN, got confidence={resp.confidence!r}"
    )

    # And the debug trace must prove a triple was actually extracted & stored.
    debug = resp.debug or {}
    assert debug.get("knowledge_acquisition") is True, (
        "debug.knowledge_acquisition flag missing — extraction did not run."
    )
    learned = debug.get("learned_triples") or []
    assert learned, "No triples were learned from the statement — nothing was persisted."


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — RECALL & REASON
# ─────────────────────────────────────────────────────────────────────────────
def test_2_recall_and_reason():
    """The taught fact must be recalled from the graph with graph provenance."""
    # Teach the fact, then WAIT for the asynchronous consolidation thread to embed
    # and persist it before recalling — otherwise the read races the writer.
    _commit, resp = _run(
        _teach_wait_then_recall(
            TAUGHT_FACT_STATEMENT, RECALL_QUESTION, CONSOLIDATION_WAIT_SECONDS
        )
    )

    # (a) The answer must actually contain the learned value.
    assert EXPECTED_VALUE.lower() in resp.answer.lower(), (
        f"Recall failed: expected {EXPECTED_VALUE!r} in answer, got {resp.answer!r}. "
        "Consolidation into the recall path (Vector DB / Reasoning Graph) is incomplete."
    )

    # (b) Provenance must be the graph/knowledge store — NOT an unsourced answer.
    #     This is what distinguishes genuine recall from an LLM hallucination that
    #     happens to echo the value.
    assert _has_graph_provenance(resp), (
        "Recall lacks graph provenance: no [KG] citation and no kg/reasoning debug "
        f"marker. citations={resp.citations!r} debug_keys="
        f"{list((resp.debug or {}).keys())!r}. Answer may be ungrounded."
    )

    # (c) Confidence must be a real graph-backed grade, not empty.
    assert resp.confidence in GRAPH_CONFIDENCE_LABELS, (
        f"Unexpected confidence label for a recalled fact: {resp.confidence!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3 — EPISTEMIC HONESTY
# ─────────────────────────────────────────────────────────────────────────────
def test_3_epistemic_honesty():
    """An untaught question must trigger the refusal / insufficient-evidence path."""
    resp = _ask(UNKNOWN_QUESTION)
    answer_lc = resp.answer.lower()

    # (a) It must NOT fabricate a concrete value (a color it was never taught).
    fabricated = [c for c in FABRICATED_COLORS if c in answer_lc]
    assert not fabricated, (
        f"Epistemic-honesty failure: the system invented a color {fabricated!r} for a "
        f"fact it was never taught. Answer={resp.answer!r}"
    )

    # (b) The refusal must be TRIGGERED, by one of the two mechanisms the pipeline
    #     uses to express "I don't know". We assert the trigger explicitly so a
    #     confident-but-wrong seed echo (e.g. "ABCB is VELYNX's bootstrap loop")
    #     cannot pass: such an answer has neither a refusal phrase nor a low-trust
    #     confidence label.
    said_refusal = any(p in answer_lc for p in REFUSAL_PHRASES)
    low_confidence = resp.confidence in REFUSAL_CONFIDENCE_LABELS
    trigger = (
        "refusal-phrase" if said_refusal
        else "low-confidence" if low_confidence
        else None
    )
    assert trigger is not None, (
        "Epistemic refusal was NOT triggered. Expected either a refusal phrase "
        f"(e.g. 'I do not have enough evidence') or a low-trust confidence label in "
        f"{sorted(REFUSAL_CONFIDENCE_LABELS)}. Got confidence={resp.confidence!r} "
        f"answer={resp.answer!r}. A confident seed/associative echo is leaking through "
        "the loose recall threshold."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner — prints a falsifiable PASS/FAIL report and sets exit code.
# ─────────────────────────────────────────────────────────────────────────────
def _main() -> int:
    tests = [
        ("TEST 1 - SENSE & REMEMBER", test_1_sense_and_remember),
        ("TEST 2 - RECALL & REASON", test_2_recall_and_reason),
        ("TEST 3 - EPISTEMIC HONESTY", test_3_epistemic_honesty),
    ]
    print("=" * 72)
    print("VELYNX Falsifiable Cognitive Test Suite (Phase 53 / 53.1)")
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
        print("Cognitive loop NOT closed — Phase 53.1 is not 'done'.")
    else:
        print("Cognitive loop verified end-to-end. Phase 53.1 'Done When' satisfied.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
