"""Test battery for program_a/types.py (PA-1..PA-4 shared value types).

Scope: tests only, no production-code changes. types.py is the one
program_a module with real (non-stub) logic today -- pure structural
validation on frozen dataclasses, no I/O. Categories: unit, integration
(cross-type assembly), replay, determinism, property, regression, fuzz.

Reference: PROGRAM_A_MODULE_SPEC.md Section 1.
"""

from __future__ import annotations

import pickle
from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given
from hypothesis import strategies as st

from program_a.types import (
    CandidateClaim,
    CandidateClaims,
    Emission,
    EvidenceItem,
    EvidenceSet,
    EvidenceStateResult,
)

_VALID_STATES = ("S0", "S1", "S2", "S3")
_VALID_TIERS = ("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")


def _evidence_item(doc_id: str = "d1", origin_domain: str = "example.com") -> EvidenceItem:
    return EvidenceItem(
        doc_id=doc_id,
        origin_domain=origin_domain,
        title="t",
        text="text body",
        snapshot_hash_ref="abc123",
    )


def _candidate_claim(
    text: str = "claim text", doc_ids: tuple[str, ...] = ("d1",)
) -> CandidateClaim:
    return CandidateClaim(claim_text=text, supporting_doc_ids=doc_ids)


# --------------------------------------------------------------------------- #
# Unit tests
# --------------------------------------------------------------------------- #


def test_evidence_item_constructs_with_valid_fields() -> None:
    item = _evidence_item()
    assert item.doc_id == "d1"
    assert item.origin_domain == "example.com"
    assert item.title == "t"
    assert item.text == "text body"
    assert item.snapshot_hash_ref == "abc123"


def test_evidence_item_rejects_empty_doc_id() -> None:
    with pytest.raises(ValueError, match="doc_id is required"):
        _evidence_item(doc_id="")


def test_evidence_item_rejects_empty_origin_domain() -> None:
    with pytest.raises(ValueError, match="origin_domain is required"):
        _evidence_item(origin_domain="")


def test_evidence_set_len_iter_getitem() -> None:
    items = (_evidence_item("d1"), _evidence_item("d2"))
    es = EvidenceSet(items=items)
    assert len(es) == 2
    assert list(es) == list(items)
    assert es[0].doc_id == "d1"
    assert es[1].doc_id == "d2"


def test_evidence_set_empty_is_valid() -> None:
    es = EvidenceSet(items=())
    assert len(es) == 0
    assert list(es) == []


def test_evidence_set_rejects_list_instead_of_tuple() -> None:
    with pytest.raises(TypeError, match="items must be a tuple"):
        EvidenceSet(items=[_evidence_item()])  # type: ignore[arg-type]


def test_candidate_claim_constructs_with_fields() -> None:
    claim = _candidate_claim("x is true", ("d1", "d2"))
    assert claim.claim_text == "x is true"
    assert claim.supporting_doc_ids == ("d1", "d2")


def test_candidate_claims_len_iter_getitem() -> None:
    claims = (_candidate_claim("a"), _candidate_claim("b"))
    cc = CandidateClaims(claims=claims)
    assert len(cc) == 2
    assert list(cc) == list(claims)
    assert cc[0].claim_text == "a"


@pytest.mark.parametrize("state", _VALID_STATES)
def test_evidence_state_result_accepts_each_valid_state(state: str) -> None:
    result = EvidenceStateResult(
        state=state,
        selected_claim=None,
        support_doc_ids=(),
        contradiction_doc_ids=(),
        independent_origin_count=0,
    )
    assert result.state == state


def test_evidence_state_result_rejects_invalid_state() -> None:
    with pytest.raises(ValueError, match="must be one of S0..S3"):
        EvidenceStateResult(
            state="S4",
            selected_claim=None,
            support_doc_ids=(),
            contradiction_doc_ids=(),
            independent_origin_count=0,
        )


@pytest.mark.parametrize("tier", _VALID_TIERS)
def test_emission_accepts_each_valid_tier(tier: str) -> None:
    emission = Emission(answer="a", tier=tier, raw_numeric_confidence=None, metadata={})
    assert emission.tier == tier


def test_emission_rejects_invalid_tier() -> None:
    with pytest.raises(ValueError, match="must be one of"):
        Emission(answer="a", tier="MAYBE", raw_numeric_confidence=None, metadata={})


# --------------------------------------------------------------------------- #
# Integration tests (cross-type assembly mirroring the PA-1..PA-4 dataflow)
# --------------------------------------------------------------------------- #


def test_full_object_graph_assembles_pa1_through_pa4() -> None:
    item_a = _evidence_item("d1", "example.com")
    item_b = _evidence_item("d2", "other.com")
    evidence = EvidenceSet(items=(item_a, item_b))

    claim = _candidate_claim("x is true", ("d1", "d2"))
    claims = CandidateClaims(claims=(claim,))

    state_result = EvidenceStateResult(
        state="S3",
        selected_claim=claim,
        support_doc_ids=("d1", "d2"),
        contradiction_doc_ids=(),
        independent_origin_count=2,
    )

    emission = Emission(
        answer="x is true",
        tier="CERTAIN",
        raw_numeric_confidence=None,
        metadata={"state": state_result.state},
    )

    assert all(doc_id in {i.doc_id for i in evidence} for doc_id in claim.supporting_doc_ids)
    assert state_result.selected_claim is claims[0]
    assert emission.metadata["state"] == state_result.state


def test_evidence_state_result_selected_claim_may_be_none_for_s0() -> None:
    result = EvidenceStateResult(
        state="S0",
        selected_claim=None,
        support_doc_ids=(),
        contradiction_doc_ids=(),
        independent_origin_count=0,
    )
    assert result.selected_claim is None


def test_types_tier_set_mirrors_constants_confidence_tiers() -> None:
    from program_a import constants

    assert set(_VALID_TIERS) == set(constants.CONFIDENCE_TIERS)
    assert set(constants.STATE_TIER_MAP.values()) <= set(constants.CONFIDENCE_TIERS)
    assert set(constants.STATE_TIER_MAP.keys()) == set(_VALID_STATES)


# --------------------------------------------------------------------------- #
# Replay tests (identical construction / serialization round-trip)
# --------------------------------------------------------------------------- #


def test_replay_identical_args_produce_equal_objects() -> None:
    first = _evidence_item("d1", "example.com")
    second = _evidence_item("d1", "example.com")
    assert first == second
    assert first is not second


@pytest.mark.parametrize(
    "obj",
    [
        _evidence_item(),
        EvidenceSet(items=(_evidence_item(),)),
        _candidate_claim(),
        CandidateClaims(claims=(_candidate_claim(),)),
        EvidenceStateResult(
            state="S1",
            selected_claim=None,
            support_doc_ids=("d1",),
            contradiction_doc_ids=(),
            independent_origin_count=1,
        ),
        Emission(answer="a", tier="DEBATED", raw_numeric_confidence=None, metadata={"k": "v"}),
    ],
)
def test_replay_pickle_roundtrip_preserves_equality(obj: object) -> None:
    replayed = pickle.loads(pickle.dumps(obj))
    assert replayed == obj


# --------------------------------------------------------------------------- #
# Determinism tests
# --------------------------------------------------------------------------- #


def test_evidence_set_iteration_order_is_stable_across_repeated_iterations() -> None:
    items = (_evidence_item("d1"), _evidence_item("d2"), _evidence_item("d3"))
    es = EvidenceSet(items=items)
    first_pass = [i.doc_id for i in es]
    second_pass = [i.doc_id for i in es]
    assert first_pass == second_pass == ["d1", "d2", "d3"]


def test_frozen_dataclasses_hash_consistent_with_equality() -> None:
    a = _evidence_item("d1", "example.com")
    b = _evidence_item("d1", "example.com")
    assert a == b
    assert hash(a) == hash(b)


def test_repr_is_deterministic_across_calls() -> None:
    item = _evidence_item()
    assert repr(item) == repr(item)
    emission = Emission(answer="a", tier="UNKNOWN", raw_numeric_confidence=None, metadata={})
    assert repr(emission) == repr(emission)


# --------------------------------------------------------------------------- #
# Property tests (hypothesis)
# --------------------------------------------------------------------------- #


@given(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10))
def test_property_evidence_set_len_matches_items_length(doc_ids: list[str]) -> None:
    items = tuple(_evidence_item(doc_id=f"d-{i}-{d}") for i, d in enumerate(doc_ids))
    es = EvidenceSet(items=items)
    assert len(es) == len(items)
    assert list(es) == list(items)


@given(st.integers())
def test_property_evidence_state_result_independent_origin_count_unconstrained(
    count: int,
) -> None:
    # independent_origin_count carries no validation in types.py by design --
    # range checks belong to the PA-3 mechanism layer, not the value type.
    result = EvidenceStateResult(
        state="S2",
        selected_claim=None,
        support_doc_ids=(),
        contradiction_doc_ids=(),
        independent_origin_count=count,
    )
    assert result.independent_origin_count == count


@given(st.dictionaries(st.text(max_size=10), st.text(max_size=10)))
def test_property_emission_metadata_accepts_any_dict(metadata: dict) -> None:
    emission = Emission(answer="a", tier="PROBABLE", raw_numeric_confidence=None, metadata=metadata)
    assert emission.metadata == metadata


# --------------------------------------------------------------------------- #
# Regression tests (pin invariants stated in the module docstring)
# --------------------------------------------------------------------------- #


def test_regression_evidence_item_has_no_score_field() -> None:
    fields = {f for f in EvidenceItem.__dataclass_fields__}
    assert "score" not in fields
    assert "timestamp" not in fields


def test_regression_candidate_claim_has_no_query_record_fields() -> None:
    fields = {f for f in CandidateClaim.__dataclass_fields__}
    assert "gold_rubric" not in fields
    assert "query_family" not in fields
    assert "score" not in fields


def test_regression_candidate_claim_exact_field_set_no_claim_id() -> None:
    """PA-2 closure guard (PA2_ACCEPTANCE_DECISION.md action C1): pin the
    documented CandidateClaim contract -- exactly {claim_text,
    supporting_doc_ids} and no spurious claim_id field."""
    fields = set(CandidateClaim.__dataclass_fields__)
    assert fields == {"claim_text", "supporting_doc_ids"}
    assert "claim_id" not in fields


def test_regression_evidence_state_result_exactly_four_states_valid() -> None:
    valid = []
    for candidate in ("S0", "S1", "S2", "S3", "S4", "s0", "", "UNKNOWN"):
        try:
            EvidenceStateResult(
                state=candidate,
                selected_claim=None,
                support_doc_ids=(),
                contradiction_doc_ids=(),
                independent_origin_count=0,
            )
        except ValueError:
            continue
        valid.append(candidate)
    assert valid == ["S0", "S1", "S2", "S3"]


def test_regression_emission_exactly_four_tiers_valid() -> None:
    valid = []
    for candidate in _VALID_TIERS + ("MAYBE", "certain", "", "CERTAIN "):
        try:
            Emission(answer="a", tier=candidate, raw_numeric_confidence=None, metadata={})
        except ValueError:
            continue
        valid.append(candidate)
    assert valid == list(_VALID_TIERS)


def test_regression_emission_does_not_runtime_enforce_raw_numeric_confidence_type() -> None:
    # raw_numeric_confidence is typed `None` (always-None contract) but dataclass
    # field types are not runtime-checked; documents the current absence of
    # enforcement so a future accidental relaxation of the contract is visible
    # as a deliberate change rather than a silent one.
    emission = Emission(answer="a", tier="UNKNOWN", raw_numeric_confidence=0.5, metadata={})
    assert emission.raw_numeric_confidence == 0.5


def test_regression_frozen_dataclasses_reject_attribute_mutation() -> None:
    item = _evidence_item()
    with pytest.raises(FrozenInstanceError):
        item.doc_id = "changed"  # type: ignore[misc]

    emission = Emission(answer="a", tier="UNKNOWN", raw_numeric_confidence=None, metadata={})
    with pytest.raises(FrozenInstanceError):
        emission.tier = "CERTAIN"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# Fuzz tests (hypothesis, adversarial strings)
# --------------------------------------------------------------------------- #


@given(st.text())
def test_fuzz_evidence_item_doc_id_only_raises_on_empty(doc_id: str) -> None:
    if doc_id:
        item = _evidence_item(doc_id=doc_id)
        assert item.doc_id == doc_id
    else:
        with pytest.raises(ValueError):
            _evidence_item(doc_id=doc_id)


@given(st.text())
def test_fuzz_emission_tier_rejects_anything_outside_canonical_set(tier: str) -> None:
    if tier in _VALID_TIERS:
        Emission(answer="a", tier=tier, raw_numeric_confidence=None, metadata={})
    else:
        with pytest.raises(ValueError):
            Emission(answer="a", tier=tier, raw_numeric_confidence=None, metadata={})


@given(
    st.one_of(
        st.lists(st.integers()),
        st.sets(st.integers()),
        st.text(),
        st.dictionaries(st.text(), st.integers()),
    )
)
def test_fuzz_evidence_set_rejects_any_non_tuple_container(container) -> None:
    with pytest.raises(TypeError, match="items must be a tuple"):
        EvidenceSet(items=container)  # type: ignore[arg-type]
