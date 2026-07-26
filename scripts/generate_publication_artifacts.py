#!/usr/bin/env python3
"""Publication Artifact Generation.

Generates publication-ready artifacts from experiment data:
- Statistical reports (JSON, Markdown)
- Data tables (CSV)
- Summary figures (JSON for plotting)
- Publication manifest
"""

import sys
import json
import csv
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments.metrics import MetricsRecord, MetricsReport
from experiments.artifacts import ArtifactStore
from scripts.statistical_analysis import analyze_experiment, generate_publication_report

PUBLICATION_METADATA = {
    "project": "VELYNX",
    "title": "Predictive Processing Without LLMs: A Minimal Cognitive Architecture",
    "authors": ["Program D Team"],
    "venue_targets": [
        "NeurIPS 2026",
        "ICML 2026",
        "Nature Machine Intelligence",
        "Cognitive Science",
    ],
    "generated_at": None,
}


def export_data_csv(records: List[Dict], output_path: Path):
    if not records:
        return
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)


def generate_latex_table(analysis: Dict) -> str:
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"Metric & Mean & SD & Min & Max \\",
        r"\midrule",
    ]
    for metric in ["free_energy", "surprise", "entropy", "structural_load"]:
        if metric in analysis:
            m = analysis[metric]
            lines.append(
                f"{metric.replace('_', ' ').title()} & "
                f"{m['mean']:.4f} & {m['std']:.4f} & "
                f"{m['min']:.4f} & {m['max']:.4f} \\\\"
            )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Summary statistics for " + analysis.get("experiment_id", "?") + "}",
            r"\label{tab:" + analysis.get("experiment_id", "exp") + "}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines)


def main():
    root = Path(__file__).resolve().parent.parent
    output_dir = root / "artifacts" / "publication"
    output_dir.mkdir(parents=True, exist_ok=True)

    PUBLICATION_METADATA["generated_at"] = datetime.now(timezone.utc).isoformat()

    store = ArtifactStore()
    all_experiments = []

    experiments_base = store.base / "experiments"
    if experiments_base.exists():
        for exp_dir in sorted(experiments_base.iterdir()):
            if not exp_dir.is_dir():
                continue
            experiment_id = exp_dir.name
            runs = store.list_runs(experiment_id)
            if not runs:
                continue
            latest_run = runs[0]

            artifacts = store.list_artifacts(experiment_id, latest_run)
            all_experiments.append(
                {
                    "experiment_id": experiment_id,
                    "latest_run": latest_run,
                    "artifacts": artifacts,
                }
            )

            pub_dir = store.export_for_publication(experiment_id, latest_run, output_dir)
            print(f"[EXPORT] {experiment_id}/{latest_run} -> {pub_dir}")

            metrics_file = store.base / "experiments" / experiment_id / latest_run / "metrics.jsonl"
            if metrics_file.exists():
                analysis = analyze_experiment(experiment_id, latest_run, metrics_file)
                analysis_path = pub_dir / "statistical_analysis.json"
                with open(analysis_path, "w") as f:
                    json.dump(analysis, f, indent=2)

                report_path = pub_dir / "statistical_report.md"
                generate_publication_report(analysis, report_path)

                latex_path = pub_dir / "latex_table.tex"
                latex_path.write_text(generate_latex_table(analysis))

                print(f"[STATS] {experiment_id}: analysis + report + LaTeX table generated")

    manifest = PUBLICATION_METADATA.copy()
    manifest["experiments"] = all_experiments
    manifest_path = output_dir / "publication_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    summary = [
        "=" * 60,
        "Publication Artifacts Generated",
        "=" * 60,
        f"Output: {output_dir}",
        f"Experiments: {len(all_experiments)}",
        f"Manifest: {manifest_path}",
        "-" * 60,
    ]
    for exp in all_experiments:
        summary.append(
            f"  {exp['experiment_id']} ({exp['latest_run']}): {len(exp['artifacts'])} artifacts"
        )
    summary.append("=" * 60)
    print("\n".join(summary))

    summary_path = output_dir / "generation_summary.txt"
    summary_path.write_text("\n".join(summary))


if __name__ == "__main__":
    main()
