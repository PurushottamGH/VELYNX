"""
Falsifiable Cognitive Test Suite — Phase 54 (Semantic Grounding / Canonical Entity Resolution)
==============================================================================================

Phase 54 teaches VELYNX that different surface strings can denote the SAME
real-world entity — most concretely that "Bangalore" and "Bengaluru" are the
same city. A system without semantic grounding stores "Bengaluru" as an opaque
token; when later asked about "Bangalore" it sees an unknown string, fails to
link it to the stored fact, and either refuses or fabricates. Grounding closes
that gap by resolving both surface forms to one canonical entity.

This suite drives the EXACT backend entry point the CLI and the FastAPI
``/query`` route both call — ``app.pipeline.answer_question`` (an async
coroutine) — bypassing the terminal surface so the test is immune to rendering
and route plumbing. It mirrors the setup of ``backend/tests/test_cognition.py``.

  TEST 1 — SENSE & REMEMBER
      Feed "The creator of VELYNX lives in Bengaluru." and assert the system
      commits it to memory (the deterministic Knowledge-Acquisition
      acknowledgement) rather than answering it as a query.

  TEST 2 — CANONICAL RECALL (the Phase 54 contract)
      Ask "Does the creator of VELYNX live in Bangalore?" — using the OTHER
      surface form. Assert the system answers AFFIRMATIVELY and grounds the
      answer in the stored "Bengaluru" fact (graph provenance), proving it
      resolved "Bangalore" -> "Bengaluru" as one canonical entity.

Falsifiability
--------------
Every assertion is concrete and can FAIL. Until Phase 54 (entity grounding /
alias resolution) is implemented, TEST 2 is EXPECTED to fail — that failure is
the signal the feature does not yet exist. A green run is the definition of
"done".

Run it either way:

    pytest backend/tests/test_semantic_grounding.py -v
    python  backend/tests/test_semantic_grounding.py     # standalone PASS/FAIL report
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
# the ``backend/`` directory and the repository root must be importable. Same
# convention as the existing backend/tests/* suite.
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
SESSION_ID = "semantic-grounding-suite"

# The fact is TAUGHT with one surface form ("Bengaluru") ...
TAUGHT_FACT_STATEMENT = "The creator of VELYNX lives in Bengaluru."
CANONICAL_CITY = "Bengaluru"

# ... and RECALLED with the OTHER surface form ("Bangalore"). The whole point of
# Phase 54 is that these two strings resolve to the same canonical entity.
RECALL_QUESTION = "Does the creator of VELYNX live in Bangalore?"
ALIAS_CITY = "Bangalore"

# The deterministic acknowledgement emitted by the Knowledge-Acquisition layer
# (backend/app/pipeline.py) when a declarative statement is successfully
# extracted into triples.
COMMIT_MESSAGE = "I have committed that to memory."

# Phase 53.1 consolidation (embedding the fact + writing vectors to the store and
# the Reasoning Graph) runs on a BACKGROUND thread. The recall test must wait for
# that thread to finish before querying, otherwise it races the embedder and
# reads a half-built store. 4s covers cold model load + embed + write locally.
CONSOLIDATION_WAIT_SECONDS = 4

# Provenance markers proving an answer came from the graph / knowledge store and
# not from free-form generation. Graph-sourced citations carry the literal
# "[KG]" prefix; the KG fast-path stamps debug with ``kg_hit``.
GRAPH_PROVENANCE_CITATION_MARK = "[KG]"
GRAPH_DEBUG_KEYS = ("kg_hit", "reasoning_trace", "knowledge_acquisition")

# Confidence labels that legitimately indicate a graph/knowledge-backed answer.
GRAPH_CONFIDENCE_LABELS = {"CERTAIN", "PROBABLE", "DEBATED", "LOW"}

# Affirmative markers: phrases proving the system CONFIRMED the proposition
# rather than denying it or dodging. Mentioning the canonical city ("bengaluru")
# in answer to a "Bangalore" question is itself strong affirmative grounding.
AFFIRMATIVE_MARKERS = (
    "yes",
    "correct",
    "indeed",
    "that is right",
    "that's right",
    "affirmative",
    "he does",
    "she does",
    "they do",
    "does live",
    "do live",
    "lives in bengaluru",
    "lives in bangalore",
    "live in bengaluru",
    "is in bengaluru",
)

# Refusal / "I don't know" markers. If the system emits any of these for the
# Bangalore question, it FAILED to resolve the alias to the stored Bengaluru
# fact — the precise failure Phase 54 must eliminate.
REFUSAL_PHRASES = (
    "i do not have enough evidence",
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
    "no information",
)

# Negation markers: an explicit "no, the creator does not live there" would be a
# wrong answer (the fact says they DO). Caught to prevent a confident denial from
# masquerading as a pass.
NEGATIVE_MARKERS = (
    "does not live",
    "doesn't live",
    "do not live",
    "no, ",
    "not in bangalore",
    "not in bengaluru",
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
    """The Bengaluru statement must be committed to memory, not answered as a query."""
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

    # The debug trace must prove a triple was actually extracted & stored, and
    # that the canonical city survived extraction.
    debug = resp.debug or {}
    assert debug.get("knowledge_acquisition") is True, (
        "debug.knowledge_acquisition flag missing — extraction did not run."
    )
    learned = debug.get("learned_triples") or []
    assert learned, "No triples were learned from the statement — nothing was persisted."
    flat = " ".join(str(part) for triple in learned for part in triple).lower()
    assert CANONICAL_CITY.lower() in flat, (
        f"The canonical city {CANONICAL_CITY!r} was not captured in any learned "
        f"triple: {learned!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2 — CANONICAL RECALL  (Phase 54 contract)
# ─────────────────────────────────────────────────────────────────────────────
def test_2_canonical_recall():
    """
    Asking about "Bangalore" must affirm the fact taught about "Bengaluru",
    proving both surface forms resolved to ONE canonical entity.
    """
    # Teach the Bengaluru fact, WAIT for the async consolidation thread to embed
    # and persist it, then ask the Bangalore question.
    _commit, resp = _run(
        _teach_wait_then_recall(
            TAUGHT_FACT_STATEMENT, RECALL_QUESTION, CONSOLIDATION_WAIT_SECONDS
        )
    )
    answer_lc = resp.answer.lower()

    # (a) It must NOT refuse. A refusal here means the alias "Bangalore" was never
    #     linked to the stored "Bengaluru" entity — the core Phase 54 failure.
    said_refusal = [p for p in REFUSAL_PHRASES if p in answer_lc]
    assert not said_refusal, (
        f"Semantic grounding failure: the system refused the {ALIAS_CITY!r} question "
        f"({said_refusal!r}) despite having been taught the {CANONICAL_CITY!r} fact. "
        f"It did not resolve {ALIAS_CITY!r} -> {CANONICAL_CITY!r}. Answer={resp.answer!r}"
    )

    # (b) It must NOT deny the (true) proposition.
    denied = [n for n in NEGATIVE_MARKERS if n in answer_lc]
    assert not denied, (
        f"The system denied a TRUE fact ({denied!r}). The creator does live there. "
        f"Answer={resp.answer!r}"
    )

    # (c) It must AFFIRM — either with an explicit affirmative marker or by citing
    #     the canonical city in response to the alias query.
    affirmed = any(m in answer_lc for m in AFFIRMATIVE_MARKERS)
    cites_canonical = CANONICAL_CITY.lower() in answer_lc
    assert affirmed or cites_canonical, (
        "No affirmative grounding detected: the answer neither confirmed the "
        f"proposition nor cited {CANONICAL_CITY!r} when asked about {ALIAS_CITY!r}. "
        f"Answer={resp.answer!r}"
    )

    # (d) The affirmation must be GRAPH-GROUNDED, not a free-form lucky guess —
    #     this is what proves real canonical recall rather than hallucination.
    assert _has_graph_provenance(resp), (
        "Affirmation lacks graph provenance: no [KG] citation and no kg/reasoning "
        f"debug marker. citations={resp.citations!r} "
        f"debug_keys={list((resp.debug or {}).keys())!r}. The answer may be ungrounded."
    )

    # (e) Confidence must be a real graph-backed grade.
    assert resp.confidence in GRAPH_CONFIDENCE_LABELS, (
        f"Unexpected confidence label for a recalled fact: {resp.confidence!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner — prints a falsifiable PASS/FAIL report and sets exit code.
# ─────────────────────────────────────────────────────────────────────────────
def _main() -> int:
    tests = [
        ("TEST 1 - SENSE & REMEMBER", test_1_sense_and_remember),
        ("TEST 2 - CANONICAL RECALL (Bangalore == Bengaluru)", test_2_canonical_recall),
    ]
    print("=" * 72)
    print("VELYNX Falsifiable Cognitive Test Suite (Phase 54 — Semantic Grounding)")
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
        print("Semantic grounding NOT achieved — Phase 54 is not 'done'.")
    else:
        print("Canonical entity resolution verified. Phase 54 'Done When' satisfied.")
    print("=" * 72)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
