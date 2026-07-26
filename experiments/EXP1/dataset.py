"""EXP-1 frozen dataset and answer-record schemas.

The EXP-1 outcome is binary answer correctness under the frozen query-specific
gold rubric. Query family and confidence tier are kept as separate label spaces.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from experiments.EXP1.rubric import validate_gold_rubrics

CONFIDENCE_TIERS: tuple[str, ...] = ("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")
QUERY_FAMILIES: tuple[str, ...] = (
    "known_factual",
    "ambiguous_or_debated",
    "hallucinated_unanswerable_or_false_premise",
)
HALLUCINATED_FAMILY = "hallucinated_unanswerable_or_false_premise"
MINIMUM_SAMPLE_SIZE = 200
PLANNED_BALANCED_DATASET_SIZE = 210
PLANNED_FAMILY_ALLOCATION: dict[str, int] = {
    "known_factual": 70,
    "ambiguous_or_debated": 70,
    "hallucinated_unanswerable_or_false_premise": 70,
}


@dataclass(frozen=True)
class QueryRecord:
    """Frozen held-out EXP-1 query and its gold rubric."""

    query_id: str
    query: str
    query_family: str
    gold_rubric: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "QueryRecord":
        query_id = str(row.get("query_id", "")).strip()
        query = str(row.get("query", "")).strip()
        query_family = str(row.get("query_family", "")).strip()
        gold_rubric = str(row.get("gold_rubric", "")).strip()
        metadata = row.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError(f"metadata for query_id={query_id!r} must be an object")
        record = cls(
            query_id=query_id,
            query=query,
            query_family=query_family,
            gold_rubric=gold_rubric,
            metadata=dict(metadata),
        )
        record.validate()
        return record

    def validate(self) -> None:
        if not self.query_id:
            raise ValueError("query_id is required")
        if not self.query:
            raise ValueError(f"query is required for query_id={self.query_id!r}")
        if self.query_family not in QUERY_FAMILIES:
            raise ValueError(
                f"query_family for query_id={self.query_id!r} must be one of {QUERY_FAMILIES}"
            )
        if not self.gold_rubric:
            raise ValueError(f"gold_rubric is required for query_id={self.query_id!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "query": self.query,
            "query_family": self.query_family,
            "gold_rubric": self.gold_rubric,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class FrozenDataset:
    """Strictly validated frozen EXP-1 corpus in immutable file order."""

    records: tuple[QueryRecord, ...]
    order_hash: str
    family_counts: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "n": len(self.records),
            "order_hash": self.order_hash,
            "family_counts": dict(self.family_counts),
            "query_ids": [record.query_id for record in self.records],
        }


@dataclass(frozen=True)
class AnswerRecord:
    """One public Program A answer for one EXP-1 query row."""

    query_id: str
    answer: str
    tier: str
    seed: int | None = None
    raw_numeric_confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Enforce the canonical-tier guard at construction (F-10 fix, T6).

        Direct construction previously bypassed ``validate()``; a non-canonical
        tier propagated to a downstream ``KeyError`` in
        ``calibration.confidence_for_tier``. The frozen dataclass
        ``__post_init__`` closes the bypass for every construction site, not
        only ``from_mapping``. ``validate()`` only reads fields and raises; it
        does not assign, so it is safe in a frozen ``__post_init__``.
        """
        self.validate()

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "AnswerRecord":
        query_id = str(row.get("query_id", "")).strip()
        answer = str(row.get("answer", row.get("answer_i", "")))
        tier = str(row.get("tier", row.get("tier_i", row.get("confidence", "")))).strip().upper()
        seed_value = row.get("seed")
        raw_numeric = row.get("raw_numeric_confidence")
        metadata = row.get("metadata", {})
        if seed_value is not None:
            seed_value = int(seed_value)
        if raw_numeric is not None:
            raw_numeric = float(raw_numeric)
        if not isinstance(metadata, dict):
            raise ValueError(f"metadata for query_id={query_id!r} must be an object")
        record = cls(
            query_id=query_id,
            answer=answer,
            tier=tier,
            seed=seed_value,
            raw_numeric_confidence=raw_numeric,
            metadata=dict(metadata),
        )
        record.validate()
        return record

    def validate(self) -> None:
        if not self.query_id:
            raise ValueError("query_id is required")
        if self.tier not in CONFIDENCE_TIERS:
            raise ValueError(
                f"tier for query_id={self.query_id!r} must be one of {CONFIDENCE_TIERS}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "answer": self.answer,
            "tier": self.tier,
            "seed": self.seed,
            "raw_numeric_confidence": self.raw_numeric_confidence,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class EvaluatedRecord:
    """Answer record joined to frozen rubric adjudication."""

    query_id: str
    answer: str
    tier: str
    correctness: int
    query_family: str
    fabricated_factual_answer: bool = False
    seed: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "EvaluatedRecord":
        correctness = row.get("correctness", row.get("y_i"))
        if correctness is None:
            raise ValueError("correctness is required")
        metadata = row.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object")
        record = cls(
            query_id=str(row.get("query_id", "")).strip(),
            answer=str(row.get("answer", row.get("answer_i", ""))),
            tier=str(row.get("tier", row.get("tier_i", row.get("confidence", "")))).strip().upper(),
            correctness=int(correctness),
            query_family=str(row.get("query_family", "")).strip(),
            fabricated_factual_answer=bool(row.get("fabricated_factual_answer", False)),
            seed=int(row["seed"]) if row.get("seed") is not None else None,
            metadata=dict(metadata),
        )
        record.validate()
        return record

    def validate(self) -> None:
        if not self.query_id:
            raise ValueError("query_id is required")
        if self.tier not in CONFIDENCE_TIERS:
            raise ValueError(
                f"tier for query_id={self.query_id!r} must be one of {CONFIDENCE_TIERS}"
            )
        if self.correctness not in (0, 1):
            raise ValueError(f"correctness for query_id={self.query_id!r} must be binary 0/1")
        if self.query_family not in QUERY_FAMILIES:
            raise ValueError(
                f"query_family for query_id={self.query_id!r} must be one of {QUERY_FAMILIES}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "answer": self.answer,
            "tier": self.tier,
            "correctness": self.correctness,
            "query_family": self.query_family,
            "fabricated_factual_answer": self.fabricated_factual_answer,
            "seed": self.seed,
            "metadata": dict(self.metadata),
        }


def load_json_records(path: str | Path) -> list[dict[str, Any]]:
    """Load JSON records from a list JSON file, {"records": [...]}, or JSONL."""

    path = Path(path)
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    payload = json.loads(text)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return payload["records"]
    raise ValueError(f"{path} must contain a JSON list, JSONL, or an object with a records list")


def load_query_records(path: str | Path) -> list[QueryRecord]:
    """Load and validate frozen EXP-1 query records."""

    return [QueryRecord.from_mapping(row) for row in load_json_records(path)]


def load_frozen_dataset(path: str | Path) -> FrozenDataset:
    """Load the execution-ready frozen EXP-1 corpus.

    Batch 2 readiness requires the frozen corpus to be exactly N=210, balanced
    70/70/70 across the three query families, free of duplicates, and returned
    in immutable file order.
    """

    raw_records = load_json_records(path)
    records = tuple(QueryRecord.from_mapping(row) for row in raw_records)
    validation = validate_frozen_dataset_records(records)
    validate_gold_rubrics(raw_records)
    return FrozenDataset(
        records=records,
        order_hash=_order_hash(records),
        family_counts=validation["family_counts"],
    )


def load_answer_records(path: str | Path) -> list[AnswerRecord]:
    """Load Program A public answer records."""

    return [AnswerRecord.from_mapping(row) for row in load_json_records(path)]


def load_evaluated_records(path: str | Path) -> list[EvaluatedRecord]:
    """Load answer records that already include frozen-rubric adjudication."""

    return [EvaluatedRecord.from_mapping(row) for row in load_json_records(path)]


def validate_query_records(records: Sequence[QueryRecord]) -> dict[str, Any]:
    """Validate preregistered EXP-1 corpus size, uniqueness, and family coverage."""

    seen: set[str] = set()
    family_counts = {family: 0 for family in QUERY_FAMILIES}
    for record in records:
        record.validate()
        if record.query_id in seen:
            raise ValueError(f"duplicate query_id={record.query_id!r}")
        seen.add(record.query_id)
        family_counts[record.query_family] += 1

    n = len(records)
    if n < MINIMUM_SAMPLE_SIZE:
        raise ValueError(f"EXP-1 requires N >= {MINIMUM_SAMPLE_SIZE}; got N={n}")
    if n == PLANNED_BALANCED_DATASET_SIZE and family_counts != PLANNED_FAMILY_ALLOCATION:
        raise ValueError(
            "EXP-1 planned N=210 corpus must allocate 70 rows to each canonical query family"
        )
    return {"n": n, "family_counts": family_counts}


def validate_frozen_dataset_records(records: Sequence[QueryRecord]) -> dict[str, Any]:
    """Validate the strict EXP-1 execution corpus invariants."""

    seen_query_ids: set[str] = set()
    seen_queries: set[str] = set()
    family_counts = {family: 0 for family in QUERY_FAMILIES}

    for record in records:
        record.validate()
        if record.query_id in seen_query_ids:
            raise ValueError(f"duplicate query_id={record.query_id!r}")
        seen_query_ids.add(record.query_id)

        normalized_query = " ".join(record.query.strip().split()).casefold()
        if normalized_query in seen_queries:
            raise ValueError(f"duplicate query text for query_id={record.query_id!r}")
        seen_queries.add(normalized_query)
        family_counts[record.query_family] += 1

    n = len(records)
    if n != PLANNED_BALANCED_DATASET_SIZE:
        raise ValueError(
            f"frozen EXP-1 dataset must contain exactly {PLANNED_BALANCED_DATASET_SIZE} records; got N={n}"
        )
    if family_counts != PLANNED_FAMILY_ALLOCATION:
        raise ValueError(
            "frozen EXP-1 dataset must allocate exactly 70 records to each canonical query family"
        )
    return {"n": n, "family_counts": family_counts}


def _order_hash(records: Sequence[QueryRecord]) -> str:
    payload = "\n".join(json.dumps(record.to_dict(), sort_keys=True) for record in records).encode(
        "utf-8"
    )
    return hashlib.sha256(payload).hexdigest()


def validate_answer_records(
    query_records: Sequence[QueryRecord],
    answer_records: Sequence[AnswerRecord],
    *,
    seed: int | None = None,
) -> dict[str, Any]:
    """Verify exactly one Program A answer exists for every frozen query row."""

    expected_ids = {record.query_id for record in query_records}
    seen: set[str] = set()
    for answer in answer_records:
        answer.validate()
        if seed is not None and answer.seed != seed:
            raise ValueError(
                f"answer query_id={answer.query_id!r} has seed={answer.seed}, expected {seed}"
            )
        if answer.query_id not in expected_ids:
            raise ValueError(f"answer query_id={answer.query_id!r} is not in frozen query set")
        if answer.query_id in seen:
            raise ValueError(f"duplicate answer for query_id={answer.query_id!r}")
        seen.add(answer.query_id)
    missing = sorted(expected_ids - seen)
    if missing:
        raise ValueError(f"missing answers for {len(missing)} query_id(s): {missing[:5]}")
    return {"n": len(answer_records), "seed": seed}


def build_evaluated_records(
    query_records: Sequence[QueryRecord],
    answer_records: Sequence[AnswerRecord],
    correctness_by_query_id: Mapping[str, int],
    fabricated_factual_by_query_id: Mapping[str, bool] | None = None,
) -> list[EvaluatedRecord]:
    """Join Program A answers to frozen-rubric binary adjudication.

    The correctness mapping must come from answer-content adjudication against
    each query's frozen gold rubric. This function never infers correctness
    from query family or emitted confidence tier.
    """

    fabricated_factual_by_query_id = fabricated_factual_by_query_id or {}
    queries = {record.query_id: record for record in query_records}
    validate_answer_records(query_records, answer_records)

    evaluated: list[EvaluatedRecord] = []
    for answer in answer_records:
        if answer.query_id not in correctness_by_query_id:
            raise ValueError(f"missing correctness adjudication for query_id={answer.query_id!r}")
        query = queries[answer.query_id]
        evaluated.append(
            EvaluatedRecord(
                query_id=answer.query_id,
                answer=answer.answer,
                tier=answer.tier,
                correctness=int(correctness_by_query_id[answer.query_id]),
                query_family=query.query_family,
                fabricated_factual_answer=bool(
                    fabricated_factual_by_query_id.get(answer.query_id, False)
                ),
                seed=answer.seed,
                metadata=dict(answer.metadata),
            )
        )
    for record in evaluated:
        record.validate()
    return evaluated


def records_to_jsonl(records: Iterable[QueryRecord | AnswerRecord | EvaluatedRecord]) -> str:
    """Serialize EXP-1 records to JSONL without changing field names."""

    return "\n".join(json.dumps(record.to_dict(), sort_keys=True) for record in records) + "\n"
