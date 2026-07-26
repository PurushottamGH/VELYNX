"""EXP-1 artifact specifications.

These functions generate output schemas only; they do not execute EXP-1 and do
not write measured reliability, calibration, or decision results.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ArtifactSpec:
    """One generated-artifact schema specification."""

    filename: str
    format: str
    purpose: str
    fields: tuple[dict[str, Any], ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "format": self.format,
            "purpose": self.purpose,
            "fields": [dict(field) for field in self.fields],
            "notes": list(self.notes),
        }


def exp1_artifact_specs() -> tuple[ArtifactSpec, ...]:
    """Return the only Batch 2 EXP-1 generated-output specifications."""

    return (
        ArtifactSpec(
            filename="reliability.csv",
            format="csv",
            purpose="Four fixed equal-width ECE/reliability bins for EXP-1.",
            fields=(
                {"name": "bin", "type": "integer", "required": True},
                {"name": "range", "type": "string", "required": True},
                {"name": "count", "type": "integer", "required": True},
                {"name": "accuracy", "type": "number|null", "required": True},
                {"name": "confidence", "type": "number|null", "required": True},
                {"name": "ece_contribution", "type": "number", "required": True},
                {"name": "tiers", "type": "string", "required": True},
            ),
            notes=(
                "Exactly four rows, one for each locked bin: [0.00,0.25), [0.25,0.50), [0.50,0.75), [0.75,1.00].",
                "Empty bins must be present with count=0, blank accuracy/confidence, and ece_contribution=0.",
            ),
        ),
        ArtifactSpec(
            filename="calibration_report.md",
            format="markdown",
            purpose="Human-readable calibration report for one completed EXP-1 execution.",
            fields=(
                {"name": "experiment_id", "type": "heading", "required": True},
                {"name": "dataset_summary", "type": "section", "required": True},
                {"name": "seed_summary", "type": "section", "required": True},
                {"name": "calibration_summary", "type": "section", "required": True},
                {"name": "kill_reasons", "type": "section", "required": True},
                {"name": "reliability_table", "type": "section", "required": True},
            ),
            notes=(
                "Report text must distinguish measured facts from interpretation.",
                "The report must not introduce post-hoc thresholds or calibration rules.",
            ),
        ),
        ArtifactSpec(
            filename="experiment_summary.json",
            format="json",
            purpose="Machine-readable EXP-1 execution summary and pass/fail decision payload.",
            fields=(
                {"name": "experiment_id", "type": "string", "required": True},
                {"name": "dataset", "type": "object", "required": True},
                {"name": "required_seed_count", "type": "integer", "required": True},
                {"name": "completed_seed_count", "type": "integer", "required": True},
                {"name": "verdict", "type": "string", "required": True},
                {"name": "pass_h1", "type": "boolean", "required": True},
                {"name": "seed_decisions", "type": "array", "required": True},
                {"name": "pooled_calibration", "type": "object|null", "required": True},
                {"name": "kill_reasons", "type": "array", "required": True},
            ),
            notes=(
                "This file records EXP-1 outputs after execution only; Batch 2 creates this schema specification, not measured values.",
                "A PASS claim requires exactly the preregistered decision rules already implemented in decision.py.",
            ),
        ),
    )


def write_artifact_specifications(output_dir: str | Path) -> dict[str, Path]:
    """Write schema specification files for the permitted EXP-1 artifacts."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for spec in exp1_artifact_specs():
        spec_path = output_path / f"{spec.filename}.spec.json"
        spec_path.write_text(
            json.dumps(spec.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        paths[spec.filename] = spec_path
    return paths
