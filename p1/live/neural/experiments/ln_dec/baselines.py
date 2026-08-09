"""Fair cheap baselines for the canonical P1-LN-DEC corpus."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

from p1.live.neural.experiments.ln_dec.types import Experience, Probe, TokenVocabulary


def _nll(probs: Sequence[float], target: int, eps: float = 1e-15) -> float:
    if target < 0 or target >= len(probs):
        return -math.log(eps)
    return -math.log(max(float(probs[target]), eps))


class Baseline(ABC):
    """A probe-blind predictor trained on the exact same experiences."""

    name = "baseline"

    def __init__(self, vocabulary: TokenVocabulary) -> None:
        self.vocabulary = vocabulary
        self.vocab_size = vocabulary.size

    @abstractmethod
    def fit(self, training: Sequence[Experience]) -> None:
        """Fit from training only; probes are never accepted by this API."""

    @abstractmethod
    def predict(self, context: Tuple[int, ...]) -> List[float]:
        """Return a categorical distribution over the shared vocabulary."""

    def score_items(self, probes: Sequence[Probe]) -> Dict[str, float]:
        """Return per-item NLL keyed by immutable probe ID."""
        return {probe.probe_id: _nll(self.predict(probe.context), probe.target) for probe in probes}


class UniformBaseline(Baseline):
    name = "uniform"

    def fit(self, training: Sequence[Experience]) -> None:
        return None

    def predict(self, context: Tuple[int, ...]) -> List[float]:
        return [1.0 / self.vocab_size] * self.vocab_size


class ExactLookupBaseline(Baseline):
    """B0: full-context empirical lookup with additive smoothing."""

    name = "B0"

    def __init__(self, vocabulary: TokenVocabulary, alpha: float = 0.1) -> None:
        super().__init__(vocabulary)
        if alpha <= 0.0:
            raise ValueError("alpha must be > 0")
        self.alpha = alpha
        self.rows: Dict[Tuple[int, ...], List[float]] = {}

    def fit(self, training: Sequence[Experience]) -> None:
        rows: Dict[Tuple[int, ...], List[float]] = {}
        for item in training:
            row = rows.setdefault(item.context, [0.0] * self.vocab_size)
            row[item.target] += 1.0
        self.rows = rows

    def predict(self, context: Tuple[int, ...]) -> List[float]:
        row = self.rows.get(tuple(context))
        if row is None:
            return [1.0 / self.vocab_size] * self.vocab_size
        smoothed = [value + self.alpha for value in row]
        total = sum(smoothed)
        return [value / total for value in smoothed]


class MarginalBaseline(Baseline):
    """B1: target marginal estimated from training."""

    name = "B1"

    def __init__(self, vocabulary: TokenVocabulary, alpha: float = 0.5) -> None:
        super().__init__(vocabulary)
        if alpha <= 0.0:
            raise ValueError("alpha must be > 0")
        self.alpha = alpha
        self.distribution = [1.0 / self.vocab_size] * self.vocab_size

    def fit(self, training: Sequence[Experience]) -> None:
        counts = [self.alpha] * self.vocab_size
        for item in training:
            counts[item.target] += 1.0
        total = sum(counts)
        self.distribution = [value / total for value in counts]

    def predict(self, context: Tuple[int, ...]) -> List[float]:
        return list(self.distribution)


class NgramBaseline(Baseline):
    """Order-n suffix model with deterministic backoff and smoothing."""

    def __init__(self, vocabulary: TokenVocabulary, order: int, alpha: float = 0.5) -> None:
        super().__init__(vocabulary)
        if order < 1:
            raise ValueError("order must be >= 1")
        if alpha <= 0.0:
            raise ValueError("alpha must be > 0")
        self.order = order
        self.alpha = alpha
        self.name = f"B{order + 1}" if order >= 2 else "B2"
        self.rows: Dict[Tuple[int, ...], List[float]] = {}

    def fit(self, training: Sequence[Experience]) -> None:
        counts: Dict[Tuple[int, ...], List[float]] = {}
        for item in training:
            context = tuple(item.context)
            for length in range(1, min(self.order, len(context)) + 1):
                key = context[-length:]
                row = counts.setdefault(key, [0.0] * self.vocab_size)
                row[item.target] += 1.0
        self.rows = counts

    def predict(self, context: Tuple[int, ...]) -> List[float]:
        context = tuple(context)
        for length in range(min(self.order, len(context)), 0, -1):
            row = self.rows.get(context[-length:])
            if row is not None:
                smoothed = [value + self.alpha for value in row]
                total = sum(smoothed)
                return [value / total for value in smoothed]
        return [1.0 / self.vocab_size] * self.vocab_size


class ContextRetrievalBaseline(Baseline):
    """One targeted retrieval control over the final four context tokens."""

    name = "context_retrieval"

    def __init__(self, vocabulary: TokenVocabulary, window: int = 4, alpha: float = 0.1) -> None:
        super().__init__(vocabulary)
        if window < 1:
            raise ValueError("window must be >= 1")
        self.window = window
        self.alpha = alpha
        self.rows: Dict[Tuple[int, ...], List[float]] = {}

    def fit(self, training: Sequence[Experience]) -> None:
        rows: Dict[Tuple[int, ...], List[float]] = {}
        for item in training:
            key = tuple(item.context[-self.window :])
            row = rows.setdefault(key, [0.0] * self.vocab_size)
            row[item.target] += 1.0
        self.rows = rows

    def predict(self, context: Tuple[int, ...]) -> List[float]:
        row = self.rows.get(tuple(context[-self.window :]))
        if row is None:
            return [1.0 / self.vocab_size] * self.vocab_size
        smoothed = [value + self.alpha for value in row]
        total = sum(smoothed)
        return [value / total for value in smoothed]


def train_baselines(vocabulary: TokenVocabulary, training: Sequence[Experience]) -> List[Baseline]:
    """Fit exactly the registered baseline set on one frozen training table."""
    baselines: List[Baseline] = [
        UniformBaseline(vocabulary),
        ExactLookupBaseline(vocabulary),
        MarginalBaseline(vocabulary),
        NgramBaseline(vocabulary, order=1),
        NgramBaseline(vocabulary, order=2),
        NgramBaseline(vocabulary, order=3),
        ContextRetrievalBaseline(vocabulary),
    ]
    for baseline in baselines:
        baseline.fit(training)
    return baselines


__all__ = [
    "Baseline",
    "ContextRetrievalBaseline",
    "ExactLookupBaseline",
    "MarginalBaseline",
    "NgramBaseline",
    "UniformBaseline",
    "train_baselines",
]

