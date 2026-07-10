# EXP-1 Execution Guide

EXP-1 is the Program A calibration gate for H1. This guide documents execution readiness only; it is not an instruction to execute EXP-1 before the frozen inputs and blockers below are complete.

## Prerequisites

- `experiments/EXP1/config.json` is committed before execution and matches `EXP1_PREREGISTRATION.md`.
- The frozen query dataset exists at the configured path, currently `data/exp1_queries.json`.
- The frozen dataset passes `load_frozen_dataset` validation: exactly 210 rows, 70 rows per canonical query family, no duplicate query IDs, no duplicate query text, and immutable file-order loading.
- Every row has a query-specific `gold_rubric` string, with no duplicate rubric IDs and no duplicate rubric text.
- Program A exposes an answer adapter that emits exactly one answer and one public tier in `{UNKNOWN, DEBATED, PROBABLE, CERTAIN}` for every frozen query row.
- A correctness adjudicator is available and scores answer content against the frozen query-specific rubric only.
- No bin boundary, tier mapping, threshold, query label, rubric, or correctness rule has been changed after seeing EXP-1 outputs.

## Expected Inputs

### Frozen Dataset

Path: `data/exp1_queries.json`

Format: JSON list, JSON object with `records`, or JSONL.

Required row fields:

- `query_id`: stable unique string.
- `query`: held-out user-facing query text.
- `query_family`: one of `known_factual`, `ambiguous_or_debated`, or `hallucinated_unanswerable_or_false_premise`.
- `gold_rubric`: frozen query-specific correctness rubric string.
- `rubric_id`: optional unique rubric identifier.
- `metadata`: optional object.

Dataset invariants:

- Total rows: exactly 210.
- Family balance: exactly 70 `known_factual`, 70 `ambiguous_or_debated`, and 70 `hallucinated_unanswerable_or_false_premise`.
- Duplicate query IDs are rejected.
- Duplicate normalized query text is rejected.
- Duplicate rubric IDs are rejected when present.
- Duplicate normalized rubric text is rejected.
- Loader output preserves file order as an immutable tuple and records an `order_hash`.

### Program A Answer Records

For each frozen query row and seed, Program A must emit:

- `query_id`: the frozen query ID.
- `answer`: natural-language answer, refusal, or uncertainty response.
- `tier`: one of `UNKNOWN`, `DEBATED`, `PROBABLE`, or `CERTAIN`.
- `seed`: current independent replicate seed.
- `raw_numeric_confidence`: optional and ignored for primary EXP-1 ECE.
- `metadata`: optional object.

### Correctness Adjudication

The adjudicator must return binary answer correctness only:

- `correctness` or `y_i`: integer `0` or `1`.
- `fabricated_factual_answer`: optional boolean for hallucinated, unanswerable, or false-premise rows.

Correctness must be based on answer content against the frozen `gold_rubric`; confidence tier and query family cannot substitute for correctness.

## Generated Outputs

Batch 2 defines specifications only for these execution artifacts:

- `reliability.csv`: four fixed ECE reliability bins, including empty bins.
- `calibration_report.md`: human-readable calibration and kill-reason report.
- `experiment_summary.json`: machine-readable execution summary and pass/fail payload.

The schema specifications are produced by `write_artifact_specifications(output_dir)` as:

- `reliability.csv.spec.json`
- `calibration_report.md.spec.json`
- `experiment_summary.json.spec.json`

These specification files are not EXP-1 results.

## Directory Layout

Expected source layout:

```text
experiments/EXP1/
  artifact_specs.py
  calibration.py
  config.json
  dataset.py
  decision.py
  report.py
  rubric.py
  run.py
data/
  exp1_queries.json
tests/EXP1/
```

Expected run-output layout after execution:

```text
artifacts/EXP-1/<run_id>/
  config_used.json
  dataset_manifest.json
  execution_manifest.json
  reliability.csv.spec.json
  calibration_report.md.spec.json
  experiment_summary.json.spec.json
  seed_<seed>/
    answers.jsonl
    evaluated.jsonl
    decision.json
  reliability.csv
  calibration_report.md
  experiment_summary.json
  experiment_decision.json
```

## Reproducibility Procedure

1. Confirm the working tree contains the intended EXP-1 code, config, frozen dataset, and rubric files before any Program A outputs are generated.
2. Validate the frozen dataset with `load_frozen_dataset("data/exp1_queries.json")` and record `n`, family counts, and `order_hash`.
3. Generate artifact schema specifications with `write_artifact_specifications` into the run directory before execution outputs are written.
4. Execute exactly the preregistered independent seeds through the EXP-1 runner only after the frozen dataset and rubric validation pass.
5. Preserve raw answer records, evaluated records, per-seed decisions, pooled summaries, config, code revision, and dataset `order_hash` in the run directory.
6. Treat any post-output change to thresholds, binning, tier mapping, query labels, rubrics, or correctness rules as a protocol violation.

## Remaining Blockers Before First Execution

- The actual frozen dataset file `data/exp1_queries.json` is not present in this workspace.
- Program A answer adapter is not wired to the EXP-1 runner.
- A frozen-rubric adjudicator is not wired to the EXP-1 runner.
- No execution manifest currently records commit hash, dataset `order_hash`, adapter identity, adjudicator identity, and seed list.
