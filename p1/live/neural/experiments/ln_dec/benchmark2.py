"""P1-LN-DEC-2: the chained-transformation benchmark.

Why a second corpus exists
--------------------------
The DEC-1 corpus (:mod:`benchmark`) emits a probe header that literally names
the rule marker whose atom is the answer, and the marker -> atom binding is
copyable verbatim out of a ``rule_component`` training episode.  A twelve-line
symbolic rule therefore scores 0.000 NLL on both decisive families without
learning anything (verified: ``outputs/dec_repair1_verify.py``, defect D).  A
benchmark that a trivial header parse solves cannot discriminate neural
learning from string matching, so DEC-1 cannot carry a decisive result.

The DEC-2 design
----------------
Vocabulary: six body values ``0..5``, three transformation markers ``6,7,8``,
one ``START`` token ``9``.  Nothing else -- there is no mode token, no rule
identifier, no separator, and no metadata token in the stream.

Each marker ``m_k`` denotes a hidden permutation ``P_k`` of the body values.

    component    (START, m_k, u)        -> P_k(u)
    composition  (START, m_i, m_j, u)   -> P_j(P_i(u))

Training shows every component (all 3x6) and a *subset* of ordered marker
pairs on a *subset* of values.  The withheld combinations are:

    pair_holdout   an ordered marker pair never composed in training  (DECISIVE)
    value_holdout  a seen pair applied to a value never composed      (diagnostic)

``value_holdout`` is deliberately *not* decisive.  A seen pair has four of its
six composed outputs on the record, so bijection closure alone pins the two
held-out values to a coin flip -- 0.693 nats, and 0.347 with the derangement
exclusion -- without composing anything.  That is measured, not assumed: it is
what baseline ``B6`` does.  Reporting it is useful (it separates bookkeeping
from composition) but it cannot carry a decisive claim.  ``pair_holdout`` is
immune: the composed map has *zero* observations, so closure is vacuous.

The answer to a decisive probe appears nowhere in its own context, and the two
obvious surface shortcuts are wrong *by construction*, not by luck:

    predicting P_j(u)  (the local (marker, value) suffix) requires P_i(u) = u
    predicting P_i(u)  (the first marker)                  requires P_j to fix P_i(u)

Every ``P_k`` is drawn as a derangement and every composed ``P_j . P_i`` is
required to be a derangement too, so both conditions are impossible.  The
answer also never equals the input value.  That is the property DEC-1 lacked.

A learner that exploits all three exclusions plus closure still faces a
uniform choice over three symbols on ``pair_holdout`` -- 1.099 nats against an
achievable ceiling of 0.  That gap, not the distance from chance, is what the
decisive experiment has to close.

Composition *order* is identifiable from the stream: on every master seed at
least one training composition distinguishes ``P_j . P_i`` from ``P_i . P_j``,
so the reversed-order hypothesis is falsified by the exposure rather than by
fiat.  Some decisive probes are order-insensitive because the two orders
happen to agree there; that fraction is reported, never assumed to be zero.

The permutations are redrawn per master seed, so nothing generalises across
seeds by memorisation.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from itertools import permutations
from typing import Dict, List, Mapping, Sequence, Tuple

from p1.live.neural.experiments.ln_dec.baselines2 import (
    DECISION_COMPARATORS,
    SOLVED_NLL,
    exposure_units,
    fit_ladder,
    ladder_report,
)
from p1.live.neural.experiments.ln_dec.rng import SeedStreams
from p1.live.neural.experiments.ln_dec.types import (
    BenchmarkManifest,
    CandidateView,
    Experience,
    Probe,
    TokenSequence,
)

BENCHMARK2_VERSION = "ln-dec-chain-2"
BENCHMARK2_NAME = "p1-ln-dec-chain"
#: Families that may carry a decisive result.  ``value_holdout`` was demoted
#: after ``B6`` was measured on it; see the module docstring.
DECISIVE_FAMILIES2: Tuple[str, ...] = ("pair_holdout",)
DIAGNOSTIC_FAMILIES2: Tuple[str, ...] = ("value_holdout",)
#: Everything withheld from training -- the structural invariants apply here,
#: the empirical anti-shortcut gate applies only to ``DECISIVE_FAMILIES2``.
HELDOUT_FAMILIES2: Tuple[str, ...] = DECISIVE_FAMILIES2 + DIAGNOSTIC_FAMILIES2
CONTROL_FAMILIES2: Tuple[str, ...] = ("memorization", "single_rule")

N_BODY = 6
N_MARKERS = 3
HELDOUT_PAIRS = 2
HELDOUT_VALUES = 2


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ChainVocabulary:
    """The whole DEC-2 token space: values, markers, START. Nothing else."""

    body_tokens: TokenSequence
    rule_tokens: TokenSequence
    start: int
    size: int
    vocabulary_id: str

    def validate(self, tokens: TokenSequence, *, allow_empty: bool = False) -> None:
        if not tokens and not allow_empty:
            raise ValueError("token sequence must not be empty")
        bad = [token for token in tokens if token < 0 or token >= self.size]
        if bad:
            raise ValueError(f"token(s) outside vocabulary {self.size}: {bad!r}")

    def as_dict(self) -> Dict[str, object]:
        return {
            "body_tokens": list(self.body_tokens),
            "rule_tokens": list(self.rule_tokens),
            "start": self.start,
            "size": self.size,
            "vocabulary_id": self.vocabulary_id,
        }


@dataclass(frozen=True)
class ChainSemantics:
    """Generator-private permutations and the withheld combinations."""

    permutations: Mapping[int, TokenSequence]
    heldout_pairs: Tuple[Tuple[int, int], ...]
    heldout_values: TokenSequence
    reference_fingerprint: str

    def apply(self, marker_index: int, value: int) -> int:
        return self.permutations[marker_index][value]

    def chain(self, pair: Tuple[int, int], value: int) -> int:
        return self.apply(pair[1], self.apply(pair[0], value))

    def as_dict(self) -> Dict[str, object]:
        return {
            "permutations": {str(k): list(v) for k, v in sorted(self.permutations.items())},
            "heldout_pairs": [list(p) for p in self.heldout_pairs],
            "heldout_values": list(self.heldout_values),
            "reference_fingerprint": self.reference_fingerprint,
        }


@dataclass(frozen=True)
class ChainCorpus:
    """Frozen DEC-2 corpus: public training/probes, private semantics."""

    benchmark_version: str
    name: str
    master_seed: int
    streams: SeedStreams
    vocabulary: ChainVocabulary
    training: Tuple[Experience, ...]
    probes: Tuple[Probe, ...]
    manifest: BenchmarkManifest
    reference: ChainSemantics = field(repr=False, compare=False)

    @property
    def training_ids(self) -> Tuple[str, ...]:
        return tuple(item.source_id for item in self.training)

    @property
    def probe_ids(self) -> Tuple[str, ...]:
        return tuple(item.source_id for item in self.probes)

    def stream(self) -> Tuple[TokenSequence, ...]:
        """The exposure a candidate receives, in order: one tuple per episode."""
        return tuple(item.sequence() for item in self.training)

    def candidate_view(self) -> CandidateView:
        return CandidateView(self.vocabulary, self.training, self.manifest)

    def probes_for(self, family: str | None = None) -> Tuple[Probe, ...]:
        if family is None:
            return self.probes
        return tuple(probe for probe in self.probes if probe.family == family)

    def decisive_probes(self) -> Tuple[Probe, ...]:
        return tuple(p for p in self.probes if p.family in DECISIVE_FAMILIES2)

    def heldout_probes(self) -> Tuple[Probe, ...]:
        """Decisive *and* diagnostic probes: everything withheld from training."""
        return tuple(p for p in self.probes if p.family in HELDOUT_FAMILIES2)

    def exposure(self) -> Dict[str, int]:
        return exposure_units(self.stream())

    # -- invariants --------------------------------------------------------

    def validate(self) -> None:
        """Every cheap corpus, leakage, and anti-shortcut invariant."""
        self.vocabulary.validate(tuple(t for e in self.training for t in e.sequence()))
        self.vocabulary.validate(tuple(t for p in self.probes for t in p.sequence()))

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
        self._assert_shortcuts_wrong()
        self._assert_no_answer_in_context()
        self._assert_composition_order_identifiable()
        if self.fingerprint() != self.manifest.corpus_fingerprint:
            raise AssertionError("frozen corpus fingerprint does not match manifest")

    def _assert_target_identifiability(self) -> None:
        targets: Dict[TokenSequence, set[int]] = {}
        for probe in self.probes:
            targets.setdefault(probe.context, set()).add(probe.target)
        bad = {c: v for c, v in targets.items() if len(v) != 1}
        if bad:
            raise AssertionError(f"probe context has multiple targets: {bad!r}")

    def _assert_target_grounding(self) -> None:
        """Every held-out answer is a symbol the candidate has predicted before."""
        observed = {token for e in self.training for token in e.sequence()[1:]}
        missing = {
            p.probe_id: p.target for p in self.heldout_probes() if p.target not in observed
        }
        if missing:
            raise AssertionError(f"held-out targets are not grounded: {missing!r}")

    def _assert_decisive_exclusion(self) -> None:
        """No held-out context or answer is present contiguously in training."""
        sequences = [e.sequence() for e in self.training]
        contexts = {e.context for e in self.training}
        prefixes = {seq[:i] for seq in sequences for i in range(1, len(seq) + 1)}
        for probe in self.heldout_probes():
            if any(_contains(seq, probe.sequence()) for seq in sequences):
                raise AssertionError(f"held-out answer leakage: {probe.probe_id}")
            if probe.context in contexts or probe.context in prefixes:
                raise AssertionError(f"held-out context seen in training: {probe.probe_id}")

    def _assert_shortcuts_wrong(self) -> None:
        """Both single-marker parses must be wrong on every held-out probe."""
        for probe in self.heldout_probes():
            first, second = probe.metadata["pair"]  # type: ignore[misc]
            value = int(probe.context[-1])
            last_marker = self.reference.apply(int(second), value)
            first_marker = self.reference.apply(int(first), value)
            if probe.target == last_marker:
                raise AssertionError(f"last-marker shortcut is correct: {probe.probe_id}")
            if probe.target == first_marker:
                raise AssertionError(f"first-marker shortcut is correct: {probe.probe_id}")

    def _assert_no_answer_in_context(self) -> None:
        for probe in self.heldout_probes():
            if probe.target in probe.context:
                raise AssertionError(f"answer token appears in context: {probe.probe_id}")

    def _assert_composition_order_identifiable(self) -> None:
        """The training stream must falsify the reversed-order hypothesis.

        ``P_j . P_i`` and ``P_i . P_j`` agree on some inputs by coincidence.  If
        they agreed on *every* training composition the ground truth of a
        decisive probe would not be recoverable from the exposure, and a
        candidate could be marked wrong for holding a hypothesis the data never
        ruled out.  At least one training composition must distinguish them.
        """
        discriminating = sum(
            1
            for e in self.training
            if e.family == "composition"
            and self.reference.chain(tuple(e.metadata["pair"]), int(e.context[-1]))  # type: ignore[arg-type]
            != self.reference.chain(tuple(reversed(e.metadata["pair"])), int(e.context[-1]))  # type: ignore[arg-type]
        )
        if discriminating == 0:
            raise AssertionError("composition order is not identifiable from training")

    def order_insensitive_fraction(self) -> float:
        """Share of decisive probes where both composition orders agree.

        Reported, not gated: those probes are still correctly labelled, they
        just carry no evidence about order.
        """
        probes = self.decisive_probes()
        agree = sum(
            1
            for p in probes
            if self.reference.chain(tuple(p.metadata["pair"]), int(p.context[-1]))  # type: ignore[arg-type]
            == self.reference.chain(tuple(reversed(p.metadata["pair"])), int(p.context[-1]))  # type: ignore[arg-type]
        )
        return agree / len(probes) if probes else 0.0

    def assert_cheap_baselines_fail(self, *, threshold: float = SOLVED_NLL) -> Dict[str, float]:
        """Empirical anti-shortcut gate over the full statistical ladder.

        Returns the per-model mean NLL on the decisive families and raises if
        any *statistical* member scores below ``threshold`` -- i.e. if the
        benchmark is solvable without composing.

        This gate is not a proof of unsolvability: the ladder is finite and a
        cleverer exposure-matched statistic is not excluded.  It is a
        falsifiable check on the specific shortcuts we know about, and the
        by-construction guarantees in ``_assert_shortcuts_wrong`` carry the
        part that a finite ladder cannot.
        """
        models = fit_ladder(self.vocabulary.size, self.stream(), N_BODY)
        items = [(p.context, p.target) for p in self.decisive_probes()]
        report = ladder_report(models, items)
        solved = {
            name: value
            for name, value in report.items()
            if name in DECISION_COMPARATORS and value < threshold
        }
        if solved:
            raise AssertionError(
                f"statistical baseline(s) solve the decisive families: {solved!r}"
            )
        return report

    def fingerprint(self) -> str:
        return _canonical_hash(
            {
                "benchmark_version": self.benchmark_version,
                "name": self.name,
                "master_seed": self.master_seed,
                "streams": self.streams.as_dict(),
                "vocabulary": self.vocabulary.as_dict(),
                "training": [item.as_dict() for item in self.training],
                "probes": [item.as_dict() for item in self.probes],
                "reference_fingerprint": self.reference.reference_fingerprint,
            }
        )

    def as_public_dict(self) -> Dict[str, object]:
        """Serialise the corpus without exposing the permutations."""
        return {
            "benchmark_version": self.benchmark_version,
            "name": self.name,
            "master_seed": self.master_seed,
            "streams": self.streams.as_dict(),
            "vocabulary": self.vocabulary.as_dict(),
            "training": [item.as_dict() for item in self.training],
            "probes": [item.as_dict() for item in self.probes],
            "manifest": self.manifest.as_dict(),
            "exposure": self.exposure(),
        }


def _contains(haystack: Sequence[int], needle: Sequence[int]) -> bool:
    n = len(needle)
    return any(
        tuple(haystack[i : i + n]) == tuple(needle) for i in range(len(haystack) - n + 1)
    )


def _is_derangement(perm: Sequence[int]) -> bool:
    return all(perm[i] != i for i in range(len(perm)))


def _compose(outer: Sequence[int], inner: Sequence[int]) -> Tuple[int, ...]:
    """``(outer . inner)(u) = outer[inner[u]]``."""
    return tuple(outer[inner[u]] for u in range(len(inner)))


class ChainBenchmark:
    """Build one deterministic DEC-2 corpus from named independent substreams."""

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

    # -- generator ---------------------------------------------------------

    def _vocabulary(self) -> ChainVocabulary:
        return ChainVocabulary(
            body_tokens=tuple(range(N_BODY)),
            rule_tokens=tuple(range(N_BODY, N_BODY + N_MARKERS)),
            start=N_BODY + N_MARKERS,
            size=N_BODY + N_MARKERS + 1,
            vocabulary_id=f"ln-dec2-vocab-body{N_BODY}-markers{N_MARKERS}-start-v1",
        )

    def _permutations(self, rng) -> Dict[int, Tuple[int, ...]]:
        """Derangements whose pairwise compositions are also derangements.

        The composition condition is what makes both single-marker shortcuts
        provably wrong; see the module docstring.
        """
        pool = [p for p in permutations(range(N_BODY)) if _is_derangement(p)]
        for _ in range(20000):
            picked = rng.sample(pool, N_MARKERS)
            if all(
                _is_derangement(_compose(picked[j], picked[i]))
                for i in range(N_MARKERS)
                for j in range(N_MARKERS)
                if i != j
            ):
                return {k: picked[k] for k in range(N_MARKERS)}
        raise RuntimeError("could not draw admissible permutations")

    def _split(self, rng) -> Tuple[Tuple[Tuple[int, int], ...], Tuple[Tuple[int, int], ...], TokenSequence, TokenSequence]:
        """Choose held-out ordered pairs and held-out values.

        Every marker must still appear in both positions among the seen pairs,
        otherwise a held-out pair is unlearnable for reasons unrelated to
        composition.
        """
        all_pairs = [(i, j) for i in range(N_MARKERS) for j in range(N_MARKERS) if i != j]
        for _ in range(20000):
            heldout = tuple(sorted(rng.sample(all_pairs, HELDOUT_PAIRS)))
            seen = tuple(p for p in all_pairs if p not in heldout)
            firsts = {p[0] for p in seen}
            seconds = {p[1] for p in seen}
            if len(firsts) == N_MARKERS and len(seconds) == N_MARKERS:
                break
        else:  # pragma: no cover - the constraint is satisfiable by inspection
            raise RuntimeError("could not split marker pairs")
        values = list(range(N_BODY))
        rng.shuffle(values)
        heldout_values = tuple(sorted(values[:HELDOUT_VALUES]))
        seen_values = tuple(sorted(values[HELDOUT_VALUES:]))
        return heldout, seen, heldout_values, seen_values

    def build(self) -> ChainCorpus:
        vocabulary = self._vocabulary()
        generator = self.streams.random("generator")
        trajectory = self.streams.random("trajectory")
        probe_rng = self.streams.random("probe")

        perms = self._permutations(generator)
        heldout_pairs, seen_pairs, heldout_values, seen_values = self._split(generator)
        markers = vocabulary.rule_tokens
        start = vocabulary.start

        reference = ChainSemantics(
            permutations=perms,
            heldout_pairs=heldout_pairs,
            heldout_values=heldout_values,
            reference_fingerprint=_canonical_hash(
                {
                    "permutations": {str(k): list(v) for k, v in sorted(perms.items())},
                    "heldout_pairs": [list(p) for p in heldout_pairs],
                    "heldout_values": list(heldout_values),
                }
            ),
        )

        specs: List[Tuple[str, TokenSequence, Dict[str, object]]] = []
        for k in range(N_MARKERS):
            for u in range(N_BODY):
                specs.append(
                    (
                        "component",
                        (start, markers[k], u, perms[k][u]),
                        {"marker": k, "value": u},
                    )
                )
        for pair in seen_pairs:
            for u in seen_values:
                specs.append(
                    (
                        "composition",
                        (start, markers[pair[0]], markers[pair[1]], u, reference.chain(pair, u)),
                        {"pair": list(pair), "value": u},
                    )
                )
        if self.tiny:
            specs = specs[: len(specs) // 2]

        trajectory.shuffle(specs)
        training = tuple(
            self._experience(index, family, tokens, meta)
            for index, (family, tokens, meta) in enumerate(specs)
        )

        probe_specs: List[Tuple[str, TokenSequence, int, Dict[str, object]]] = []
        for pair in heldout_pairs:
            for u in seen_values:
                probe_specs.append(
                    (
                        "pair_holdout",
                        (start, markers[pair[0]], markers[pair[1]], u),
                        reference.chain(pair, u),
                        {"pair": list(pair), "value": u, "withheld": "pair"},
                    )
                )
        for pair in seen_pairs:
            for u in heldout_values:
                probe_specs.append(
                    (
                        "value_holdout",
                        (start, markers[pair[0]], markers[pair[1]], u),
                        reference.chain(pair, u),
                        {"pair": list(pair), "value": u, "withheld": "value"},
                    )
                )
        seen_compositions = [e for e in training if e.family == "composition"]
        seen_components = [e for e in training if e.family == "component"]
        for e in probe_rng.sample(seen_compositions, min(4, len(seen_compositions))):
            probe_specs.append(
                ("memorization", e.context, e.target, {"control": True, **dict(e.metadata)})
            )
        for e in probe_rng.sample(seen_components, min(4, len(seen_components))):
            probe_specs.append(
                ("single_rule", e.context, e.target, {"control": True, **dict(e.metadata)})
            )

        probe_rng.shuffle(probe_specs)
        probes = tuple(
            self._probe(index, family, context, target, meta)
            for index, (family, context, target, meta) in enumerate(probe_specs)
        )

        provisional = BenchmarkManifest(
            benchmark_version=BENCHMARK2_VERSION,
            name=BENCHMARK2_NAME,
            master_seed=self.master_seed,
            substreams=self.streams.as_dict(),
            vocabulary_id=vocabulary.vocabulary_id,
            corpus_fingerprint="",
            training_ids=tuple(item.source_id for item in training),
            probe_ids=tuple(item.source_id for item in probes),
            probe_families=tuple(sorted({item.family for item in probes})),
            target_identifiability="one_target_per_context",
            oracle_semantics="achievable_ceiling_by_induction_no_private_state",
        )
        corpus = ChainCorpus(
            benchmark_version=BENCHMARK2_VERSION,
            name=BENCHMARK2_NAME,
            master_seed=self.master_seed,
            streams=self.streams,
            vocabulary=vocabulary,
            training=training,
            probes=probes,
            manifest=provisional,
            reference=reference,
        )
        manifest = BenchmarkManifest(
            **{**provisional.__dict__, "corpus_fingerprint": corpus.fingerprint()}
        )
        corpus = ChainCorpus(**{**corpus.__dict__, "manifest": manifest})
        corpus.validate()
        return corpus

    def _experience(
        self, index: int, family: str, tokens: TokenSequence, meta: Mapping[str, object]
    ) -> Experience:
        return Experience(
            experience_id=f"experience2:{self.master_seed}:{index:04d}",
            source_id=f"train:{self.master_seed}:{index:04d}",
            episode_id=f"episode2:{self.master_seed}:{index:04d}",
            context=tuple(tokens[:-1]),
            target=int(tokens[-1]),
            family=family,
            metadata=dict(meta),
        )

    def _probe(
        self,
        index: int,
        family: str,
        context: TokenSequence,
        target: int,
        meta: Mapping[str, object],
    ) -> Probe:
        return Probe(
            probe_id=f"probe:{self.master_seed}:{index:04d}",
            source_id=f"probe:{self.master_seed}:{index:04d}",
            family=family,
            context=tuple(context),
            target=int(target),
            metadata=dict(meta),
        )


def build_chain_corpus(
    master_seed: int = 0,
    *,
    seed_overrides: Mapping[str, int] | None = None,
    tiny: bool = False,
) -> ChainCorpus:
    """Convenience factory used by tests, diagnostics, and the runner."""
    return ChainBenchmark(master_seed, seed_overrides=seed_overrides, tiny=tiny).build()


def relabel_body(corpus: ChainCorpus, permutation: Mapping[int, int]) -> Tuple[
    Tuple[TokenSequence, ...], Tuple[Tuple[TokenSequence, int], ...]
]:
    """Apply a bijection to the body tokens of the stream and the probes.

    Used by the anti-memorisation test: relabelling leaves the task structure
    identical, so any model whose competence survives is using structure, and
    any model whose competence is destroyed had memorised absolute symbols.
    """
    body = set(corpus.vocabulary.body_tokens)
    if set(permutation) != body or set(permutation.values()) != body:
        raise ValueError("permutation must be a bijection on the body tokens")

    def relabel(tokens: Sequence[int]) -> TokenSequence:
        return tuple(permutation.get(t, t) for t in tokens)

    stream = tuple(relabel(e.sequence()) for e in corpus.training)
    probes = tuple(
        (relabel(p.context), permutation[p.target]) for p in corpus.decisive_probes()
    )
    return stream, probes


def uniform_nll(corpus: ChainCorpus) -> float:
    """Chance-level NLL over the whole vocabulary, for reporting scale."""
    return math.log(corpus.vocabulary.size)


__all__ = [
    "BENCHMARK2_NAME",
    "BENCHMARK2_VERSION",
    "CONTROL_FAMILIES2",
    "DECISIVE_FAMILIES2",
    "DIAGNOSTIC_FAMILIES2",
    "HELDOUT_FAMILIES2",
    "N_BODY",
    "ChainBenchmark",
    "ChainCorpus",
    "ChainSemantics",
    "ChainVocabulary",
    "build_chain_corpus",
    "relabel_body",
    "uniform_nll",
]
