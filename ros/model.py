"""P1 Research Operating System — record model.

The ROS treats `science/SKB_RECORDS_v1.0.yaml` as the single writable scientific
store (kernel invariant K1). This module is the schema of that store: what
collections exist, what identifier each uses, and how references between records
are discovered.

Reference discovery is deliberately *structural* rather than configured. Every
string anywhere in a record that matches the canonical identifier pattern is
treated as a reference and must resolve. A per-field allow-list would silently
miss a dangling reference introduced in a field nobody remembered to register,
which is the class of defect this store exists to make impossible.

This module performs validation only. It never writes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterator

#: Canonical identifier form used throughout the SKB: ``PREFIX-YYYY-NNNN``.
ID_PATTERN = re.compile(r"\b([A-Z]{3,5})-(\d{4})-(\d{4})\b")


@dataclass(frozen=True)
class Collection:
    """One top-level record collection in the SKB."""

    key: str
    prefix: str
    object_type: str
    #: Records whose status is decision-bearing may never be edited in place;
    #: they are corrected by linked supersession (SKB ``correction_policy``).
    append_only: bool = False


#: The twenty top-level SKB collections, in the frozen §1.2 order. ``relations``
#: carries no identifiers of its own and is handled separately; ``skb`` is the
#: store header. Key, prefix, ``object_type`` and ``append_only`` agree with
#: ``v2.lske.schema.COLLECTION_SPECS`` for all twenty (RB-05 cl. 6); the nine
#: collections beyond the original eleven are addressable but not yet populated.
COLLECTIONS: tuple[Collection, ...] = (
    Collection("research_questions", "RQS", "research_question"),
    Collection("hypotheses", "HYP", "hypothesis", append_only=True),
    Collection("protocols", "PROT", "protocol", append_only=True),
    Collection("experiments", "EXP", "experiment", append_only=True),
    Collection("runs", "RUN", "run", append_only=True),
    Collection("observations", "OBS", "observation", append_only=True),
    Collection("metrics", "MET", "metric"),
    Collection("datasets", "DSET", "dataset"),
    Collection("artifacts", "ART", "artifact", append_only=True),
    Collection("evidence", "EVD", "evidence", append_only=True),
    Collection("decisions", "DEC", "decision", append_only=True),
    Collection("mechanisms", "MEC", "mechanism"),
    Collection("theories", "THY", "theory"),
    Collection("assumptions", "ASM", "assumption"),
    Collection("unknowns", "UNK", "unknown"),
    Collection("scientific_debt", "SDEBT", "scientific_debt"),
    Collection("negative_results", "NEG", "negative_result", append_only=True),
    Collection("programs", "PROG", "research_program"),
    Collection("sessions", "SESS", "research_session", append_only=True),
    Collection("snapshots", "SNAP", "knowledge_snapshot", append_only=True),
)

COLLECTION_BY_KEY: dict[str, Collection] = {c.key: c for c in COLLECTIONS}
COLLECTION_BY_PREFIX: dict[str, Collection] = {c.prefix: c for c in COLLECTIONS}

#: Header and relation keys are structural, not record collections.
NON_RECORD_KEYS = frozenset({"skb", "relations"})


def prefix_of(identifier: str) -> str | None:
    """Return the identifier's collection prefix, or ``None`` if malformed."""
    match = ID_PATTERN.fullmatch(identifier.strip())
    return match.group(1) if match else None


def collection_for_id(identifier: str) -> Collection | None:
    """Return the collection an identifier belongs to, or ``None`` if unknown."""
    prefix = prefix_of(identifier)
    return COLLECTION_BY_PREFIX.get(prefix) if prefix else None


def iter_id_references(value: Any, path: str = "") -> Iterator[tuple[str, str]]:
    """Yield ``(json_path, identifier)`` for every identifier appearing in ``value``.

    Walks nested mappings and sequences. A record's own ``id`` field is yielded
    like any other match; callers filter it out when checking for dangling
    references.
    """
    if isinstance(value, str):
        for match in ID_PATTERN.finditer(value):
            yield path, match.group(0)
    elif isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}" if path else str(key)
            yield from iter_id_references(item, child)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from iter_id_references(item, f"{path}[{index}]")


#: Hypothesis statuses permitted by `SCIENTIFIC_OPERATING_SYSTEM.md` section 5.
HYPOTHESIS_STATUSES = frozenset(
    {
        "Proposed",
        "Exploratory",
        "Under Validation",
        "Validated",
        "Rejected",
        "Superseded",
        "Archived",
    }
)

#: Evidence relation directions permitted by Constitution Lock E4.
EVIDENCE_DIRECTIONS = frozenset(
    {
        "supports",
        "opposes",
        "null",
        "indeterminate",
        "invalid",
        "requires-assumption",
        "depends-on",
    }
)

#: Decision actions permitted by Constitution Lock E5 / SOS section 10.
DECISION_ACTIONS = frozenset(
    {
        "accept_within_scope",
        "reject",
        "revise",
        "narrow",
        "split",
        "merge",
        "archive",
        "no_change",
        "delete",
    }
)


def normalise_term(value: Any) -> str:
    """Normalise a controlled-vocabulary term for comparison.

    Records in the store spell the same term several ways — ``Revise``,
    ``No_Verdict``, ``requires assumption``. Case and separator differences are
    presentation, not meaning, so they are folded away here.

    This function exists so that exactly one definition of "the same term" is in
    force. Two ROS components normalising slightly differently would report
    different conformance figures for identical data, which is the drift the
    single-store invariant exists to prevent.
    """
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def conforms(value: Any, vocabulary: frozenset[str]) -> bool:
    """Whether ``value`` is drawn from ``vocabulary`` after normalisation.

    An empty value is *not* a vocabulary violation — it is a missing field, which
    a different check reports. Conflating the two would make a blank record look
    like a constitutional deviation.
    """
    term = normalise_term(value)
    if not term:
        return True
    return term in {normalise_term(v) for v in vocabulary}
