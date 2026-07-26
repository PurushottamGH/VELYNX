"""
research_benchmark.py
=====================

The VELYNX **Research Sprint R1** experimentation orchestrator.

This is the experimental sibling of the production ``benchmark.py`` — and it is
strictly additive: ``benchmark.py`` is *not* imported, *not* modified, and stays
the production regression gate. ``research_benchmark.py`` instead sweeps the
ablation matrix

    policy  ×  replay-horizon  ×  noise-level  ×  random-seed

running each cell through the :class:`~research.runner.ResearchRunner`, writing
seven immutable artifacts per experiment, then aggregating across seeds into an
honest ``ablation_report.md`` plus a machine-readable ``analysis.json``.

Usage
-----
Full default matrix (6 × 4 × 3 × 5 = 360 experiments)::

    python research_benchmark.py

A fast smoke sweep (subset + few ticks)::

    python research_benchmark.py --quick

Custom sweep::

    python research_benchmark.py \\
        --policies null free_energy --horizons 50 --noise 0.08 \\
        --seeds 1 2 3 --ticks 800

All experiments land under ``--out`` (default ``research_artifacts/``) inside a
timestamped run-group directory; the report is written there and, by default,
also copied to ``ablation_report.md`` at the repo root.

Standard library only. Run from the repository root so ``backend.*`` /
``validation.*`` / ``environment`` imports resolve.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

from research.artifacts import ArtifactWriter, allocate_experiment_dir
from research.policies import DEFAULT_POLICY_ORDER, available_policies
from research.report import build_analysis, render_report
from research.runner import RunConfig, run_single
from research.stats import SummaryStatistics

# Default sweep matrix (exactly the Sprint R1 configuration matrix).
DEFAULT_HORIZONS = [20, 50, 100, 200]
DEFAULT_NOISE = [0.01, 0.08, 0.15]
DEFAULT_SEEDS = [1, 2, 3, 4, 5]
DEFAULT_TICKS = 1000
DEFAULT_DATASET = "environment"
DEFAULT_ARTIFACTS_ROOT = "research_artifacts"


def build_matrix(args: argparse.Namespace) -> Dict[str, Any]:
    """Resolve CLI args into a concrete sweep matrix."""
    if args.quick:
        return {
            "policies": args.policies or ["null", "similarity", "free_energy"],
            "replay_horizons": args.horizons or [50],
            "noise_levels": args.noise or [0.08],
            "seeds": args.seeds or [1, 2],
            "num_ticks": args.ticks or 700,
            "dataset_name": args.dataset,
            "proximity_threshold": args.proximity,
            "max_clusters": args.max_clusters,
        }
    return {
        "policies": args.policies or list(DEFAULT_POLICY_ORDER),
        "replay_horizons": args.horizons or DEFAULT_HORIZONS,
        "noise_levels": args.noise or DEFAULT_NOISE,
        "seeds": args.seeds or DEFAULT_SEEDS,
        "num_ticks": args.ticks or DEFAULT_TICKS,
        "dataset_name": args.dataset,
        "proximity_threshold": args.proximity,
        "max_clusters": args.max_clusters,
    }


def run_sweep(matrix: Dict[str, Any], out_root: str, *, verbose: bool = True) -> Dict[str, Any]:
    """Execute the full matrix, write artifacts, and return the analysis + records."""
    group = time.strftime("run_%Y%m%dT%H%M%S")
    group_dir = os.path.join(out_root, group)
    os.makedirs(group_dir, exist_ok=True)

    writer = ArtifactWriter()
    records: List[Dict[str, Any]] = []

    combos = list(
        itertools.product(
            matrix["policies"],
            matrix["replay_horizons"],
            matrix["noise_levels"],
            matrix["seeds"],
        )
    )
    total = len(combos)
    if verbose:
        print(f"[research_benchmark] sweeping {total} experiments -> {group_dir}")

    for idx, (policy, horizon, noise, seed) in enumerate(combos, start=1):
        cfg = RunConfig(
            policy=policy,
            replay_horizon=horizon,
            noise_sigma=noise,
            seed=seed,
            num_ticks=matrix["num_ticks"],
            dataset_name=matrix["dataset_name"],
            proximity_threshold=matrix["proximity_threshold"],
            max_clusters=matrix["max_clusters"],
        )
        result = run_single(cfg)

        exp_dir = allocate_experiment_dir(group_dir)
        experiment_id = os.path.basename(exp_dir)
        writer.write(
            result,
            exp_dir,
            experiment_id=experiment_id,
            name="velynx_research_r1",
            group=group,
        )

        records.append(
            {
                "experiment_id": experiment_id,
                "exp_dir": exp_dir,
                "policy": policy,
                "replay_horizon": horizon,
                "noise_sigma": noise,
                "seed": seed,
                "measurements": result.measurements,
            }
        )
        if verbose:
            rmse = result.measurements.get("prediction_rmse")
            energy = result.measurements.get("final_energy")
            print(
                f"  [{idx}/{total}] {policy:<11} h={horizon:<3} noise={noise:<4} "
                f"seed={seed}  RMSE={_fmt(rmse)}  E={_fmt(energy)}  -> {experiment_id}"
            )

    # -- aggregate + report ------------------------------------------------
    analysis = build_analysis(records)
    report_md = render_report(analysis, matrix)

    report_path = os.path.join(group_dir, "ablation_report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report_md)

    analysis_path = os.path.join(group_dir, "analysis.json")
    with open(analysis_path, "w", encoding="utf-8") as fh:
        json.dump(_jsonable(analysis), fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")

    return {
        "group_dir": group_dir,
        "report_path": report_path,
        "analysis_path": analysis_path,
        "analysis": analysis,
        "records": records,
        "matrix": matrix,
    }


def _fmt(x: Optional[float]) -> str:
    return "n/a" if x is None else f"{x:.4f}"


def _jsonable(obj: Any) -> Any:
    """Recursively convert SummaryStatistics (and friends) into JSON-safe data."""
    if isinstance(obj, SummaryStatistics):
        return obj.as_dict()
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    return obj


def _parse_args(argv: Optional[List[str]]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="VELYNX Research Sprint R1 sweep.")
    p.add_argument("--policies", nargs="*", help=f"Subset of {available_policies()}.")
    p.add_argument("--horizons", nargs="*", type=int, help="Replay horizons.")
    p.add_argument("--noise", nargs="*", type=float, help="Sensor noise sigmas.")
    p.add_argument("--seeds", nargs="*", type=int, help="Random seeds.")
    p.add_argument("--ticks", type=int, help="Ticks per run.")
    p.add_argument("--dataset", default=DEFAULT_DATASET, help="Dataset name.")
    p.add_argument("--proximity", type=float, default=0.25, help="Proximity threshold.")
    p.add_argument("--max-clusters", dest="max_clusters", type=int, default=50)
    p.add_argument("--out", default=DEFAULT_ARTIFACTS_ROOT, help="Artifacts root dir.")
    p.add_argument(
        "--report-out",
        dest="report_out",
        default="ablation_report.md",
        help="Where to copy the rendered report (repo root by default; '' to skip).",
    )
    p.add_argument("--quick", action="store_true", help="Fast smoke sweep.")
    p.add_argument("--quiet", action="store_true", help="Suppress per-run output.")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    matrix = build_matrix(args)
    outcome = run_sweep(matrix, args.out, verbose=not args.quiet)

    # Copy the report to the requested location (repo root by default).
    if args.report_out:
        with open(outcome["report_path"], "r", encoding="utf-8") as fh:
            report_md = fh.read()
        with open(args.report_out, "w", encoding="utf-8") as fh:
            fh.write(report_md)

    print(f"\n[research_benchmark] artifacts: {outcome['group_dir']}")
    print(f"[research_benchmark] report:    {outcome['report_path']}")
    if args.report_out:
        print(f"[research_benchmark] report copy: {args.report_out}")

    # Print the headline verdict to stdout for at-a-glance results.
    print("\n=== VERDICT (FreeEnergy vs best baseline) ===")
    for metric, v in outcome["analysis"]["verdict"].items():
        print(
            f"  {metric}: {v['decision']} "
            f"(FE={_fmt(v['treatment_mean'])} vs "
            f"best baseline {v['best_baseline']}={_fmt(v['best_baseline_mean'])})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
