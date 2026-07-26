"""Deterministic EXP-1 execution manifest support."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from experiments.EXP1.dataset import FrozenDataset, QueryRecord, load_frozen_dataset

MANIFEST_FILENAME = "execution_manifest.json"


@dataclass(frozen=True)
class ExecutionManifest:
    """Execution inputs that must be fixed before Program A outputs are emitted."""

    experiment_id: str
    git_commit: str
    dataset_path: str
    dataset_order_hash: str
    dataset_n: int
    dataset_family_counts: dict[str, int]
    seed_list: tuple[int, ...]
    program_a_adapter_id: str
    adjudicator_id: str
    config_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "git_commit": self.git_commit,
            "dataset_path": self.dataset_path,
            "dataset_order_hash": self.dataset_order_hash,
            "dataset_n": self.dataset_n,
            "dataset_family_counts": dict(sorted(self.dataset_family_counts.items())),
            "seed_list": list(self.seed_list),
            "program_a_adapter_id": self.program_a_adapter_id,
            "adjudicator_id": self.adjudicator_id,
            "config_path": self.config_path,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def build_execution_manifest(
    *,
    dataset_path: str | Path,
    seeds: Sequence[int],
    program_a_adapter_id: str,
    adjudicator_id: str,
    config_path: str | Path | None = None,
    git_commit: str | None = None,
) -> tuple[ExecutionManifest, FrozenDataset]:
    """Validate fixed EXP-1 inputs and return a manifest plus frozen dataset."""

    seed_list = tuple(int(seed) for seed in seeds)
    if len(set(seed_list)) != len(seed_list):
        raise ValueError("seeds must be distinct")
    dataset = load_frozen_dataset(dataset_path)
    manifest = ExecutionManifest(
        experiment_id="EXP-1",
        git_commit=git_commit or current_git_commit(),
        dataset_path=str(Path(dataset_path)),
        dataset_order_hash=dataset.order_hash,
        dataset_n=len(dataset.records),
        dataset_family_counts=dict(dataset.family_counts),
        seed_list=seed_list,
        program_a_adapter_id=program_a_adapter_id,
        adjudicator_id=adjudicator_id,
        config_path=str(
            Path(config_path)
            if config_path is not None
            else Path(__file__).with_name("config.json")
        ),
    )
    validate_execution_manifest(manifest)
    return manifest, dataset


def manifest_for_records(
    *,
    query_records: Sequence[QueryRecord],
    seed: int,
    program_a_adapter_id: str,
    adjudicator_id: str,
    config_path: str | Path | None = None,
    git_commit: str | None = None,
) -> ExecutionManifest:
    """Build a single-seed manifest for caller-provided query records."""

    from experiments.EXP1.dataset import validate_query_records

    validation = validate_query_records(query_records)
    payload = "\n".join(
        json.dumps(record.to_dict(), sort_keys=True) for record in query_records
    ).encode("utf-8")
    manifest = ExecutionManifest(
        experiment_id="EXP-1",
        git_commit=git_commit or current_git_commit(),
        dataset_path="<in_memory>",
        dataset_order_hash=hashlib.sha256(payload).hexdigest(),
        dataset_n=len(query_records),
        dataset_family_counts=validation["family_counts"],
        seed_list=(int(seed),),
        program_a_adapter_id=program_a_adapter_id,
        adjudicator_id=adjudicator_id,
        config_path=str(
            Path(config_path)
            if config_path is not None
            else Path(__file__).with_name("config.json")
        ),
    )
    validate_execution_manifest(manifest)
    return manifest


def validate_execution_manifest(manifest: ExecutionManifest) -> None:
    if manifest.experiment_id != "EXP-1":
        raise ValueError("execution manifest experiment_id must be EXP-1")
    if not manifest.git_commit:
        raise ValueError("execution manifest git_commit is required")
    if not manifest.dataset_order_hash:
        raise ValueError("execution manifest dataset_order_hash is required")
    if manifest.dataset_n <= 0:
        raise ValueError("execution manifest dataset_n must be positive")
    if len(set(manifest.seed_list)) != len(manifest.seed_list):
        raise ValueError("execution manifest seed_list must contain distinct seeds")
    if not manifest.program_a_adapter_id.strip():
        raise ValueError("execution manifest program_a_adapter_id is required")
    if not manifest.adjudicator_id.strip():
        raise ValueError("execution manifest adjudicator_id is required")


def write_execution_manifest(manifest: ExecutionManifest, output_dir: str | Path) -> Path:
    path = Path(output_dir) / MANIFEST_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.to_json(), encoding="utf-8")
    return path


def current_git_commit() -> str:
    root = Path(__file__).resolve().parents[2]
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            check=False,
            cwd=root,
            text=True,
        )
    except OSError:
        return "unknown"
    commit = result.stdout.strip()
    return commit or "unknown"
