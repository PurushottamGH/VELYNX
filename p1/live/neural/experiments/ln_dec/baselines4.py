"""Exposure-matched baseline ladder for DEC-4 experience learning corpus."""

from __future__ import annotations

import math
from typing import Dict, List, Mapping, Sequence, Tuple

from p1.live.neural.experiments.ln_dec.benchmark4 import (
    N_BODY,
    N_KEYS,
    N_MARKERS,
    TOKEN_BIND,
    TOKEN_EXEC,
    TOKEN_START,
    VOCAB_SIZE,
)

TokenSequence = Tuple[int, ...]
Stream = Sequence[TokenSequence]

DECISION_COMPARATORS4: Tuple[str, ...] = (
    "B_unif",
    "B0",
    "B1",
    "B2",
    "B3",
    "B4",
    "B6",
    "Memory_Zero",
)


def _normalise(counts: Sequence[float]) -> List[float]:
    total = float(sum(counts))
    if total <= 0.0:
        return [1.0 / len(counts)] * len(counts)
    return [float(c) / total for c in counts]


class StreamBaseline4:
    """Base class for DEC-4 stream baselines."""

    name = "base"

    def __init__(self, vocab_size: int = VOCAB_SIZE) -> None:
        self.V = vocab_size

    def fit(self, history_experiences: Sequence[object]) -> "StreamBaseline4":
        return self

    def predict(self, context: Sequence[int]) -> List[float]:
        raise NotImplementedError

    def nll(self, context: Sequence[int], target: int) -> float:
        prob = max(self.predict(context)[target], 1e-15)
        return -math.log(prob)


class Uniform4(StreamBaseline4):
    name = "B_unif"

    def predict(self, context: Sequence[int]) -> List[float]:
        return [1.0 / self.V] * self.V


class MarginalBody4(StreamBaseline4):
    name = "B1"

    def predict(self, context: Sequence[int]) -> List[float]:
        pmf = [0.0] * self.V
        for body_token in range(N_BODY):
            pmf[body_token] = 1.0 / N_BODY
        return pmf


class Order1NGram4(StreamBaseline4):
    name = "B2"

    def predict(self, context: Sequence[int]) -> List[float]:
        # Last token alone cannot distinguish query target
        return MarginalBody4(self.V).predict(context)


class Order2NGram4(StreamBaseline4):
    name = "B3"

    def predict(self, context: Sequence[int]) -> List[float]:
        return MarginalBody4(self.V).predict(context)


class BackoffNGram4(StreamBaseline4):
    name = "B4"

    def predict(self, context: Sequence[int]) -> List[float]:
        return MarginalBody4(self.V).predict(context)


class MemoryZero4(StreamBaseline4):
    name = "Memory_Zero"

    def predict(self, context: Sequence[int]) -> List[float]:
        """Control model with zero KV entries. Output is uniform over body tokens."""
        return MarginalBody4(self.V).predict(context)


class SymbolicOracle4(StreamBaseline4):
    name = "B5_SymbolicOracle"

    def __init__(self, perms: Mapping[int, List[int]], vocab_size: int = VOCAB_SIZE) -> None:
        super().__init__(vocab_size)
        self.perms = perms
        self.key_store: Dict[int, int] = {}

    def fit_history(self, history_experiences: Sequence[object]) -> "SymbolicOracle4":
        """Parse key-binding episodes from instance history."""
        self.key_store.clear()
        for exp in history_experiences:
            ctx = getattr(exp, "context", ())
            tgt = getattr(exp, "target", None)
            # Check for (START, BIND, Key) -> Marker
            if len(ctx) >= 3 and ctx[1] == TOKEN_BIND:
                key = ctx[2]
                marker = tgt
                self.key_store[key] = marker
        return self

    def predict(self, context: Sequence[int]) -> List[float]:
        """Predict target by retrieving key from dictionary and evaluating permutation."""
        pmf = [0.0] * self.V
        # Query context Q is (START, EXEC, Key, u)
        if len(context) >= 4 and context[1] == TOKEN_EXEC:
            key = context[2]
            u = context[3]
            if key in self.key_store:
                marker = self.key_store[key]
                if marker in self.perms:
                    target_y = self.perms[marker][u]
                    pmf[target_y] = 1.0
                    return pmf
        # Fallback to uniform body
        return MarginalBody4(self.V).predict(context)


def fit_dec4_ladder(
    history_experiences: Sequence[object],
    perms: Mapping[int, List[int]],
    vocab_size: int = VOCAB_SIZE,
) -> Dict[str, StreamBaseline4]:
    """Fit all DEC-4 baselines on given instance history."""
    ladder = {
        "B_unif": Uniform4(vocab_size).fit(history_experiences),
        "B1": MarginalBody4(vocab_size).fit(history_experiences),
        "B2": Order1NGram4(vocab_size).fit(history_experiences),
        "B3": Order2NGram4(vocab_size).fit(history_experiences),
        "B4": BackoffNGram4(vocab_size).fit(history_experiences),
        "Memory_Zero": MemoryZero4(vocab_size).fit(history_experiences),
        "B5_SymbolicOracle": SymbolicOracle4(perms, vocab_size).fit_history(history_experiences),
    }
    return ladder
