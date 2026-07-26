"""Fixed-capacity control condition.

A control that maintains a fixed number of clusters/slots, replacing oldest
entries when capacity is exceeded. This provides a null baseline where no
genuine structure discovery can occur beyond the fixed capacity limit.
"""

from typing import List, Optional, Tuple
from collections import OrderedDict


class FixedCapacityControl:
    """Fixed-capacity memory with FIFO eviction.

    Mimics a bounded memory buffer that cannot discover new structure
    beyond its fixed slot count. Used as a null control for emergence
    experiments.
    """

    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self.slots: OrderedDict = OrderedDict()
        self._tick = 0

    def observe(self, item: Tuple[int, List[float]]) -> Optional[Tuple[int, List[float]]]:
        """Store an observation. Returns evicted item if capacity exceeded."""
        key, vector = item
        self.slots[key] = vector
        self._tick += 1

        evicted = None
        if len(self.slots) > self.capacity:
            evicted_key, evicted_vec = self.slots.popitem(last=False)
            evicted = (evicted_key, evicted_vec)

        return evicted

    def predict(self, context: List[float]) -> Optional[List[float]]:
        """Predict next observation (returns nearest centroid or None)."""
        if not self.slots:
            return None
        nearest = min(
            self.slots.values(),
            key=lambda v: sum((a - b) ** 2 for a, b in zip(v, context)),
        )
        return nearest

    @property
    def fill(self) -> float:
        return len(self.slots) / self.capacity if self.capacity > 0 else 0.0

    def reset(self) -> None:
        self.slots.clear()
        self._tick = 0
