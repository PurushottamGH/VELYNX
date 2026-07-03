#!/usr/bin/env python3
"""Automated kill criteria validation.

Checks all experiments against defined kill criteria thresholds.
"""
import sys
import yaml
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments.metrics import (
    ENERGY_EXHAUSTION, ENTROPY_HIGH, SURPRISE_HIGH,
    SURPRISE_MILD, PRESSURE_HIGH, PRESSURE_MILD,
)


KILL_CRITERIA = [
    {
        "id": "energy_exhaustion",
        "metric": "free_energy",
        "threshold": ENERGY_EXHAUSTION,
        "description": f"Free energy exceeds {ENERGY_EXHAUSTION}",
        "level": "critical",
    },
    {
        "id": "entropy_collapse",
        "metric": "entropy",
        "threshold": ENTROPY_HIGH,
        "comparison": "above",
        "description": f"Entropy exceeds {ENTROPY_HIGH} bits",
        "level": "critical",
    },
    {
        "id": "surprise_overload",
        "metric": "surprise",
        "threshold": SURPRISE_HIGH,
        "comparison": "above",
        "description": f"Surprise exceeds {SURPRISE_HIGH}",
        "level": "warning",
    },
    {
        "id": "divergence",
        "metric": "free_energy",
        "threshold": float('inf'),
        "description": "Free energy diverges to infinity or NaN",
        "level": "critical",
    },
]


def check_experiment(experiment_dir: Path) -> dict:
    result = {
        "experiment": experiment_dir.name,
        "kill_criteria_triggered": [],
        "all_clear": True,
    }

    metrics_file = experiment_dir / "metrics.jsonl"
    if not metrics_file.exists():
        result["error"] = "metrics.jsonl not found"
        result["all_clear"] = False
        return result

    try:
        with open(metrics_file) as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                for kc in KILL_CRITERIA:
                    metric_value = record.get(kc["metric"])
                    if metric_value is None:
                        continue
                    if np.isnan(metric_value) or np.isinf(metric_value):
                        result["kill_criteria_triggered"].append({
                            "criteria": kc["id"],
                            "value": metric_value,
                            "tick": record.get("tick", 0),
                            "level": kc["level"],
                        })
                        result["all_clear"] = False
                        continue
                    if kc["comparison"] == "above" and metric_value > kc["threshold"]:
                        result["kill_criteria_triggered"].append({
                            "criteria": kc["id"],
                            "value": metric_value,
                            "threshold": kc["threshold"],
                            "tick": record.get("tick", 0),
                            "level": kc["level"],
                        })
                        result["all_clear"] = False
    except Exception as e:
        result["error"] = str(e)
        result["all_clear"] = False

    return result


def main():
    root = Path(__file__).resolve().parent.parent
    experiments_dir = root / "experiments"

    print("=" * 60)
    print("Kill Criteria Validation")
    print("=" * 60)

    all_clear = True
    for exp_dir in sorted(experiments_dir.iterdir()):
        if not exp_dir.is_dir() or exp_dir.name.startswith("_"):
            continue
        result = check_experiment(exp_dir)
        status = "PASS" if result["all_clear"] else "TRIGGERED"
        print(f"\n[{status}] {result['experiment']}:")
        if "error" in result:
            print(f"  Error: {result['error']}")
            all_clear = False
        for kc in result.get("kill_criteria_triggered", []):
            print(f"  [{kc['level']}] {kc['criteria']} = {kc['value']} @ tick {kc['tick']}")
            all_clear = False

    print("-" * 60)
    if all_clear:
        print("ALL KILL CRITERIA CHECKS PASSED")
        sys.exit(0)
    else:
        print("KILL CRITERIA TRIGGERED - review required")
        sys.exit(1)


if __name__ == "__main__":
    main()
