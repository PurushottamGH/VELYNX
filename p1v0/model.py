"""Online predictor.

Responsibility: map a context symbol to a predictive distribution, and absorb
a single (context, symbol) observation.

`CountModel` is an order-1 count table with additive smoothing. The `decay`
parameter multiplies a row's counts before each increment, giving the model a
finite effective memory. decay == 1.0 means no forgetting; decay < 1.0 makes
the model recency-biased, which is the mechanism under study. Forgetting is
therefore a tunable property of the rig, not an accident.
"""

from __future__ import annotations

import math
from typing import Dict, List


class CountModel:
    """Order-1 categorical predictor with additive smoothing and recency decay."""

    def __init__(self, alphabet: int, alpha: float = 0.5, decay: float = 1.0) -> None:
        if alphabet < 2:
            raise ValueError("alphabet must be >= 2")
        if alpha <= 0.0:
            raise ValueError("alpha must be > 0")
        if not 0.0 < decay <= 1.0:
            raise ValueError("decay must be in (0, 1]")

        self.alphabet = alphabet
        self.alpha = alpha
        self.decay = decay
        self.counts: List[List[float]] = [[0.0] * alphabet for _ in range(alphabet)]
        self.n_updates = 0

    def predict(self, prev: int) -> List[float]:
        """Posterior predictive distribution over the next symbol."""
        row = self.counts[prev]
        total = sum(row) + self.alpha * self.alphabet
        return [(c + self.alpha) / total for c in row]

    def learn(self, prev: int, sym: int, weight: float = 1.0) -> None:
        """Absorb one observation. Decay is applied to the touched row only."""
        row = self.counts[prev]
        if self.decay < 1.0:
            for i in range(self.alphabet):
                row[i] *= self.decay
        row[sym] += weight
        self.n_updates += 1

    def state_dict(self) -> Dict:
        return {
            "alphabet": self.alphabet,
            "alpha": self.alpha,
            "decay": self.decay,
            "counts": [row[:] for row in self.counts],
            "n_updates": self.n_updates,
        }

    def load_state_dict(self, state: Dict) -> None:
        self.alphabet = state["alphabet"]
        self.alpha = state["alpha"]
        self.decay = state["decay"]
        self.counts = [row[:] for row in state["counts"]]
        self.n_updates = state["n_updates"]


def scoring_loss(probs: List[float], index: int, eps: float = 1e-15) -> float:
    """Proper scoring loss L = -log p(observed). Lower is better, 0.0 is perfect.

    Local, strictly proper. The only loss v0 reports, so that model comparison
    is not confounded by metric choice.
    """
    if index < 0 or index >= len(probs):
        return -math.log(eps)
    p = min(max(probs[index], eps), 1.0 - eps)
    return -math.log(p)
