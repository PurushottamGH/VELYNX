#!/usr/bin/env python3
"""Verify artifact integrity across all stored experiment runs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments.artifacts import ArtifactStore


def main():
    store = ArtifactStore()
    base = store.base / "experiments"

    if not base.exists():
        print("No experiment artifacts found")
        sys.exit(0)

    all_ok = True
    for exp_dir in sorted(base.iterdir()):
        if not exp_dir.is_dir():
            continue
        experiment_id = exp_dir.name
        for run_dir in sorted(exp_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            run_id = run_dir.name
            ok = store.verify_integrity(experiment_id, run_id)
            status = "OK" if ok else "FAILED"
            if not ok:
                all_ok = False
            print(f"  [{status}] {experiment_id}/{run_id}")

    if all_ok:
        print("\nALL ARTIFACT INTEGRITY CHECKS PASSED")
        sys.exit(0)
    else:
        print("\nARTIFACT INTEGRITY FAILURES DETECTED")
        sys.exit(1)


if __name__ == "__main__":
    main()
