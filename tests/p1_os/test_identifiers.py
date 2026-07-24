"""Tests for permanent-ID and actor-handle validation (spec section 11, 12)."""

from __future__ import annotations

import pytest

from p1_os.identifiers import (
    ID_PREFIXES,
    InvalidActorHandleError,
    InvalidIdentifierError,
    is_valid_actor_handle,
    object_type_for_id,
    validate_actor_handle,
    validate_id,
)


@pytest.mark.parametrize("object_type,prefix", list(ID_PREFIXES.items()))
def test_valid_id_for_every_object_type(object_type, prefix):
    identifier = f"{prefix}000001"
    assert validate_id(identifier, object_type=object_type) == object_type
    assert object_type_for_id(identifier) == object_type


@pytest.mark.parametrize("object_type,prefix", list(ID_PREFIXES.items()))
def test_zero_sequence_is_invalid(object_type, prefix):
    identifier = f"{prefix}000000"
    with pytest.raises(InvalidIdentifierError):
        validate_id(identifier, object_type=object_type)
    with pytest.raises(InvalidIdentifierError):
        object_type_for_id(identifier)


def test_prefix_must_match_object_type():
    with pytest.raises(InvalidIdentifierError):
        validate_id("P1-Q000001", object_type="claim")


@pytest.mark.parametrize(
    "identifier",
    [
        "P1-C00001",  # five digits
        "P1-C0000001",  # seven digits
        "p1-c000001",  # lowercase prefix
        "P1-C000001 ",  # trailing space
        "P1-Z000001",  # unknown prefix
        "P1C000001",  # missing dash
        "",
    ],
)
def test_malformed_ids_are_rejected(identifier):
    with pytest.raises(InvalidIdentifierError):
        object_type_for_id(identifier)


def test_id_validation_is_case_sensitive():
    with pytest.raises(InvalidIdentifierError):
        validate_id("p1-c000001", object_type="claim")


@pytest.mark.parametrize(
    "handle",
    ["pi", "reviewer_1", "research-engineer", "sonnet5", "ab", "z" * 32],
)
def test_valid_actor_handles(handle):
    assert is_valid_actor_handle(handle)
    assert validate_actor_handle(handle) == handle


def test_single_character_handle_is_invalid():
    """The spec's own pattern ^[a-z][a-z0-9_-]{1,31}$ requires a second
    character (the {1,31} quantifier applies after the mandatory first
    char), so a bare single-letter handle like "a" does not match."""
    assert not is_valid_actor_handle("a")
    with pytest.raises(InvalidActorHandleError):
        validate_actor_handle("a")


@pytest.mark.parametrize(
    "handle",
    [
        "P1a",
        "user@example.com",
        "_reviewer",
        "two words",
        "z" * 33,
        "",
        "1abc",
        "ABC",
    ],
)
def test_invalid_actor_handles(handle):
    assert not is_valid_actor_handle(handle)
    with pytest.raises(InvalidActorHandleError):
        validate_actor_handle(handle)
