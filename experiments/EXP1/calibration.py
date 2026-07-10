"""EXP-1 Expected Calibration Error computation.

All probabilities and bins are locked by EXP1_PREREGISTRATION.md before
execution. Numeric confidence emitted by Program A is ignored for primary ECE.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from experiments.EXP1.dataset import CONFIDENCE_TIERS, EvaluatedRecord


TIER_TO_CONFIDENCE: dict[str, float] = {
    "UNKNOWN": 0.125,
    "DEBATED": 0.375,
    "PROBABLE": 0.625,
    "CERTAIN": 0.875,
}
BIN_BOUNDARIES: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)
BIN_COUNT = 4
ECE_PASS_THRESHOLD = 0.10


@dataclass(frozen=True)
class ReliabilityBin:
    """One fixed equal-width EXP-1 reliability bin."""

    index: int
    lower: float
    upper: float
    right_closed: bool
    count: int
    accuracy: float | None
    confidence: float | None
    ece_contribution: float
    tiers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "lower": self.lower,
            "upper": self.upper,
            "right_closed": self.right_closed,
            "count": self.count,
            "accuracy": self.accuracy,
            "confidence": self.confidence,
            "ece_contribution": self.ece_contribution,
            "tiers": list(self.tiers),
        }


@dataclass(frozen=True)
class CalibrationResult:
    """EXP-1 ECE and reliability table."""

    n: int
    ece: float
    bins: tuple[ReliabilityBin, ...]
    tier_counts: dict[str, int]

    @property
    def passes_ece_gate(self) -> bool:
        return self.ece < ECE_PASS_THRESHOLD

    def to_dict(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "ece": self.ece,
            "passes_ece_gate": self.passes_ece_gate,
            "ece_pass_threshold": ECE_PASS_THRESHOLD,
            "tier_counts": dict(self.tier_counts),
            "bins": [bin_result.to_dict() for bin_result in self.bins],
        }


def confidence_for_tier(tier: str) -> float:
    """Return the locked numeric midpoint for an emitted public tier."""

    normalized = tier.strip().upper()
    try:
        return TIER_TO_CONFIDENCE[normalized]
    except KeyError as exc:
        raise ValueError(f"unknown EXP-1 confidence tier: {tier!r}") from exc


def bin_index_for_confidence(confidence: float) -> int:
    """Return the fixed equal-width bin index for a confidence in [0, 1]."""

    if confidence < 0.0 or confidence > 1.0:
        raise ValueError(f"confidence must be in [0, 1], got {confidence}")
    if confidence == 1.0:
        return BIN_COUNT - 1
    for idx in range(BIN_COUNT):
        lower = BIN_BOUNDARIES[idx]
        upper = BIN_BOUNDARIES[idx + 1]
        if lower <= confidence < upper:
            return idx
    raise ValueError(f"confidence did not fall into an EXP-1 bin: {confidence}")


def compute_ece(records: Sequence[EvaluatedRecord]) -> CalibrationResult:
    """Compute preregistered four-bin equal-width ECE."""

    n = len(records)
    if n == 0:
        raise ValueError("EXP-1 ECE requires at least one evaluated record")

    grouped: list[list[tuple[EvaluatedRecord, float]]] = [[] for _ in range(BIN_COUNT)]
    tier_counts = {tier: 0 for tier in CONFIDENCE_TIERS}

    for record in records:
        record.validate()
        confidence = confidence_for_tier(record.tier)
        grouped[bin_index_for_confidence(confidence)].append((record, confidence))
        tier_counts[record.tier] += 1

    bins: list[ReliabilityBin] = []
    ece = 0.0
    for idx, rows in enumerate(grouped):
        lower = BIN_BOUNDARIES[idx]
        upper = BIN_BOUNDARIES[idx + 1]
        count = len(rows)
        right_closed = idx == BIN_COUNT - 1
        if count == 0:
            bins.append(
                ReliabilityBin(
                    index=idx + 1,
                    lower=lower,
                    upper=upper,
                    right_closed=right_closed,
                    count=0,
                    accuracy=None,
                    confidence=None,
                    ece_contribution=0.0,
                    tiers=(),
                )
            )
            continue
        accuracy = sum(record.correctness for record, _ in rows) / count
        confidence = sum(confidence for _, confidence in rows) / count
        contribution = (count / n) * abs(accuracy - confidence)
        ece += contribution
        bins.append(
            ReliabilityBin(
                index=idx + 1,
                lower=lower,
                upper=upper,
                right_closed=right_closed,
                count=count,
                accuracy=accuracy,
                confidence=confidence,
                ece_contribution=contribution,
                tiers=tuple(sorted({record.tier for record, _ in rows}, key=CONFIDENCE_TIERS.index)),
            )
        )

    return CalibrationResult(n=n, ece=ece, bins=tuple(bins), tier_counts=tier_counts)
