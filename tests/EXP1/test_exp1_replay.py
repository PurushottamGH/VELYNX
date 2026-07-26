"""Byte-identical replay test for the EXP-1 runner (experiments/EXP1/run.py).

Specced but missing on disk: PROGRAM_A_MASTER_SPECIFICATION.md Section 9
defines "replay" for this project as "given the frozen dataset (order_hash),
the frozen config, the recorded program_a_adapter_id and adjudicator_id, and
the seed list, a re-run must reproduce the recorded answers and decisions."
This test operationalizes that definition directly against run.py -- the only
module in the whole tree with a fully real, non-stub execution path today --
by running run_experiment_sync() twice, independently, from the same frozen
inputs, and diffing every written artifact byte-for-byte.

This deliberately does NOT touch program_a.* (still mostly stubs); the answer
function is a synthetic deterministic stand-in, exactly as
program_a_adapter.py's own docstring prescribes ("callers must inject ...
Program A answer function").

Scope: tests only, no production-code changes.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments.EXP1.dataset import AnswerRecord, QueryRecord
from experiments.EXP1.manifest import MANIFEST_FILENAME
from experiments.EXP1.run import run_experiment_sync


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


def _dataset_path(tmp_path: Path, name: str = "exp1_queries.json") -> Path:
    path = tmp_path / name
    path.write_text(
        json.dumps([record.to_dict() for record in _query_records()]),
        encoding="utf-8",
    )
    return path


def _deterministic_answer_fn(query: QueryRecord, seed: int) -> AnswerRecord:
    # A pure function of (query_id, seed) only -- no randomness, no wall
    # clock, no shared mutable state -- so a byte-identical replay is even
    # possible to assert in the first place.
    index = int(query.query_id.removeprefix("q"))
    tiers = ("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")
    tier = tiers[(index + seed) % 4]
    return AnswerRecord(
        query_id=query.query_id,
        answer=f"deterministic answer for {query.query_id} seed={seed}",
        tier=tier,
        seed=seed,
        metadata={"index": index},
    )


def _deterministic_adjudicator_fn(query: QueryRecord, answer: AnswerRecord) -> int:
    index = int(query.query_id.removeprefix("q"))
    return index % 2


def _artifact_bytes(output_dir: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(output_dir)): p.read_bytes()
        for p in sorted(output_dir.rglob("*"))
        if p.is_file()
    }


def test_two_independent_runs_from_identical_inputs_produce_byte_identical_artifacts(
    tmp_path: Path,
) -> None:
    dataset_path = _dataset_path(tmp_path)
    run_a_dir = tmp_path / "run_a"
    run_b_dir = tmp_path / "run_b"

    run_experiment_sync(
        dataset_path=dataset_path,
        seeds=[11, 22],
        answer_fn=_deterministic_answer_fn,
        program_a_adapter_id="program-a-public-v1+test",
        adjudicator_fn=_deterministic_adjudicator_fn,
        output_dir=run_a_dir,
    )
    run_experiment_sync(
        dataset_path=dataset_path,
        seeds=[11, 22],
        answer_fn=_deterministic_answer_fn,
        program_a_adapter_id="program-a-public-v1+test",
        adjudicator_fn=_deterministic_adjudicator_fn,
        output_dir=run_b_dir,
    )

    artifacts_a = _artifact_bytes(run_a_dir)
    artifacts_b = _artifact_bytes(run_b_dir)

    # git_commit is not pinned here (run_experiment_sync has no such kwarg;
    # it always shells out via current_git_commit()), so the manifest's
    # git_commit field is excluded from the byte-identical comparison -- it
    # is legitimately environment-derived, not part of Program A's own
    # determinism contract. Every OTHER byte, including the rest of the
    # manifest, must still match exactly.
    def _strip_git_commit(raw: bytes) -> bytes:
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            return raw
        if isinstance(obj, dict) and "git_commit" in obj:
            obj = dict(obj)
            obj["git_commit"] = "<normalized>"
            return json.dumps(obj, indent=2, sort_keys=True).encode("utf-8")
        return raw

    assert artifacts_a.keys() == artifacts_b.keys(), (
        f"replay produced a different artifact SET: only-in-A="
        f"{artifacts_a.keys() - artifacts_b.keys()} only-in-B="
        f"{artifacts_b.keys() - artifacts_a.keys()}"
    )
    mismatches = [
        name
        for name in artifacts_a
        if _strip_git_commit(artifacts_a[name]) != _strip_git_commit(artifacts_b[name])
    ]
    assert mismatches == [], f"non-byte-identical replay artifacts: {mismatches}"

    # Sanity: the artifact set is non-trivial (catches a vacuously-passing
    # test if output_dir writing silently broke and both dirs ended up empty).
    assert len(artifacts_a) > 0
    assert any(name == MANIFEST_FILENAME for name in artifacts_a)
    assert any("experiment_decision.json" in name for name in artifacts_a)


def test_run_experiment_execution_manifest_records_a_real_git_commit(
    tmp_path: Path,
) -> None:
    # run_experiment_sync has no git_commit override kwarg; it always derives
    # the manifest's git_commit via current_git_commit() (a `git rev-parse
    # HEAD` subprocess call). Assert it actually resolves to a real commit
    # (not the "unknown" fallback) when run from within this repo checkout --
    # if this starts failing, replay identity provenance has silently
    # degraded to "unknown" for every run.
    dataset_path = _dataset_path(tmp_path)
    output_dir = tmp_path / "out"

    run_experiment_sync(
        dataset_path=dataset_path,
        seeds=[1],
        answer_fn=_deterministic_answer_fn,
        program_a_adapter_id="program-a-public-v1+test",
        adjudicator_fn=_deterministic_adjudicator_fn,
        output_dir=output_dir,
    )

    manifest = json.loads((output_dir / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    assert manifest["git_commit"] != "unknown"
    assert len(manifest["git_commit"]) == 40  # full SHA-1 hex digest


def test_replay_with_mismatched_answer_fn_content_is_not_byte_identical(
    tmp_path: Path,
) -> None:
    # Negative control: proves the byte-identical assertion above is actually
    # discriminating (not vacuously true because e.g. only the manifest was
    # compared). A DIFFERENT deterministic answer function must produce
    # artifacts that diverge from the baseline.
    dataset_path = _dataset_path(tmp_path)
    baseline_dir = tmp_path / "baseline"
    divergent_dir = tmp_path / "divergent"

    def divergent_answer_fn(query: QueryRecord, seed: int) -> AnswerRecord:
        return AnswerRecord(
            query_id=query.query_id,
            answer="a different deterministic answer text",
            tier="UNKNOWN",
            seed=seed,
        )

    run_experiment_sync(
        dataset_path=dataset_path,
        seeds=[11],
        answer_fn=_deterministic_answer_fn,
        program_a_adapter_id="program-a-public-v1+test",
        adjudicator_fn=_deterministic_adjudicator_fn,
        output_dir=baseline_dir,
    )
    run_experiment_sync(
        dataset_path=dataset_path,
        seeds=[11],
        answer_fn=divergent_answer_fn,
        program_a_adapter_id="program-a-public-v1+test-divergent",
        adjudicator_fn=_deterministic_adjudicator_fn,
        output_dir=divergent_dir,
    )

    answers_baseline = (baseline_dir / "seed_11" / "answers.jsonl").read_bytes()
    answers_divergent = (divergent_dir / "seed_11" / "answers.jsonl").read_bytes()
    assert answers_baseline != answers_divergent
