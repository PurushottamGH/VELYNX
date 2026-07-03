#!/usr/bin/env python3
"""Verify reproducibility specification compliance."""
import sys
import yaml
from pathlib import Path

REQUIRED_FILES = [
    "reproducibility.yaml",
    "experiment_registry.yaml",
    "parameter_registry.yaml",
    "requirements.txt",
    ".env.example",
    ".gitignore",
]

REQUIRED_EXPERIMENT_DIRS = [
    "experiments/E0",
    "experiments/R1",
    "experiments/R3F",
    "experiments/EXP1",
    "experiments/EXP2",
    "experiments/EXP3",
    "experiments/EXP4",
]

REQUIRED_CONFIGS = [
    "configs/baseline.json",
    "configs/noisy.json",
    "configs/simple.json",
]


def main():
    errors = []
    root = Path(__file__).resolve().parent.parent

    print("=" * 60)
    print("Reproducibility Verification")
    print("=" * 60)

    for f in REQUIRED_FILES:
        path = root / f
        if path.exists():
            print(f"  [OK] {f}")
        else:
            print(f"  [MISSING] {f}")
            errors.append(f)

    for d in REQUIRED_EXPERIMENT_DIRS:
        path = root / d
        if path.exists():
            has_run_py = (path / "run.py").exists()
            print(f"  [OK] {d}/" + (" (+run.py)" if has_run_py else ""))
        else:
            print(f"  [MISSING] {d}/")
            errors.append(d)

    for c in REQUIRED_CONFIGS:
        path = root / c
        if path.exists():
            print(f"  [OK] {c}")
        else:
            print(f"  [MISSING] {c}")
            errors.append(c)

    try:
        with open(root / "reproducibility.yaml") as f:
            spec = yaml.safe_load(f)
        print(f"  [OK] reproducibility.yaml parsed: v{spec.get('reproducibility', {}).get('version', '?')}")
    except Exception as e:
        print(f"  [ERROR] reproducibility.yaml: {e}")
        errors.append(str(e))

    try:
        with open(root / "experiment_registry.yaml") as f:
            reg = yaml.safe_load(f)
        experiments = reg.get("experiment_registry", {})
        print(f"  [OK] experiment_registry.yaml: {len(experiments)} experiments registered")
    except Exception as e:
        print(f"  [ERROR] experiment_registry.yaml: {e}")
        errors.append(str(e))

    try:
        with open(root / "parameter_registry.yaml") as f:
            params = yaml.safe_load(f)
        print(f"  [OK] parameter_registry.yaml: {len(params)} parameter groups")
    except Exception as e:
        print(f"  [ERROR] parameter_registry.yaml: {e}")
        errors.append(str(e))

    print("-" * 60)
    if errors:
        print(f"FAILED: {len(errors)} issues found")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
