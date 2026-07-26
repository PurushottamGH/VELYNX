#!/usr/bin/env python3
"""Validate parameter registry consistency against actual code."""

import sys
import yaml
import ast
from pathlib import Path


def check_value_in_file(filepath: Path, name: str, expected_value) -> bool:
    if not filepath.exists():
        return False
    try:
        source = filepath.read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        if isinstance(node.value, ast.Constant):
                            return node.value.value == expected_value
                        if isinstance(node.value, ast.UnaryOp) and isinstance(
                            node.value.op, ast.USub
                        ):
                            return -node.value.operand.value == expected_value
        return False
    except Exception:
        return False


def main():
    root = Path(__file__).resolve().parent.parent
    param_path = root / "parameter_registry.yaml"

    if not param_path.exists():
        print("FAILED: parameter_registry.yaml not found")
        sys.exit(1)

    with open(param_path) as f:
        params = yaml.safe_load(f)

    errors = []
    warnings = []

    fe = params.get("free_energy", {})
    coefs = fe.get("coefficients", {})
    thresholds = fe.get("thresholds", {})

    for name, info in coefs.items():
        val = info.get("value")
        loc = info.get("location", "")
        print(f"  [CHECK] {name} = {val} @ {loc}")
        if loc:
            parts = loc.rsplit(":", 1)
            filepath = root / parts[0]
            if not check_value_in_file(filepath, name.upper(), val):
                warnings.append(f"{name}: value {val} not verified at {loc}")

    for name, info in thresholds.items():
        val = info.get("value")
        loc = info.get("location", "")
        print(f"  [CHECK] {name} = {val} @ {loc}")
        if loc:
            parts = loc.rsplit(":", 1)
            filepath = root / parts[0]
            if not check_value_in_file(filepath, name, val):
                warnings.append(f"{name}: value {val} not verified at {loc}")

    mdl = params.get("mdl", {}).get("description_length", {})
    for name, info in mdl.items():
        loc = info.get("location", "")
        print(f"  [CHECK] {name} @ {loc}")

    mem = params.get("memory", {})
    for name, info in mem.items():
        val = info.get("value")
        loc = info.get("location", "")
        print(f"  [CHECK] {name} = {val} @ {loc}")
        if loc:
            filepath = root / loc.rsplit(":", 1)[0]
            if not check_value_in_file(filepath, name, val):
                warnings.append(f"{name}: value {val} not verified at {loc}")

    if warnings:
        print(f"\nWARNINGS: {len(warnings)}")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\nFAILED: {len(errors)} errors")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\nPARAMETER REGISTRY VALIDATION COMPLETE")
        sys.exit(0)


if __name__ == "__main__":
    main()
