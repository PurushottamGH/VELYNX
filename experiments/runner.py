"""VELYNX Experiment Runner.

Single entry point for all registered experiments.
Usage:
    python -m experiments.runner <experiment_id> [--config <path>] [--seed <n>]
"""
import argparse
import importlib
import os
import sys
import time
import yaml
import json
from pathlib import Path
from datetime import datetime, timezone


EXPERIMENT_REGISTRY_PATH = Path(__file__).resolve().parent.parent / "experiment_registry.yaml"
PARAMETER_REGISTRY_PATH = Path(__file__).resolve().parent.parent / "parameter_registry.yaml"
ARTIFACTS_BASE = Path(__file__).resolve().parent.parent / "artifacts" / "experiments"


def load_registry(path):
    with open(path) as f:
        return yaml.safe_load(f)


def resolve_experiment_path(experiment_id, registry):
    entry = registry.get("experiment_registry", {}).get(experiment_id)
    if not entry:
        print(f"Error: experiment '{experiment_id}' not found in registry")
        sys.exit(1)
    return entry


def run_experiment(experiment_id, config_override=None, seed=None):
    registry_data = load_registry(EXPERIMENT_REGISTRY_PATH)
    entry = resolve_experiment_path(experiment_id, registry_data)
    params = load_registry(PARAMETER_REGISTRY_PATH)

    experiment_dir = Path(entry["location"]).resolve()
    if not experiment_dir.exists():
        print(f"Error: experiment directory not found: {experiment_dir}")
        sys.exit(1)

    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    output_dir = ARTIFACTS_BASE / experiment_id / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    if seed is not None:
        env["BENCHMARK_SEED"] = str(seed)
    elif "BENCHMARK_SEED" not in env:
        env["BENCHMARK_SEED"] = str(params.get("randomness", {}).get("default_seed", 42))

    manifest = {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": int(env["BENCHMARK_SEED"]),
        "config": config_override or entry.get("config", "default"),
        "git_commit": _get_git_commit(),
        "status": "started",
    }
    _write_json(output_dir / "manifest.json", manifest)

    status = entry.get("status", "unknown")
    if status in ("planned", "gated", "archived"):
        print(f"[{experiment_id}] Status is '{status}' — skipping")
        manifest["status"] = "skipped"
        manifest["reason"] = f"Experiment status is '{status}'"
        _write_json(output_dir / "manifest.json", manifest)
        return

    print(f"[{experiment_id}] Starting run {run_id}")
    print(f"[{experiment_id}] Seed: {env['BENCHMARK_SEED']}")
    print(f"[{experiment_id}] Output: {output_dir}")

    entry_point = experiment_dir / "run.py"
    if not entry_point.exists():
        manifest["status"] = "failed"
        manifest["error"] = f"run.py not found in {experiment_dir}"
        _write_json(output_dir / "manifest.json", manifest)
        print(f"[{experiment_id}] Error: run.py not found in {experiment_dir}")
        return

    try:
        spec = importlib.util.spec_from_file_location(f"experiments.{experiment_id}.run", entry_point)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "main"):
            module.main(output_dir=str(output_dir), config=config_override, seed=int(env["BENCHMARK_SEED"]))
        elif hasattr(module, "run"):
            module.run(output_dir=str(output_dir), config=config_override, seed=int(env["BENCHMARK_SEED"]))
        else:
            print(f"Warning: experiment {experiment_id} has no main() or run() entry point")

        manifest["status"] = "completed"
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        _write_json(output_dir / "manifest.json", manifest)
        print(f"[{experiment_id}] Run completed successfully")

    except Exception as e:
        manifest["status"] = "failed"
        manifest["error"] = str(e)
        manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
        _write_json(output_dir / "manifest.json", manifest)
        print(f"[{experiment_id}] Run failed: {e}")
        raise


def _get_git_commit():
    try:
        import subprocess
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def list_experiments():
    registry_data = load_registry(EXPERIMENT_REGISTRY_PATH)
    experiments = registry_data.get("experiment_registry", {})
    print("Registered experiments:")
    for eid, entry in experiments.items():
        status = entry.get("status", "unknown")
        print(f"  {eid}: {entry.get('name', '?')} [{status}]")
    return list(experiments.keys())


def main():
    parser = argparse.ArgumentParser(description="VELYNX Experiment Runner")
    parser.add_argument("experiment_id", nargs="?", help="Experiment ID from registry")
    parser.add_argument("--config", help="Path to experiment config JSON")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--list", action="store_true", help="List registered experiments")
    args = parser.parse_args()

    if args.list:
        list_experiments()
        return

    if not args.experiment_id:
        parser.print_help()
        return

    run_experiment(args.experiment_id, config_override=args.config, seed=args.seed)


if __name__ == "__main__":
    main()
