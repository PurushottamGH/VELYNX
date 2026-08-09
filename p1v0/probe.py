"""Frozen-model probes.

Responsibility: measure the model's loss on held-out data from every task,
without letting the model learn from it. This is the only measurement that can
detect forgetting, because online loss on the current task cannot.
"""

from __future__ import annotations

from typing import List, Tuple

from p1v0.model import CountModel, scoring_loss
from p1v0.stream import TaskStream


class ProbeSuite:
    """Held-out (prev, sym) pairs for each task in a stream."""

    def __init__(self, stream: TaskStream, n_pairs: int = 500) -> None:
        self.n_tasks = stream.n_tasks
        self.pairs: List[List[Tuple[int, int]]] = [
            task.sample_pairs(n_pairs, seed=stream.seed * 10_000 + 5_000 + task.task_id)
            for task in stream.tasks
        ]

    def evaluate(self, model: CountModel) -> List[float]:
        """Mean scoring loss per task. Read-only with respect to the model."""
        out: List[float] = []
        for pairs in self.pairs:
            if not pairs:
                out.append(float("nan"))
                continue
            total = sum(scoring_loss(model.predict(prev), sym) for prev, sym in pairs)
            out.append(total / len(pairs))
        return out
