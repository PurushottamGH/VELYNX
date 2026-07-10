"""Integration tests for the EXP-1 Program A adapter through the runner.

Director-implemented due to specialist runtime failure (2026-07-07).

These tests run the adapter end-to-end through ``run_seed_sync`` with an
externally-injected canonical ``answer_fn`` (no retriever/synthesizer binding,
no tier computation). They assert the adapter/coercion plumbing faithfully
transports the injected canonical answer+tier into the recorded
``AnswerRecord`` files. A passing experiment (H1 pass) is NOT asserted - only
plumbing fidelity.

Scope: tests only. No production-code changes. No canonical-document edits.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.EXP1.dataset import AnswerRecord, QueryRecord
from experiments.EXP1.run import run_seed_sync


def _query_records() -> list[QueryRecord]:
    families = (
        ["known_factual"] * 70
        + ["ambiguous_or_debated"] * 70
        + ["hallucinated_unanswerable_or_false_premise"] * 70
    )
    return [
        QueryRecord(
            query_id=f"q{i:03d}",
            query=f"query {i}",
            query_family=family,
            gold_rubric=f"frozen rubric {i}",
        )
        for i, family in enumerate(families)
    ]


def _adjudicator(query: QueryRecord, answer: AnswerRecord) -> int:
    # Correctness is irrelevant to adapter plumbing; return a constant.
    return 0


def _read_answers(output_dir: Path, seed: int) -> list[dict]:
    path = output_dir / f"seed_{seed}" / "answers.jsonl"
    assert path.exists(), f"missing {path}"
    text = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def test_mapping_return_path_is_coerced_to_answer_record(tmp_path: Path) -> None:
    """An answer_fn returning a plain dict is coerced to AnswerRecord."""

    def answer_fn(query: QueryRecord, seed: int) -> dict:
        return {"answer": "mapped", "tier": "UNKNOWN"}

    output_dir = tmp_path / "out"
    decision = run_seed_sync(
        _query_records(),
        seed=1,
        answer_fn=answer_fn,
        adjudicator_fn=_adjudicator,
        output_dir=output_dir,
    )

    rows = _read_answers(output_dir, 1)
    assert len(rows) == 210
    assert all(row["tier"] == "UNKNOWN" for row in rows)
    assert all(row["answer"] == "mapped" for row in rows)
    assert all(row["seed"] == 1 for row in rows)
    assert all(row["query_id"].startswith("q") for row in rows)
    # The runner returns a decision (it may be a kill; plumbing is what matters).
    assert decision.seed == 1


def test_awaitable_return_path_is_awaited_and_coerced(tmp_path: Path) -> None:
    """An async answer_fn returning AnswerRecord is awaited and coerced."""

    async def answer_fn(query: QueryRecord, seed: int) -> AnswerRecord:
        return AnswerRecord(
            query_id=query.query_id,
            answer="async",
            tier="PROBABLE",
            seed=seed,
        )

    output_dir = tmp_path / "out"
    decision = run_seed_sync(
        _query_records(),
        seed=2,
        answer_fn=answer_fn,
        adjudicator_fn=_adjudicator,
        output_dir=output_dir,
    )

    rows = _read_answers(output_dir, 2)
    assert len(rows) == 210
    assert all(row["tier"] == "PROBABLE" for row in rows)
    assert all(row["answer"] == "async" for row in rows)
    assert all(row["seed"] == 2 for row in rows)
    assert decision.seed == 2


def test_mapping_uses_answer_i_tier_i_aliases(tmp_path: Path) -> None:
    """The answer_i / tier_i aliases are accepted through the coercion path."""

    def answer_fn(query: QueryRecord, seed: int) -> dict:
        return {"answer_i": "aliased", "tier_i": "DEBATED"}

    output_dir = tmp_path / "out"
    run_seed_sync(
        _query_records(),
        seed=3,
        answer_fn=answer_fn,
        adjudicator_fn=_adjudicator,
        output_dir=output_dir,
    )

    rows = _read_answers(output_dir, 3)
    assert len(rows) == 210
    assert all(row["tier"] == "DEBATED" for row in rows)
    assert all(row["answer"] == "aliased" for row in rows)
    assert all(row["seed"] == 3 for row in rows)
