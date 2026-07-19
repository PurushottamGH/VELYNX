# Program A Adapter Test Plan

**Status:** Director-implemented due to specialist runtime failure.

**Reason:** The Builder specialist agent returned no output across all
invocation attempts in this session. This test plan and the associated test
files are produced by the Director under explicit, one-time user authorization
(2026-07-07). They have NOT passed a formal Reviewer or ScientificAuditor gate
(both unavailable). No specialist approvals are claimed or implied.

**Scope:** Test the EXISTING `experiments/EXP1/program_a_adapter.py` framework
and its integration with the EXP-1 runner. Tests only. No production code
changes. No new adapter class. No retriever/synthesizer binding. No tier
computation. No canonical-document edits. No parameter changes. No
architecture changes.

**Subject under test:** `experiments/EXP1/program_a_adapter.py` (76 lines),
exercising `experiments/EXP1/dataset.py` (`AnswerRecord`, `QueryRecord`,
`CONFIDENCE_TIERS`) and `experiments/EXP1/run.py` (`_coerce_answer_record`,
`_maybe_await`, `run_seed_sync`, `run_experiment_sync`).

**Import policy:** tests import ONLY from `experiments.EXP1.*` and stdlib +
`pytest`. They do NOT import `backend.*`, `program_a.*`, or `core.*`. This
respects the dependency boundary and avoids touching the scientific path or
`[REJECTED]` mechanisms.

---

## 1. Existing coverage (do not duplicate)

| Test | File:line | What it covers |
|---|---|---|
| `test_program_a_callable_adapter_has_stable_identity` | `tests/EXP1/test_exp1_readiness.py:174` | `coerce_program_a_adapter(answer_fn=..., adapter_id=...)` returns `CallableProgramAAdapter` with the given id |
| `test_validate_execution_manifest_rejects_missing_adapter_identity` | `test_exp1_readiness.py:233` | manifest rejects empty `program_a_adapter_id` |
| `test_answer_record_mismatched_query_id_raises` | `tests/EXP1/test_exp1_run.py:65` | answer query_id mismatch |
| `test_answer_record_mismatched_seed_raises` | `test_exp1_run.py:83` | answer seed mismatch |
| `test_run_experiment_accepts_program_a_adapter_object` | `test_exp1_run.py:191` | runner accepts a `CallableProgramAAdapter` |
| `test_run_experiment_protocol_violation_path` | `test_exp1_run.py:122` | protocol-violation kill |
| `test_run_experiment_mixed_pass_fail_aggregation` | `test_exp1_run.py:137` | seed-level kill aggregation |

These exercise the adapter THROUGH the runner. They do NOT directly cover the
adapter module's own contract surface.

---

## 2. New unit tests - `tests/EXP1/test_program_a_adapter.py`

Direct contract tests for `program_a_adapter.py` (not through the runner).

| # | Test name | Contract area |
|---|---|---|
| U1 | `test_protocol_runtime_checkable_accepts_conforming_class` | `ProgramAAdapter` is `@runtime_checkable`; a class with `adapter_id` + `answer` satisfies `isinstance` |
| U2 | `test_protocol_rejects_non_conforming_object` | a bare `object()` is not a `ProgramAAdapter` |
| U3 | `test_callable_adapter_constructs_with_valid_inputs` | `CallableProgramAAdapter` stores `adapter_id` + `answer_fn` |
| U4 | `test_callable_adapter_rejects_empty_adapter_id` | empty/whitespace id -> `ValueError("adapter_id is required")` |
| U5 | `test_callable_adapter_rejects_non_callable_answer_fn` | non-callable -> `TypeError("answer_fn must be callable")` |
| U6 | `test_callable_adapter_answer_delegates_verbatim` | `answer(query, seed)` calls `answer_fn` with exactly `(query, seed)` and returns its result unchanged (spy) |
| U7 | `test_callable_identity_is_deterministic_for_function` | same function -> identical string; format `module.qualname` |
| U8 | `test_callable_identity_distinguishes_different_functions` | two functions -> different identities |
| U9 | `test_callable_identity_works_for_object` | uses `__class__.__module__` / `__qualname__` for an object |
| U10 | `test_coerce_returns_explicit_adapter_unchanged` | valid `adapter` returned as the same object |
| U11 | `test_coerce_answer_fn_uses_callable_identity_when_no_id` | `answer_fn` + no `adapter_id` -> id = `callable_identity(answer_fn)` |
| U12 | `test_coerce_answer_fn_uses_explicit_id_when_given` | explicit `adapter_id` wins |
| U13 | `test_coerce_rejects_both_adapter_and_answer_fn` | both -> `ValueError("provide either ... not both")` |
| U14 | `test_coerce_rejects_adapter_not_implementing_protocol` | non-Protocol object -> `TypeError("adapter must implement ProgramAAdapter")` |
| U15 | `test_coerce_rejects_adapter_with_empty_id` | Protocol-conforming object with empty id -> `ValueError("adapter_id is required")` |
| U16 | `test_coerce_rejects_both_none` | both None -> `ValueError("Program A adapter or answer_fn is required")` |
| U17 | `test_callable_adapter_passes_through_each_canonical_tier` | UNKNOWN/DEBATED/PROBABLE/CERTAIN flow through `answer()` unchanged |
| U18 | `test_answer_record_rejects_non_canonical_tiers` | INSUFFICIENT/SPECULATIVE/MAYBE/empty -> `ValueError` (guards synthesizer 5-grade leak) |
| U19 | `test_answer_record_from_mapping_uppercases_tier` | `from_mapping` uppercases "certain" -> "CERTAIN" (documents case normalization) |
| U20 | `test_answer_record_from_mapping_rejects_speculative_after_uppercase` | "speculative" -> "SPECULATIVE" -> rejected (non-canonical) |
| U21 | `test_answer_record_from_mapping_accepts_aliases` | `answer`/`answer_i`, `tier`/`tier_i`/`confidence`; `seed`->int; `raw_numeric_confidence`->float; non-dict metadata rejected |
| U22 | `test_answer_propagates_seed_to_fn_and_record` | seed reaches `answer_fn` and is stamped on `AnswerRecord` |
| U23 | `test_answer_is_deterministic_and_side_effect_free` | two calls, same `(query, seed)` -> equal `to_dict()`; query record unchanged |
| U24 | `test_raw_numeric_confidence_and_metadata_preserved` | `raw_numeric_confidence` + `metadata` survive the adapter and `to_dict()` round-trip |

---

## 3. New integration tests - `tests/EXP1/test_program_a_adapter_integration.py`

End-to-end through `run_seed_sync` with a 210-row balanced synthetic corpus
(matching `PLANNED_BALANCED_DATASET_SIZE`). The `answer_fn` is
externally-injected and emits canonical tiers; the adapter only passes them
through. No retriever/synthesizer binding; no tier computation.

| # | Test name | Contract area |
|---|---|---|
| I1 | `test_mapping_return_path_is_coerced_to_answer_record` | `answer_fn` returns a `dict`; `_coerce_answer_record` builds the `AnswerRecord`; `answers.jsonl` records the injected tier |
| I2 | `test_awaitable_return_path_is_awaited_and_coerced` | `async def answer_fn` returns an `AnswerRecord`; `_maybe_await` awaits it; `answers.jsonl` records the injected tier |
| I3 | `test_mapping_uses_answer_i_tier_i_aliases` | `answer_fn` returns a dict with `answer_i`/`tier_i` aliases; coerced correctly |

A passing experiment (H1 pass) is NOT asserted - these tests assert only that
the adapter/coercion plumbing faithfully transports the injected canonical
answer+tier into the recorded `AnswerRecord`s.

---

## 4. Determinism, isolation, and gate

- Unit tests are pure-Python, no I/O, no network, no DB.
- Integration tests write to `tmp_path` only.
- No `VELYNX_TEST_MODE` required.
- Float comparisons use `pytest.approx` where floats arise (tier tests are
  string-based, so this is mostly unused).
- Gate command: `python -m pytest tests/EXP1/ -v`, plus the default project
  gate `python -m pytest tests/ -m "not slow"`.
- Baseline before adding tests: 36 passed in 6.13s (verified this session).

---

## 5. What is NOT tested (out of scope)

- The retriever (`backend/retrieval/unified_retriever.py`) - not bound.
- The synthesizer (`backend/cognition/answer_synthesizer.py`) - not bound.
- Tier computation / mapping / calibration - forbidden by the brief.
- The scientific ECE/decision path - already covered by
  `test_exp1_calibration.py` and `test_exp1_decision.py`; not extended here.
- The frozen 210-row corpus itself - not the subject of this re-scope.

---

## 6. Actual tests as implemented (2026-07-07)

The committed unit suite contains 25 tests. The plan's U18 was split into two
tests after testing revealed that `AnswerRecord.__init__` does not validate
the tier (see PROGRAM_A_ADAPTER_AUDIT.md F-10):

- `test_from_mapping_rejects_non_canonical_synthesizer_grades` (U18a) - the
  non-canonical 5-grade synthesizer taxonomy is rejected at `from_mapping`.
- `test_direct_construction_does_not_validate_tier` (U18b) - documents the
  observed behavior that direct construction bypasses validation.

Final implemented test names:

Unit (`tests/EXP1/test_program_a_adapter.py`, 25 tests):
test_protocol_runtime_checkable_accepts_conforming_class,
test_protocol_rejects_non_conforming_object,
test_callable_adapter_constructs_with_valid_inputs,
test_callable_adapter_rejects_empty_adapter_id,
test_callable_adapter_rejects_non_callable_answer_fn,
test_callable_adapter_answer_delegates_verbatim,
test_callable_identity_is_deterministic_for_function,
test_callable_identity_distinguishes_different_functions,
test_callable_identity_works_for_object,
test_coerce_returns_explicit_adapter_unchanged,
test_coerce_answer_fn_uses_callable_identity_when_no_id,
test_coerce_answer_fn_uses_explicit_id_when_given,
test_coerce_rejects_both_adapter_and_answer_fn,
test_coerce_rejects_adapter_not_implementing_protocol,
test_coerce_rejects_adapter_with_empty_id,
test_coerce_rejects_both_none,
test_callable_adapter_passes_through_each_canonical_tier,
test_from_mapping_rejects_non_canonical_synthesizer_grades,
test_direct_construction_does_not_validate_tier,
test_answer_record_from_mapping_uppercases_tier,
test_answer_record_from_mapping_rejects_speculative_after_uppercase,
test_answer_record_from_mapping_accepts_aliases_and_coerces_types,
test_answer_propagates_seed_to_fn_and_record,
test_answer_is_deterministic_and_side_effect_free,
test_raw_numeric_confidence_and_metadata_preserved.

Integration (`tests/EXP1/test_program_a_adapter_integration.py`, 3 tests):
test_mapping_return_path_is_coerced_to_answer_record,
test_awaitable_return_path_is_awaited_and_coerced,
test_mapping_uses_answer_i_tier_i_aliases.

Final results (this session):
- New unit tests: 25 passed.
- New integration tests: 3 passed.
- Full tests/EXP1/ suite: 64 passed (36 existing + 28 new), 0 failed.
- Project default gate `pytest tests/ -m "not slow"`: 177 passed, 1 skipped,
  1 deselected, 0 failed (3 pre-existing scipy warnings, unrelated).
