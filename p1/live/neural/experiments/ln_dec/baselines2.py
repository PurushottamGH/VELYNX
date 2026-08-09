"""Exposure-matched baseline ladder for the P1-LN-DEC-2 corpus.

Every model here is fitted from *exactly* the stream NN-0 is trained on: the
ordered list of training episodes, scored as next-token prediction at every
position.  That is the frozen definition of one unit of training exposure --
one token transition in the ordered training stream -- so no member of this
ladder can be accused of having seen less (or more) than the candidate.

The old :mod:`baselines` module fits ``(full context -> final target)`` rows
only, which is 11 rows against NN-0's 53 gradient steps on the DEC-1 corpus.
That asymmetry is the reason this module exists; see
``outputs/P1_LIVE_NN_DEC_REPAIR_1_REPORT.md`` section 6.

Ladder
------
``B_unif``   uniform over the whole vocabulary
``B0``       exact full-prefix lookup (no backoff)
``B1``       marginal next-token distribution
``B2``       order-1 n-gram
``B3``       order-2 n-gram
``B4``       longest-suffix backoff n-gram -- strongest exposure-matched
             statistical model on this stream
``B6``       marker-sequence bijection closure -- the strongest model that
             does *not* compose
``B5a``      symbolic chain induction -- the *achievable-learner ceiling*
``B5b``      symbolic naive last-marker parse -- the shortcut adversary

``B5a``/``B5b`` are program-induction baselines, not statistical ones: they are
handed the episode grammar a priori and only *induce the tables* from the
stream.  They are reported, never used as the decision comparator; see
``DECISION_COMPARATORS``.

``B6`` *is* a decision comparator.  It is handed the same grammar prior as
``B5a`` but is forbidden to chain: it treats each marker sequence as an opaque
label and reasons only about what a bijection plus the exclusions it observed
in training allow.  Beating ``B6`` is the part of the claim that cannot be had
by bookkeeping, so it belongs in the gate rather than in the commentary.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, List, Mapping, Sequence, Tuple

TokenSequence = Tuple[int, ...]
Stream = Sequence[TokenSequence]

#: Ladder members that may serve as the decision comparator.  ``B5a``/``B5b``
#: are excluded by construction and by pre-registration; every model that could
#: reach the target accuracy *without* composing is included.
DECISION_COMPARATORS: Tuple[str, ...] = (
    "B_unif",
    "B0",
    "B1",
    "B2",
    "B3",
    "B4",
    "B6",
)

#: Pre-registered "this benchmark is solved" threshold, in nats.  ``1.0`` nat is
#: ``p(correct) >= 1/e ~= 0.368``, i.e. more than twice the 1/6 chance rate on a
#: six-symbol answer space.  Stated before measurement, not fitted to it.
SOLVED_NLL = 1.0


def _normalise(counts: Sequence[float]) -> List[float]:
    total = float(sum(counts))
    if total <= 0.0:
        return [1.0 / len(counts)] * len(counts)
    return [float(c) / total for c in counts]


class StreamBaseline:
    """Fit from the ordered training stream; predict a next-token pmf."""

    name = "base"

    def __init__(self, vocab_size: int) -> None:
        self.V = vocab_size

    def fit(self, stream: Stream) -> "StreamBaseline":  # pragma: no cover - abstract
        raise NotImplementedError

    def predict(self, context: Sequence[int]) -> List[float]:  # pragma: no cover
        raise NotImplementedError

    def nll(self, context: Sequence[int], target: int) -> float:
        return -math.log(max(self.predict(context)[target], 1e-15))


class Uniform(StreamBaseline):
    name = "B_unif"

    def fit(self, stream: Stream) -> "Uniform":
        return self

    def predict(self, context: Sequence[int]) -> List[float]:
        return [1.0 / self.V] * self.V


class ExactPrefix(StreamBaseline):
    """B0: memorise every full prefix from the episode start. No backoff."""

    name = "B0"

    def __init__(self, vocab_size: int) -> None:
        super().__init__(vocab_size)
        self.rows: Dict[TokenSequence, List[float]] = {}

    def fit(self, stream: Stream) -> "ExactPrefix":
        for episode in stream:
            for i in range(1, len(episode)):
                row = self.rows.setdefault(tuple(episode[:i]), [0.0] * self.V)
                row[episode[i]] += 1.0
        return self

    def predict(self, context: Sequence[int]) -> List[float]:
        row = self.rows.get(tuple(context))
        return [1.0 / self.V] * self.V if row is None else _normalise(row)


class Marginal(StreamBaseline):
    """B1: the context-free next-token distribution -- the informed floor."""

    name = "B1"

    def __init__(self, vocab_size: int) -> None:
        super().__init__(vocab_size)
        self.row = [0.0] * vocab_size

    def fit(self, stream: Stream) -> "Marginal":
        for episode in stream:
            for token in episode[1:]:
                self.row[token] += 1.0
        return self

    def predict(self, context: Sequence[int]) -> List[float]:
        return _normalise(self.row)


class Ngram(StreamBaseline):
    """B2/B3: fixed-order n-gram, add-alpha, backing off to the marginal."""

    def __init__(self, vocab_size: int, order: int, alpha: float = 0.5) -> None:
        super().__init__(vocab_size)
        self.order = int(order)
        self.alpha = float(alpha)
        self.name = f"B{order + 1}"
        self.rows: Dict[TokenSequence, List[float]] = defaultdict(
            lambda: [0.0] * vocab_size
        )
        self._marginal = Marginal(vocab_size)

    def fit(self, stream: Stream) -> "Ngram":
        self._marginal.fit(stream)
        for episode in stream:
            for i in range(1, len(episode)):
                start = max(0, i - self.order)
                self.rows[tuple(episode[start:i])][episode[i]] += 1.0
        return self

    def predict(self, context: Sequence[int]) -> List[float]:
        key = tuple(context[-self.order :])
        row = self.rows.get(key)
        if row is None:
            return self._marginal.predict(context)
        return _normalise([c + self.alpha for c in row])


class BackoffNgram(StreamBaseline):
    """B4: longest seen suffix wins; add-alpha; marginal as the final backoff.

    This is the strongest purely statistical model available on this exposure:
    it uses the full context when the full context was seen and degrades one
    token at a time otherwise.
    """

    name = "B4"

    def __init__(self, vocab_size: int, max_order: int = 8, alpha: float = 0.5) -> None:
        super().__init__(vocab_size)
        self.max_order = int(max_order)
        self.alpha = float(alpha)
        self.rows: Dict[TokenSequence, List[float]] = defaultdict(
            lambda: [0.0] * vocab_size
        )
        self._marginal = Marginal(vocab_size)

    def fit(self, stream: Stream) -> "BackoffNgram":
        self._marginal.fit(stream)
        for episode in stream:
            for i in range(1, len(episode)):
                for order in range(1, min(self.max_order, i) + 1):
                    self.rows[tuple(episode[i - order : i])][episode[i]] += 1.0
        return self

    def predict(self, context: Sequence[int]) -> List[float]:
        for order in range(min(self.max_order, len(context)), 0, -1):
            row = self.rows.get(tuple(context[-order:]))
            if row is not None:
                return _normalise([c + self.alpha for c in row])
        return self._marginal.predict(context)


class SymbolicChain(StreamBaseline):
    """B5a: induce one transformation table per marker, then chain them.

    Given a priori: episodes are ``(START, marker, value, outcome)`` for a
    component and ``(START, m_i, m_j, value, outcome)`` for a composition, and
    composition applies markers left to right.  Induced from the stream: the
    marker tables themselves.  Nothing private to the generator is used, which
    is what makes this an *achievable* ceiling rather than an answer key -- a
    learner with the right inductive bias could reach it from the same data.
    """

    name = "B5a"

    def __init__(self, vocab_size: int) -> None:
        super().__init__(vocab_size)
        self.table: Dict[int, Dict[int, int]] = defaultdict(dict)

    def fit(self, stream: Stream) -> "SymbolicChain":
        for episode in stream:
            if len(episode) == 4:  # (START, marker, value, outcome)
                _, marker, value, outcome = episode
                self.table[marker][value] = outcome
        return self

    def _apply(self, markers: Sequence[int], value: int) -> int | None:
        current = value
        for marker in markers:
            row = self.table.get(marker)
            if row is None or current not in row:
                return None
            current = row[current]
        return current

    def predict(self, context: Sequence[int]) -> List[float]:
        if len(context) < 3:
            return [1.0 / self.V] * self.V
        markers, value = context[1:-1], context[-1]
        answer = self._apply(markers, value)
        if answer is None:
            return [1.0 / self.V] * self.V
        pmf = [1e-12] * self.V
        pmf[answer] = 1.0
        return _normalise(pmf)


class SymbolicNaive(SymbolicChain):
    """B5b: the shortcut adversary -- apply only the *last* marker.

    This is what a model does if it reads the local suffix ``(marker, value)``
    and ignores everything before it.  The corpus is constructed so that this
    answer is always wrong on decisive items.
    """

    name = "B5b"

    def predict(self, context: Sequence[int]) -> List[float]:
        if len(context) < 3:
            return [1.0 / self.V] * self.V
        answer = self._apply(context[-2:-1], context[-1])
        if answer is None:
            return [1.0 / self.V] * self.V
        pmf = [1e-12] * self.V
        pmf[answer] = 1.0
        return _normalise(pmf)


class PairBijection(SymbolicChain):
    """B6: the strongest model on this stream that never composes.

    It shares ``B5a``'s grammar prior -- it knows where the marker run stops and
    the value begins -- and induces the same per-marker tables.  What it may not
    do is chain them.  It treats the whole marker run as an opaque label and
    answers from three things it can read off the stream:

    * the ``(marker run, value) -> outcome`` rows it actually saw;
    * bijection closure -- one marker run never sends two values to the same
      outcome, so an unseen value cannot take an outcome already spoken for;
    * exclusions that held in *every* training composition -- the outcome is
      never the input value, never the first marker's own answer, never the last
      marker's own answer.

    That is enough to pin a held-out *value* on a seen marker run to within a
    coin flip, which is why ``value_holdout`` is not a decisive family.  It is
    not enough for a held-out marker *run*, where closure is vacuous.
    """

    name = "B6"

    def __init__(self, vocab_size: int, body_size: int = 6) -> None:
        super().__init__(vocab_size)
        self.body: Tuple[int, ...] = tuple(range(body_size))
        self.rows: Dict[TokenSequence, Dict[int, int]] = defaultdict(dict)
        self.exclude_identity = True
        self.exclude_first = True
        self.exclude_last = True

    def fit(self, stream: Stream) -> "PairBijection":
        super().fit(stream)
        for episode in stream:
            if len(episode) < 4:
                continue
            self.rows[tuple(episode[1:-2])][episode[-2]] = episode[-1]
        for episode in stream:
            if len(episode) < 5:  # only a composition can falsify an exclusion
                continue
            markers, value, outcome = tuple(episode[1:-2]), episode[-2], episode[-1]
            if outcome == value:
                self.exclude_identity = False
            if self._apply(markers[:1], value) == outcome:
                self.exclude_first = False
            if self._apply(markers[-1:], value) == outcome:
                self.exclude_last = False
        return self

    def predict(self, context: Sequence[int]) -> List[float]:
        if len(context) < 3:
            return [1.0 / self.V] * self.V
        markers, value = tuple(context[1:-1]), context[-1]
        row = self.rows.get(markers, {})
        pmf = [1e-12] * self.V
        if value in row:
            pmf[row[value]] = 1.0
            return _normalise(pmf)
        taken = set(row.values())
        blocked = set(taken)
        if self.exclude_identity:
            blocked.add(value)
        if self.exclude_first:
            blocked.add(self._apply(markers[:1], value))
        if self.exclude_last:
            blocked.add(self._apply(markers[-1:], value))
        candidates = [u for u in self.body if u not in blocked]
        if not candidates:  # exclusions over-constrained; fall back to closure
            candidates = [u for u in self.body if u not in taken] or list(self.body)
        for token in candidates:
            pmf[token] = 1.0 / len(candidates)
        return _normalise(pmf)


def build_ladder(vocab_size: int, body_size: int = 6) -> Tuple[StreamBaseline, ...]:
    """The full ladder, unfitted, in reporting order."""
    return (
        Uniform(vocab_size),
        ExactPrefix(vocab_size),
        Marginal(vocab_size),
        Ngram(vocab_size, 1),
        Ngram(vocab_size, 2),
        BackoffNgram(vocab_size),
        PairBijection(vocab_size, body_size),
        SymbolicChain(vocab_size),
        SymbolicNaive(vocab_size),
    )


def fit_ladder(
    vocab_size: int, stream: Stream, body_size: int = 6
) -> Dict[str, StreamBaseline]:
    """Fit every ladder member on one identical training stream."""
    return {
        model.name: model.fit(stream)
        for model in build_ladder(vocab_size, body_size)
    }


def exposure_units(stream: Stream) -> Dict[str, int]:
    """Count the frozen exposure unit: token transitions in the ordered stream."""
    transitions = sum(len(episode) - 1 for episode in stream)
    distinct = {
        (episode[i], episode[i + 1])
        for episode in stream
        for i in range(len(episode) - 1)
    }
    return {
        "episodes": len(stream),
        "tokens": sum(len(episode) for episode in stream),
        "transitions": transitions,
        "distinct_transitions": len(distinct),
    }


def ladder_report(
    models: Mapping[str, StreamBaseline],
    items: Sequence[Tuple[Sequence[int], int]],
) -> Dict[str, float]:
    """Mean NLL per ladder member over ``(context, target)`` items."""
    if not items:
        raise ValueError("no items to score")
    return {
        name: sum(model.nll(context, target) for context, target in items) / len(items)
        for name, model in models.items()
    }


def ladder_accuracy(
    models: Mapping[str, StreamBaseline],
    items: Sequence[Tuple[Sequence[int], int]],
) -> Dict[str, float]:
    """Top-1 accuracy per ladder member.

    Reported alongside NLL because a deterministic baseline that is *always
    wrong* scores an NLL set by the probability floor, not by the data; its
    magnitude is an artefact and only the accuracy is interpretable.
    """
    if not items:
        raise ValueError("no items to score")
    scores: Dict[str, float] = {}
    for name, model in models.items():
        hits = 0
        for context, target in items:
            pmf = model.predict(context)
            hits += int(max(range(len(pmf)), key=pmf.__getitem__) == target)
        scores[name] = hits / len(items)
    return scores


__all__ = [
    "DECISION_COMPARATORS",
    "SOLVED_NLL",
    "BackoffNgram",
    "ExactPrefix",
    "Marginal",
    "Ngram",
    "PairBijection",
    "StreamBaseline",
    "SymbolicChain",
    "SymbolicNaive",
    "Uniform",
    "build_ladder",
    "exposure_units",
    "fit_ladder",
    "ladder_accuracy",
    "ladder_report",
]
