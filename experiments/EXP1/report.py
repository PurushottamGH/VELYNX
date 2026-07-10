"""EXP-1 report rendering utilities."""
from __future__ import annotations

import csv
import io
from pathlib import Path

from experiments.EXP1.calibration import CalibrationResult
from experiments.EXP1.decision import ExperimentDecision, SeedDecision


def reliability_table_csv(calibration: CalibrationResult) -> str:
    """Render the EXP-1 reliability table as CSV."""

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "bin",
            "range",
            "count",
            "accuracy",
            "confidence",
            "ece_contribution",
            "tiers",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    for bin_result in calibration.bins:
        close = "]" if bin_result.right_closed else ")"
        writer.writerow(
            {
                "bin": bin_result.index,
                "range": f"[{bin_result.lower:.2f}, {bin_result.upper:.2f}{close}",
                "count": bin_result.count,
                "accuracy": _format_optional_float(bin_result.accuracy),
                "confidence": _format_optional_float(bin_result.confidence),
                "ece_contribution": f"{bin_result.ece_contribution:.12g}",
                "tiers": "|".join(bin_result.tiers),
            }
        )
    return output.getvalue()


def seed_report_markdown(decision: SeedDecision) -> str:
    """Render a [FACT]-tagged markdown report for one seed replicate."""

    lines = [
        "# EXP-1 Seed Report",
        "",
        "**[FACT]** EXP-1 evaluates emitted public confidence tiers against binary answer correctness under the frozen gold rubric.",
        "",
        "## Seed Decision",
        f"- Seed: {decision.seed}",
        f"- Verdict: {decision.verdict}",
        f"- Supports H1: {decision.pass_h1}",
        f"- ECE: {decision.calibration.ece:.12g}",
        f"- ECE pass threshold: < {decision.calibration.to_dict()['ece_pass_threshold']:.2f}",
        f"- Independence p-value: {decision.independence.p_value:.12g}",
        f"- Rejects tier/correctness independence: {decision.independence.rejects_independence}",
        f"- Emitted tier count: {decision.emitted_tier_count}",
        f"- Hard hallucination-honesty failures: {decision.hard_hallucination_failures}",
        "",
        "## Kill Reasons",
    ]
    if decision.kill_reasons:
        lines.extend(f"- {reason}" for reason in decision.kill_reasons)
    else:
        lines.append("- None")
    lines.extend(["", "## Reliability Table", _markdown_reliability_table(decision.calibration), ""])
    return "\n".join(lines)


def experiment_report_markdown(decision: ExperimentDecision) -> str:
    """Render a [FACT]-tagged markdown report for EXP-1."""

    lines = [
        "# EXP-1 Experiment Report",
        "",
        "**[FACT]** EXP-1 supports H1 only if every preregistered seed replicate passes all seed-level criteria and 22 independent seeds are completed.",
        "",
        "## Experiment Decision",
        f"- Verdict: {decision.verdict}",
        f"- Supports H1: {decision.pass_h1}",
        f"- Completed seeds: {decision.completed_seed_count}",
        f"- Required seeds: {decision.required_seed_count}",
        "",
        "## Kill Reasons",
    ]
    if decision.kill_reasons:
        lines.extend(f"- {reason}" for reason in decision.kill_reasons)
    else:
        lines.append("- None")
    if decision.pooled_calibration is not None:
        lines.extend(
            [
                "",
                "## Pooled Reliability Table",
                "**[FACT]** Pooled ECE is reported for inspection only and cannot override a seed-level kill.",
                _markdown_reliability_table(decision.pooled_calibration),
            ]
        )
    lines.extend(["", "## Seed Summary"])
    for seed_decision in decision.seed_decisions:
        reasons = "; ".join(seed_decision.kill_reasons) if seed_decision.kill_reasons else "None"
        lines.append(
            f"- Seed {seed_decision.seed}: {seed_decision.verdict}, ECE={seed_decision.calibration.ece:.12g}, kill_reasons={reasons}"
        )
    lines.append("")
    return "\n".join(lines)


def write_seed_report(decision: SeedDecision, output_dir: str | Path) -> dict[str, Path]:
    """Write seed markdown and reliability CSV report artifacts."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / "exp1_seed_report.md"
    csv_path = output_path / "exp1_reliability_table.csv"
    report_path.write_text(seed_report_markdown(decision), encoding="utf-8")
    csv_path.write_text(reliability_table_csv(decision.calibration), encoding="utf-8")
    return {"report": report_path, "reliability_table": csv_path}


def write_experiment_report(decision: ExperimentDecision, output_dir: str | Path) -> dict[str, Path]:
    """Write experiment markdown and pooled reliability CSV report artifacts."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / "exp1_report.md"
    report_path.write_text(experiment_report_markdown(decision), encoding="utf-8")
    paths = {"report": report_path}
    if decision.pooled_calibration is not None:
        csv_path = output_path / "exp1_pooled_reliability_table.csv"
        csv_path.write_text(reliability_table_csv(decision.pooled_calibration), encoding="utf-8")
        paths["pooled_reliability_table"] = csv_path
    return paths


def _markdown_reliability_table(calibration: CalibrationResult) -> str:
    lines = [
        "| Bin | Range | Count | Accuracy | Confidence | ECE contribution | Tiers |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for bin_result in calibration.bins:
        close = "]" if bin_result.right_closed else ")"
        lines.append(
            "| {index} | [{lower:.2f}, {upper:.2f}{close} | {count} | {accuracy} | {confidence} | {ece} | {tiers} |".format(
                index=bin_result.index,
                lower=bin_result.lower,
                upper=bin_result.upper,
                close=close,
                count=bin_result.count,
                accuracy=_format_optional_float(bin_result.accuracy),
                confidence=_format_optional_float(bin_result.confidence),
                ece=f"{bin_result.ece_contribution:.12g}",
                tiers=", ".join(bin_result.tiers) if bin_result.tiers else "",
            )
        )
    return "\n".join(lines)


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.12g}"
