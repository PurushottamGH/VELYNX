"""Predictor interface.

Every predictor in the VELYNX cognitive architecture implements this ABC.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple


class Predictor(ABC):
    """Abstract predictor interface.

    A predictor maintains a distribution over latent states and produces
    forecasts for the next observation.
    """

    @abstractmethod
    def predict(self, context: List[float]) -> List[float]:
        """Predict the next observation given current context."""
        ...

    @abstractmethod
    def update(self, observation: List[float]) -> None:
        """Update internal state with observed data."""
        ...

    @abstractmethod
    def entropy(self) -> float:
        """Return current predictive uncertainty in bits."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset to initial state."""
        ...

    @abstractmethod
    def state_dict(self) -> dict:
        """Return serializable state for reproducibility."""
        ...

    @abstractmethod
    def load_state_dict(self, state: dict) -> None:
        """Restore state from serialized representation."""
        ...
