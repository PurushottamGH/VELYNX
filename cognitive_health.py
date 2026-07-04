"""
cognitive_health.py  --  PROXY MODULE
=====================================

Cognitive Health Monitor for the VELYNX vector cognitive architecture,
grounded in Karl Friston's *Free Energy Principle* (FEP).

.. note::
   **This module has been refactored.** Its logic now lives in the
   ``validation`` subsystem and this file is a thin compatibility proxy:

       * Free-Energy quantities, constants, the ``Regime`` enum and the
         ``Metric`` implementations  ->  :mod:`validation.metrics`
       * The ``HealthReport`` "Vitals Screen" rendering  ->  :mod:`validation.report`

   Every public name that used to live here is re-exported below, so existing
   imports such as ``from cognitive_health import HealthReport, Regime`` (used
   by ``cognitive_core.py``) continue to work unchanged. No behaviour has
   changed -- the code simply moved.

Free-Energy proxy (unchanged):

        E = (lambda * H) + (mu * S) + (nu * A)

    H -- Entropy:     conditional Shannon entropy of the cluster-transition
                      Markov chain (bits).
    S -- Surprise:    raw Euclidean distance between predicted centroid and
                      observed sensory vector.
    A -- Active Load: live K-Means clusters + spatial volume of the quarantined
                      anomaly cloud.
"""

from __future__ import annotations

# --- Core quantitative logic (migrated to validation.metrics) --------------
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
    euclidean_distance,
    surprise,
    transition_entropy,
)

# --- Vitals Screen rendering (migrated to validation.report) ---------------
from validation.report import HealthReport, run_demo

__all__ = [
    # type alias
    "Vector",
    # constants
    "LAMBDA", "MU", "NU",
    "ENTROPY_HIGH", "SURPRISE_HIGH", "SURPRISE_MILD",
    "PRESSURE_HIGH", "PRESSURE_MILD", "ENERGY_EXHAUSTION",
    # enum
    "Regime",
    # pure functions
    "euclidean_distance", "transition_entropy", "surprise",
    "anomaly_spatial_volume", "active_load", "cognitive_energy",
    # rendering
    "HealthReport",
]


if __name__ == "__main__":
    # Preserve the original ``python cognitive_health.py`` walkthrough.
    run_demo()
