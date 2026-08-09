"""Memory-zero evaluation harness (NN-0 ablation N1).

The decisive-experiment protocol: evaluate a *frozen* predictor against probe
items while holding the "memory = zero" condition — the predictor's memory is
reset before every item, so no cross-item credit can be retrieved. This is the
environment-side instrument for NN-0's ablation ``N1 (memory zeroed)`` in the
P1-LN-DEC decisive experiment.

Protocol contract
-----------------
- The harness **never trains**. NN-0 is not built or trained by this package.
- It interacts with a predictor through a narrow interface:
  ``predict(context) -> (token, probability)`` and optional ``reset()``.
  A ``learn``/``fit`` method, if present, is **never called** (and the tests
  assert that with a guard model that raises on ``learn``).
- ``memory_zero=True`` calls ``reset()`` before each item; with
  ``memory_zero=False`` the model is left untouched between items.

Reference baselines
-------------------
``NGramLookupModel`` wraps :class:`verification.NGramLookup`: the strongest
naive exact retriever, used to *demonstrate* the boundary — it solves the
anti-memorisation control and cannot solve the constructed holdouts. This is
not a model that learns; it is the retrieval floor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol, Sequence, Tuple

from p1.live.neural.playgarden import verification
from p1.live.neural.playgarden.worlds import Probe


class Predictor(Protocol):
    """A frozen, predict-only item scorer.

    ``predict`` returns ``(top_token, probability)``. ``reset`` is optional
    and is invoked by the harness only under ``memory_zero=True``.
    """

    def predict(self, context: Tuple[str, ...]) -> Tuple[Optional[str], float]:
        ...


class NGramLookupModel:
    """Deterministic exact-lookup baseline (see module docstring)."""

    def __init__(self, corpus: Sequence[str], order_n: int = 3) -> None:
        self.lookup = verification.NGramLookup(order_n=order_n, corpus=tuple(corpus))

    def predict(self, context: Tuple[str, ...]) -> Tuple[Optional[str], float]:
        res = self.lookup.score(context)
        top = res["top"]
        return (top, 1.0 if top is not None else 0.0)

    def reset(self) -> None:
        # Stateless; present so the harness exercises the reset protocol.
        return None


@dataclass
class ProbeScore:
    """Score of one probe item under the harness."""

    kind: str
    context_len: int
    predicted: Optional[str]
    expected: Optional[str]
    confidence: float
    solved: bool
    memory_zero: bool


@dataclass(frozen=True)
class MemoryZeroReport:
    """Aggregate results of a memory-zero run.

    `accuracy` is overall exact-continuation accuracy; ``by_kind`` breaks it
    down per probe kind; ``n_items`` and ``expected_zeroed`` (True when the
    memory-zero protocol was requested by the run).
    """

    memory_zero: bool
    n_items: int
    n_solved: int
    accuracy: float
    by_kind: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_scores(cls, scores: Sequence[ProbeScore], memory_zero: bool) -> "MemoryZeroReport":
        n = len(scores)
        solved = sum(1 for s in scores if s.solved)
        by_kind: Dict[str, float] = {}
        per_kind: Dict[str, List[bool]] = {}
        for s in scores:
            per_kind.setdefault(s.kind, []).append(s.solved)
        for kind, flags in per_kind.items():
            by_kind[kind] = sum(flags) / len(flags)
        return cls(
            memory_zero=memory_zero,
            n_items=n,
            n_solved=solved,
            accuracy=(solved / n) if n else 0.0,
            by_kind=by_kind,
        )


class MemoryZeroEvaluator:
    """Evaluate a frozen predictor under the memory-zero protocol.

    The evaluator never trains and never calls a ``learn`` method. It is a
    pure measurement surface over probe items.
    """

    def __init__(self, model: Predictor) -> None:
        self.model = model

    def evaluate(self, probes: Sequence[Probe], memory_zero: bool = True) -> MemoryZeroReport:
        scores: List[ProbeScore] = []
        for p in probes:
            if memory_zero and hasattr(self.model, "reset"):
                self.model.reset()
            pred, prob = self.model.predict(p.context)
            expected = p.expected[0] if p.expected else None
            scores.append(
                ProbeScore(
                    kind=p.kind,
                    context_len=len(p.context),
                    predicted=pred,
                    expected=expected,
                    confidence=prob,
                    solved=pred == expected,
                    memory_zero=memory_zero,
                )
            )
        return MemoryZeroReport.from_scores(scores, memory_zero)


__all__ = [
    "MemoryZeroEvaluator",
    "MemoryZeroReport",
    "NGramLookupModel",
    "Predictor",
    "ProbeScore",
]