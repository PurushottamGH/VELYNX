"""
research/evaluation/
====================

**Research Sprint R2A — Minimal Independent Validation.**

A small, side-effect-free layer that lets a *trained* :class:`VectorMonitor`
be scored on a **held-out, seed-disjoint** probe stream without ever mutating
the live model. It exists to answer one honest scientific question that the
in-sample ``PredictionRMSE`` cannot: *how well does the consolidated model
predict data it was never trained on?*

The slice is deliberately minimal. It provides exactly three components:

* :mod:`research.evaluation.split` — deterministic seed partitioning that
  guarantees the evaluation stream shares no RNG lineage with training.
* :mod:`research.evaluation.read_only` — a :class:`ReadOnlyEvaluator` that
  ``deepcopy``-isolates the monitor and rehearses a probe stream against the
  clone, yielding a :class:`ProbeTrace` of per-tick prediction errors.
* :mod:`research.evaluation.protocol` — an :class:`EvaluationProtocol` hook
  whose :meth:`~research.evaluation.protocol.EvaluationProtocol.finalize`
  turns a trained monitor into a single held-out predictive RMSE measurement.

Out of scope for R2A (NOT implemented here): rare-event recall, catastrophic
forgetting / knowledge-retention protocols, curriculum streams, and Gaussian
observation models. Those belong to later sprints (R2B/R2C).

Standard library only. Python 3.11+.
"""

from __future__ import annotations

from research.evaluation.protocol import EvaluationProtocol
from research.evaluation.read_only import ProbeTrace, ReadOnlyEvaluator
from research.evaluation.split import (
    EVAL_SEED_BASE,
    EVAL_SEED_STRIDE,
    assert_disjoint,
    probe_seed,
    seed_lineage,
)

__all__ = [
    "EVAL_SEED_BASE",
    "EVAL_SEED_STRIDE",
    "probe_seed",
    "seed_lineage",
    "assert_disjoint",
    "ProbeTrace",
    "ReadOnlyEvaluator",
    "EvaluationProtocol",
]
