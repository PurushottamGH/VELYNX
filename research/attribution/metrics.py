"""
research/attribution/metrics.py
================================

Post-hoc hypothesis statistics for the R3 counterfactual evaluation.

Key metrics:

* **Top-K Accuracy** (k=3) — was the decision policy's selected winner in the
  top 3 of the ``counterfactual_best`` ranking? This quantifies how often the
  live policy picks a merge that is genuinely among the best available.
* **Strategy Attribution** — how often each source strategy produced the
  counterfactual_best proposal.
* **Summary Statistics** — aggregate over an experiment's worth of evaluation
  windows: top-K hit rate, Pareto coverage rate, average replay error, etc.

Standard library only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def top_k_accuracy(
    selected_id: Optional[str],
    ranking: List[str],
    k: int = 3,
) -> Optional[bool]:
    """Was ``selected_id`` in the top ``k`` of ``ranking``?

    ``ranking`` should be a list of proposal_ids, best-first. Returns ``None``
    when ``selected_id`` is ``None`` (no selection made).
    """
    if selected_id is None:
        return None
    return selected_id in ranking[:k]


def strategy_attribution_counts(
    counterfactual_best_ids: List[str],
) -> Dict[str, int]:
    """Count how often each strategy produced the counterfactual_best proposal.

    Each id is formatted as ``"<strategy>:<lo>-<hi>"`` (see
    :func:`research.proposals.proposal.make_proposal_id`). We extract the
    strategy prefix.
    """
    counts: Dict[str, int] = {}
    for pid in counterfactual_best_ids:
        strategy = pid.split(":", 1)[0] if ":" in pid else "unknown"
        counts[strategy] = counts.get(strategy, 0) + 1
    return counts


@dataclass
class AttributionSummary:
    """Aggregated statistics over many evaluation windows.

    Attributes
    ----------
    num_windows :
        Total number of evaluation windows.
    top_k_hit_count :
        Number of windows where the selected winner was in the top 3 of the
        counterfactual ranking.
    top_k_attempts :
        Number of windows where a selection was made (non-None winner).
    top_k_hit_rate :
        ``top_k_hit_count / top_k_attempts``, or ``None`` when no selections
        were made.
    avg_replay_error :
        Mean replay_error across all proposals evaluated, or ``None`` when no
        replay errors were computed.
    pareto_coverage_rate :
        Fraction of selected winners that lie on the Pareto frontier.
    strategy_attribution :
        Counts of which strategy produced the counterfactual_best proposal.
    winner_strategy_counts :
        Counts of which strategy the live policy selected as winner.
    """

    num_windows: int = 0
    top_k_hit_count: int = 0
    top_k_attempts: int = 0
    top_k_hit_rate: Optional[float] = None
    avg_replay_error: Optional[float] = None
    pareto_coverage_rate: Optional[float] = None
    strategy_attribution: Dict[str, int] = field(default_factory=dict)
    winner_strategy_counts: Dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "num_windows": self.num_windows,
            "top_k_hit_count": self.top_k_hit_count,
            "top_k_attempts": self.top_k_attempts,
            "top_k_hit_rate": _json_float(self.top_k_hit_rate),
            "avg_replay_error": _json_float(self.avg_replay_error),
            "pareto_coverage_rate": _json_float(self.pareto_coverage_rate),
            "strategy_attribution": self.strategy_attribution,
            "winner_strategy_counts": self.winner_strategy_counts,
        }


def aggregate_attribution(
    windows: List[Dict[str, Any]],
    *,
    top_k: int = 3,
) -> AttributionSummary:
    """Aggregate attribution statistics across evaluation ``windows``.

    Each window dict should have keys:

    * ``winner_id`` — the proposal_id the policy selected (or ``None``)
    * ``counterfactual_best_id`` — the optimal post-hoc proposal_id
    * ``counterfactual_ranking`` — list of proposal_ids in best-first order
      (the counterfactual_best ranking)
    * ``winner_is_pareto_optimal`` — bool
    * ``avg_replay_error`` — mean replay_error for this window (or ``None``)
    """
    summary = AttributionSummary(num_windows=len(windows))

    replay_errors: List[float] = []
    cb_best_ids: List[str] = []
    winner_strategies: Dict[str, int] = {}
    pareto_winners = 0
    pareto_total = 0

    for w in windows:
        winner_id = w.get("winner_id")
        cb_best = w.get("counterfactual_best_id")
        ranking = w.get("counterfactual_ranking", [])
        replay_err = w.get("avg_replay_error")

        # Top-K accuracy.
        hit = top_k_accuracy(winner_id, ranking, k=top_k)
        if hit is not None:
            summary.top_k_attempts += 1
            if hit:
                summary.top_k_hit_count += 1

        # Replay errors.
        if replay_err is not None:
            replay_errors.append(float(replay_err))

        # Counterfactual best id for strategy attribution.
        if cb_best:
            cb_best_ids.append(cb_best)

        # Winner strategy.
        if winner_id:
            strategy = winner_id.split(":", 1)[0] if ":" in winner_id else "unknown"
            winner_strategies[strategy] = winner_strategies.get(strategy, 0) + 1

        # Pareto coverage.
        is_pareto = w.get("winner_is_pareto_optimal")
        if is_pareto is not None and winner_id is not None:
            pareto_total += 1
            if is_pareto:
                pareto_winners += 1

    # Finalise.
    if summary.top_k_attempts > 0:
        summary.top_k_hit_rate = summary.top_k_hit_count / summary.top_k_attempts

    if replay_errors:
        summary.avg_replay_error = sum(replay_errors) / len(replay_errors)

    if pareto_total > 0:
        summary.pareto_coverage_rate = pareto_winners / pareto_total

    summary.strategy_attribution = strategy_attribution_counts(cb_best_ids)
    summary.winner_strategy_counts = winner_strategies

    return summary


def _json_float(value: Optional[float]) -> Optional[float]:
    """Coerce a float to JSON-safe (``nan``/``inf`` -> ``None``)."""
    if value is None:
        return None
    f = float(value)
    if math.isnan(f) or math.isinf(f):
        return None
    return f


__all__ = [
    "top_k_accuracy",
    "strategy_attribution_counts",
    "AttributionSummary",
    "aggregate_attribution",
]
