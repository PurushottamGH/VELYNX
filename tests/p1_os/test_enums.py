"""Tests for shared enums (spec section 3, 10, 15)."""

from __future__ import annotations

import pytest

from p1_os.enums import (
    AccessStatus,
    ClaimMaturity,
    ClaimRole,
    ClaimStatus,
    ObjectType,
    OutcomeClass,
    Stance,
    UnknownStatus,
    VerificationStatus,
)


def test_object_type_has_exactly_twelve_members():
    assert len(list(ObjectType)) == 12


@pytest.mark.parametrize(
    "value",
    [
        "research_artifact",
        "question",
        "unknown",
        "claim",
        "source",
        "evidence",
        "hypothesis",
        "experiment",
        "result",
        "interpretation",
        "decision",
        "principle_candidate",
    ],
)
def test_object_type_members(value):
    assert ObjectType(value).value == value


def test_claim_maturity_ladder_l0_to_l5():
    assert [m.value for m in ClaimMaturity] == ["L0", "L1", "L2", "L3", "L4", "L5"]


@pytest.mark.parametrize(
    "value", ["candidate", "competing", "constraint", "scope_limit"]
)
def test_claim_role_members(value):
    assert ClaimRole(value).value == value


@pytest.mark.parametrize(
    "value", ["not_checked", "abstract_only", "full_text_checked", "inaccessible"]
)
def test_access_status_members(value):
    assert AccessStatus(value).value == value


@pytest.mark.parametrize(
    "value", ["supports", "contradicts", "contextualizes", "null_evidence", "limits"]
)
def test_stance_members(value):
    assert Stance(value).value == value


@pytest.mark.parametrize(
    "value", ["pending", "partially_verified", "verified", "unverifiable"]
)
def test_verification_status_members(value):
    assert VerificationStatus(value).value == value


@pytest.mark.parametrize(
    "value", ["supports_primary", "supports_competing", "inconclusive", "invalid"]
)
def test_outcome_class_members(value):
    assert OutcomeClass(value).value == value


def test_invalid_enum_value_raises():
    with pytest.raises(ValueError):
        ClaimMaturity("L6")
    with pytest.raises(ValueError):
        AccessStatus("checked")
    with pytest.raises(ValueError):
        ClaimRole("primary")


def test_claim_status_restricted_to_textually_evidenced_values():
    """Section 10 requires object-specific status enums, but no section
    enumerates the full value set for any type. Only 'draft' (used by
    every template) plus the values that literally appear in the Decision
    schema example (spec section 15) are treated as valid, to avoid
    inventing unstated status values."""
    assert {m.value for m in ClaimStatus} == {"draft", "active", "accepted_for_use"}
    with pytest.raises(ValueError):
        ClaimStatus("rejected")


def test_unknown_status_restricted_to_textually_evidenced_values():
    assert {m.value for m in UnknownStatus} == {"draft", "active", "closed"}
    with pytest.raises(ValueError):
        UnknownStatus("archived")
