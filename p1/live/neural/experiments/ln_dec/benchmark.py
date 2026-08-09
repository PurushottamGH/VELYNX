"""Canonical P1-LN-DEC benchmark and its executable invariants.

This module is the single data-generating boundary for the repaired experiment.
It deliberately uses one integer vocabulary for training, NN-0, baselines, and
probes.  The old Playgarden string probes and the old all-OOV DEC abstraction
family are not part of this corpus.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from p1.live.neural.experiments.ln_dec.rng import SeedStreams
from p1.live.neural.experiments.ln_dec.types import (
    BenchmarkManifest,
    CandidateView,
    Experience,
    Probe,
    TokenSequence,
    TokenVocabulary,
)


BENCHMARK_VERSION = "ln-dec-canonical-1"
BENCHMARK_NAME = "p1-ln-dec-canonical"
DECISIVE_FAMILIES: Tuple[str, ...] = ("composition", "symbol_transfer")


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReferenceSemantics:
    """Generator-private semantics used only for a labelled reference ceiling."""

    atoms: Mapping[int, TokenSequence]
    mapping: Mapping[int, int]
    heldout_templates: Tuple[Tuple[int, ...], ...]
    reference_fingerprint: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "atoms": {str(k): list(v) for k, v in sorted(self.atoms.items())},
            "mapping": {str(k): v for k, v in sorted(self.mapping.items())},
            "heldout_templates": [list(t) for t in self.heldout_templates],
            "reference_fingerprint": self.reference_fingerprint,
        }


@dataclass(frozen=True)
class BenchmarkCorpus:
    """Frozen corpus with public candidate data and private reference semantics."""

    benchmark_version: str
    name: str
    master_seed: int
    streams: SeedStreams
    vocabulary: TokenVocabulary
    training: Tuple[Experience, ...]
    probes: Tuple[Probe, ...]
    manifest: BenchmarkManifest
    reference: ReferenceSemantics = field(repr=False, compare=False)

    @property
    def training_ids(self) -> Tuple[str, ...]:
        return tuple(item.source_id for item in self.training)

    @property
    def probe_ids(self) -> Tuple[str, ...]:
        return tuple(item.source_id for item in self.probes)

    def candidate_view(self) -> CandidateView:
        """Return the only benchmark slice a candidate is allowed to receive."""
        return CandidateView(self.vocabulary, self.training, self.manifest)

    def probes_for(self, family: str | None = None) -> Tuple[Probe, ...]:
        if family is None:
            return self.probes
        return tuple(probe for probe in self.probes if probe.family == family)

    def validate(self) -> None:
        """Run all cheap corpus and contamination invariants."""
        self.vocabulary.validate(tuple(token for exp in self.training for token in exp.sequence()))
        self.vocabulary.validate(tuple(token for probe in self.probes for token in probe.sequence()))

        training_sources = set(self.training_ids)
        probe_sources = set(self.probe_ids)
        if training_sources & probe_sources:
            raise AssertionError("training and probe source IDs overlap")
        if len(training_sources) != len(self.training):
            raise AssertionError("training source IDs are not unique")
        if len(probe_sources) != len(self.probes):
            raise AssertionError("probe source IDs are not unique")

        self._assert_target_identifiability()
        self._assert_target_grounding()
        self._assert_decisive_exclusion()
        if self.fingerprint() != self.manifest.corpus_fingerprint:
            raise AssertionError("frozen corpus fingerprint does not match manifest")

    def _assert_target_identifiability(self) -> None:
        targets: Dict[Tuple[int, ...], set[int]] = {}
        for probe in self.probes:
            if probe.family not in DECISIVE_FAMILIES:
                continue
            targets.setdefault(probe.context, set()).add(probe.target)
        ambiguous = {context: values for context, values in targets.items() if len(values) != 1}
        if ambiguous:
            raise AssertionError(f"decisive probe context has multiple targets: {ambiguous!r}")

    def _assert_target_grounding(self) -> None:
        """Every decisive target is observable in training in principle."""
        observed = {token for exp in self.training for token in exp.sequence()[1:]}
        missing = {
            probe.probe_id: probe.target
            for probe in self.probes
            if probe.family in DECISIVE_FAMILIES and probe.target not in observed
        }
        if missing:
            raise AssertionError(f"decisive target symbols are not learnably grounded: {missing!r}")

        calibration = {
            exp.context[-1]: exp.target
            for exp in self.training
            if exp.family == "calibration"
        }
        for probe in self.probes_for("symbol_transfer"):
            source = probe.metadata.get("source_body_token")
            if not isinstance(source, int) or calibration.get(source) != probe.target:
                raise AssertionError(
                    f"symbol-transfer target lacks an explicit calibration exposure: {probe.probe_id}"
                )

    def _assert_decisive_exclusion(self) -> None:
        training_sequences = [exp.sequence() for exp in self.training]
        for probe in self.probes:
            if probe.family not in DECISIVE_FAMILIES:
                continue
            needle = probe.sequence()
            if any(_contains(sequence, needle) for sequence in training_sequences):
                raise AssertionError(f"decisive answer leakage for probe {probe.probe_id}")

        train_contexts = {exp.context for exp in self.training}
        for probe in self.probes_for("symbol_transfer"):
            if probe.context in train_contexts:
                raise AssertionError(f"symbol-transfer context appeared in training: {probe.probe_id}")

    def fingerprint(self) -> str:
        payload = {
            "benchmark_version": self.benchmark_version,
            "name": self.name,
            "master_seed": self.master_seed,
            "streams": self.streams.as_dict(),
            "vocabulary": self.vocabulary.as_dict(),
            "training": [item.as_dict() for item in self.training],
            "probes": [item.as_dict() for item in self.probes],
            "reference_fingerprint": self.reference.reference_fingerprint,
        }
        return _canonical_hash(payload)

    def as_public_dict(self) -> Dict[str, object]:
        """Serialize corpus evidence without exposing the reference mapping."""
        return {
            "benchmark_version": self.benchmark_version,
            "name": self.name,
            "master_seed": self.master_seed,
            "streams": self.streams.as_dict(),
            "vocabulary": self.vocabulary.as_dict(),
            "training": [item.as_dict() for item in self.training],
            "probes": [item.as_dict() for item in self.probes],
            "manifest": self.manifest.as_dict(),
        }


class CanonicalBenchmark:
    """Build one deterministic benchmark from named independent substreams."""

    def __init__(
        self,
        master_seed: int,
        *,
        seed_overrides: Mapping[str, int] | None = None,
        tiny: bool = False,
    ) -> None:
        self.master_seed = int(master_seed)
        self.streams = SeedStreams.build(master_seed, seed_overrides)
        self.tiny = bool(tiny)

    def build(self) -> BenchmarkCorpus:
        vocabulary = self._vocabulary()
        generator = self.streams.random("generator")
        trajectory = self.streams.random("trajectory")
        probe_rng = self.streams.random("probe")

        body = list(vocabulary.body_tokens)
        atoms: Dict[int, TokenSequence] = {}
        for rule in range(3):
            band = body[rule * 2 : (rule + 1) * 2]
            generator.shuffle(band)
            atoms[rule] = (band[0], band[1], band[0])

        permuted = list(body)
        generator.shuffle(permuted)
        mapping = {source: vocabulary.abstract_tokens[index] for index, source in enumerate(permuted)}
        heldout_templates = [(0, 1, 2), (2, 0, 1)]
        if self.tiny:
            heldout_templates = heldout_templates[:1]

        reference_payload = {
            "atoms": {str(k): list(v) for k, v in sorted(atoms.items())},
            "mapping": {str(k): v for k, v in sorted(mapping.items())},
            "heldout_templates": heldout_templates,
        }
        reference = ReferenceSemantics(
            atoms=atoms,
            mapping=mapping,
            heldout_templates=tuple(tuple(t) for t in heldout_templates),
            reference_fingerprint=_canonical_hash(reference_payload),
        )

        train_specs: List[Tuple[str, TokenSequence, Mapping[str, object]]] = []
        for index, token in enumerate(vocabulary.body_tokens):
            train_specs.append(
                (
                    "calibration",
                    (vocabulary.start, vocabulary.calibrate, token, mapping[token]),
                    {"body_token": token, "abstract_token": mapping[token]},
                )
            )
        for rule in range(3):
            train_specs.append(
                (
                    "rule_component",
                    (vocabulary.start, vocabulary.rule_tokens[rule]) + atoms[rule] + (vocabulary.eos,),
                    {"rule": rule},
                )
            )
        for template in ((0, 1), (1, 2)):
            train_specs.append(
                (
                    "seen_composition",
                    self._program(vocabulary, atoms, template),
                    {"template": template},
                )
            )
        if self.tiny:
            train_specs = [spec for spec in train_specs if spec[0] != "rule_component" or spec[2]["rule"] < 2]

        trajectory.shuffle(train_specs)
        training = tuple(
            self._experience(index, family, tokens, metadata)
            for index, (family, tokens, metadata) in enumerate(train_specs)
        )

        probe_specs: List[Tuple[str, TokenSequence, int, Mapping[str, object]]] = []
        for template in heldout_templates:
            prefix = self._probe_prefix(vocabulary, atoms, template, mode=vocabulary.compose)
            target = atoms[template[-1]][0]
            probe_specs.append(
                (
                    "composition",
                    prefix,
                    target,
                    {"template": template, "target_rule": template[-1]},
                )
            )
            transfer_prefix = self._probe_prefix(vocabulary, atoms, template, mode=vocabulary.transfer)
            transfer_target = mapping[target]
            probe_specs.append(
                (
                    "symbol_transfer",
                    transfer_prefix,
                    transfer_target,
                    {
                        "template": template,
                        "target_rule": template[-1],
                        "source_body_token": target,
                    },
                )
            )

        # Positive controls are intentionally outside the decisive gate.
        first_training = training[0]
        probe_specs.append(
            (
                "memorization",
                first_training.context,
                first_training.target,
                {"control": True, "training_source_id": first_training.source_id},
            )
        )
        seen_template = (0, 1)
        seen_context = self._prefix(vocabulary, atoms, (0,), mode=vocabulary.compose)
        probe_specs.append(
            (
                "tail",
                seen_context,
                atoms[1][0],
                {"control": True, "template": seen_template},
            )
        )
        probe_rng.shuffle(probe_specs)
        probes = tuple(
            self._probe(index, family, context, target, metadata)
            for index, (family, context, target, metadata) in enumerate(probe_specs)
        )

        provisional = BenchmarkManifest(
            benchmark_version=BENCHMARK_VERSION,
            name=BENCHMARK_NAME,
            master_seed=self.master_seed,
            substreams=self.streams.as_dict(),
            vocabulary_id=vocabulary.vocabulary_id,
            corpus_fingerprint="",
            training_ids=tuple(item.source_id for item in training),
            probe_ids=tuple(item.source_id for item in probes),
            probe_families=tuple(sorted({item.family for item in probes})),
            target_identifiability="one_target_per_context",
            oracle_semantics="reference_ceiling_and_achievable_calibration_audit",
        )
        corpus = BenchmarkCorpus(
            benchmark_version=BENCHMARK_VERSION,
            name=BENCHMARK_NAME,
            master_seed=self.master_seed,
            streams=self.streams,
            vocabulary=vocabulary,
            training=training,
            probes=probes,
            manifest=provisional,
            reference=reference,
        )
        manifest = BenchmarkManifest(
            benchmark_version=provisional.benchmark_version,
            name=provisional.name,
            master_seed=provisional.master_seed,
            substreams=provisional.substreams,
            vocabulary_id=provisional.vocabulary_id,
            corpus_fingerprint=corpus.fingerprint(),
            training_ids=provisional.training_ids,
            probe_ids=provisional.probe_ids,
            probe_families=provisional.probe_families,
            target_identifiability=provisional.target_identifiability,
            oracle_semantics=provisional.oracle_semantics,
        )
        corpus = BenchmarkCorpus(**{**corpus.__dict__, "manifest": manifest})
        corpus.validate()
        return corpus

    def _vocabulary(self) -> TokenVocabulary:
        body = tuple(range(6))
        abstract = tuple(range(6, 12))
        start, separator, eos = 12, 13, 14
        calibrate, compose, transfer = 15, 16, 17
        rule_tokens = (18, 19, 20)
        return TokenVocabulary(
            body_tokens=body,
            abstract_tokens=abstract,
            start=start,
            separator=separator,
            eos=eos,
            calibrate=calibrate,
            compose=compose,
            transfer=transfer,
            rule_tokens=rule_tokens,
            size=21,
            vocabulary_id="ln-dec-vocab-body6-abstract6-special5-v1",
        )

    @staticmethod
    def _program(
        vocabulary: TokenVocabulary,
        atoms: Mapping[int, TokenSequence],
        template: Sequence[int],
    ) -> TokenSequence:
        tokens: List[int] = [vocabulary.start, vocabulary.compose]
        tokens.extend(vocabulary.rule_tokens[rule] for rule in template)
        for rule in template:
            tokens.extend(atoms[rule])
        tokens.append(vocabulary.eos)
        return tuple(tokens)

    @staticmethod
    def _prefix(
        vocabulary: TokenVocabulary,
        atoms: Mapping[int, TokenSequence],
        template: Sequence[int],
        *,
        mode: int,
    ) -> TokenSequence:
        tokens: List[int] = [vocabulary.start, mode]
        tokens.extend(vocabulary.rule_tokens[rule] for rule in template)
        for rule in template:
            tokens.extend(atoms[rule])
        return tuple(tokens)

    @staticmethod
    def _probe_prefix(
        vocabulary: TokenVocabulary,
        atoms: Mapping[int, TokenSequence],
        template: Sequence[int],
        *,
        mode: int,
    ) -> TokenSequence:
        """Build an identifiable query: the target rule marker is observable.

        The held-out target atom is deliberately *not* emitted in the context,
        but its rule marker is.  This prevents the old Playgarden defect where
        one context (a completed seen composition) had both EOS and a novel
        continuation as possible labels.
        """
        tokens: List[int] = [vocabulary.start, mode]
        tokens.extend(vocabulary.rule_tokens[rule] for rule in template)
        for rule in template[:-1]:
            tokens.extend(atoms[rule])
        return tuple(tokens)

    def _experience(
        self,
        index: int,
        family: str,
        tokens: TokenSequence,
        metadata: Mapping[str, object],
    ) -> Experience:
        return Experience(
            experience_id=f"experience:{self.master_seed}:{index:04d}",
            source_id=f"train:{self.master_seed}:{index:04d}",
            episode_id=f"episode:{self.master_seed}:{index:04d}",
            context=tokens[:-1],
            target=tokens[-1],
            family=family,
            metadata=dict(metadata),
        )

    def _probe(
        self,
        index: int,
        family: str,
        context: TokenSequence,
        target: int,
        metadata: Mapping[str, object],
    ) -> Probe:
        return Probe(
            probe_id=f"probe:{self.master_seed}:{index:04d}",
            source_id=f"probe:{self.master_seed}:{index:04d}",
            family=family,
            context=tuple(context),
            target=int(target),
            metadata=dict(metadata),
        )


def _contains(haystack: Sequence[int], needle: Sequence[int]) -> bool:
    if not needle:
        return True
    n = len(needle)
    return any(tuple(haystack[index : index + n]) == tuple(needle) for index in range(len(haystack) - n + 1))


def build_corpus(
    master_seed: int = 0,
    *,
    seed_overrides: Mapping[str, int] | None = None,
    tiny: bool = False,
) -> BenchmarkCorpus:
    """Convenience factory used by tests and the isolated runner."""
    return CanonicalBenchmark(
        master_seed, seed_overrides=seed_overrides, tiny=tiny
    ).build()


__all__ = [
    "BENCHMARK_NAME",
    "BENCHMARK_VERSION",
    "DECISIVE_FAMILIES",
    "BenchmarkCorpus",
    "CanonicalBenchmark",
    "ReferenceSemantics",
    "build_corpus",
]
