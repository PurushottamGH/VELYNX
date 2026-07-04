"""
research/attribution
====================

**Research Sprint R3 — the Counterfactual Merge Evaluation layer.**

This package evaluates the quality of merge decisions made by a decision policy
against a counterfactual baseline. It answers: *did the policy select the best
possible merge from the candidate pool?*

Core components:

* :class:`CounterfactualMergeEvaluator` — the "market" that ranks proposals,
  selects a winner by ``argmin energy_after`` among accepted proposals, and logs
  the full ranking with margins.
* :class:`CounterfactualEvaluator` — post-hoc evaluation computing replay error,
  the Pareto frontier on (Prediction Delta vs. Complexity Delta), and
  identifying the ``counterfactual_best`` proposal.
* :class:`AttributionLogger` — JSONL structured logging plus an
  ``experiment_manifest.json`` with full reproducibility metadata.
* :mod:`research.attribution.metrics` — hypothesis statistics: top-K accuracy,
  strategy attribution counts, and summary aggregation.
* :class:`AttributionRunner` — end-to-end orchestration for the R3 experiment,
  driving the proposal market loop under a configurable decision policy.

Standard library only. Python 3.11+.
"""

from __future__ import annotations

from research.attribution.counterfactual import CounterfactualEvaluator
from research.attribution.evaluator import CounterfactualMergeEvaluator
from research.attribution.logger import AttributionLogger
from research.attribution.runner import AttributionRunner

__all__ = [
    "CounterfactualMergeEvaluator",
    "CounterfactualEvaluator",
    "AttributionLogger",
    "AttributionRunner",
]
