"""Shuffled-input control condition.

Preserves the input marginal distribution but destroys temporal structure
by shuffling. This tests whether temporal dependencies are necessary for
the observed cognitive behavior.
"""

import numpy as np
from typing import List, Optional


class ShuffledInputControl:
    """Shuffled-input control.

    Takes an input stream, stores it, and replays it with temporal order
    destroyed. This preserves the marginal distribution (frequency of
    observations) while removing temporal structure.
    """

    def __init__(self, seed: Optional[int] = None):
        self.buffer: List[List[float]] = []
        self._replay: List[List[float]] = []
        self._idx = 0
        self.rng = np.random.RandomState(seed)

    def observe(self, vector: List[float]) -> None:
        """Buffer an observation. Shuffling happens on reset/replay."""
        self.buffer.append(vector)

    def shuffle_and_replay(self) -> None:
        """Shuffle all buffered observations and prepare for replay."""
        self._replay = list(self.buffer)
        self.rng.shuffle(self._replay)
        self._idx = 0

    def next(self) -> Optional[List[float]]:
        """Get next shuffled observation."""
        if self._idx >= len(self._replay):
            return None
        result = self._replay[self._idx]
        self._idx += 1
        return result

    @property
    def size(self) -> int:
        return len(self.buffer)

    def reset(self) -> None:
        self.buffer.clear()
        self._replay.clear()
        self._idx = 0
