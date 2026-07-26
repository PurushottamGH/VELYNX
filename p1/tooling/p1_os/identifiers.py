"""Permanent-ID and actor-handle validation (spec section 11, 12)."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator

ACTOR_HANDLE_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,31}$")

ID_PREFIXES: dict[str, str] = {
    "research_artifact": "P1-AR",
    "question": "P1-Q",
    "unknown": "P1-U",
    "claim": "P1-C",
    "source": "P1-S",
    "evidence": "P1-V",
    "hypothesis": "P1-H",
    "experiment": "P1-E",
    "result": "P1-R",
    "interpretation": "P1-I",
    "decision": "P1-D",
    "principle_candidate": "P1-P",
}

_PREFIX_TO_OBJECT_TYPE: dict[str, str] = {v: k for k, v in ID_PREFIXES.items()}

_ID_PATTERNS: dict[str, re.Pattern[str]] = {
    prefix: re.compile(rf"^{re.escape(prefix)}(\d{{6}})$") for prefix in ID_PREFIXES.values()
}


class InvalidIdentifierError(ValueError):
    """Raised when a permanent ID does not satisfy the Milestone 1 format."""


class InvalidActorHandleError(ValueError):
    """Raised when an actor handle does not satisfy the Milestone 1 pattern."""


def is_valid_actor_handle(handle: str) -> bool:
    if not isinstance(handle, str):
        return False
    return bool(ACTOR_HANDLE_PATTERN.match(handle))


def validate_actor_handle(handle: str) -> str:
    if not is_valid_actor_handle(handle):
        raise InvalidActorHandleError(f"Invalid actor handle: {handle!r}")
    return handle


ActorHandleField = Annotated[str, AfterValidator(validate_actor_handle)]


def prefix_for_object_type(object_type: str) -> str:
    try:
        return ID_PREFIXES[object_type]
    except KeyError as exc:
        raise InvalidIdentifierError(f"Unknown object type: {object_type!r}") from exc


def object_type_for_id(identifier: str) -> str:
    for prefix in sorted(_PREFIX_TO_OBJECT_TYPE, key=len, reverse=True):
        if identifier.startswith(prefix):
            pattern = _ID_PATTERNS[prefix]
            match = pattern.match(identifier)
            if match:
                digits = match.group(1)
                if digits == "000000":
                    raise InvalidIdentifierError(
                        f"Identifier sequence number must not be 000000: {identifier!r}"
                    )
                return _PREFIX_TO_OBJECT_TYPE[prefix]
    raise InvalidIdentifierError(f"Identifier does not match any known prefix: {identifier!r}")


def is_valid_id(identifier: str, object_type: str | None = None) -> bool:
    try:
        resolved_type = validate_id(identifier, object_type=object_type)
    except InvalidIdentifierError:
        return False
    return resolved_type is not None


def validate_id(identifier: str, object_type: str | None = None) -> str:
    """Validate a permanent ID's format and, if given, that it matches object_type.

    Returns the resolved object type on success.
    """
    if not isinstance(identifier, str):
        raise InvalidIdentifierError(f"Identifier must be a string: {identifier!r}")

    if object_type is not None:
        expected_prefix = prefix_for_object_type(object_type)
        pattern = _ID_PATTERNS[expected_prefix]
        match = pattern.match(identifier)
        if not match:
            raise InvalidIdentifierError(
                f"Identifier {identifier!r} does not match prefix {expected_prefix!r} "
                f"for object type {object_type!r}"
            )
        if match.group(1) == "000000":
            raise InvalidIdentifierError(
                f"Identifier sequence number must not be 000000: {identifier!r}"
            )
        return object_type

    return object_type_for_id(identifier)


def _check_single_id(object_type: str | None):
    def _validate(value: str) -> str:
        validate_id(value, object_type=object_type)
        return value

    return _validate


def _check_id_list(object_type: str | None):
    def _validate(values: list[str]) -> list[str]:
        for value in values:
            validate_id(value, object_type=object_type)
        return values

    return _validate


def IdField(object_type: str | None = None) -> type:
    """An Annotated str type validated as a permanent ID.

    If object_type is given, the ID's prefix must match that object type.
    """
    return Annotated[str, AfterValidator(_check_single_id(object_type))]


def IdListField(object_type: str | None = None) -> type:
    """An Annotated list[str] type whose items are each validated as permanent IDs."""
    return Annotated[list[str], AfterValidator(_check_id_list(object_type))]
