"""Episodic memory.

Responsibility: retain a bounded, unbiased sample of past observations and
draw from it on request. It does not learn, score, or decide.

Reservoir sampling is used so the retained set stays a uniform sample of the
entire stream seen so far. A FIFO ring buffer would bias the buffer toward the
current task, which would confound the replay ablation.
"""

from __future__ import annotations

import random
from typing import List, Tuple

Sample = Tuple[int, int]  # (prev, sym)


class ReplayBuffer:
    """Fixed-capacity reservoir of (prev, sym) pairs."""

    def __init__(self, capacity: int = 1000, seed: int = 0) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self.items: List[Sample] = []
        self.n_seen = 0
        self._rng = random.Random(seed + 31)

    def append(self, item: Sample) -> None:
        self.n_seen += 1
        if len(self.items) < self.capacity:
            self.items.append(item)
            return
        j = self._rng.randrange(self.n_seen)
        if j < self.capacity:
            self.items[j] = item

    def sample(self, k: int) -> List[Sample]:
        """Draw k items with replacement. Empty list if k <= 0 or buffer empty."""
        if k <= 0 or not self.items:
            return []
        return [self.items[self._rng.randrange(len(self.items))] for _ in range(k)]

    def __len__(self) -> int:
        return len(self.items)


class NullBuffer(ReplayBuffer):
    """Control: stores nothing, returns nothing. Isolates the memory mechanism."""

    def __init__(self, seed: int = 0) -> None:
        super().__init__(capacity=1, seed=seed)

    def append(self, item: Sample) -> None:  # noqa: D102
        self.n_seen += 1

    def sample(self, k: int) -> List[Sample]:  # noqa: D102
        return []
