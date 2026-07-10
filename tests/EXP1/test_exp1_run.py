from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.EXP1.dataset import AnswerRecord, QueryRecord
from experiments.EXP1.manifest import MANIFEST_FILENAME, build_execution_manifest
from experiments.EXP1.program_a_adapter import CallableProgramAAdapter
from experiments.EXP1.run import run_experiment_sync, run_seed_sync


def _query_records() -> list[QueryRecord]:
    families = (
        ["known_factual"] * 70
        + ["ambiguous_or_debated"] * 70
        + ["hallucinated_unanswerable_or_false_premise"] * 70
    )
    return [
        QueryRecord(
            query_id=f"q{index:03d}",
            query=f"query {index}",
            query_family=family,
            gold_rubric=f"frozen rubric {index}",
        )
        for index, family in enumerate(families)
    ]


def _dataset_path(tmp_path: Path) -> Path:
    path = tmp_path / "exp1_queries.json"
    path.write_text(
        json.dumps([record.to_dict() for record in _query_records()]),
        encoding="utf-8",
    )
    return path


def _passing_tier_and_correctness(index: int) -> tuple[str, int]:
    if index < 80:
        return "UNKNOWN", int(index < 10)
    if index < 130:
        return "DEBATED", int(index - 80 < 19)
    return "CERTAIN", int(index - 130 < 70)


def _mixed_answer_fn(query: QueryRecord, seed: int) -> AnswerRecord:
    index = int(query.query_id.removeprefix("q"))
    if seed == 202:
        tier = "PROBABLE"
    else:
        tier, _ = _passing_tier_and_correctness(index)
    return AnswerRecord(query_id=query.query_id, answer="answer", tier=tier, seed=seed)


def _mixed_adjudicator_fn(query: QueryRecord, answer: AnswerRecord) -> int:
    index = int(query.query_id.removeprefix("q"))
    if answer.seed == 202:
        return 1
    _, correctness = _passing_tier_and_correctness(index)
    return correctness


def test_answer_record_mismatched_query_id_raises() -> None:
    def answer_fn(query: QueryRecord, seed: int) -> AnswerRecord:
        return AnswerRecord(
            query_id=f"wrong-{query.query_id}",
            answer="answer",
            tier="UNKNOWN",
            seed=seed,
        )

    with pytest.raises(ValueError, match="query_id"):
        run_seed_sync(
            _query_records(),
            seed=11,
            answer_fn=answer_fn,
            adjudicator_fn=_mixed_adjudicator_fn,
        )


def test_answer_record_mismatched_seed_raises() -> None:
    def answer_fn(query: QueryRecord, seed: int) -> AnswerRecord:
        return AnswerRecord(
            query_id=query.query_id,
            answer="answer",
            tier="UNKNOWN",
            seed=seed + 1,
        )

    with pytest.raises(ValueError, match="seed"):
        run_seed_sync(
            _query_records(),
            seed=11,
            answer_fn=answer_fn,
            adjudicator_fn=_mixed_adjudicator_fn,
        )


def test_run_experiment_duplicate_seed_list_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="distinct"):
        run_experiment_sync(
            dataset_path=_dataset_path(tmp_path),
            seeds=[7, 7],
            answer_fn=_mixed_answer_fn,
            adjudicator_fn=_mixed_adjudicator_fn,
        )


def test_run_experiment_empty_protocol_violations_list_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="protocol_violations length"):
        run_experiment_sync(
            dataset_path=_dataset_path(tmp_path),
            seeds=[7],
            answer_fn=_mixed_answer_fn,
            adjudicator_fn=_mixed_adjudicator_fn,
            protocol_violations=[],
        )


def test_run_experiment_protocol_violation_path(tmp_path: Path) -> None:
    decision = run_experiment_sync(
        dataset_path=_dataset_path(tmp_path),
        seeds=[101],
        answer_fn=_mixed_answer_fn,
        adjudicator_fn=_mixed_adjudicator_fn,
        protocol_violations=[True],
    )

    seed_decision = decision.seed_decisions[0]
    assert seed_decision.pass_h1 is False
    assert seed_decision.protocol_violation is True
    assert any("Protocol violation" in reason for reason in seed_decision.kill_reasons)


def test_run_experiment_mixed_pass_fail_aggregation(tmp_path: Path) -> None:
    decision = run_experiment_sync(
        dataset_path=_dataset_path(tmp_path),
        seeds=[101, 202],
        answer_fn=_mixed_answer_fn,
        adjudicator_fn=_mixed_adjudicator_fn,
    )

    assert [seed_decision.pass_h1 for seed_decision in decision.seed_decisions] == [
        True,
        False,
    ]
    assert decision.pass_h1 is False
    assert any("Seed 202 failed" in reason for reason in decision.kill_reasons)


def test_run_seed_and_run_experiment_produce_identical_per_seed_results(
    tmp_path: Path,
) -> None:
    seed_decision = run_seed_sync(
        _query_records(),
        seed=101,
        answer_fn=_mixed_answer_fn,
        adjudicator_fn=_mixed_adjudicator_fn,
    )
    experiment_decision = run_experiment_sync(
        dataset_path=_dataset_path(tmp_path),
        seeds=[101],
        answer_fn=_mixed_answer_fn,
        adjudicator_fn=_mixed_adjudicator_fn,
    )

    assert experiment_decision.seed_decisions[0].to_dict() == seed_decision.to_dict()


def test_run_experiment_writes_execution_manifest_before_outputs(tmp_path: Path) -> None:
    output_dir = tmp_path / "out"
    run_experiment_sync(
        dataset_path=_dataset_path(tmp_path),
        seeds=[101],
        answer_fn=_mixed_answer_fn,
        program_a_adapter_id="program-a-public-v1",
        adjudicator_fn=_mixed_adjudicator_fn,
        output_dir=output_dir,
    )

    manifest = json.loads((output_dir / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    assert manifest["experiment_id"] == "EXP-1"
    assert manifest["program_a_adapter_id"] == "program-a-public-v1"
    assert manifest["adjudicator_id"].endswith("._mixed_adjudicator_fn")
    assert manifest["seed_list"] == [101]
    assert (output_dir / "seed_101" / "answers.jsonl").exists()


def test_run_experiment_accepts_program_a_adapter_object(tmp_path: Path) -> None:
    adapter = CallableProgramAAdapter("program-a-public-v1", _mixed_answer_fn)

    decision = run_experiment_sync(
        dataset_path=_dataset_path(tmp_path),
        seeds=[101],
        program_a_adapter=adapter,
        adjudicator_fn=_mixed_adjudicator_fn,
    )

    assert decision.seed_decisions[0].seed == 101


def test_run_experiment_rejects_manifest_seed_mismatch(tmp_path: Path) -> None:
    dataset_path = _dataset_path(tmp_path)
    manifest, _ = build_execution_manifest(
        dataset_path=dataset_path,
        seeds=[202],
        program_a_adapter_id="program-a-public-v1",
        adjudicator_id="tests.EXP1.test_exp1_run._mixed_adjudicator_fn",
        git_commit="abc123",
    )

    with pytest.raises(ValueError, match="seed_list"):
        run_experiment_sync(
            dataset_path=dataset_path,
            seeds=[101],
            answer_fn=_mixed_answer_fn,
            program_a_adapter_id="program-a-public-v1",
            adjudicator_fn=_mixed_adjudicator_fn,
            execution_manifest=manifest,
        )
