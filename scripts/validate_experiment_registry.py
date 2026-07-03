#!/usr/bin/env python3
"""Validate experiment registry against actual filesystem structure."""
import sys
import yaml
from pathlib import Path


def main():
    errors = []
    root = Path(__file__).resolve().parent.parent
    registry_path = root / "experiment_registry.yaml"

    if not registry_path.exists():
        print("FAILED: experiment_registry.yaml not found")
        sys.exit(1)

    with open(registry_path) as f:
        registry = yaml.safe_load(f)

    experiments = registry.get("experiment_registry", {})
    if not experiments:
        print("FAILED: no experiments in registry")
        sys.exit(1)

    print(f"Validating {len(experiments)} experiments...")

    for eid, entry in experiments.items():
        location = entry.get("location", "")
        loc_path = root / location
        if not loc_path.exists():
            errors.append(f"{eid}: directory not found: {location}")
            print(f"  [MISSING] {eid}: {location}")
        else:
            has_run_py = (loc_path / "run.py").exists()
            status = entry.get("status", "unknown")
            print(f"  [OK] {eid}: {location} ({status})" + (" [+run.py]" if has_run_py else ""))

        components = entry.get("components", [])
        for comp in components:
            comp_path = root / comp
            ext_path = root / comp.replace("backend/", "program_c/").replace("backend/", "program_b/").replace("backend/", "program_a/")
            if not comp_path.exists():
                if not ext_path.exists():
                    print(f"  [WARN] {eid}: component not found: {comp}")

    if errors:
        print(f"\nFAILED: {len(errors)} issues")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\nALL EXPERIMENT REGISTRY CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
