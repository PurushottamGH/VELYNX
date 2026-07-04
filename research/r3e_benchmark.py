"""
research/r3e_benchmark.py - R3E Objective Benchmark Harness
===========================================================

Compares candidate decision objectives under identical experimental conditions.

Candidate objectives:
  1. Replay ΔS   — prediction-error improvement (delta_prediction)
  2. Replay ΔE   — cognitive-energy improvement   (delta_energy)
  3. Replay ΔR   — representation-error improvement (nearest-centroid Δ)
  4. Always Merge — accept unconditionally
  5. Never Merge  — reject unconditionally
  6. Random Merge — accept with probability 0.5 (seeded)

For every objective computes (separately, no composite score):
  • Pearson  r        • Spearman ρ         • Sign Agreement
  • ROC AUC           • MAE                • RMSE
  • Bootstrap 95 % CI • Effect size vs ΔE baseline

Inputs
------
  --log         Path to an evaluation_log.jsonl  (R3B proposal log)
  --held-out    Optional held-out metrics JSON  (default: inferred from log)
  --horizon     Replay horizon                  (default: 200)
  --seed        Random seed for RandomMerge     (default: 42)
  --output      Output path for the report      (default: stdout)

Standard library only.  Python 3.11 + .
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------
# Metrics — standalone, pure functions
# --------------------------------------------------------------------------


def pearson_r(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    """Pearson product-moment correlation coefficient."""
    a = [float(v) for v in x if v is not None]
    b = [float(v) for v in y if v is not None]
    if len(a) != len(b) or len(a) < 2:
        return None
    n = len(a)
    mx = statistics.fmean(a)
    my = statistics.fmean(b)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(a, b))
    dx = sum((xi - mx) ** 2 for xi in a)
    dy = sum((yi - my) ** 2 for yi in b)
    if dx <= 0 or dy <= 0:
        return None
    return num / math.sqrt(dx * dy)


def spearman_r(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    """Spearman rank correlation coefficient."""
    a = [float(v) for v in x if v is not None]
    b = [float(v) for v in y if v is not None]
    if len(a) != len(b) or len(a) < 2:
        return None

    def _rank(seq: List[float]) -> List[float]:
        indexed = sorted(enumerate(seq), key=lambda t: t[1])
        ranks = [0.0] * len(seq)
        for pos, (orig_idx, _) in enumerate(indexed):
            ranks[orig_idx] = float(pos)
        return ranks

    return pearson_r(_rank(a), _rank(b))


def sign_agreement(
    pred_a: Sequence[float],
    pred_b: Sequence[float],
    actual_a: Sequence[float],
    actual_b: Sequence[float],
) -> Optional[float]:
    """Fraction of pairs where (pred_a − pred_b) and (actual_a − actual_b)
    have the same sign (or at least one is zero = tie = agreement)."""
    if len(pred_a) != len(pred_b) or len(pred_a) != len(actual_a) or len(pred_a) != len(actual_b):
        return None
    n = len(pred_a)
    agree = 0
    total = 0
    for i in range(n):
        dp = pred_a[i] - pred_b[i]
        da = actual_a[i] - actual_b[i]
        if dp == 0 and da == 0:
            agree += 1
            total += 1
        elif dp == 0 or da == 0:
            total += 1
        elif (dp > 0) == (da > 0):
            agree += 1
            total += 1
        else:
            total += 1
    return agree / total if total > 0 else None


def roc_auc(scores: Sequence[float], labels: Sequence[int]) -> Optional[float]:
    """Area Under the ROC Curve using the Mann-Whitney U statistic."""
    pos_scores = [float(s) for s, l in zip(scores, labels) if l == 1]
    neg_scores = [float(s) for s, l in zip(scores, labels) if l == 0]
    if not pos_scores or not neg_scores:
        return None
    n_pos = len(pos_scores)
    n_neg = len(neg_scores)
    u = 0.0
    for ps in pos_scores:
        for ns in neg_scores:
            if ps > ns:
                u += 1.0
            elif ps == ns:
                u += 0.5
    return u / (n_pos * n_neg)


def mae(y_true: Sequence[float], y_pred: Sequence[float]) -> Optional[float]:
    """Mean Absolute Error."""
    a = [float(v) for v in y_true if v is not None]
    b = [float(v) for v in y_pred if v is not None]
    if len(a) != len(b) or not a:
        return None
    return sum(abs(t - p) for t, p in zip(a, b)) / len(a)


def rmse(y_true: Sequence[float], y_pred: Sequence[float]) -> Optional[float]:
    """Root Mean Squared Error."""
    a = [float(v) for v in y_true if v is not None]
    b = [float(v) for v in y_pred if v is not None]
    if len(a) != len(b) or not a:
        return None
    return math.sqrt(sum((t - p) ** 2 for t, p in zip(a, b)) / len(a))


def bootstrap_ci(
    x: Sequence[float],
    y: Sequence[float],
    metric_fn: Callable[[Sequence[float], Sequence[float]], Optional[float]],
    *,
    iterations: int = 10_000,
    seed: int = 0,
    ci: float = 0.95,
) -> Dict[str, Optional[float]]:
    """Bootstrap confidence interval for a two-argument metric (e.g. pearson_r)."""
    a = [float(v) for v in x if v is not None]
    b = [float(v) for v in y if v is not None]
    if len(a) != len(b) or len(a) < 4:
        return {"ci95_low": None, "ci95_high": None, "std_err": None}

    rng = random.Random(seed)
    n = len(a)
    stats: List[float] = []
    for _ in range(iterations):
        idx = [rng.randint(0, n - 1) for _ in range(n)]
        bx = [a[i] for i in idx]
        by = [b[i] for i in idx]
        val = metric_fn(bx, by)
        if val is not None:
            stats.append(val)

    if not stats:
        return {"ci95_low": None, "ci95_high": None, "std_err": None}

    stats.sort()
    alpha = (1.0 - ci) / 2.0
    lo = stats[int(alpha * len(stats))]
    hi = stats[min(len(stats) - 1, int((1.0 - alpha) * len(stats)))]
    return {
        "ci95_low": lo,
        "ci95_high": hi,
        "std_err": statistics.stdev(stats) if len(stats) > 1 else 0.0,
    }


def effect_size_cohens_d(
    treatment: Sequence[float], baseline: Sequence[float]
) -> Optional[float]:
    """Cohen's d: (mean_t − mean_b) / pooled_std."""
    t = [float(v) for v in treatment if v is not None]
    b = [float(v) for v in baseline if v is not None]
    if len(t) < 2 or len(b) < 2:
        return None
    mt = statistics.fmean(t)
    mb = statistics.fmean(b)
    st = statistics.stdev(t)
    sb = statistics.stdev(b)
    pooled = math.sqrt(((len(t) - 1) * st ** 2 + (len(b) - 1) * sb ** 2) / (len(t) + len(b) - 2))
    if pooled == 0:
        return None
    return (mt - mb) / pooled


# --------------------------------------------------------------------------
# Ground-truth labels extracted from each evaluation window
# --------------------------------------------------------------------------


@dataclass
class ProposalRecord:
    """One proposal within a single consolidation window."""

    proposal_id: str
    energy_after: float           # predicted post-merge energy from replay

    # Recovered fields (all Optional for backward compatibility with old logs)
    prediction_before: Optional[float] = None
    prediction_after: Optional[float] = None
    delta_prediction: Optional[float] = None
    entropy_before: Optional[float] = None
    entropy_after: Optional[float] = None
    delta_entropy: Optional[float] = None
    load_before: Optional[float] = None
    load_after: Optional[float] = None
    delta_load: Optional[float] = None
    energy_before: Optional[float] = None
    delta_energy: Optional[float] = None

    # Existing fields
    cf_rank: int = -1             # 0-based rank in counterfactual ranking
    is_cf_best: bool = False      # True iff this is the counterfactual best
    replay_error: Optional[float] = None # absolute replay error


@dataclass
class WindowRecord:
    """One consolidation window with all proposals and metadata."""

    window_index: int
    tick: int
    energy_before: float          # no-merge baseline energy
    prediction_before: Optional[float] = None  # no-merge baseline S (recovered)
    proposals: List[ProposalRecord] = field(default_factory=list)
    cf_best_id: str = ""
    cf_best_energy: float = float("nan")


# --------------------------------------------------------------------------
# Objectives — each maps a proposal to a continuous score (higher = better)
# --------------------------------------------------------------------------


class Objective(ABC):
    """Abstract base for a candidate decision objective."""

    name: str = "abstract"

    @abstractmethod
    def score(self, proposal: ProposalRecord, window: WindowRecord) -> float:
        ...

    @abstractmethod
    def describe(self) -> Dict[str, Any]:
        ...


class ReplayDeltaE(Objective):
    """ΔE = E_before − E_after. Accept when ΔE >= 0."""

    name = "Replay_ΔE"

    def score(self, proposal: ProposalRecord, window: WindowRecord) -> float:
        return window.energy_before - proposal.energy_after

    def describe(self) -> Dict[str, Any]:
        return {"objective": self.name, "criterion": "ΔE = E_before − E_after ≥ 0"}


class ReplayDeltaS(Objective):
    """ΔS = prediction_error_before − prediction_error_after.

    Uses the recovered ``delta_prediction`` field from the serialised
    decision_trace, which equals S_before − S_after (higher is better:
    positive means the merge reduced prediction error).
    """

    name = "Replay_ΔS"

    def score(self, proposal: ProposalRecord, window: WindowRecord) -> float:
        if proposal.delta_prediction is not None:
            return proposal.delta_prediction
        fallback = _safe_delta_s(proposal, window)
        if fallback is not None:
            return fallback
        raise ValueError(
            "ΔS unavailable: neither delta_prediction nor "
            "prediction_before/prediction_after are present in the log data."
        )

    def describe(self) -> Dict[str, Any]:
        return {
            "objective": self.name,
            "criterion": "ΔS = S_before − S_after ≥ 0",
            "available": True,
        }


def _safe_delta_s(proposal: ProposalRecord, window: WindowRecord) -> Optional[float]:
    """Fallback: compute ΔS from individual before/after fields when
    delta_prediction is absent (legacy log compatibility)."""
    if proposal.prediction_before is not None and proposal.prediction_after is not None:
        return proposal.prediction_before - proposal.prediction_after
    if window.prediction_before is not None and proposal.prediction_after is not None:
        return window.prediction_before - proposal.prediction_after
    return None


class ReplayDeltaR(Objective):
    """ΔR = representation_error_before − representation_error_after.

    NOTE: Representation error (nearest-centroid distance, shared_metrics_v1
    compute_R_representation_error) is NOT a standard vital in the replay
    engine or decision policy.  This objective requires adding R to the
    vitals set before it can be computed.
    """

    name = "Replay_ΔR"

    def score(self, proposal: ProposalRecord, window: WindowRecord) -> float:
        raise NotImplementedError(
            "ΔR requires representation-error (R) to be measured during "
            "replay, which the current ReplayEngine does not compute. "
            "See shared_metrics_v1.compute_R_representation_error."
        )

    def describe(self) -> Dict[str, Any]:
        return {
            "objective": self.name,
            "criterion": "ΔR = R_before − R_after ≥ 0",
            "available": False,
            "reason": "R not measured by ReplayEngine",
        }


class AlwaysMerge(Objective):
    """Accept unconditionally — every merge is beneficial."""

    name = "Always_Merge"

    def score(self, proposal: ProposalRecord, window: WindowRecord) -> float:
        return 1.0

    def describe(self) -> Dict[str, Any]:
        return {"objective": self.name, "criterion": "always accept (score = 1.0)"}


class NeverMerge(Objective):
    """Reject unconditionally — no merge is beneficial."""

    name = "Never_Merge"

    def score(self, proposal: ProposalRecord, window: WindowRecord) -> float:
        return 0.0

    def describe(self) -> Dict[str, Any]:
        return {"objective": self.name, "criterion": "never accept (score = 0.0)"}


class RandomMerge(Objective):
    """Accept with probability 0.5 (seeded reproducibility)."""

    name = "Random_Merge"

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def score(self, proposal: ProposalRecord, window: WindowRecord) -> float:
        return self._rng.random()

    def describe(self) -> Dict[str, Any]:
        return {"objective": self.name, "criterion": "random accept (p = 0.5)"}


# --------------------------------------------------------------------------
# Log loader
# --------------------------------------------------------------------------


def load_windows(path: str) -> List[WindowRecord]:
    """Parse an ``evaluation_log.jsonl`` into a list of :class:`WindowRecord`."""
    windows: List[WindowRecord] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            windows.append(_parse_window(row))
    return windows


def _opt_float(v: Any) -> Optional[float]:
    """Safely coerce a JSON value to float or None."""
    if v is None:
        return None
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (ValueError, TypeError):
        return None


def _parse_window(row: Dict[str, Any]) -> WindowRecord:
    w_idx = int(row.get("window_index", -1))
    tick = int(row.get("tick", -1))

    cf_result = row.get("counterfactual_result", {}) or {}
    energy_before = float(cf_result.get("no_merge_energy", float("nan")))
    cf_best_id = str(cf_result.get("counterfactual_best_id", ""))
    cf_best_energy_raw = cf_result.get("counterfactual_best_energy")
    cf_best_energy = float(cf_best_energy_raw) if cf_best_energy_raw is not None else float("nan")

    cf_ranking_ids: List[str] = row.get("counterfactual_ranking_ids", [])
    replay_errors_raw: Dict[str, Optional[float]] = row.get("replay_errors_per_proposal", {}) or {}

    rankings: List[Dict[str, Any]] = (
        (row.get("evaluator_result", {}) or {}).get("rankings", [])
    )

    proposals: List[ProposalRecord] = []
    for entry in rankings:
        pid = entry.get("proposal_id", "?")
        energy_after = float(entry.get("energy_after", float("nan")))
        try:
            cf_rank = cf_ranking_ids.index(pid) if pid in cf_ranking_ids else -1
        except ValueError:
            cf_rank = -1
        re_raw = replay_errors_raw.get(pid)
        replay_error = float(re_raw) if re_raw is not None else None
        proposals.append(ProposalRecord(
            proposal_id=pid,
            energy_after=energy_after,
            # Recovered fields (Optional — backward compatible)
            prediction_before=_opt_float(entry.get("prediction_before")),
            prediction_after=_opt_float(entry.get("prediction_after")),
            delta_prediction=_opt_float(entry.get("delta_prediction")),
            entropy_before=_opt_float(entry.get("entropy_before")),
            entropy_after=_opt_float(entry.get("entropy_after")),
            delta_entropy=_opt_float(entry.get("delta_entropy")),
            load_before=_opt_float(entry.get("load_before")),
            load_after=_opt_float(entry.get("load_after")),
            delta_load=_opt_float(entry.get("delta_load")),
            energy_before=_opt_float(entry.get("energy_before")),
            delta_energy=_opt_float(entry.get("delta_energy")),
            # Existing fields
            cf_rank=cf_rank,
            is_cf_best=(pid == cf_best_id),
            replay_error=replay_error,
        ))

    # Extract window-level prediction_baseline from the first proposal with data.
    prediction_before: Optional[float] = None
    for p in proposals:
        if p.prediction_before is not None:
            prediction_before = p.prediction_before
            break

    return WindowRecord(
        window_index=w_idx,
        tick=tick,
        energy_before=energy_before,
        prediction_before=prediction_before,
        proposals=proposals,
        cf_best_id=cf_best_id,
        cf_best_energy=cf_best_energy,
    )


# --------------------------------------------------------------------------
# Field validation
# --------------------------------------------------------------------------


RECOVERED_FIELDS = [
    "prediction_before", "prediction_after", "delta_prediction",
    "entropy_before", "entropy_after", "delta_entropy",
    "load_before", "load_after", "delta_load",
    "energy_before", "delta_energy",
]


def validate_fields(windows: List[WindowRecord]) -> Dict[str, Any]:
    """Check that every recovered field is present for every proposal.

    Returns a dict with per-field presence counts and any missing-value
    warnings.
    """
    total = sum(len(w.proposals) for w in windows)
    present: Dict[str, int] = {f: 0 for f in RECOVERED_FIELDS}
    for w in windows:
        for p in w.proposals:
            for f in RECOVERED_FIELDS:
                if getattr(p, f, None) is not None:
                    present[f] += 1

    missing: Dict[str, List[str]] = {f: [] for f in RECOVERED_FIELDS}
    for w in windows:
        for p in w.proposals:
            for f in RECOVERED_FIELDS:
                if getattr(p, f, None) is None:
                    missing[f].append(
                        f"window={w.window_index}, proposal={p.proposal_id}"
                    )

    # Only report first 3 missing examples per field.
    missing_sample = {
        f: examples[:3] for f, examples in missing.items() if examples
    }

    all_present = all(v == total for v in present.values())

    return {
        "total_proposals": total,
        "all_fields_present": all_present,
        "per_field_proportion": {
            f: f"{cnt}/{total} ({100*cnt/total:.1f}%)"
            for f, cnt in present.items()
        },
        "missing_samples": missing_sample,
    }


# --------------------------------------------------------------------------
# Per-objective evaluation
# --------------------------------------------------------------------------


@dataclass
class ObjectiveResult:
    """All metrics for one objective evaluated on a log."""

    name: str
    num_proposals: int
    num_windows: int
    pearson: Optional[float]
    spearman: Optional[float]
    sign_agreement: Optional[float]
    roc_auc: Optional[float]
    mae: Optional[float]
    rmse: Optional[float]
    pearson_ci: Dict[str, Optional[float]]
    spearman_ci: Dict[str, Optional[float]]
    roc_auc_ci: Dict[str, Optional[float]]
    effect_size_vs_de: Optional[float]
    details: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.name,
            "n_proposals": self.num_proposals,
            "n_windows": self.num_windows,
            "pearson_r": _jf(self.pearson),
            "pearson_ci95_low": _jf(self.pearson_ci.get("ci95_low")),
            "pearson_ci95_high": _jf(self.pearson_ci.get("ci95_high")),
            "spearman_rho": _jf(self.spearman),
            "spearman_ci95_low": _jf(self.spearman_ci.get("ci95_low")),
            "spearman_ci95_high": _jf(self.spearman_ci.get("ci95_high")),
            "sign_agreement": _jf(self.sign_agreement),
            "roc_auc": _jf(self.roc_auc),
            "roc_auc_ci95_low": _jf(self.roc_auc_ci.get("ci95_low")),
            "roc_auc_ci95_high": _jf(self.roc_auc_ci.get("ci95_high")),
            "mae": _jf(self.mae),
            "rmse": _jf(self.rmse),
            "effect_size_vs_Replay_ΔE": _jf(self.effect_size_vs_de),
            "details": self.details,
        }

    def short_line(self) -> str:
        def _s(v: Optional[float]) -> str:
            if v is None:
                return "  N/A  "
            return f"{v:7.4f}"
        return (
            f"  {self.name:<16s}"
            f" r={_s(self.pearson)}  ρ={_s(self.spearman)}"
            f"  AUC={_s(self.roc_auc)}"
            f"  MAE={_s(self.mae)}  RMSE={_s(self.rmse)}"
            f"  d={_s(self.effect_size_vs_de)}"
        )


def _jf(v: Any) -> Optional[float]:
    """JSON-safe float."""
    if v is None:
        return None
    f = float(v)
    if math.isnan(f) or math.isinf(f):
        return None
    return round(f, 6)


def evaluate_objective(
    objective: Objective,
    windows: List[WindowRecord],
    *,
    de_scores: Optional[List[float]] = None,
    bootstrap_iterations: int = 10_000,
    bootstrap_seed: int = 0,
) -> ObjectiveResult:
    """Run a single objective against the logged windows and return all metrics.

    Parameters
    ----------
    objective :
        The objective to evaluate.
    windows :
        Parsed window records from :func:`load_windows`.
    de_scores :
        The ΔE predicted scores (for effect-size comparison). Pass once and
        reuse across objectives.
    """
    y_true_list: List[float] = []
    y_pred_list: List[float] = []
    labels_list: List[int] = []
    pair_pred_a: List[float] = []
    pair_pred_b: List[float] = []
    pair_actual_a: List[float] = []
    pair_actual_b: List[float] = []
    total_proposals = 0

    for w in windows:
        n = len(w.proposals)
        if n < 2:
            continue

        # Compute scores for this window.
        try:
            scores = [objective.score(p, w) for p in w.proposals]
        except NotImplementedError:
            return ObjectiveResult(
                name=objective.name,
                num_proposals=0,
                num_windows=len(windows),
                pearson=None, spearman=None, sign_agreement=None,
                roc_auc=None, mae=None, rmse=None,
                pearson_ci={}, spearman_ci={}, roc_auc_ci={},
                effect_size_vs_de=None,
                details={"available": False, "note": str(__import__("sys").exc_info()[1])},
            )

        for p, s in zip(w.proposals, scores):
            y_true_list.append(float(p.cf_rank))
            y_pred_list.append(float(s))
            labels_list.append(1 if p.is_cf_best else 0)
            total_proposals += 1

        # Pairwise sign agreement: (i, j) for i < j
        for i in range(n):
            for j in range(i + 1, n):
                pair_pred_a.append(scores[i])
                pair_pred_b.append(scores[j])
                pair_actual_a.append(float(w.proposals[i].cf_rank))
                pair_actual_b.append(float(w.proposals[j].cf_rank))

    if total_proposals < 4:
        return ObjectiveResult(
            name=objective.name,
            num_proposals=total_proposals,
            num_windows=len(windows),
            pearson=None, spearman=None, sign_agreement=None,
            roc_auc=None, mae=None, rmse=None,
            pearson_ci={}, spearman_ci={}, roc_auc_ci={},
            effect_size_vs_de=None,
            details={"available": True, "note": "insufficient data"},
        )

    # Correlation (negate y_true so positive r = alignment)
    neg_rank = [-v for v in y_true_list]
    pears = pearson_r(y_pred_list, neg_rank)
    spear = spearman_r(y_pred_list, neg_rank)
    sa = sign_agreement(pair_pred_a, pair_pred_b, pair_actual_b, pair_actual_a)
    auc = roc_auc(y_pred_list, labels_list)
    mae_val = mae(y_true_list, y_pred_list)
    rmse_val = rmse(y_true_list, y_pred_list)

    # Bootstrap CIs
    pears_ci = bootstrap_ci(y_pred_list, neg_rank, pearson_r,
                            iterations=bootstrap_iterations, seed=bootstrap_seed)
    spear_ci = bootstrap_ci(y_pred_list, neg_rank, spearman_r,
                            iterations=bootstrap_iterations, seed=bootstrap_seed + 1)
    auc_ci = bootstrap_ci(y_pred_list, [float(l) for l in labels_list], roc_auc,
                          iterations=bootstrap_iterations, seed=bootstrap_seed + 2)

    # Effect size vs ΔE
    eff = None
    if de_scores is not None and len(de_scores) == len(y_pred_list):
        eff = effect_size_cohens_d(y_pred_list, de_scores)

    return ObjectiveResult(
        name=objective.name,
        num_proposals=total_proposals,
        num_windows=len(windows),
        pearson=pears,
        spearman=spear,
        sign_agreement=sa,
        roc_auc=auc,
        mae=mae_val,
        rmse=rmse_val,
        pearson_ci=pears_ci,
        spearman_ci=spear_ci,
        roc_auc_ci=auc_ci,
        effect_size_vs_de=eff,
        details={"available": True},
    )


# --------------------------------------------------------------------------
# Report printer
# --------------------------------------------------------------------------


def format_report(
    results: List[ObjectiveResult],
    log_path: str,
    config: Dict[str, Any],
) -> str:
    """Build a plain-text report from all objective results."""
    lines: List[str] = []
    _sep = "=" * 78

    lines.append(_sep)
    lines.append("R3E OBJECTIVE BENCHMARK REPORT")
    lines.append(_sep)
    lines.append(f"  Log file          : {log_path}")
    lines.append(f"  Windows           : {config.get('num_windows', '?')}")
    lines.append(f"  Horizon           : {config.get('horizon', '?')}")
    lines.append(f"  Held-out available: {config.get('has_held_out', '?')}")
    lines.append("")

    # Check which objectives are available.
    available = [r for r in results if r.num_proposals > 0]
    unavailable = [r for r in results if r.num_proposals == 0]
    for r in unavailable:
        lines.append(f"  [!] {r.name}: not computable from current log data")

    if not available:
        lines.append("\n  No objectives could be evaluated.")
        return "\n".join(lines)

    # Field validation section
    field_report = config.get("field_validation", {})
    if field_report:
        lines.append("─" * 78)
        lines.append("FIELD VALIDATION — Serialization Recovery Audit")
        lines.append("─" * 78)
        lines.append(f"  Total proposals  : {field_report.get('total_proposals', '?')}")
        lines.append(f"  All fields present: {field_report.get('all_fields_present', '?')}")
        lines.append("")
        lines.append("  Per-field presence:")
        for f_name, proportion in field_report.get("per_field_proportion", {}).items():
            lines.append(f"    {f_name:<25s} {proportion}")
        missing = field_report.get("missing_samples", {})
        if missing:
            lines.append("")
            lines.append("  [!] Missing value examples (first 3 per field):")
            for f_name, examples in missing.items():
                for ex in examples:
                    lines.append(f"    {f_name:<25s} {ex}")
        lines.append("")

    lines.append("")
    lines.append("─" * 78)
    lines.append("PER-OBJECTIVE METRICS  (higher-is-better: r, ρ, AUC; lower-is-better: MAE, RMSE)")
    lines.append("─" * 78)
    header = (
        f"  {'Objective':<16s} {'Pearson r':>8s} {'Spearman ρ':>8s}"
        f" {'AUC':>8s} {'MAE':>8s} {'RMSE':>8s}"
        f" {'d(vsΔE)':>8s}"
    )
    lines.append(header)
    lines.append("  " + "-" * 72)
    for r in available:
        lines.append(r.short_line())
    lines.append("")

    # Detail: confidence intervals
    lines.append("─" * 78)
    lines.append("BOOTSTRAP 95 % CONFIDENCE INTERVALS  (10 000 iterations)")
    lines.append("─" * 78)
    ci_header = (
        f"  {'Objective':<16s} {'Pearson CI':>22s}"
        f" {'Spearman CI':>22s} {'AUC CI':>22s}"
    )
    lines.append(ci_header)
    lines.append("  " + "-" * 82)
    for r in available:
        pc = r.pearson_ci
        sc = r.spearman_ci
        ac = r.roc_auc_ci
        def _ci(d: Dict) -> str:
            lo = d.get("ci95_low")
            hi = d.get("ci95_high")
            if lo is None or hi is None:
                return "  N/A  "
            return f"[{lo:7.4f}, {hi:7.4f}]"
        lines.append(
            f"  {r.name:<16s} {_ci(pc):>22s} {_ci(sc):>22s} {_ci(ac):>22s}"
        )
    lines.append("")

    # Sign agreement
    lines.append("─" * 78)
    lines.append("SIGN AGREEMENT  (pairwise: fraction where objective & ground-truth agree)")
    lines.append("─" * 78)
    for r in available:
        sa = r.sign_agreement
        sa_str = f"{sa:.4f}" if sa is not None else "N/A"
        lines.append(f"  {r.name:<16s}  {sa_str}")
    lines.append("")

    # Effect sizes
    lines.append("─" * 78)
    lines.append("EFFECT SIZE (Cohen's d) vs Replay_ΔE baseline")
    lines.append("─" * 78)
    for r in available:
        if r.name == "Replay_ΔE":
            lines.append(f"  {r.name:<16s}  (baseline)")
        else:
            d_str = f"{r.effect_size_vs_de:.4f}" if r.effect_size_vs_de is not None else "N/A"
            lines.append(f"  {r.name:<16s}  d = {d_str}")
    lines.append("")

    # Statistical superiority test
    lines.append("─" * 78)
    lines.append("STATISTICAL SUPERIORITY TEST")
    lines.append("─" * 78)
    de_result = next((r for r in available if r.name == "Replay_ΔE"), None)
    if de_result is not None and de_result.pearson is not None:
        lines.append(
            f"  Replay_ΔE achieves Pearson r = {de_result.pearson:.4f}"
        )
        dominated = True
        for r in available:
            if r.name == "Replay_ΔE":
                continue
            if r.pearson is not None and r.pearson > de_result.pearson:
                lines.append(
                    f"  [!]  {r.name} has HIGHER Pearson r ({r.pearson:.4f}) "
                    f"than Replay_ΔE — ΔE is not strictly dominant."
                )
                dominated = False
        if dominated:
            lines.append(
                "  Replay_ΔE achieves the highest Pearson r among all "
                "evaluated objectives."
            )
        else:
            lines.append(
                "  Replay_ΔE does NOT strictly dominate all alternatives. "
                "See the individual metrics for nuance."
            )
    else:
        lines.append("  (Cannot assess — ΔE is not available or has no Pearson r.)")
    lines.append("")

    # Final conclusion
    lines.append(_sep)
    lines.append("CONCLUSION")
    lines.append(_sep)
    if not available:
        lines.append("  No objectives could be evaluated on the provided log data.")
    elif len(available) == 1:
        lines.append(
            f"  Only {available[0].name} could be evaluated.  "
            "Insufficient data for a comparative conclusion."
        )
    else:
        # Check if any objective clearly dominates all others on every metric.
        best_pearson = max((r for r in available if r.pearson is not None), key=lambda r: r.pearson, default=None)
        best_spearman = max((r for r in available if r.spearman is not None), key=lambda r: r.spearman, default=None)
        best_auc = max((r for r in available if r.roc_auc is not None), key=lambda r: r.roc_auc, default=None)
        best_mae = min((r for r in available if r.mae is not None), key=lambda r: r.mae, default=None)
        best_rmse = min((r for r in available if r.rmse is not None), key=lambda r: r.rmse, default=None)

        if best_pearson is not None and best_spearman is not None and best_auc is not None:
            all_names = {r.name for r in available if r.name != "Replay_ΔE"}
            # Check if Replay_ΔE wins on ALL metrics.
            de = de_result
            if de is not None:
                dominates = True
                for r in available:
                    if r.name == "Replay_ΔE":
                        continue
                    if r.pearson is not None and r.pearson > de.pearson:
                        dominates = False
                    if r.spearman is not None and r.spearman > de.spearman:
                        dominates = False
                    if r.roc_auc is not None and r.roc_auc > de.roc_auc:
                        dominates = False
                if dominates:
                    lines.append(
                        "  Replay_ΔE dominates all evaluated alternatives "
                        "on every metric."
                    )
                else:
                    lines.append(
                        "  No single objective clearly dominates.  "
                        "Different objectives lead on different metrics:"
                    )
                    field_map = {
                        "Pearson r": "pearson",
                        "Spearman ρ": "spearman",
                        "ROC AUC": "roc_auc",
                        "MAE": "mae",
                        "RMSE": "rmse",
                    }
                    for metric, best_obj, is_higher in [
                        ("Pearson r", best_pearson, True),
                        ("Spearman ρ", best_spearman, True),
                        ("ROC AUC", best_auc, True),
                        ("MAE", best_mae, False),
                        ("RMSE", best_rmse, False),
                    ]:
                        if best_obj is not None:
                            direction = "highest" if is_higher else "lowest"
                            val = getattr(best_obj, field_map[metric])
                            lines.append(
                                f"    {metric}: {best_obj.name} ({direction} = {val:.4f})"
                            )
                lines.append("")
                if de_result is not None:
                    de_r = de_result.pearson
                    ds_result = next((r for r in available if r.name == "Replay_ΔS"), None)
                    ds_r = ds_result.pearson if ds_result else None
                    if ds_r is not None and de_r is not None:
                        if ds_r > 0.30 and ds_r > de_r:
                            lines.append(
                                "  R3F.1 DECISION: Case A — ΔS r > 0.30 and ΔS r > ΔE r.  "
                                "Replay objective function is the likely bottleneck.  "
                                "Next sprint: Objective Reformulation."
                            )
                        elif ds_r <= de_r and de_r is not None:
                            lines.append(
                                "  R3F.1 DECISION: Case B — ΔS ≤ ΔE.  "
                                "Objective is not the bottleneck.  "
                                "Replay representation or horizon likely limits performance.  "
                                "Next sprint: Replay Information Content Audit."
                            )
                        elif ds_r < 0:
                            lines.append(
                                "  R3F.1 DECISION: Case C — ΔS < 0.  "
                                "Evaluation pipeline is suspect.  "
                                "STOP: audit benchmark correctness before further research."
                            )
                        else:
                            lines.append(
                                "  R3F.1: No clear decision case matched.  "
                                "Review metrics for nuance."
                            )
                    else:
                        lines.append(
                            "  R3F.1: ΔS not computable — no decision possible."
                        )
            else:
                lines.append("  (Cannot assess — ΔE not available.)")
        else:
            lines.append("  Insufficient metrics for a dominance determination.")

    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description="R3E Objective Benchmark Harness"
    )
    parser.add_argument("--log", required=True,
                        help="Path to evaluation_log.jsonl")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for RandomMerge (default: 42)")
    parser.add_argument("--bootstrap-iterations", type=int, default=10_000)
    parser.add_argument("--bootstrap-seed", type=int, default=0)
    parser.add_argument("--output", default=None,
                        help="Output file path (default: stdout)")
    args = parser.parse_args()

    # Load data.
    windows = load_windows(args.log)
    has_held_out = any(p.replay_error is not None for w in windows for p in w.proposals)

    config: Dict[str, Any] = {
        "num_windows": len(windows),
        "horizon": 200,
        "has_held_out": has_held_out,
    }

    # Build objectives.
    objectives: List[Objective] = [
        ReplayDeltaE(),
        ReplayDeltaS(),
        ReplayDeltaR(),
        AlwaysMerge(),
        NeverMerge(),
        RandomMerge(seed=args.seed),
    ]

    # Pre-compute ΔE scores for effect-size baseline.
    de_obj = ReplayDeltaE()
    de_scores: List[float] = []
    for w in windows:
        for p in w.proposals:
            de_scores.append(de_obj.score(p, w))

    # Field validation.
    field_validation = validate_fields(windows)
    config["field_validation"] = field_validation

    # Evaluate every objective.
    results: List[ObjectiveResult] = []
    for obj in objectives:
        res = evaluate_objective(
            obj, windows,
            de_scores=de_scores,
            bootstrap_iterations=args.bootstrap_iterations,
            bootstrap_seed=args.bootstrap_seed,
        )
        results.append(res)

    report = format_report(results, args.log, config)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)

    # Also emit JSON for programmatic consumption.
    json_path = (args.output.rsplit(".", 1)[0] + ".json") if args.output else "r3e_results.json"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "config": config,
                "objectives": [r.as_dict() for r in results],
            },
            fh, indent=2, sort_keys=True,
        )
    print(f"JSON results written to {json_path}")


if __name__ == "__main__":
    main()
