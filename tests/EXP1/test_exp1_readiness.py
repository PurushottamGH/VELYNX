from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from experiments.EXP1.artifact_specs import exp1_artifact_specs, write_artifact_specifications
from experiments.EXP1.dataset import (
    PLANNED_BALANCED_DATASET_SIZE,
    PLANNED_FAMILY_ALLOCATION,
    FrozenDataset,
    QueryRecord,
    load_frozen_dataset,
    validate_frozen_dataset_records,
)
from experiments.EXP1.manifest import (
    MANIFEST_FILENAME,
    ExecutionManifest,
    build_execution_manifest,
    validate_execution_manifest,
    write_execution_manifest,
)
from experiments.EXP1.program_a_adapter import CallableProgramAAdapter, coerce_program_a_adapter
from experiments.EXP1.rubric import validate_gold_rubrics


def _frozen_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    families = (
        ["known_factual"] * 70
        + ["ambiguous_or_debated"] * 70
        + ["hallucinated_unanswerable_or_false_premise"] * 70
    )
    for index, family in enumerate(families):
        rows.append(
            {
                "query_id": f"q{index:03d}",
                "query": f"frozen EXP-1 query {index}",
                "query_family": family,
                "gold_rubric": f"Unique rubric {index}: adjudicate answer content only.",
                "rubric_id": f"r{index:03d}",
            }
        )
    return rows


def _write_rows(tmp_path: Path, rows: list[dict[str, object]]) -> Path:
    path = tmp_path / "exp1_queries.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


def test_load_frozen_dataset_requires_exact_210_balanced_records(tmp_path: Path) -> None:
    dataset = load_frozen_dataset(_write_rows(tmp_path, _frozen_rows()))

    assert isinstance(dataset, FrozenDataset)
    assert len(dataset.records) == PLANNED_BALANCED_DATASET_SIZE
    assert dataset.family_counts == PLANNED_FAMILY_ALLOCATION


def test_load_frozen_dataset_rejects_wrong_record_count(tmp_path: Path) -> None:
    rows = _frozen_rows()[:-1]

    with pytest.raises(ValueError, match="exactly 210"):
        load_frozen_dataset(_write_rows(tmp_path, rows))


def test_load_frozen_dataset_rejects_family_imbalance(tmp_path: Path) -> None:
    rows = _frozen_rows()
    rows[0]["query_family"] = "ambiguous_or_debated"

    with pytest.raises(ValueError, match="70 records"):
        load_frozen_dataset(_write_rows(tmp_path, rows))


def test_load_frozen_dataset_rejects_duplicate_query_id_and_query_text(tmp_path: Path) -> None:
    rows = _frozen_rows()
    rows[1]["query_id"] = rows[0]["query_id"]

    with pytest.raises(ValueError, match="duplicate query_id"):
        load_frozen_dataset(_write_rows(tmp_path, rows))

    rows = _frozen_rows()
    rows[1]["query"] = rows[0]["query"]
    with pytest.raises(ValueError, match="duplicate query text"):
        load_frozen_dataset(_write_rows(tmp_path, rows))


def test_load_frozen_dataset_preserves_immutable_order_with_order_hash(tmp_path: Path) -> None:
    rows = _frozen_rows()
    dataset = load_frozen_dataset(_write_rows(tmp_path, rows))

    expected_order = tuple(f"q{index:03d}" for index in range(210))
    expected_payload = "\n".join(
        json.dumps(record.to_dict(), sort_keys=True) for record in dataset.records
    ).encode("utf-8")
    expected_hash = hashlib.sha256(expected_payload).hexdigest()

    assert isinstance(dataset.records, tuple)
    assert tuple(record.query_id for record in dataset.records) == expected_order
    assert dataset.order_hash == expected_hash


def test_validate_frozen_dataset_records_rejects_duplicate_query_record() -> None:
    record = QueryRecord(
        query_id="q000",
        query="query",
        query_family="known_factual",
        gold_rubric="unique rubric",
    )

    with pytest.raises(ValueError, match="exactly 210"):
        validate_frozen_dataset_records([record])


def test_validate_gold_rubrics_rejects_missing_duplicate_and_malformed_rubrics() -> None:
    rows = _frozen_rows()
    validate_gold_rubrics(rows)

    missing = _frozen_rows()
    del missing[0]["gold_rubric"]
    with pytest.raises(ValueError, match="missing gold_rubric"):
        validate_gold_rubrics(missing)

    duplicate_query_id = _frozen_rows()
    duplicate_query_id[1]["query_id"] = duplicate_query_id[0]["query_id"]
    with pytest.raises(ValueError, match="duplicate rubric query_id"):
        validate_gold_rubrics(duplicate_query_id)

    duplicate_text = _frozen_rows()
    duplicate_text[1]["gold_rubric"] = duplicate_text[0]["gold_rubric"]
    with pytest.raises(ValueError, match="duplicate gold_rubric text"):
        validate_gold_rubrics(duplicate_text)

    duplicate_id = _frozen_rows()
    duplicate_id[1]["rubric_id"] = duplicate_id[0]["rubric_id"]
    with pytest.raises(ValueError, match="duplicate rubric_id"):
        validate_gold_rubrics(duplicate_id)

    malformed = _frozen_rows()
    malformed[0]["gold_rubric"] = {"correct_if": "structured rubric is not frozen schema"}
    with pytest.raises(ValueError, match="malformed gold_rubric"):
        validate_gold_rubrics(malformed)


def test_artifact_specs_are_limited_to_required_outputs(tmp_path: Path) -> None:
    specs = exp1_artifact_specs()

    assert [spec.filename for spec in specs] == [
        "reliability.csv",
        "calibration_report.md",
        "experiment_summary.json",
    ]
    assert all(spec.fields for spec in specs)

    paths = write_artifact_specifications(tmp_path)
    assert sorted(paths) == [
        "calibration_report.md",
        "experiment_summary.json",
        "reliability.csv",
    ]
    assert sorted(path.name for path in paths.values()) == [
        "calibration_report.md.spec.json",
        "experiment_summary.json.spec.json",
        "reliability.csv.spec.json",
    ]
    assert not (tmp_path / "reliability.csv").exists()
    assert not (tmp_path / "calibration_report.md").exists()
    assert not (tmp_path / "experiment_summary.json").exists()


def test_program_a_callable_adapter_has_stable_identity() -> None:
    def answer_fn(query: QueryRecord, seed: int) -> dict[str, object]:
        return {"query_id": query.query_id, "answer": "answer", "tier": "UNKNOWN", "seed": seed}

    adapter = coerce_program_a_adapter(answer_fn=answer_fn, adapter_id="program-a-public-v1")

    assert isinstance(adapter, CallableProgramAAdapter)
    assert adapter.adapter_id == "program-a-public-v1"


def test_build_execution_manifest_records_fixed_inputs_deterministically(tmp_path: Path) -> None:
    dataset_path = _write_rows(tmp_path, _frozen_rows())
    config_path = tmp_path / "config.json"

    manifest, dataset = build_execution_manifest(
        dataset_path=dataset_path,
        seeds=[101, 202],
        program_a_adapter_id="program-a-public-v1",
        adjudicator_id="frozen-rubric-v1",
        config_path=config_path,
        git_commit="abc123",
    )

    assert manifest.to_dict() == {
        "experiment_id": "EXP-1",
        "git_commit": "abc123",
        "dataset_path": str(dataset_path),
        "dataset_order_hash": dataset.order_hash,
        "dataset_n": 210,
        "dataset_family_counts": dict(sorted(PLANNED_FAMILY_ALLOCATION.items())),
        "seed_list": [101, 202],
        "program_a_adapter_id": "program-a-public-v1",
        "adjudicator_id": "frozen-rubric-v1",
        "config_path": str(config_path),
    }
    assert json.loads(manifest.to_json()) == manifest.to_dict()


def test_write_execution_manifest_writes_only_manifest_file(tmp_path: Path) -> None:
    manifest = ExecutionManifest(
        experiment_id="EXP-1",
        git_commit="abc123",
        dataset_path="data/exp1_queries.json",
        dataset_order_hash="orderhash",
        dataset_n=210,
        dataset_family_counts=PLANNED_FAMILY_ALLOCATION,
        seed_list=(101, 202),
        program_a_adapter_id="program-a-public-v1",
        adjudicator_id="frozen-rubric-v1",
        config_path="experiments/EXP1/config.json",
    )

    path = write_execution_manifest(manifest, tmp_path)

    assert path == tmp_path / MANIFEST_FILENAME
    assert json.loads(path.read_text(encoding="utf-8")) == manifest.to_dict()
    assert sorted(child.name for child in tmp_path.iterdir()) == [MANIFEST_FILENAME]


def test_validate_execution_manifest_rejects_missing_adapter_identity() -> None:
    manifest = ExecutionManifest(
        experiment_id="EXP-1",
        git_commit="abc123",
        dataset_path="data/exp1_queries.json",
        dataset_order_hash="orderhash",
        dataset_n=210,
        dataset_family_counts=PLANNED_FAMILY_ALLOCATION,
        seed_list=(101, 202),
        program_a_adapter_id="",
        adjudicator_id="frozen-rubric-v1",
        config_path="experiments/EXP1/config.json",
    )

    with pytest.raises(ValueError, match="program_a_adapter_id"):
        validate_execution_manifest(manifest)
