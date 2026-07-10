"""EXP-1 runner adapter.

This module defines callable orchestration only. It does not execute Program A at
import time and does not own correctness adjudication; callers must inject both
the Program A answer function and the frozen-rubric adjudicator.
"""
from __future__ import annotations

import asyncio
import inspect
import json
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import Any

from experiments.EXP1.dataset import (
    AnswerRecord,
    EvaluatedRecord,
    QueryRecord,
    build_evaluated_records,
    load_query_records,
    records_to_jsonl,
    validate_query_records,
)
from experiments.EXP1.decision import ExperimentDecision, SeedDecision, decide_experiment, decide_seed
from experiments.EXP1.manifest import (
    ExecutionManifest,
    build_execution_manifest,
    manifest_for_records,
    write_execution_manifest,
)
from experiments.EXP1.program_a_adapter import (
    ProgramAAdapter,
    callable_identity,
    coerce_program_a_adapter,
)


AnswerFunction = Callable[[QueryRecord, int], AnswerRecord | Mapping[str, Any] | Awaitable[Any]]
AdjudicatorFunction = Callable[[QueryRecord, AnswerRecord], int | Mapping[str, Any] | Awaitable[Any]]


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load EXP-1 frozen configuration JSON."""

    config_path = Path(path) if path is not None else Path(__file__).with_name("config.json")
    return json.loads(config_path.read_text(encoding="utf-8"))


async def run_seed(
    query_records: list[QueryRecord],
    *,
    seed: int,
    answer_fn: AnswerFunction | None = None,
    program_a_adapter: ProgramAAdapter | None = None,
    program_a_adapter_id: str | None = None,
    adjudicator_fn: AdjudicatorFunction | None = None,
    output_dir: str | Path | None = None,
    protocol_violation: bool = False,
) -> SeedDecision:
    """Evaluate one independent EXP-1 seed replicate."""

    if adjudicator_fn is None:
        raise ValueError("adjudicator_fn is required")
    validate_query_records(query_records)
    adapter = coerce_program_a_adapter(
        adapter=program_a_adapter,
        answer_fn=answer_fn,
        adapter_id=program_a_adapter_id,
    )
    manifest = manifest_for_records(
        query_records=query_records,
        seed=seed,
        program_a_adapter_id=adapter.adapter_id,
        adjudicator_id=callable_identity(adjudicator_fn),
    )
    if output_dir is not None:
        write_execution_manifest(manifest, output_dir)
    answers: list[AnswerRecord] = []
    correctness_by_query_id: dict[str, int] = {}
    fabricated_by_query_id: dict[str, bool] = {}

    for query in query_records:
        answer_result = await _maybe_await(adapter.answer(query, seed))
        answer = _coerce_answer_record(answer_result, query.query_id, seed)
        answers.append(answer)

        adjudication = await _maybe_await(adjudicator_fn(query, answer))
        correctness, fabricated = _coerce_adjudication(adjudication)
        correctness_by_query_id[query.query_id] = correctness
        fabricated_by_query_id[query.query_id] = fabricated

    evaluated = build_evaluated_records(
        query_records,
        answers,
        correctness_by_query_id,
        fabricated_by_query_id,
    )
    decision = decide_seed(evaluated, seed=seed, protocol_violation=protocol_violation)

    if output_dir is not None:
        seed_dir = Path(output_dir) / f"seed_{seed}"
        seed_dir.mkdir(parents=True, exist_ok=True)
        (seed_dir / "answers.jsonl").write_text(records_to_jsonl(answers), encoding="utf-8")
        (seed_dir / "evaluated.jsonl").write_text(records_to_jsonl(evaluated), encoding="utf-8")
        (seed_dir / "decision.json").write_text(
            json.dumps(decision.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return decision


async def run_experiment(
    *,
    dataset_path: str | Path,
    seeds: list[int],
    answer_fn: AnswerFunction | None = None,
    program_a_adapter: ProgramAAdapter | None = None,
    program_a_adapter_id: str | None = None,
    adjudicator_fn: AdjudicatorFunction | None = None,
    output_dir: str | Path | None = None,
    protocol_violations: list[bool] | None = None,
    execution_manifest: ExecutionManifest | None = None,
) -> ExperimentDecision:
    """Run EXP-1 across caller-provided independent seeds."""

    if adjudicator_fn is None:
        raise ValueError("adjudicator_fn is required")
    adapter = coerce_program_a_adapter(
        adapter=program_a_adapter,
        answer_fn=answer_fn,
        adapter_id=program_a_adapter_id,
    )
    if execution_manifest is None:
        execution_manifest, frozen_dataset = build_execution_manifest(
            dataset_path=dataset_path,
            seeds=seeds,
            program_a_adapter_id=adapter.adapter_id,
            adjudicator_id=callable_identity(adjudicator_fn),
        )
    else:
        if execution_manifest.dataset_path != str(Path(dataset_path)):
            raise ValueError("execution manifest dataset_path must match dataset_path")
        if tuple(seeds) != execution_manifest.seed_list:
            raise ValueError("execution manifest seed_list must match requested seeds")
        if execution_manifest.program_a_adapter_id != adapter.adapter_id:
            raise ValueError("execution manifest adapter identity must match Program A adapter")
        if execution_manifest.adjudicator_id != callable_identity(adjudicator_fn):
            raise ValueError("execution manifest adjudicator identity must match adjudicator_fn")
        _, frozen_dataset = build_execution_manifest(
            dataset_path=dataset_path,
            seeds=seeds,
            program_a_adapter_id=adapter.adapter_id,
            adjudicator_id=callable_identity(adjudicator_fn),
            config_path=execution_manifest.config_path,
            git_commit=execution_manifest.git_commit,
        )
        if execution_manifest.dataset_order_hash != frozen_dataset.order_hash:
            raise ValueError("execution manifest dataset_order_hash must match dataset")
        if execution_manifest.dataset_n != len(frozen_dataset.records):
            raise ValueError("execution manifest dataset_n must match dataset")
        if execution_manifest.dataset_family_counts != frozen_dataset.family_counts:
            raise ValueError("execution manifest family counts must match dataset")
    query_records = list(frozen_dataset.records)
    if protocol_violations is None:
        protocol_violations = [False] * len(seeds)
    if len(protocol_violations) != len(seeds):
        raise ValueError("protocol_violations length must match seeds length")

    seed_record_sets: list[list[EvaluatedRecord]] = []
    seed_decisions: list[SeedDecision] = []
    if output_dir is not None:
        write_execution_manifest(execution_manifest, output_dir)

    for index, seed in enumerate(seeds):
        answers: list[AnswerRecord] = []
        correctness_by_query_id: dict[str, int] = {}
        fabricated_by_query_id: dict[str, bool] = {}
        for query in query_records:
            answer_result = await _maybe_await(adapter.answer(query, seed))
            answer = _coerce_answer_record(answer_result, query.query_id, seed)
            answers.append(answer)
            adjudication = await _maybe_await(adjudicator_fn(query, answer))
            correctness, fabricated = _coerce_adjudication(adjudication)
            correctness_by_query_id[query.query_id] = correctness
            fabricated_by_query_id[query.query_id] = fabricated

        evaluated = build_evaluated_records(
            query_records,
            answers,
            correctness_by_query_id,
            fabricated_by_query_id,
        )
        seed_record_sets.append(evaluated)
        seed_decisions.append(
            decide_seed(evaluated, seed=seed, protocol_violation=protocol_violations[index])
        )

        if output_dir is not None:
            seed_dir = Path(output_dir) / f"seed_{seed}"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "answers.jsonl").write_text(records_to_jsonl(answers), encoding="utf-8")
            (seed_dir / "evaluated.jsonl").write_text(records_to_jsonl(evaluated), encoding="utf-8")
            (seed_dir / "decision.json").write_text(
                json.dumps(seed_decisions[-1].to_dict(), indent=2, sort_keys=True),
                encoding="utf-8",
            )

    experiment_decision = decide_experiment(
        seed_record_sets,
        protocol_violations=protocol_violations,
    )
    if output_dir is not None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        (output_path / "experiment_decision.json").write_text(
            json.dumps(experiment_decision.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
    return experiment_decision


def run_seed_sync(*args: Any, **kwargs: Any) -> SeedDecision:
    """Synchronous wrapper for callers that do not already own an event loop."""

    return asyncio.run(run_seed(*args, **kwargs))


def run_experiment_sync(*args: Any, **kwargs: Any) -> ExperimentDecision:
    """Synchronous wrapper for callers that do not already own an event loop."""

    return asyncio.run(run_experiment(*args, **kwargs))


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _coerce_answer_record(value: Any, query_id: str, seed: int) -> AnswerRecord:
    if isinstance(value, AnswerRecord):
        if value.query_id != query_id:
            raise ValueError(
                f"answer query_id={value.query_id!r} does not match expected {query_id!r}"
            )
        if value.seed != seed:
            raise ValueError(
                f"answer query_id={query_id!r} has seed={value.seed}, expected {seed}"
            )
        return value
    if not isinstance(value, Mapping):
        raise TypeError("answer_fn must return AnswerRecord or mapping")
    row = dict(value)
    row["query_id"] = query_id
    row["seed"] = seed
    return AnswerRecord.from_mapping(row)


def _coerce_adjudication(value: Any) -> tuple[int, bool]:
    if isinstance(value, bool):
        return int(value), False
    if isinstance(value, int):
        if value not in (0, 1):
            raise ValueError("integer adjudication must be 0 or 1")
        return value, False
    if not isinstance(value, Mapping):
        raise TypeError("adjudicator_fn must return 0/1, bool, or mapping")
    correctness = value.get("correctness", value.get("y_i"))
    if correctness is None:
        raise ValueError("adjudication mapping must include correctness or y_i")
    correctness = int(correctness)
    if correctness not in (0, 1):
        raise ValueError("adjudication correctness must be 0 or 1")
    return correctness, bool(value.get("fabricated_factual_answer", False))
