"""
validation/report.py
=====================

The "Vitals Screen" rendering layer, migrated out of ``cognitive_health.py``
under the Proxy-Refactoring strategy.

This module owns :class:`HealthReport` -- the dataclass that ingests the spatial
cognitive variables, computes the Free-Energy vitals via the pure functions in
:mod:`validation.metrics`, classifies the engine into a :class:`~validation.metrics.Regime`,
and renders the human-readable monitor screen.

All the actual quantitative logic (entropy, surprise, load, energy, thresholds,
the ``Regime`` enum) lives in :mod:`validation.metrics`; this file only assembles
and presents it. ``cognitive_health.py`` re-exports :class:`HealthReport` from
here so legacy imports (and ``cognitive_core.py``) keep working unchanged.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from validation.metrics import (
    ENERGY_EXHAUSTION,
    ENTROPY_HIGH,
    LAMBDA,
    MU,
    NU,
    PRESSURE_HIGH,
    PRESSURE_MILD,
    SURPRISE_HIGH,
    SURPRISE_MILD,
    Regime,
    Vector,
    active_load,
    anomaly_spatial_volume,
    cognitive_energy,
    surprise,
    transition_entropy,
)


# ---------------------------------------------------------------------------
# The Vitals Screen
# ---------------------------------------------------------------------------

@dataclass
class HealthReport:
    """Ingests the spatial cognitive variables and renders a Vitals Screen.

    Parameters
    ----------
    transitions : Mapping[int, Mapping[int, float]]
        First-order Markov chain over cluster IDs,
        ``{src_cluster: {dst_cluster: count}}`` -- e.g. the output of
        ``VectorPredictor.transition_matrix()``. Drives Entropy H.
    predicted_centroid : Sequence[float]
        The centroid the predictor forecast for this step. Drives Surprise S.
    observed_vector : Sequence[float]
        The sensory vector actually observed. Drives Surprise S.
    cluster_count : int
        Number of active K-Means clusters. Half of Active Load A.
    anomaly_vectors : Sequence[Sequence[float]]
        The quarantined anomaly vectors. Their spatial volume is the other
        half of Active Load A.
    label : str
        Optional human-friendly tag for this snapshot.
    """

    transitions: Mapping[int, Mapping[int, float]]
    predicted_centroid: Vector
    observed_vector: Vector
    cluster_count: int
    anomaly_vectors: Sequence[Vector] = field(default_factory=list)
    label: str = "snapshot"

    # Computed fields (populated in __post_init__)
    entropy: float = field(init=False)
    surprise: float = field(init=False)
    anomaly_volume: float = field(init=False)
    active: float = field(init=False)
    energy: float = field(init=False)
    regime: Regime = field(init=False)

    def __post_init__(self) -> None:
        self.entropy = transition_entropy(self.transitions)
        self.surprise = surprise(self.predicted_centroid, self.observed_vector)
        self.anomaly_volume = anomaly_spatial_volume(self.anomaly_vectors)
        self.active = active_load(self.cluster_count, self.anomaly_vectors)
        self.energy = cognitive_energy(self.entropy, self.surprise, self.active)
        self.regime = self._classify()

    # -- adapters ----------------------------------------------------------

    @classmethod
    def from_core(
        cls,
        core: Any,
        observed_vector: Vector,
        predicted_centroid: Vector | None = None,
        label: str = "snapshot",
    ) -> "HealthReport":
        """Build a report straight from a ``VectorPredictionCore``-like object.

        Duck-typed against ``backend.cognition.vector_prediction_core`` so this
        monitor never has to import (and risk a circular dependency on) the
        core engine. We read:

        * ``core.predictor.transition_matrix()`` -> Markov chain for H
        * ``core.cluster_engine.cluster_count``  -> live clusters for A
        * ``core.cluster_engine.anomaly_vectors``-> quarantine cloud for A
        * ``core.last_prediction``               -> predicted centroid for S
          (overridable via ``predicted_centroid``)
        """
        predictor = core.predictor
        cluster_engine = core.cluster_engine

        if predicted_centroid is None:
            predicted_centroid = getattr(core, "last_prediction", None)
            if predicted_centroid is None:
                # No prediction yet: identity prediction -> zero surprise.
                predicted_centroid = list(observed_vector)

        return cls(
            transitions=predictor.transition_matrix(),
            predicted_centroid=predicted_centroid,
            observed_vector=observed_vector,
            cluster_count=cluster_engine.cluster_count,
            anomaly_vectors=cluster_engine.anomaly_vectors,
            label=label,
        )

    # -- classification ----------------------------------------------------

    @property
    def anomaly_pressure(self) -> float:
        """Quarantined anomaly vectors per active cluster."""
        return len(self.anomaly_vectors) / max(self.cluster_count, 1)

    def _classify(self) -> Regime:
        """Partition the spatial state space into the three regimes.

        * EXHAUSTION -- the substrate is fragmenting: highly unpredictable
                        transitions WHILE anomalies pile up faster than
                        clusters can absorb them, or raw free energy is
                        runaway.
        * LEARNING   -- meaningful spatial surprise is arriving, or anomalies
                        are accumulating at a bounded rate. Healthy adaptation.
        * OPTIMAL    -- predictable dynamics, small prediction error, and a
                        quarantine cloud that is not straining the model.
        """
        pressure = self.anomaly_pressure

        if self.entropy >= ENTROPY_HIGH and pressure >= PRESSURE_HIGH:
            return Regime.EXHAUSTION
        if self.energy >= ENERGY_EXHAUSTION and pressure >= 0.75 * PRESSURE_HIGH:
            return Regime.EXHAUSTION
        if self.surprise >= SURPRISE_HIGH and pressure >= PRESSURE_MILD:
            return Regime.EXHAUSTION

        if self.surprise >= SURPRISE_MILD or PRESSURE_MILD <= pressure < PRESSURE_HIGH:
            return Regime.LEARNING

        if (
            self.entropy <= 0.5 * ENTROPY_HIGH
            and self.surprise < SURPRISE_MILD
            and pressure < PRESSURE_MILD
        ):
            return Regime.OPTIMAL

        # Default middle ground: doing work but coping.
        return Regime.LEARNING

    # -- rendering ---------------------------------------------------------

    def _bar(self, value: float, ceiling: float, width: int = 24) -> str:
        """A little ASCII gauge for a single vital."""
        if ceiling <= 0:
            ceiling = 1.0
        filled = int(round(min(max(value, 0.0) / ceiling, 1.0) * width))
        return "#" * filled + "." * (width - filled)

    def render(self) -> str:
        """Return the formatted, human-readable Vitals Screen."""
        line = "+" + "-" * 52 + "+"
        anomaly_n = len(self.anomaly_vectors)
        # Entropy ceiling is the theoretical max for this many clusters.
        h_ceiling = max(math.log2(max(self.cluster_count, 2)), 1.0)
        rows = [
            line,
            "|  COGNITIVE VITALS  ::  Free-Energy Health Monitor   |",
            "+" + "-" * 52 + "+",
            f"|  snapshot : {self.label:<37.37}|",
            f"|  state    : {self.regime.glyph} {self.regime.value:<31.31}|",
            "+" + "-" * 52 + "+",
            f"|  H  Entropy    {self.entropy:6.2f}  {self._bar(self.entropy, h_ceiling)} |",
            f"|  S  Surprise   {self.surprise:6.2f}  {self._bar(self.surprise, 1.0)} |",
            f"|  A  Load       {self.active:6.2f}  {self._bar(self.active, 60.0)} |",
            "+" + "-" * 52 + "+",
            f"|  clusters: {self.cluster_count:<4d} anomalies: {anomaly_n:<4d}"
            f" pressure: {self.anomaly_pressure:>5.2f}  |",
            f"|  anomaly spatial volume (variance): {self.anomaly_volume:>10.4f} |",
            "+" + "-" * 52 + "+",
            f"|  E = ({LAMBDA}*H) + ({MU}*S) + ({NU}*A)"
            f"{'':<19}|",
            f"|  >> COGNITIVE ENERGY  E = {self.energy:8.2f}"
            f"{'':<17}|",
            line,
        ]
        return "\n".join(rows)

    def __str__(self) -> str:  # pragma: no cover - convenience
        return self.render()


__all__ = ["HealthReport", "run_demo"]


# ---------------------------------------------------------------------------
# Mock run: a vector brain travelling from Optimal -> Exhaustion
# ---------------------------------------------------------------------------

def run_demo() -> None:
    """Render the Optimal -> Exhaustion vitals walkthrough.

    Migrated verbatim from the original ``cognitive_health.py`` ``__main__``
    block so both ``python validation/report.py`` and the legacy
    ``python cognitive_health.py`` produce the same output.
    """
    timeline = [
        {
            "label": "t0  dawn / rested",
            "transitions": {0: {1: 20}, 1: {2: 19}, 2: {0: 18}},
            "predicted_centroid": [0.50, 0.50, 0.50, 0.50],
            "observed_vector":    [0.51, 0.49, 0.50, 0.52],
            "cluster_count": 3,
            "anomaly_vectors": [],
        },
        {
            "label": "t1  first anomaly",
            "transitions": {0: {1: 18, 2: 3}, 1: {2: 16, 0: 2}, 2: {0: 15}},
            "predicted_centroid": [0.50, 0.50, 0.50, 0.50],
            "observed_vector":    [0.62, 0.41, 0.55, 0.44],
            "cluster_count": 4,
            "anomaly_vectors": [[0.91, 0.10, 0.88, 0.12]],
        },
        {
            "label": "t2  active learning",
            "transitions": {0: {1: 10, 2: 7}, 1: {2: 8, 0: 6}, 2: {0: 7, 1: 5}},
            "predicted_centroid": [0.50, 0.50, 0.50, 0.50],
            "observed_vector":    [0.78, 0.30, 0.66, 0.35],
            "cluster_count": 6,
            "anomaly_vectors": [
                [0.91, 0.10, 0.88, 0.12],
                [0.15, 0.83, 0.20, 0.79],
            ],
        },
        {
            "label": "t3  strain rising",
            "transitions": {
                0: {1: 5, 2: 4, 3: 4}, 1: {2: 5, 0: 4, 3: 3},
                2: {0: 4, 1: 4, 3: 4}, 3: {0: 3, 1: 4, 2: 3},
            },
            "predicted_centroid": [0.50, 0.50, 0.50, 0.50],
            "observed_vector":    [0.95, 0.08, 0.90, 0.05],
            "cluster_count": 8,
            "anomaly_vectors": [
                [0.91, 0.10, 0.88, 0.12],
                [0.15, 0.83, 0.20, 0.79],
                [0.05, 0.95, 0.50, 0.10],
                [0.88, 0.40, 0.05, 0.92],
            ],
        },
        {
            "label": "t4  chaos / collapse",
            "transitions": {
                0: {1: 2, 2: 2, 3: 2, 4: 2, 5: 1},
                1: {0: 2, 2: 2, 3: 1, 4: 2, 5: 2},
                2: {0: 2, 1: 2, 3: 2, 4: 1, 5: 2},
                3: {0: 1, 1: 2, 2: 2, 4: 2, 5: 2},
                4: {0: 2, 1: 1, 2: 2, 3: 2, 5: 2},
                5: {0: 2, 1: 2, 2: 1, 3: 2, 4: 2},
            },
            "predicted_centroid": [0.50, 0.50, 0.50, 0.50],
            "observed_vector":    [0.99, 0.02, 0.97, 0.01],
            "cluster_count": 9,
            "anomaly_vectors": [
                [0.91, 0.10, 0.88, 0.12], [0.15, 0.83, 0.20, 0.79],
                [0.05, 0.95, 0.50, 0.10], [0.88, 0.40, 0.05, 0.92],
                [0.02, 0.30, 0.97, 0.44], [0.70, 0.99, 0.01, 0.33],
                [0.44, 0.01, 0.66, 0.98], [0.99, 0.55, 0.33, 0.02],
            ],
        },
    ]

    print("\n" + "=" * 54)
    print("  SIMULATION: vector engine, Optimal -> Exhaustion")
    print("=" * 54)

    for beat in timeline:
        report = HealthReport(
            transitions=beat["transitions"],
            predicted_centroid=beat["predicted_centroid"],
            observed_vector=beat["observed_vector"],
            cluster_count=beat["cluster_count"],
            anomaly_vectors=beat["anomaly_vectors"],
            label=beat["label"],
        )
        print()
        print(report.render())

    print("\n" + "=" * 54)
    print("  End of simulation. Free energy minimised -> health.")
    print("=" * 54 + "\n")


if __name__ == "__main__":
    run_demo()
