"""Core evaluation harness.

Standard interfaces for datasets, metrics, and regression gates.
Consolidated from validation/interfaces.py, validation/runner.py.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


Vector = Tuple[float, ...]


class Dataset(ABC):
    """Reproducible data source for benchmarks."""

    @abstractmethod
    def reset(self) -> None:
        ...

    @abstractmethod
    def get_next_tick(self) -> Vector:
        ...


class Metric(ABC):
    """Abstract scoring function over a run's logs."""

    @abstractmethod
    def score(self, logs: Dict[str, Any]) -> float:
        ...


class Regression(ABC):
    """Baseline comparison gate: enforces no-regression."""

    @abstractmethod
    def check(self, new_score: float, baseline_score: float) -> bool:
        ...
