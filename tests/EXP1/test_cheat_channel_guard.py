"""CR-3 cheat-channel guard (B-4 / W3.1).

Sentinel-substitution guardrail proving the EXP-1 adapter's emitted
``AnswerRecord`` does not depend on the ``gold_rubric`` or ``query_family``
fields of the ``QueryRecord`` (L11 / CR-3 input restriction). A mechanism
reading either field could fake calibration undetectably in the ECE number.

The real ES-1 emission surface is gated behind a separate GO; this guard
runs green against a conforming stub ``answer_fn`` at the adapter boundary
(``CallableProgramAAdapter.answer`` -- the exact point the runner hands the
full ``QueryRecord`` to the surface). It is structured so the real ES-1
adapter can be dropped in as the ``answer_fn`` parameter without rewriting
the test. An adversarial counter-test proves the harness is not vacuous.

Director-implemented due to specialist runtime failure (2026-07-07); subject
to Reviewer + ScientificAuditor sign-off (roadmap T6 / CR-3 verification).
"""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

from experiments.EXP1.dataset import AnswerRecord, QueryRecord
from experiments.EXP1.program_a_adapter import CallableProgramAAdapter


def _base_query(
    query_id: str = "q1",
    query: str = "What is the capital of France?",
    query_family: str = "known_factual",
    gold_rubric: str = "frozen rubric text A",
) -> QueryRecord:
    return QueryRecord(
        query_id=query_id,
        query=query,
        query_family=query_family,
        gold_rubric=gold_rubric,
    )


def _conforming_answer_fn(query: QueryRecord, seed: int) -> AnswerRecord:
    """Stub adapter derived ONLY from lawful inputs (query_id, query, seed).

    Never reads ``query.gold_rubric`` or ``query.query_family`` (the CR-3
    cheat-channel fields).
    """
    return AnswerRecord(
        query_id=query.query_id,
        answer=f"stub:{query.query}",
        tier="UNKNOWN",
        seed=seed,
    )


def _rubric_echoing_answer_fn(query: QueryRecord, seed: int) -> AnswerRecord:
    """NON-conforming: reads ``gold_rubric`` and echoes it into the answer.

    Used only by the adversarial counter-test to prove the guard has teeth.
    """
    return AnswerRecord(
        query_id=query.query_id,
        answer=f"echo:{query.gold_rubric}",
        tier="UNKNOWN",
        seed=seed,
    )


def _adapter(answer_fn: Any) -> CallableProgramAAdapter:
    return CallableProgramAAdapter("cr3-guard-stub", answer_fn)


def _assert_answer_independent_of(
    answer_fn: Any, base: QueryRecord, mutated: QueryRecord, field: str
) -> None:
    """Assert the adapter's emitted AnswerRecord is byte-identical when
    ``field`` is changed between ``base`` and ``mutated``.

    When the real ES-1 adapter exists, call this helper with its answer_fn
    for both ``gold_rubric`` and ``query_family`` mutations.
    """
    base_out = _adapter(answer_fn).answer(base, 7)
    mutated_out = _adapter(answer_fn).answer(mutated, 7)
    assert isinstance(base_out, AnswerRecord)
    assert isinstance(mutated_out, AnswerRecord)
    assert (
        base_out.to_dict() == mutated_out.to_dict()
    ), f"emitted AnswerRecord depends on cheat-channel field {field!r}"


def test_answer_does_not_depend_on_gold_rubric() -> None:
    """CR-3 guard: emitted answer must not depend on ``gold_rubric``."""
    base = _base_query()
    sentinel = dataclasses.replace(base, gold_rubric="__SENTINEL_RUBRIC_A__")
    # gold_rubric has no enum constraint; query_family stays canonical -> valid.
    assert sentinel.query_family == "known_factual"
    _assert_answer_independent_of(_conforming_answer_fn, base, sentinel, "gold_rubric")


def test_answer_does_not_depend_on_query_family() -> None:
    """CR-3 guard: emitted answer must not depend on ``query_family``."""
    base = _base_query(query_family="known_factual")
    swapped = dataclasses.replace(base, query_family="ambiguous_or_debated")
    # both are canonical QUERY_FAMILIES -> both valid QueryRecords.
    _assert_answer_independent_of(_conforming_answer_fn, base, swapped, "query_family")


def test_guard_catches_rubric_echoing_adapter() -> None:
    """Adversarial counter-test: the harness catches an adapter that reads
    ``gold_rubric``, proving the guard is not vacuous."""
    base = _base_query()
    sentinel = dataclasses.replace(base, gold_rubric="__SENTINEL_RUBRIC_A__")

    base_out = _adapter(_rubric_echoing_answer_fn).answer(base, 7)
    sentinel_out = _adapter(_rubric_echoing_answer_fn).answer(sentinel, 7)

    assert base_out.to_dict() != sentinel_out.to_dict()
    assert base_out.answer != sentinel_out.answer
