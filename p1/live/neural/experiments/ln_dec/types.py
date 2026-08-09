"""Typed records for the canonical P1-LN-DEC benchmark.

The records in this module are the only data objects that cross the benchmark
boundary.  In particular, a candidate receives :class:`Experience` objects
and evaluation receives only the context from a :class:`Probe`; generator
private state is kept in the reference side of the corpus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Tuple


TokenSequence = Tuple[int, ...]


@dataclass(frozen=True)
class TokenVocabulary:
    """One immutable token space shared by candidate and all baselines."""

    body_tokens: TokenSequence
    abstract_tokens: TokenSequence
    start: int
    separator: int
    eos: int
    calibrate: int
    compose: int
    transfer: int
    rule_tokens: TokenSequence
    size: int
    vocabulary_id: str

    def validate(self, tokens: TokenSequence, *, allow_empty: bool = False) -> None:
        """Reject tokens outside the protocol vocabulary."""
        if not tokens and not allow_empty:
            raise ValueError("token sequence must not be empty")
        bad = [token for token in tokens if token < 0 or token >= self.size]
        if bad:
            raise ValueError(f"token(s) outside vocabulary {self.size}: {bad!r}")

    @property
    def target_symbols(self) -> TokenSequence:
        """Symbols that may legally be predicted by the benchmark."""
        return tuple(range(self.size))

    def as_dict(self) -> Dict[str, object]:
        return {
            "body_tokens": list(self.body_tokens),
            "abstract_tokens": list(self.abstract_tokens),
            "start": self.start,
            "separator": self.separator,
            "eos": self.eos,
            "calibrate": self.calibrate,
            "compose": self.compose,
            "transfer": self.transfer,
            "rule_tokens": list(self.rule_tokens),
            "size": self.size,
            "vocabulary_id": self.vocabulary_id,
        }


@dataclass(frozen=True)
class Experience:
    """One frozen training experience with complete provenance."""

    experience_id: str
    source_id: str
    episode_id: str
    context: TokenSequence
    target: int
    family: str
    episode_start: bool = True
    episode_end: bool = True
    metadata: Mapping[str, object] = field(default_factory=dict)

    def sequence(self) -> TokenSequence:
        return self.context + (self.target,)

    def as_dict(self) -> Dict[str, object]:
        return {
            "experience_id": self.experience_id,
            "source_id": self.source_id,
            "episode_id": self.episode_id,
            "context": list(self.context),
            "target": self.target,
            "family": self.family,
            "episode_start": self.episode_start,
            "episode_end": self.episode_end,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class Probe:
    """One frozen held-out item and its expected next token."""

    probe_id: str
    source_id: str
    family: str
    context: TokenSequence
    target: int
    metadata: Mapping[str, object] = field(default_factory=dict)

    def sequence(self) -> TokenSequence:
        return self.context + (self.target,)

    def as_dict(self) -> Dict[str, object]:
        return {
            "probe_id": self.probe_id,
            "source_id": self.source_id,
            "family": self.family,
            "context": list(self.context),
            "target": self.target,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class BenchmarkManifest:
    """Machine-readable identity for one frozen benchmark corpus."""

    benchmark_version: str
    name: str
    master_seed: int
    substreams: Mapping[str, int]
    vocabulary_id: str
    corpus_fingerprint: str
    training_ids: Tuple[str, ...]
    probe_ids: Tuple[str, ...]
    probe_families: Tuple[str, ...]
    target_identifiability: str
    oracle_semantics: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "benchmark_version": self.benchmark_version,
            "name": self.name,
            "master_seed": self.master_seed,
            "substreams": dict(self.substreams),
            "vocabulary_id": self.vocabulary_id,
            "corpus_fingerprint": self.corpus_fingerprint,
            "training_ids": list(self.training_ids),
            "probe_ids": list(self.probe_ids),
            "probe_families": list(self.probe_families),
            "target_identifiability": self.target_identifiability,
            "oracle_semantics": self.oracle_semantics,
        }


@dataclass(frozen=True)
class CandidateView:
    """The public benchmark slice available to a candidate implementation."""

    vocabulary: TokenVocabulary
    training: Tuple[Experience, ...]
    manifest: BenchmarkManifest

