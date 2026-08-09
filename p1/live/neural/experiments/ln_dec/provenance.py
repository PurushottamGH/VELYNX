"""Hard provenance and anti-contamination guards for the canonical path."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Iterable, Set


class ProvenanceViolation(AssertionError):
    """Raised when a source crosses a forbidden train/evaluation boundary."""


class EvaluationMutationError(AssertionError):
    """Raised when evaluation attempts to update model or external state."""


@dataclass
class SourceBlacklist:
    """Frozen probe blacklist plus auditable write ledgers."""

    probe_ids: FrozenSet[str]
    training_ids: FrozenSet[str] = field(default_factory=frozenset)
    updates: Set[str] = field(default_factory=set)
    replay_writes: Set[str] = field(default_factory=set)
    kv_writes: Set[str] = field(default_factory=set)

    @classmethod
    def from_ids(cls, probe_ids: Iterable[str], training_ids: Iterable[str] = ()) -> "SourceBlacklist":
        probes = frozenset(str(value) for value in probe_ids)
        training = frozenset(str(value) for value in training_ids)
        if probes & training:
            raise ValueError("a source cannot be both a probe and a training item")
        return cls(probe_ids=probes, training_ids=training)

    def assert_training(self, source_id: str) -> None:
        source_id = str(source_id)
        if source_id in self.probe_ids or source_id.startswith("probe:"):
            raise ProvenanceViolation(f"probe source entered a training update: {source_id}")

    def assert_probe(self, source_id: str) -> None:
        source_id = str(source_id)
        if source_id not in self.probe_ids:
            raise ProvenanceViolation(f"unknown or mutable probe source: {source_id}")

    def assert_memory_write(self, source_id: str, surface: str) -> None:
        self.assert_training(source_id)
        if surface == "kv":
            self.kv_writes.add(str(source_id))
        elif surface == "replay":
            self.replay_writes.add(str(source_id))
        else:
            raise ValueError(f"unknown memory surface {surface!r}")

    def record_update(self, source_id: str) -> None:
        self.assert_training(source_id)
        self.updates.add(str(source_id))

    def assert_no_probe_writes(self) -> None:
        for label, values in (
            ("updates", self.updates),
            ("replay", self.replay_writes),
            ("kv", self.kv_writes),
        ):
            overlap = values & self.probe_ids
            if overlap:
                raise ProvenanceViolation(f"probe IDs reached {label}: {sorted(overlap)}")

