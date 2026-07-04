"""
research/metrics.py
===================

The Sprint R1 research-metric registry (Task 2).

Every metric is declared as a :class:`MetricSpec` carrying its scientific
category (primary / secondary / engineering), directionality, units, an
``available`` flag, and an extractor that pulls a single scalar out of one
run's *measurement record*. Aggregation across the repeated runs of a cell
(the seeds) is delegated to :class:`~research.stats.SummaryStatistics`, so every
metric automatically exposes **mean, standard deviation, 95% confidence interval
and sample count** as the sprint requires.

Honesty first
-------------
The sprint lists six *primary* metrics. Only one of them — ``PredictionRMSE`` —
is actually measurable from the current C7/C8 substrate and the
:class:`~research.runner.ResearchRunner`'s measurement record. The other five
(held-out predictive log-likelihood, rare-event recall, knowledge retention,
generalization, transfer) require machinery this codebase does **not** have:
a held-out evaluation split, exposed ground-truth regime labels, and multi-task
/ multi-phase protocols. Fabricating numbers for them would defeat the entire
purpose of this sprint (establishing *honest* scientific controls), so they are
registered with ``available=False`` and extract to ``None``. The aggregator
represents an all-``None`` metric as ``n=0`` with null statistics, and the
ablation report lists them under "Limitations" / "Future Work".

The *measurement record* contract
---------------------------------
A run's measurement record is the plain ``dict`` the runner returns under
``RunResult.measurements``. Its canonical keys are the ``source`` strings below.
Keeping extraction keyed on a flat dict (rather than the rich result object)
keeps this module decoupled from the runner and trivially unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional, Sequence

from research.stats import SummaryStatistics

# Metric categories (the three tiers the sprint defines).
PRIMARY = "primary"
SECONDARY = "secondary"
ENGINEERING = "engineering"

# Directionality of "good".
LOWER_IS_BETTER = "lower_is_better"
HIGHER_IS_BETTER = "higher_is_better"
NEUTRAL = "neutral"  # descriptive only; no inherent good direction


def _reader(source: str) -> Callable[[Mapping[str, object]], Optional[float]]:
    """Build an extractor that reads ``source`` from a measurement record.

    Returns ``None`` (not 0.0) when the key is absent or null, so "we did not
    measure this" is never silently conflated with "we measured zero".
    """

    def extract(record: Mapping[str, object]) -> Optional[float]:
        value = record.get(source)
        if value is None:
            return None
        try:
            return float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None

    return extract


def _unavailable(record: Mapping[str, object]) -> Optional[float]:
    """Extractor for metrics that are not measurable in the current substrate."""
    return None


@dataclass(frozen=True)
class MetricSpec:
    """Declarative description of a single research metric.

    Attributes
    ----------
    name :
        Stable identifier (the sprint's metric name, e.g. ``"PredictionRMSE"``).
    category :
        One of :data:`PRIMARY` / :data:`SECONDARY` / :data:`ENGINEERING`.
    direction :
        Directionality of improvement (see the module constants).
    units :
        Human-readable units, surfaced in the report.
    available :
        ``True`` iff this metric is genuinely measurable here. ``False`` metrics
        always aggregate to an empty summary and are reported as limitations.
    extract :
        ``record -> Optional[float]`` pulling this metric's scalar from one run.
    note :
        Optional rationale (especially *why* an unavailable metric is missing).
    """

    name: str
    category: str
    direction: str
    units: str
    available: bool
    extract: Callable[[Mapping[str, object]], Optional[float]]
    note: str = ""


# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------

_PRIMARY_SPECS: List[MetricSpec] = [
    MetricSpec(
        "PredictionRMSE", PRIMARY, LOWER_IS_BETTER, "sensor-vector distance",
        available=True, extract=_reader("prediction_rmse"),
        note="Root-mean-square per-tick prediction error over the whole run.",
    ),
    MetricSpec(
        "HeldOutPredictiveRMSE", PRIMARY, LOWER_IS_BETTER, "sensor-vector distance",
        available=True, extract=_reader("held_out_predictive_rmse"),
        note="R2A: root-mean-square per-tick prediction error over a held-out, "
             "seed-disjoint probe stream, scored read-only against a deepcopy "
             "of the trained monitor (no leakage, no mutation). Populated only "
             "when a run carries an EvaluationProtocol; null otherwise.",
    ),
    MetricSpec(
        "HeldOutPredictiveLogLikelihood", PRIMARY, HIGHER_IS_BETTER, "nats",
        available=False, extract=_unavailable,
        note="Requires a held-out split and a probabilistic predictor; the C7 "
             "core emits point predictions only. Not measurable in R1.",
    ),
    MetricSpec(
        "RareEventRecall", PRIMARY, HIGHER_IS_BETTER, "fraction",
        available=False, extract=_unavailable,
        note="Requires exposed ground-truth rare-event labels; the Dataset "
             "contract deliberately hides ground truth. Not measurable in R1.",
    ),
    MetricSpec(
        "KnowledgeRetentionScore", PRIMARY, HIGHER_IS_BETTER, "fraction",
        available=False, extract=_unavailable,
        note="Requires a re-test of earlier-learned regimes after later "
             "learning (a retention protocol not present). Not measurable in R1.",
    ),
    MetricSpec(
        "GeneralizationScore", PRIMARY, HIGHER_IS_BETTER, "fraction",
        available=False, extract=_unavailable,
        note="Requires an unseen-but-related evaluation distribution. "
             "Not measurable in R1.",
    ),
    MetricSpec(
        "TransferScore", PRIMARY, HIGHER_IS_BETTER, "fraction",
        available=False, extract=_unavailable,
        note="Requires a distinct downstream task to transfer to. "
             "Not measurable in R1.",
    ),
]

_SECONDARY_SPECS: List[MetricSpec] = [
    MetricSpec(
        "FinalEnergy", SECONDARY, LOWER_IS_BETTER, "free-energy (a.u.)",
        available=True, extract=_reader("final_energy"),
        note="Run-level cognitive free-energy proxy E=lam*H+mu*S_mean+nu*A at "
             "end of run. NOTE: FreeEnergyPolicy optimizes a closely related "
             "quantity by construction, so a FreeEnergy advantage here is "
             "partly definitional — see report 'Threats to Validity'.",
    ),
    MetricSpec(
        "ReplayEfficiency", SECONDARY, HIGHER_IS_BETTER, "percent",
        available=True, extract=_reader("replay_efficiency"),
        note="Committed merges as a percentage of replay evaluations.",
    ),
    MetricSpec(
        "MergeAcceptanceRate", SECONDARY, NEUTRAL, "fraction",
        available=True, extract=_reader("merge_acceptance_rate"),
        note="Accepted proposals / evaluated proposals.",
    ),
    MetricSpec(
        "AverageReplayCost", SECONDARY, LOWER_IS_BETTER, "vectors / replay",
        available=True, extract=_reader("avg_replay_cost"),
        note="Mean replay-window size per proposal evaluation.",
    ),
    MetricSpec(
        "ClusterCount", SECONDARY, NEUTRAL, "clusters",
        available=True, extract=_reader("final_cluster_count"),
        note="Live clusters at end of run.",
    ),
    MetricSpec(
        "Entropy", SECONDARY, LOWER_IS_BETTER, "bits",
        available=True, extract=_reader("final_entropy"),
        note="Conditional transition entropy of the final cluster chain.",
    ),
    MetricSpec(
        "ActiveLoad", SECONDARY, LOWER_IS_BETTER, "clusters + variance",
        available=True, extract=_reader("final_active_load"),
        note="Structural load at end of run.",
    ),
    MetricSpec(
        "AverageLifetime", SECONDARY, NEUTRAL, "ticks",
        available=True, extract=_reader("avg_anomaly_lifetime"),
        note="Mean resolved-anomaly quarantine lifetime.",
    ),
]

_ENGINEERING_SPECS: List[MetricSpec] = [
    MetricSpec(
        "Runtime", ENGINEERING, LOWER_IS_BETTER, "seconds",
        available=True, extract=_reader("runtime_seconds"),
        note="Wall-clock duration of the run loop.",
    ),
    MetricSpec(
        "MemoryUsage", ENGINEERING, LOWER_IS_BETTER, "bytes",
        available=True, extract=_reader("peak_memory_bytes"),
        note="Peak Python heap during the run (tracemalloc).",
    ),
    MetricSpec(
        "ReplayDuration", ENGINEERING, LOWER_IS_BETTER, "seconds",
        available=True, extract=_reader("replay_seconds"),
        note="Cumulative time spent in read-only replay rehearsals.",
    ),
    MetricSpec(
        "MergeCount", ENGINEERING, NEUTRAL, "merges",
        available=True, extract=_reader("merges_committed"),
        note="Total merges committed to the live engine.",
    ),
    MetricSpec(
        "ArtifactSize", ENGINEERING, LOWER_IS_BETTER, "bytes",
        available=True, extract=_reader("artifact_size_bytes"),
        note="On-disk size of this experiment's artifact directory "
             "(populated post-write; may be null in the live metrics record).",
    ),
]

#: Ordered registry: primary first, then secondary, then engineering.
METRIC_REGISTRY: List[MetricSpec] = (
    _PRIMARY_SPECS + _SECONDARY_SPECS + _ENGINEERING_SPECS
)

#: Name -> spec for direct lookup.
METRICS_BY_NAME: Dict[str, MetricSpec] = {m.name: m for m in METRIC_REGISTRY}


def metrics_for(category: Optional[str] = None) -> List[MetricSpec]:
    """All metric specs, optionally filtered to one category."""
    if category is None:
        return list(METRIC_REGISTRY)
    return [m for m in METRIC_REGISTRY if m.category == category]


def available_metrics() -> List[MetricSpec]:
    """Only the metrics that are genuinely measurable in this substrate."""
    return [m for m in METRIC_REGISTRY if m.available]


def extract_all(record: Mapping[str, object]) -> Dict[str, Optional[float]]:
    """Extract every metric's scalar from one run's measurement record."""
    return {m.name: m.extract(record) for m in METRIC_REGISTRY}


def aggregate(
    records: Sequence[Mapping[str, object]],
) -> Dict[str, SummaryStatistics]:
    """Aggregate a group of runs into per-metric mean/std/CI/n summaries.

    Parameters
    ----------
    records :
        The measurement records of every run in a cell (typically the seeds
        for one (policy, replay-horizon, noise) combination).

    Returns
    -------
    dict
        ``metric_name -> SummaryStatistics``. Unavailable or all-null metrics
        summarise to ``n=0`` with null statistics, never to a fabricated value.
    """
    summaries: Dict[str, SummaryStatistics] = {}
    for spec in METRIC_REGISTRY:
        values = [spec.extract(r) for r in records]
        present = [v for v in values if v is not None]
        summaries[spec.name] = SummaryStatistics.from_samples(present)
    return summaries


def spec_metadata() -> List[Dict[str, object]]:
    """JSON-safe description of the whole registry (for artifacts/report)."""
    return [
        {
            "name": m.name,
            "category": m.category,
            "direction": m.direction,
            "units": m.units,
            "available": m.available,
            "note": m.note,
        }
        for m in METRIC_REGISTRY
    ]


__all__ = [
    "PRIMARY", "SECONDARY", "ENGINEERING",
    "LOWER_IS_BETTER", "HIGHER_IS_BETTER", "NEUTRAL",
    "MetricSpec",
    "METRIC_REGISTRY", "METRICS_BY_NAME",
    "metrics_for", "available_metrics",
    "extract_all", "aggregate", "spec_metadata",
]
