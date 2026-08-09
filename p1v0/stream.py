"""Task stream generation.

Responsibility: emit a deterministic, piecewise-stationary sequence of
symbol observations, labelled by which task generated them.

A task is an order-1 Markov chain over an alphabet of size A. Each row puts
mass on `fanout` symbols only, so tasks are sparse and mutually distinguishable
-- a model tuned to task i is measurably wrong on task j.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterator, List, Tuple


@dataclass(frozen=True)
class Event:
    """One observation in the stream."""

    t: int  # global step index
    task: int  # generating task id
    prev: int  # context symbol (previous observation)
    sym: int  # observed symbol


class MarkovTask:
    """Sparse order-1 Markov chain over `alphabet` symbols."""

    def __init__(self, task_id: int, alphabet: int, seed: int, fanout: int = 2) -> None:
        if alphabet < 2:
            raise ValueError("alphabet must be >= 2")
        if fanout < 1:
            raise ValueError("fanout must be >= 1")

        self.task_id = task_id
        self.alphabet = alphabet
        self.fanout = min(fanout, alphabet)

        rng = random.Random(seed)
        self.rows: List[List[float]] = []
        for _ in range(alphabet):
            targets = rng.sample(range(alphabet), self.fanout)
            weights = [rng.random() + 0.1 for _ in targets]
            total = sum(weights)
            row = [0.0] * alphabet
            for tgt, w in zip(targets, weights):
                row[tgt] = w / total
            self.rows.append(row)

    def next_symbol(self, prev: int, rng: random.Random) -> int:
        """Sample the successor of `prev`."""
        acc = 0.0
        r = rng.random()
        for i, p in enumerate(self.rows[prev]):
            acc += p
            if r <= acc:
                return i
        return self.alphabet - 1

    def sample_pairs(self, n: int, seed: int) -> List[Tuple[int, int]]:
        """Draw `n` held-out (prev, sym) pairs from this chain.

        Uses its own rng seed so probe data is disjoint from training draws.
        """
        rng = random.Random(seed)
        prev = rng.randrange(self.alphabet)
        pairs: List[Tuple[int, int]] = []
        for _ in range(n):
            sym = self.next_symbol(prev, rng)
            pairs.append((prev, sym))
            prev = sym
        return pairs


class TaskStream:
    """Sequence of tasks presented in blocks, optionally repeated in cycles."""

    def __init__(
        self,
        n_tasks: int = 4,
        alphabet: int = 8,
        steps_per_task: int = 2000,
        seed: int = 0,
        cycles: int = 1,
        fanout: int = 2,
    ) -> None:
        if n_tasks < 1:
            raise ValueError("n_tasks must be >= 1")
        if steps_per_task < 1:
            raise ValueError("steps_per_task must be >= 1")

        self.n_tasks = n_tasks
        self.alphabet = alphabet
        self.steps_per_task = steps_per_task
        self.seed = seed
        self.cycles = cycles
        self.tasks: List[MarkovTask] = [
            MarkovTask(i, alphabet, seed * 10_000 + 7 * i + 1, fanout) for i in range(n_tasks)
        ]

    @property
    def total_steps(self) -> int:
        return self.n_tasks * self.steps_per_task * self.cycles

    def blocks(self) -> List[Tuple[int, int]]:
        """Return [(task_id, last_step_index)] -- the probe checkpoints."""
        out: List[Tuple[int, int]] = []
        t = 0
        for _ in range(self.cycles):
            for task in self.tasks:
                t += self.steps_per_task
                out.append((task.task_id, t - 1))
        return out

    def __iter__(self) -> Iterator[Event]:
        rng = random.Random(self.seed + 991)
        prev = 0
        t = 0
        for _ in range(self.cycles):
            for task in self.tasks:
                for _ in range(self.steps_per_task):
                    sym = task.next_symbol(prev, rng)
                    yield Event(t=t, task=task.task_id, prev=prev, sym=sym)
                    prev = sym
                    t += 1
