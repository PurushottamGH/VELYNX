"""
benchmark.py
============

The VELYNX Cognitive Lab's **headless orchestrator**.

This script is deliberately *thin*: it owns no cognitive logic of its own. It
only ever wires together the components of the :mod:`validation` subsystem in a
fixed sequence and translates the final verdict into a process exit code:

    load_config -> run_experiment -> evaluate -> archive -> report -> exit

Every unit of real work lives in a component:

* **Dataset**         -- :func:`validation.datasets.build_dataset`
* **Runner**          -- :class:`validation.runner.BenchmarkRunner`
* **Monitor / bridge**-- :class:`validation.monitor.VectorMonitor`
* **Metrics**         -- :mod:`validation.metrics`
* **Regression gate** -- :class:`validation.regression.RegressionGate`
* **Archiver**        -- :class:`validation.artifact.ResultSerializer`
* **Dashboard**       -- :class:`validation.report.HealthReport`

Usage::

    python benchmark.py --dataset environment --ticks 2000 --seed 7
    python benchmark.py --config experiment.json
    python benchmark.py --ticks 2000 --baseline artifacts/exp_001

Exit code is ``0`` when the regression gate PASSES and ``1`` when it FAILS, so
CI / pre-commit hooks can enforce the project's Freeze Rule directly.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from validation.artifact import ResultSerializer
from validation.datasets import build_dataset
from validation.metrics import (
    ActiveLoadMetric,
    CognitiveEnergyMetric,
    EntropyMetric,
    SurpriseMetric,
)
from backend.cognition.decision_policy import resolve_coefficients
from validation.monitor import VectorMonitor
from validation.regression import DEFAULT_TOLERANCE, RegressionGate, RegressionResult
from validation.report import HealthReport
from validation.runner import BenchmarkRunner


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkConfig:
    """Everything needed to run, score, and archive one experiment."""

    dataset_name: str = "environment"
    seed: Optional[int] = 7
    num_ticks: int = 1000
    noise_sigma: float = 0.05
    tolerance: float = DEFAULT_TOLERANCE
    proximity_threshold: float = 0.25
    max_clusters: int = 50
    experiment_name: str = "velynx_benchmark"
    baseline: Optional[str] = None
    artifacts_root: Optional[str] = None
    critical_metrics: Optional[List[str]] = None
    decision_policy: Optional[Dict[str, float]] = None
    metrics: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Execution flow (each step delegates; no domain logic lives here)
# ---------------------------------------------------------------------------

def load_config(argv: Optional[List[str]] = None) -> BenchmarkConfig:
    """Build a :class:`BenchmarkConfig` from CLI args and/or a JSON file."""
    parser = argparse.ArgumentParser(description="VELYNX validation benchmark.")
    parser.add_argument("--config", help="Path to a JSON config file.")
    parser.add_argument("--dataset", dest="dataset_name")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--ticks", dest="num_ticks", type=int)
    parser.add_argument("--noise", dest="noise_sigma", type=float)
    parser.add_argument("--tolerance", type=float)
    parser.add_argument("--max-clusters", dest="max_clusters", type=int)
    parser.add_argument("--name", dest="experiment_name")
    parser.add_argument("--baseline", help="Path to a baseline exp_NNN dir.")
    parser.add_argument("--artifacts-root", dest="artifacts_root")
    args = parser.parse_args(argv)

    values: Dict[str, Any] = {}
    if args.config:
        with open(args.config, "r", encoding="utf-8") as fh:
            values.update(json.load(fh))
    # CLI flags override the JSON file; ignore unset (None) flags.
    cli = {k: v for k, v in vars(args).items() if k != "config" and v is not None}
    values.update(cli)

    fields = {f for f in BenchmarkConfig.__dataclass_fields__}
    return BenchmarkConfig(**{k: v for k, v in values.items() if k in fields})


def run_experiment(cfg: BenchmarkConfig) -> Tuple[BenchmarkRunner, VectorMonitor]:
    """Instantiate the Dataset, Monitor, and Runner, then drive the loop."""
    # Externalised free-energy coupling coefficients: read (lam, mu, nu) from
    # the experiment config's ``decision_policy`` section, falling back to the
    # (1.0, 2.0, 0.5) defaults when absent. The *same* resolved weights are
    # handed to both the ClusterEngine (via the monitor's core) and the
    # DecisionPolicy (via the runner), so a sweep tunes a single knob.
    policy_weights = resolve_coefficients(cfg.decision_policy)

    dataset = build_dataset(
        cfg.dataset_name, seed=cfg.seed, noise_sigma=cfg.noise_sigma
    )
    monitor = VectorMonitor(
        proximity_threshold=cfg.proximity_threshold,
        max_clusters=cfg.max_clusters,
        decision_policy_weights=policy_weights,
    )
    runner = BenchmarkRunner(
        dataset=dataset, monitor=monitor, policy_weights=policy_weights
    )
    runner.run_experiment({"num_ticks": cfg.num_ticks})
    return runner, monitor


def evaluate(
    cfg: BenchmarkConfig, monitor: VectorMonitor
) -> Tuple[Dict[str, float], RegressionResult]:
    """Score the run and trigger the RegressionGate against the baseline."""
    metrics = [
        EntropyMetric(),
        SurpriseMetric(),
        ActiveLoadMetric(),
        CognitiveEnergyMetric(),
    ]
    scores = monitor.score(metrics)

    baseline = _load_baseline_metrics(cfg) or scores  # first run is its own base
    gate = RegressionGate(
        tolerance=cfg.tolerance, critical_metrics=cfg.critical_metrics
    )
    return scores, gate.evaluate(scores, baseline)


def archive(
    cfg: BenchmarkConfig,
    runner: BenchmarkRunner,
    result: RegressionResult,
    scores: Dict[str, float],
) -> str:
    """Persist the run via :meth:`ResultSerializer.save_experiment`."""
    cfg.metrics = scores  # store scores in config so future runs can baseline off them
    serializer = ResultSerializer(root_dir=cfg.artifacts_root)
    path = serializer.save_experiment(
        experiment_name=cfg.experiment_name,
        logs=runner.output_log,
        result=result,
        config=asdict(cfg),
    )
    # The C8 decision-audit artifact (Task 2): write the per-proposal decision
    # traces alongside this run's data.csv / metadata.json in the same exp dir.
    runner.write_decision_audit(path)
    return str(path)


def report(monitor: VectorMonitor, result: RegressionResult, cfg: BenchmarkConfig) -> None:
    """Render the ASCII vitals dashboard and the regression verdict."""
    snapshot = monitor.snapshot(label=cfg.experiment_name)
    print(HealthReport(**snapshot).render())

    summary = monitor.get_memory_summary()
    print("+----------------------------------------------------+")
    print("|  MEMORY & ANOMALY LIFECYCLE                        |")
    print("+----------------------------------------------------+")
    print(f"|  Total Clusters:        {summary['total_clusters']:<27} |")
    print(f"|  Active Anomalies:      {summary['active_anomalies_count']:<27} |")
    print(f"|  Resolved Anomalies:    {summary['resolved_anomalies_count']:<27} |")
    print(f"|  Avg Lifetime (ticks):  {summary['average_anomaly_lifetime']:<27.1f} |")
    print(f"|  Max Lifetime (ticks):  {summary['longest_anomaly_lifetime']:<27} |")
    print("+----------------------------------------------------+")

    print()
    print(result.summary)


def _consolidation_row(label: str, value: str) -> str:
    """Render one ``| label   value |`` row of the consolidation table.

    The frame is 52 chars wide (``+`` + 50 dashes + ``+``). Each row is
    ``|`` + space + a 26-wide label field + a 23-wide value field + ``|``,
    so values line up in a fixed column regardless of label length.
    """
    return f"| {label:<26}{value:<23}|"


def render_consolidation_pipeline(tracker: Any) -> str:
    """Render the C8 CONSOLIDATION PIPELINE ASCII dashboard.

    Reads the (pure-observability) :class:`ConsolidationTracker` counters and
    safe percentage metrics into the fixed table format. Percentages are
    computed by the tracker with division-by-zero guarded to ``0.0``.
    """
    border = "+" + "-" * 50 + "+"
    lines = [
        border,
        _consolidation_row("CONSOLIDATION PIPELINE", ""),
        border,
        _consolidation_row("Scheduler Triggered", str(tracker.scheduler_triggers)),
        _consolidation_row("Proposals Generated", str(tracker.proposals_generated)),
        _consolidation_row("Replay Evaluated", str(tracker.replay_evaluations)),
        _consolidation_row("Accepted", str(tracker.replay_accepted)),
        _consolidation_row("Rejected", str(tracker.replay_rejected)),
        _consolidation_row("Committed", str(tracker.merges_committed)),
        _consolidation_row("Queue Replayed", str(tracker.queue_replayed)),
        _consolidation_row("Quarantine Replayed", str(tracker.quarantine_replayed)),
        _consolidation_row("Absorbed", str(tracker.anomalies_absorbed)),
        _consolidation_row("Retired", str(tracker.anomalies_retired)),
        border,
        _consolidation_row("Proposal Success", f"{tracker.proposal_success_rate:.1f}%"),
        _consolidation_row("Replay Efficiency", f"{tracker.replay_efficiency:.1f}%"),
        _consolidation_row("Absorption Rate", f"{tracker.absorption_rate:.1f}%"),
        border,
    ]
    return "\n".join(lines)


def render_average_deltas(tracker: Any) -> str:
    """Render the C8 AVERAGE ACCEPTED DELTAS ASCII dashboard (Task 3).

    Reports the mean signed (before − after) improvement each cognitive vital
    saw across the run's **accepted** merges — the running sums the
    :class:`ConsolidationTracker` banked on every acceptance, divided by the
    number of accepted merges. A positive value means accepted merges, on
    average, *lowered* (improved) that vital. With no accepted merges every mean
    is a safe ``0.0``. Pure observability; computed entirely from the tracker.
    """
    n = tracker.replay_accepted
    border = "+" + "-" * 50 + "+"
    lines = [
        border,
        _consolidation_row("AVERAGE ACCEPTED DELTAS", ""),
        _consolidation_row("Accepted Merges (n)", str(n)),
        border,
        _consolidation_row("Mean Delta Prediction", f"{tracker.avg_delta_prediction:+.4f}"),
        _consolidation_row("Mean Delta Entropy", f"{tracker.avg_delta_entropy:+.4f}"),
        _consolidation_row("Mean Delta Load", f"{tracker.avg_delta_load:+.4f}"),
        _consolidation_row("Mean Delta Energy", f"{tracker.avg_delta_energy:+.4f}"),
        border,
    ]
    return "\n".join(lines)


def _load_baseline_metrics(cfg: BenchmarkConfig) -> Optional[Dict[str, float]]:
    """Load a prior run's metric scores from its artifact dir, if provided."""
    if not cfg.baseline:
        return None
    serializer = ResultSerializer(root_dir=cfg.artifacts_root)
    data = serializer.load_experiment(cfg.baseline)
    metrics = data.get("config", {}).get("metrics")
    return metrics or None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    """Run the full pipeline and return ``0`` (PASS) or ``1`` (FAIL)."""
    cfg = load_config(argv)
    runner, monitor = run_experiment(cfg)
    scores, result = evaluate(cfg, monitor)
    artifact_path = archive(cfg, runner, result, scores)
    report(monitor, result, cfg)
    print(f"\nArtifact: {artifact_path}")

    # C8 consolidation-pipeline observability dashboard. Rendered at the very
    # end of the run from the runner's pure-observability counters.
    print()
    print(render_consolidation_pipeline(runner.consolidation_tracker))

    # C8 AVERAGE ACCEPTED DELTAS dashboard (Task 3): the mean per-vital
    # improvement across every accepted merge this run.
    print()
    print(render_average_deltas(runner.consolidation_tracker))

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
