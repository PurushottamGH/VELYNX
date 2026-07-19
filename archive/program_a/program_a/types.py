"""PA-1..PA-4 shared value types (frozen dataclasses).

Leaf module: no logic beyond structural validation, no I/O, no constants.
Deliberately *below* ``QueryRecord``: nothing here has a ``gold_rubric``,
``query_family``, or ``score`` field -- the L11 cheat channel and the
retrieval-relevance channel are unrepresentable by construction
(PROGRAM_A_FINAL_ARCHITECTURE.md Section 4 PA-1/PA-3;
PROGRAM_A_MODULE_SPEC.md Section 1).

``EvidenceItem`` carries no ``score`` and no timestamp by design: the
retrieval-relevance score must never flow toward the tier (prereg Section 5;
DATAFLOW Section 3 row 1), and wall-clock values are a determinism leak
(MASTER_SPEC Section 8 RISK).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

# The four canonical ES-1 confidence tiers. Mirrors
# ``experiments.EXP1.dataset.CONFIDENCE_TIERS``; equality is asserted by the
# structural/conformance tests. Duplicated here ONLY because this is a leaf
# module forbidden from importing ``experiments``; it is a frozen structural
# label set, not a tunable.
_TIERS: tuple[str, ...] = ("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")


@dataclass(frozen=True)
class EvidenceItem:
    """One provenance-tagged evidence snippet from a frozen snapshot."""

    doc_id: str
    origin_domain: str
    title: str
    text: str
    snapshot_hash_ref: str

    def __post_init__(self) -> None:
        if not self.doc_id:
            raise ValueError("EvidenceItem.doc_id is required")
        if not self.origin_domain:
            raise ValueError("EvidenceItem.origin_domain is required")


@dataclass(frozen=True)
class EvidenceSet:
    """Ordered evidence set preserving PA-1's frozen total order."""

    items: tuple[EvidenceItem, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.items, tuple):
            raise TypeError("EvidenceSet.items must be a tuple")

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[EvidenceItem]:
        return iter(self.items)

    def __getitem__(self, index: int) -> EvidenceItem:
        return self.items[index]


@dataclass(frozen=True)
class CandidateClaim:
    """One candidate claim with refs into the EvidenceSet by doc_id."""

    claim_text: str
    supporting_doc_ids: tuple[str, ...]


@dataclass(frozen=True)
class CandidateClaims:
    """Ordered candidate-claim set (PA-2 output)."""

    claims: tuple[CandidateClaim, ...]

    def __len__(self) -> int:
        return len(self.claims)

    def __iter__(self) -> Iterator[CandidateClaim]:
        return iter(self.claims)

    def __getitem__(self, index: int) -> CandidateClaim:
        return self.claims[index]


@dataclass(frozen=True)
class EvidenceStateResult:
    """The ES-1 evidence-state partition result (PA-3 output).

    ``state`` is exactly one of ``S0``/``S1``/``S2``/``S3``. Support and
    contradiction are computed with respect to the selected claim, never from
    source rank (M10 lawfulness condition).
    """

    state: str
    selected_claim: CandidateClaim | None
    support_doc_ids: tuple[str, ...]
    contradiction_doc_ids: tuple[str, ...]
    independent_origin_count: int

    def __post_init__(self) -> None:
        if self.state not in ("S0", "S1", "S2", "S3"):
            raise ValueError(f"EvidenceStateResult.state must be one of S0..S3; got {self.state!r}")


@dataclass(frozen=True)
class Emission:
    """Program A's public answer surface (PA-4 output).

    ``answer`` and ``tier`` both derive from one ``EvidenceStateResult`` (CR-9
    structural coupling). ``raw_numeric_confidence`` is always ``None`` under
    ES-1 (the mechanism contains no numeric confidence; prereg Section 1 line
    35 makes it exploratory-only).
    """

    answer: str
    tier: str
    raw_numeric_confidence: None
    metadata: dict

    def __post_init__(self) -> None:
        if self.tier not in _TIERS:
            raise ValueError(f"Emission.tier must be one of {_TIERS}; got {self.tier!r}")


__all__ = [
    "EvidenceItem",
    "EvidenceSet",
    "CandidateClaim",
    "CandidateClaims",
    "EvidenceStateResult",
    "Emission",
]
