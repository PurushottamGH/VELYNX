"""
validation/datasets.py
=======================

Concrete :class:`~validation.interfaces.Dataset` implementations and a
name-keyed factory for the VELYNX validation harness.

The harness (``benchmark.py``) is forbidden from constructing a world by hand;
it only ever asks this component for a dataset *by name*. That keeps the
orchestrator thin (it knows names, not physics) and keeps every bit of
world-construction logic here, behind the Interface-First contract.

Currently provided
-------------------
``EnvironmentDataset``
    Wraps the C7 Sensorium (:mod:`environment`): an :class:`Environment` driving
    a hidden continuous state through latent regimes, observed only through a
    noisy :class:`SensorArray`. The brain therefore sees nothing but a real-valued
    sensory vector per tick -- exactly the contract :class:`Dataset` promises.

Registry
--------
``build_dataset(name, **cfg)`` resolves a human-friendly ``dataset_name`` (the
field on ``BenchmarkConfig``) to a freshly-constructed, reproducible dataset.
"""

from __future__ import annotations

from typing import Callable, Dict

from framework.core.environment import Environment, SensorArray
from validation.interfaces import Dataset, Vector


class EnvironmentDataset(Dataset):
    """A reproducible sensory-vector stream over the C7 Sensorium.

    Each tick advances the hidden world one step and emits the noisy sensor
    reading -- the only channel the cognitive core is permitted to observe.
    Ground-truth regime labels are deliberately *not* exposed here; they live
    on :meth:`Environment.ground_truth` for offline scoring only.

    Parameters
    ----------
    seed : int or None
        Master seed. When set, the entire tick stream is deterministic across
        :meth:`reset` calls, which is what makes an experiment replayable.
    noise_sigma : float
        Std-dev of the Gaussian sensor noise. Higher == harder perception.
    """

    def __init__(self, seed: int | None = None, noise_sigma: float = 0.05) -> None:
        self._seed = seed
        self._noise_sigma = noise_sigma
        self._env: Environment | None = None
        self._sensors: SensorArray | None = None
        self.reset()

    def reset(self) -> None:
        """Rebuild the world and sensor bank from the configured seed.

        Re-seeding both RNGs here is what guarantees a subsequent run of
        :meth:`get_next_tick` reproduces the previous stream tick-for-tick.
        The sensor bank gets ``seed + 1`` so its noise process is independent
        of, but still reproducible with, the world's dynamics.
        """
        sensor_seed = None if self._seed is None else self._seed + 1
        self._env = Environment(seed=self._seed)
        self._sensors = SensorArray(noise_sigma=self._noise_sigma, seed=sensor_seed)

    def get_next_tick(self) -> Vector:
        """Advance the world one step and return the next noisy sensor vector."""
        assert self._env is not None and self._sensors is not None  # reset() ran
        self._env.step()
        return self._sensors.read(self._env)

    @property
    def dimensions(self) -> int:
        """Number of sensor channels in each emitted vector."""
        assert self._sensors is not None
        return self._sensors.dimensions


# ---------------------------------------------------------------------------
# Factory / registry
# ---------------------------------------------------------------------------

#: Maps a ``dataset_name`` to a builder ``(seed, noise_sigma) -> Dataset``.
DATASETS: Dict[str, Callable[..., Dataset]] = {
    "environment": EnvironmentDataset,
    "sensorium": EnvironmentDataset,  # friendly alias for the C7 world
}


def build_dataset(
    name: str,
    *,
    seed: int | None = None,
    noise_sigma: float = 0.05,
) -> Dataset:
    """Resolve a ``dataset_name`` to a freshly-built, reproducible dataset.

    Parameters
    ----------
    name : str
        A key registered in :data:`DATASETS` (e.g. ``"environment"``).
    seed : int or None
        Forwarded to the dataset for deterministic replay.
    noise_sigma : float
        Forwarded to the dataset's sensor noise model.

    Raises
    ------
    KeyError
        If ``name`` is not a registered dataset, with the list of valid names.
    """
    try:
        builder = DATASETS[name]
    except KeyError:
        valid = ", ".join(sorted(DATASETS)) or "(none registered)"
        raise KeyError(f"Unknown dataset_name {name!r}. Registered datasets: {valid}.") from None
    return builder(seed=seed, noise_sigma=noise_sigma)


__all__ = ["EnvironmentDataset", "DATASETS", "build_dataset"]
