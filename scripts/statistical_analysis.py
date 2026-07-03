#!/usr/bin/env python3
"""Statistical Analysis Pipeline.

Produces statistical reports for all experiment runs.
"""
import sys
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments.metrics import (
    MetricsRecord, MetricsReport,
    bootstrap_ci, effect_size_cohens_d, permutation_test,
    compute_nmi,
)


def load_metrics(metrics_path: Path) -> List[MetricsRecord]:
    records = []
    with open(metrics_path) as f:
        for line in f:
            if line.strip():
                records.append(MetricsRecord.from_dict(json.loads(line)))
    return records


def analyze_experiment(experiment_id: str, run_id: str, metrics_path: Path) -> Dict:
    records = load_metrics(metrics_path)
    if not records:
        return {"experiment_id": experiment_id, "error": "no data"}

    energies = np.array([r.free_energy for r in records])
    surprises = np.array([r.surprise for r in records])
    entropies = np.array([r.entropy for r in records])
    structural_loads = np.array([r.structural_load for r in records])

    result = {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "num_ticks": len(records),
        "free_energy": {
            "mean": float(np.mean(energies)),
            "std": float(np.std(energies)),
            "min": float(np.min(energies)),
            "max": float(np.max(energies)),
            "median": float(np.median(energies)),
            "ci_95": list(bootstrap_ci(energies)),
            "trend": _compute_trend(energies),
        },
        "surprise": {
            "mean": float(np.mean(surprises)),
            "std": float(np.std(surprises)),
            "min": float(np.min(surprises)),
            "max": float(np.max(surprises)),
            "trend": _compute_trend(surprises),
        },
        "entropy": {
            "mean": float(np.mean(entropies)),
            "std": float(np.std(entropies)),
            "trend": _compute_trend(entropies),
        },
        "structural_load": {
            "mean": float(np.mean(structural_loads)),
            "std": float(np.std(structural_loads)),
            "trend": _compute_trend(structural_loads),
        },
    }

    if records[0].kill_criteria_triggered:
        result["kill_criteria"] = records[0].kill_criteria_triggered

    return result


def _compute_trend(data: np.ndarray) -> str:
    """Simple trend analysis: increasing, decreasing, or stable."""
    if len(data) < 2:
        return "insufficient_data"
    half = len(data) // 2
    first_half = np.mean(data[:half])
    second_half = np.mean(data[half:])
    threshold = 0.05 * max(abs(first_half), abs(second_half)) if max(abs(first_half), abs(second_half)) > 0 else 0.001
    if second_half - first_half > threshold:
        return "increasing"
    elif first_half - second_half > threshold:
        return "decreasing"
    else:
        return "stable"


def compare_experiments(control_id: str, treatment_id: str,
                        control_records: List[MetricsRecord],
                        treatment_records: List[MetricsRecord]) -> Dict:
    c_energies = np.array([r.free_energy for r in control_records])
    t_energies = np.array([r.free_energy for r in treatment_records])

    return {
        "control": control_id,
        "treatment": treatment_id,
        "cohens_d": {
            "free_energy": effect_size_cohens_d(c_energies, t_energies),
        },
        "permutation_test": {
            "free_energy_p_value": permutation_test(c_energies, t_energies),
        },
        "control_mean_fe": float(np.mean(c_energies)),
        "treatment_mean_fe": float(np.mean(t_energies)),
        "difference_mean_fe": float(np.mean(t_energies) - np.mean(c_energies)),
    }


def generate_publication_report(analysis: Dict, output_path: Path):
    lines = [
        "=" * 72,
        "VELYNX Statistical Analysis Report",
        "=" * 72,
        f"Experiment: {analysis.get('experiment_id', '?')}",
        f"Run: {analysis.get('run_id', '?')}",
        f"Ticks: {analysis.get('num_ticks', 0)}",
        "-" * 72,
    ]

    for metric in ["free_energy", "surprise", "entropy", "structural_load"]:
        if metric in analysis:
            m = analysis[metric]
            lines.append(f"\n{metric.upper()}:")
            lines.append(f"  Mean ± SD:    {m['mean']:.4f} ± {m['std']:.4f}")
            lines.append(f"  Median:       {m['median'] if 'median' in m else 'N/A'}")
            lines.append(f"  Range:        [{m['min']:.4f}, {m['max']:.4f}]")
            lines.append(f"  95% CI:       [{m['ci_95'][0]:.4f}, {m['ci_95'][1]:.4f}]" if 'ci_95' in m else "")
            lines.append(f"  Trend:        {m.get('trend', 'N/A')}")

    lines.append("\n" + "=" * 72)
    report = "\n".join(lines)
    output_path.write_text(report)
    return report


def main():
    root = Path(__file__).resolve().parent.parent
    artifacts_base = root / "artifacts" / "experiments"
    output_dir = root / "artifacts" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not artifacts_base.exists():
        print("No experiment artifacts found")
        return

    all_analyses = []
    for exp_dir in sorted(artifacts_base.iterdir()):
        if not exp_dir.is_dir():
            continue
        experiment_id = exp_dir.name
        for run_dir in sorted(exp_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            run_id = run_dir.name
            metrics_path = run_dir / "metrics.jsonl"
            if not metrics_path.exists():
                print(f"[SKIP] {experiment_id}/{run_id}: no metrics.jsonl")
                continue

            print(f"[ANALYZE] {experiment_id}/{run_id}")
            analysis = analyze_experiment(experiment_id, run_id, metrics_path)
            report_path = run_dir / "statistical_analysis.json"
            with open(report_path, "w") as f:
                json.dump(analysis, f, indent=2)

            pub_report_path = run_dir / "statistical_report.md"
            generate_publication_report(analysis, pub_report_path)

            all_analyses.append(analysis)

    summary_path = output_dir / "all_analyses.json"
    with open(summary_path, "w") as f:
        json.dump(all_analyses, f, indent=2)
    print(f"\nAnalyses saved to {summary_path}")


if __name__ == "__main__":
    main()
