"""Replay gating policy.

Responsibility: given this step's prediction loss, return how many replay
samples to consolidate. Nothing else. Every gate is stateless apart from its
own counters, so gates are interchangeable in an ablation.
"""

from __future__ import annotations


class Gate:
    """Base gate. Returns a replay count for the current step."""

    def __init__(self) -> None:
        self.n_fired = 0
        self.n_replays = 0

    def replay_count(self, loss: float) -> int:
        raise NotImplementedError

    def _record(self, k: int) -> int:
        if k > 0:
            self.n_fired += 1
            self.n_replays += k
        return k


class NeverGate(Gate):
    """Control: never replay. Online learning only."""

    def replay_count(self, loss: float) -> int:
        return self._record(0)


class AlwaysGate(Gate):
    """Control: replay a constant amount every step, ignoring surprise."""

    def __init__(self, k: int = 4) -> None:
        super().__init__()
        self.k = k

    def replay_count(self, loss: float) -> int:
        return self._record(self.k)


class SurpriseGate(Gate):
    """Replay only when the step's loss exceeds a threshold (in nats)."""

    def __init__(self, threshold: float = 1.5, k: int = 4) -> None:
        super().__init__()
        self.threshold = threshold
        self.k = k

    def replay_count(self, loss: float) -> int:
        return self._record(self.k if loss > self.threshold else 0)
