"""EXP-1 gold-rubric validation.

This module validates rubric records before EXP-1 execution. It does not
adjudicate answers and does not infer correctness.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class RubricValidationResult:
    """Summary of a successful gold-rubric validation pass."""

    n: int
    query_ids: tuple[str, ...]
    rubric_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "query_ids": list(self.query_ids),
            "rubric_ids": list(self.rubric_ids),
        }


def validate_gold_rubrics(records: Sequence[Mapping[str, Any]]) -> RubricValidationResult:
    """Reject missing, duplicated, or malformed EXP-1 gold rubrics.

    The frozen dataset keeps rubrics query-specific. `gold_rubric` must be a
    non-empty string, must not be reused verbatim across query rows, and may use
    an optional `rubric_id` that must also be unique when present.
    """

    seen_query_ids: set[str] = set()
    seen_rubric_texts: set[str] = set()
    seen_rubric_ids: set[str] = set()
    query_ids: list[str] = []
    rubric_ids: list[str] = []

    for index, row in enumerate(records):
        query_id = str(row.get("query_id", "")).strip()
        if not query_id:
            raise ValueError(f"query_id is required for rubric row {index}")
        if query_id in seen_query_ids:
            raise ValueError(f"duplicate rubric query_id={query_id!r}")
        seen_query_ids.add(query_id)
        query_ids.append(query_id)

        if "gold_rubric" not in row or row.get("gold_rubric") is None:
            raise ValueError(f"missing gold_rubric for query_id={query_id!r}")
        rubric = row["gold_rubric"]
        if not isinstance(rubric, str):
            raise ValueError(f"malformed gold_rubric for query_id={query_id!r}: must be a string")
        normalized_rubric = _normalize_rubric_text(rubric)
        if not normalized_rubric:
            raise ValueError(f"missing gold_rubric for query_id={query_id!r}")
        if _has_disallowed_control_character(normalized_rubric):
            raise ValueError(
                f"malformed gold_rubric for query_id={query_id!r}: contains control characters"
            )
        if normalized_rubric in seen_rubric_texts:
            raise ValueError(f"duplicate gold_rubric text for query_id={query_id!r}")
        seen_rubric_texts.add(normalized_rubric)

        raw_rubric_id = row.get("rubric_id")
        if raw_rubric_id is None:
            continue
        rubric_id = str(raw_rubric_id).strip()
        if not rubric_id:
            raise ValueError(f"malformed rubric_id for query_id={query_id!r}")
        if rubric_id in seen_rubric_ids:
            raise ValueError(f"duplicate rubric_id={rubric_id!r}")
        seen_rubric_ids.add(rubric_id)
        rubric_ids.append(rubric_id)

    return RubricValidationResult(
        n=len(records),
        query_ids=tuple(query_ids),
        rubric_ids=tuple(rubric_ids),
    )


def _normalize_rubric_text(value: str) -> str:
    return " ".join(value.strip().split()).casefold()


def _has_disallowed_control_character(value: str) -> bool:
    return any(ord(character) < 32 for character in value if character not in "\t\n\r")
