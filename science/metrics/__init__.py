"""Measurement definitions — one metric per module, one responsibility each.

Responsibility: make the available metrics visible in one place. Importing this
package registers them all.

    online_loss    prequential loss while learning
    retention      M0's change-from-learned scalar, kept for comparability
    excess_loss    loss above the task oracle; the primary outcome family
    plasticity     adaptation cost after switches; the guardrail
    compute        learning-update accounting for resource-matched contrasts
    gate_activity  realised gate timing, incl. boundary-clustering diagnostic

Adding a metric means adding a module and one line here. It never means touching
the experiment loop.
"""

from __future__ import annotations

from science.metrics import (  # noqa: F401  (registration side effects)
    compute,
    excess_loss,
    gate_activity,
    online_loss,
    plasticity,
    retention,
)
from science.metrics.base import BaseMetric, mean

__all__ = [
    "BaseMetric",
    "compute",
    "excess_loss",
    "gate_activity",
    "mean",
    "online_loss",
    "plasticity",
    "retention",
]
