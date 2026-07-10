"""Unit tests for the EXP-1 Program A adapter framework.

Director-implemented due to specialist runtime failure (2026-07-07).

These tests cover the EXISTING adapter framework at
``experiments/EXP1/program_a_adapter.py`` directly (not through the runner).
They assert the framework is deterministic, seed-aware, dependency-injected,
and side-effect free, and that non-canonical tiers are rejected at the
``from_mapping`` coercion boundary (guarding against the synthesizer's 5-grade
taxonomy leaking into the EXP-1 path).

Scope: tests only. No production-code changes. No retriever/synthesizer
binding. No tier computation. No canonical-document edits.
"""
from __future__ import annotations

import pytest

from experiments.EXP1.dataset import CONFIDENCE_TIERS, AnswerRecord, QueryRecord
from experiments.EXP1.program_a_adapter import (
    CallableProgramAAdapter,
    ProgramAAdapter,
    callable_identity,
    coerce_program_a_adapter,
)


def _query(
    query_id: str = "q1",
    query: str = "what is x?",
    family: str = "known_factual",
    rubric: str = "frozen rubric",
) -> QueryRecord:
    return QueryRecord(
        query_id=query_id,
        query=query,
        query_family=family,
        gold_rubric=rubric,
    )


# --------------------------------------------------------------------------- #
# U1-U2: Protocol conformance
# --------------------------------------------------------------------------- #


def test_protocol_runtime_checkable_accepts_conforming_class() -> None:
    class Conforming:
        @property
        def adapter_id(self) -> str:
            return "conf-id"

        def answer(self, query: QueryRecord, seed: int):  # noqa: D401
            return None

    obj = Conforming()
    assert isinstance(obj, ProgramAAdapter)


def test_protocol_rejects_non_conforming_object() -> None:
    assert not isinstance(object(), ProgramAAdapter)


# --------------------------------------------------------------------------- #
# U3-U5: CallableProgramAAdapter construction + validation
# --------------------------------------------------------------------------- #


def test_callable_adapter_constructs_with_valid_inputs() -> None:
    def fn(query: QueryRecord, seed: int) -> AnswerRecord:
        return AnswerRecord(query_id=query.query_id, answer="a", tier="UNKNOWN", seed=seed)

    adapter = CallableProgramAAdapter("id-1", fn)

    assert adapter.adapter_id == "id-1"
    assert adapter.answer_fn is fn
    assert isinstance(adapter, ProgramAAdapter)


def test_callable_adapter_rejects_empty_adapter_id() -> None:
    with pytest.raises(ValueError, match="adapter_id is required"):
        CallableProgramAAdapter("   ", lambda q, s: None)

    with pytest.raises(ValueError, match="adapter_id is required"):
        CallableProgramAAdapter("", lambda q, s: None)


def test_callable_adapter_rejects_non_callable_answer_fn() -> None:
    with pytest.raises(TypeError, match="answer_fn must be callable"):
        CallableProgramAAdapter("id", "not-a-callable")

    with pytest.raises(TypeError, match="answer_fn must be callable"):
        CallableProgramAAdapter("id", 42)


# --------------------------------------------------------------------------- #
# U6: answer() delegation
# --------------------------------------------------------------------------- #


def test_callable_adapter_answer_delegates_verbatim() -> None:
    calls: list[tuple[QueryRecord, int]] = []

    def spy(query: QueryRecord, seed: int) -> AnswerRecord:
        calls.append((query, seed))
        return AnswerRecord(query_id=query.query_id, answer="spy", tier="UNKNOWN", seed=seed)

    adapter = CallableProgramAAdapter("spy-id", spy)
    query = _query()

    result = adapter.answer(query, 7)

    assert len(calls) == 1
    assert calls[0][0] is query
    assert calls[0][1] == 7
    assert isinstance(result, AnswerRecord)
    assert result.query_id == "q1"
    assert result.answer == "spy"
    assert result.tier == "UNKNOWN"
    assert result.seed == 7


# --------------------------------------------------------------------------- #
# U7-U9: callable_identity
# --------------------------------------------------------------------------- #


def _sample_fn() -> None:
    pass


def _other_fn() -> None:
    pass


class _SampleObj:
    pass


def test_callable_identity_is_deterministic_for_function() -> None:
    expected = f"{_sample_fn.__module__}.{_sample_fn.__qualname__}"
    assert callable_identity(_sample_fn) == expected
    assert callable_identity(_sample_fn) == callable_identity(_sample_fn)


def test_callable_identity_distinguishes_different_functions() -> None:
    assert callable_identity(_sample_fn) != callable_identity(_other_fn)


def test_callable_identity_works_for_object() -> None:
    obj = _SampleObj()
    expected = f"{type(obj).__module__}.{type(obj).__qualname__}"
    assert callable_identity(obj) == expected


# --------------------------------------------------------------------------- #
# U10-U16: coerce_program_a_adapter branch matrix
# --------------------------------------------------------------------------- #


def test_coerce_returns_explicit_adapter_unchanged() -> None:
    adapter = CallableProgramAAdapter("explicit", _sample_fn)
    result = coerce_program_a_adapter(adapter=adapter)
    assert result is adapter


def test_coerce_answer_fn_uses_callable_identity_when_no_id() -> None:
    result = coerce_program_a_adapter(answer_fn=_sample_fn)
    assert isinstance(result, CallableProgramAAdapter)
    assert result.adapter_id == callable_identity(_sample_fn)


def test_coerce_answer_fn_uses_explicit_id_when_given() -> None:
    result = coerce_program_a_adapter(answer_fn=_sample_fn, adapter_id="custom-id")
    assert isinstance(result, CallableProgramAAdapter)
    assert result.adapter_id == "custom-id"


def test_coerce_rejects_both_adapter_and_answer_fn() -> None:
    adapter = CallableProgramAAdapter("explicit", _sample_fn)
    with pytest.raises(ValueError, match="provide either adapter or answer_fn, not both"):
        coerce_program_a_adapter(adapter=adapter, answer_fn=_sample_fn)


def test_coerce_rejects_adapter_not_implementing_protocol() -> None:
    with pytest.raises(TypeError, match="adapter must implement ProgramAAdapter"):
        coerce_program_a_adapter(adapter=object())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="adapter must implement ProgramAAdapter"):
        coerce_program_a_adapter(adapter="a-string")  # type: ignore[arg-type]


class _EmptyIdAdapter:
    @property
    def adapter_id(self) -> str:
        return ""

    def answer(self, query: QueryRecord, seed: int):
        return None


def test_coerce_rejects_adapter_with_empty_id() -> None:
    with pytest.raises(ValueError, match="adapter_id is required"):
        coerce_program_a_adapter(adapter=_EmptyIdAdapter())


def test_coerce_rejects_both_none() -> None:
    with pytest.raises(ValueError, match="Program A adapter or answer_fn is required"):
        coerce_program_a_adapter()


# --------------------------------------------------------------------------- #
# U17-U21: tier pass-through and AnswerRecord validation/coercion
# --------------------------------------------------------------------------- #


def test_callable_adapter_passes_through_each_canonical_tier() -> None:
    for tier in CONFIDENCE_TIERS:
        def fn(query: QueryRecord, seed: int, tier: str = tier) -> AnswerRecord:
            return AnswerRecord(query_id=query.query_id, answer="a", tier=tier, seed=seed)

        adapter = CallableProgramAAdapter(f"id-{tier}", fn)
        result = adapter.answer(_query(), 11)
        assert result.tier == tier


def test_from_mapping_rejects_non_canonical_synthesizer_grades() -> None:
    # The non-canonical 5-grade taxonomy emitted by AnswerSynthesizer
    # {CERTAIN, PROBABLE, UNCERTAIN, SPECULATIVE, INSUFFICIENT} is rejected at
    # the from_mapping coercion boundary (the boundary the runner uses for the
    # Mapping return path).
    for bad_tier in ("INSUFFICIENT", "SPECULATIVE", "UNCERTAIN", "MAYBE", ""):
        with pytest.raises(ValueError, match="must be one of"):
            AnswerRecord.from_mapping(
                {"query_id": "q", "answer": "a", "tier": bad_tier}
            )


@pytest.mark.parametrize(
    "bad_tier",
    ["INSUFFICIENT", "SPECULATIVE", "UNCERTAIN", "MAYBE", "", "speculative"],
)
def test_direct_construction_rejects_non_canonical_tier(bad_tier: str) -> None:
    # F-10 fix (roadmap T6): the AnswerRecord @dataclass __post_init__ now
    # calls validate(), so direct construction enforces the canonical-tier
    # guard. A non-canonical tier raises at construction instead of
    # propagating to a downstream KeyError in calibration.confidence_for_tier.
    # "speculative" (lowercase) confirms direct construction does NOT uppercase
    # (only from_mapping does); the non-canonical value is rejected verbatim.
    #
    # Director-implemented due to specialist runtime failure (2026-07-07);
    # subject to Reviewer + ScientificAuditor sign-off (roadmap T6).
    with pytest.raises(ValueError, match="must be one of"):
        AnswerRecord(query_id="q", answer="a", tier=bad_tier)


def test_answer_record_from_mapping_uppercases_tier() -> None:
    record = AnswerRecord.from_mapping(
        {"query_id": "q", "answer": "a", "tier": "certain"}
    )
    assert record.tier == "CERTAIN"


def test_answer_record_from_mapping_rejects_speculative_after_uppercase() -> None:
    with pytest.raises(ValueError, match="must be one of"):
        AnswerRecord.from_mapping(
            {"query_id": "q", "answer": "a", "tier": "speculative"}
        )


def test_answer_record_from_mapping_accepts_aliases_and_coerces_types() -> None:
    record = AnswerRecord.from_mapping(
        {
            "query_id": "q",
            "answer_i": "a",
            "tier_i": "UNKNOWN",
            "seed": "5",
            "raw_numeric_confidence": "0.5",
            "metadata": {"k": "v"},
        }
    )
    assert record.answer == "a"
    assert record.tier == "UNKNOWN"
    assert record.seed == 5
    assert isinstance(record.seed, int)
    assert record.raw_numeric_confidence == 0.5
    assert isinstance(record.raw_numeric_confidence, float)
    assert record.metadata == {"k": "v"}

    with pytest.raises(ValueError, match="metadata"):
        AnswerRecord.from_mapping(
            {"query_id": "q", "answer": "a", "tier": "UNKNOWN", "metadata": "notdict"}
        )


# --------------------------------------------------------------------------- #
# U22-U24: seed-awareness, determinism, side-effect-freeness, pass-through
# --------------------------------------------------------------------------- #


def test_answer_propagates_seed_to_fn_and_record() -> None:
    received: list[int] = []

    def fn(query: QueryRecord, seed: int) -> AnswerRecord:
        received.append(seed)
        return AnswerRecord(query_id=query.query_id, answer="a", tier="DEBATED", seed=seed)

    adapter = CallableProgramAAdapter("seed-id", fn)
    result = adapter.answer(_query(), 99)

    assert received == [99]
    assert result.seed == 99


def test_answer_is_deterministic_and_side_effect_free() -> None:
    def fn(query: QueryRecord, seed: int) -> AnswerRecord:
        return AnswerRecord(query_id=query.query_id, answer="d", tier="PROBABLE", seed=seed)

    adapter = CallableProgramAAdapter("det-id", fn)
    query = _query()

    first = adapter.answer(query, 3)
    second = adapter.answer(query, 3)

    assert first.to_dict() == second.to_dict()
    # The frozen query record is not mutated by the adapter.
    assert query.query_id == "q1"
    assert query.query == "what is x?"


def test_raw_numeric_confidence_and_metadata_preserved() -> None:
    def fn(query: QueryRecord, seed: int) -> AnswerRecord:
        return AnswerRecord(
            query_id=query.query_id,
            answer="a",
            tier="PROBABLE",
            seed=seed,
            raw_numeric_confidence=0.42,
            metadata={"src": "x", "n": 2},
        )

    adapter = CallableProgramAAdapter("meta-id", fn)
    result = adapter.answer(_query(), 5)
    dumped = result.to_dict()

    assert dumped["raw_numeric_confidence"] == pytest.approx(0.42)
    assert dumped["metadata"] == {"src": "x", "n": 2}
    assert dumped["tier"] == "PROBABLE"
    assert dumped["seed"] == 5
