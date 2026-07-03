"""Capacity-matched random-growth control.

A control that adds new clusters at the same rate as the experimental
condition, but with random content. This tests whether any observed
improvement is due to capacity increase alone rather than structured
representation learning.
"""
import random
import math
from typing import List, Optional, Tuple


class RandomGrowthControl:
    """Random-growth control with capacity-matched growth rate.

    Adds new clusters at a fixed rate but with random centroids,
    ensuring any observed advantage of the experimental condition
    cannot be attributed to capacity alone.
    """

    def __init__(self, dim: int = 64, seed: Optional[int] = None):
        self.dim = dim
        self.rng = random.Random(seed)
        self.clusters: List[List[float]] = []
        self._growth_target: int = 0

    def set_growth_rate(self, clusters_per_tick: float) -> None:
        """Set the target growth rate (clusters per tick)."""
        self._growth_target = clusters_per_tick

    def tick(self) -> List[List[float]]:
        """Advance one tick. May grow new random clusters."""
        new_clusters = []
        if self._growth_target > 0:
            n_new = int(self._growth_target)
            remainder = self._growth_target - n_new
            if self.rng.random() < remainder:
                n_new += 1
            for _ in range(n_new):
                centroid = [self.rng.gauss(0, 1) for _ in range(self.dim)]
                norm = math.sqrt(sum(x * x for x in centroid))
                if norm > 0:
                    centroid = [x / norm for x in centroid]
                centroid_id = len(self.clusters)
                self.clusters.append(centroid)
                new_clusters.append(centroid)
        return new_clusters

    def predict(self, context: List[float]) -> Optional[List[float]]:
        if not self.clusters:
            return None
        return self.rng.choice(self.clusters)

    @property
    def size(self) -> int:
        return len(self.clusters)

    def reset(self) -> None:
        self.clusters.clear()
        self._growth_target = 0
