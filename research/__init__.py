"""
research/
=========

The VELYNX **Research Sprint R1** infrastructure: a self-contained,
side-effect-free layer that lets the existing C8 consolidation machinery be
studied scientifically without modifying any frozen cognition.

Nothing in this package mutates, imports-and-monkeypatches, or otherwise alters
the production components it wraps:

* :class:`backend.cognition.decision_policy.DecisionPolicy` (the FreeEnergyPolicy)
* :class:`backend.cognition.replay_engine.ReplayEngine`
* :class:`backend.cognition.candidate_generator.CandidateGenerator`
* :class:`backend.cognition.vector_prediction_core.VectorPredictionCore`
* the entire ``validation`` harness and ``benchmark.py``

Instead it *composes* them behind a small set of research-grade abstractions:

* :mod:`research.policies` — a hot-swappable :class:`ConsolidationPolicy` family
  (Null / Random / FIFOAge / Similarity / Utility / FreeEnergy / Oracle).
* :mod:`research.runner`   — a :class:`ResearchRunner` that drives the same
  scheduler→propose→replay→commit loop as production, but with a *pluggable*
  consolidation policy and a configurable replay horizon, and always measures
  every proposal identically so policies stay comparable.
* :mod:`research.metrics`  — primary / secondary / engineering metric registry,
  honest about which quantities are currently measurable.
* :mod:`research.stats`    — distribution summaries (mean/median/std/CI/min/max)
  and an extensible :class:`HypothesisTest` family.
* :mod:`research.artifacts`— immutable, reproducible per-experiment artifacts.
* :mod:`research.report`   — the ablation-study report generator.

Standard library only. Python 3.11+.
"""

from __future__ import annotations

__all__ = [
    "policies",
    "stats",
    "metrics",
    "runner",
    "artifacts",
    "report",
]
