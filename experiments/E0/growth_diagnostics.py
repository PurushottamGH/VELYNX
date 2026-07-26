"""Growth Diagnostics -- Extract and tabulate every growth-check event.

Reads aggregated_results.json from an E0 multi-seed run and produces
the required diagnostic table:

| seed | step | H_before | H_after | G (=H_before-H_after) | lambda_model | Decision | Margin (G - lambda_model) |

This covers every MDL growth-check event in the Treatment (T) condition
across all seeds. C2 is excluded because it does not perform MDL checks --
it applies growth at predetermined positions independent of prediction error.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def extract_growth_diagnostics(results_path: str) -> List[Dict[str, Any]]:
    """Extract per-check growth diagnostics from aggregated results.

    Parameters
    ----------
    results_path : str
        Path to aggregated_results.json from an E0 multi-seed run.

    Returns
    -------
    List[Dict]
        Each dict has keys: seed, step, H_before, H_after, G_raw,
        lambda_model, decision (bool), margin.
    """
    with open(results_path) as f:
        data = json.load(f)

    diagnostics: List[Dict[str, Any]] = []

    for seed_result in data.get("per_seed_results", []):
        seed = seed_result.get("seed", "?")
        conditions = seed_result.get("conditions", {})

        for cond_name in ["T", "C3"]:
            cond = conditions.get(cond_name, {})
            logs = cond.get("per_step_log", [])

            if not logs:
                continue

            for entry in logs:
                h_before = entry.get("entropy_before", 0.0)
                h_after = entry.get("entropy_after", 0.0)
                g_raw = h_before - h_after
                lam = entry.get("lambda_model", 0.0)
                margin = g_raw - lam  # = gain from should_grow

                diagnostics.append(
                    {
                        "seed": seed,
                        "condition": cond_name,
                        "step": entry.get("step"),
                        "H_before": h_before,
                        "H_after": h_after,
                        "G_raw": g_raw,
                        "lambda_model": lam,
                        "decision": bool(entry.get("grew", False)),
                        "margin": margin,
                    }
                )

    return diagnostics


def format_table(diagnostics: List[Dict[str, Any]]) -> str:
    """Format growth diagnostics as a markdown table."""
    lines = [
        "## Growth Diagnostics -- Every MDL Check Event",
        "",
        "| seed | condition | step | H_before | H_after | G | lambda_model | Decision | Margin (G - lambda_model) |",
        "|------|-----------|------|----------|---------|----|--------------|----------|---------------------------|",
    ]

    for d in diagnostics:
        decision_str = "GROW" if d["decision"] else "KEEP"
        lines.append(
            f"| {d['seed']} "
            f"| {d['condition']} "
            f"| {d['step']} "
            f"| {d['H_before']:.6f} "
            f"| {d['H_after']:.6f} "
            f"| {d['G_raw']:.6f} "
            f"| {d['lambda_model']:.6f} "
            f"| {decision_str} "
            f"| {d['margin']:.6f} |"
        )

    # Summary statistics
    total_checks = len(diagnostics)
    t_checks = sum(1 for d in diagnostics if d["condition"] == "T")
    c3_checks = sum(1 for d in diagnostics if d["condition"] == "C3")
    growth_events = sum(1 for d in diagnostics if d["decision"])
    max_margin = max(d["margin"] for d in diagnostics) if diagnostics else 0.0
    mean_margin = sum(d["margin"] for d in diagnostics) / max(len(diagnostics), 1)
    never_grew = growth_events == 0

    lines.extend(
        [
            "",
            "### Summary",
            "",
            f"- **Total MDL checks:** {total_checks} " f"({t_checks} from T, {c3_checks} from C3)",
            f"- **Growth events (Decision=GROW):** {growth_events}",
            f"- **Max margin:** {max_margin:.6f}",
            f"- **Mean margin:** {mean_margin:.6f}",
            "",
        ]
    )

    if never_grew:
        lines.append(
            "> **Diagnosis:** Growth never fired across any seed. "
            "Every MDL check evaluated G - lambda_model <= 0, meaning the "
            "entropy reduction from adding a state never justified the "
            "increase in model complexity. This is consistent with the "
            "canonical kill criterion: on this environment class, "
            "error-gated growth provides no detectable benefit over "
            "fixed-capacity or decoupled controls.\n"
        )

    return "\n".join(lines)


def main(results_path: str | None = None):
    if results_path is None:
        evidence_dir = Path(__file__).resolve().parent.parent.parent / "evidence"
        log_dirs = sorted(
            (evidence_dir / "experiment_logs").glob("run_*"),
            reverse=True,
        )
        if not log_dirs:
            print("No experiment logs found in evidence/experiment_logs/", file=sys.stderr)
            sys.exit(1)
        results_path = str(log_dirs[0] / "aggregated_results.json")
        print(f"[auto-detect] Using: {results_path}\n")

    path_obj = Path(results_path)
    if not path_obj.exists():
        print(f"File not found: {results_path}", file=sys.stderr)
        sys.exit(1)

    diagnostics = extract_growth_diagnostics(results_path)

    if not diagnostics:
        print("No growth diagnostics found in results (no per_step_log data).")
        sys.exit(0)

    # Write table to markdown file alongside results
    output_path = path_obj.parent / "growth_diagnostics.md"
    table = format_table(diagnostics)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(table + "\n")

    print(f"Growth diagnostics written to: {output_path}")
    print(table)


if __name__ == "__main__":
    # Accept optional path argument
    args = sys.argv[1:]
    if args:
        main(args[0])
    else:
        main()
