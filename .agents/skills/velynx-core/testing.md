# Testing

This document covers the test layout, the categories of tests VELYNX
maintains, and the gates that block a change. The review workflow itself is
in `validation.md`.

## 1. pytest configuration (`pyproject.toml`)

- **testpaths:** `tests`, `validation`, `research/tests`, `experiments`.
- **markers:** `slow` (deselect with `-m "not slow"`), `integration`,
  `smoke`.
- **filterwarnings:** `ignore::DeprecationWarning`.
- **coverage sources:** `core`, `experiments`, `validation`, `benchmarks`;
  `*/tests/*` and `*/__pycache__/*` omitted.

Default gate command (`reproducibility.yaml`):

    pytest tests/ -m "not slow"

Target: 100% pass on the pinned commit.

## 2. Test layout

```
tests/
  unit/           test_core_canonical.py, test_e0_components.py, test_fa_trigger_fix.py
  integration/    test_e0_pipeline.py
  EXP1/           test_exp1_calibration.py, test_exp1_decision.py,
                  test_exp1_readiness.py, test_exp1_run.py
  fixtures/       (package marker; shared fixtures live with the tests that use them)
validation/        runner.py, regression.py, report.py, metrics.py, monitor.py,
                  artifact.py, datasets.py, interfaces.py, shared_metrics_v1.py (+ tests)
research/tests/    test_read_only_nonmutation.py, ...
experiments/       test_calc.py (and per-experiment tests)
backend/tests/     extensive application-layer tests (live-fire harness, ontology,
                  concept_birth, self_model, cognition, ...)
root-level test_*.py   legacy-placed tests, e.g. test_replay_engine_vitals_r3c.py,
                      test_c8_control_upgrade.py, test_c8_decision_policy.py,
                      test_shared_metrics_v1.py, test_decay.py, test_knowledge.py,
                      test_metacog.py, test_probe*.py, test_sleep.py, test_stem.py,
                      test_agency.py, test_velynx_core.py
```

The root-level `test_*.py` files predate the `tests/` reorganization and are
still collected. Prefer the `tests/<unit|integration|EXP1>/` layout for new
tests.

## 3. Unit tests

Unit tests guard primitive contracts with no I/O and no large compute.

- `tests/unit/test_core_canonical.py` - the **canon-exactness** suite (see
  Section 5). Reference: PROGRAM_D_CANONICAL.md Section 5.
- `tests/unit/test_e0_components.py` - E0 component contracts.
- `tests/unit/test_fa_trigger_fix.py` - the F-A MDL trigger dimensional
  fix (see `prediction.md`).
- `research/tests/test_read_only_nonmutation.py` - the **deepcopy safety
  spike** (see Section 6).
- `backend/tests/` - application-layer unit tests (ontology structural
  integrity, concept_birth, self_model, cognition, etc.).

Use `pytest.approx(value, rel=1e-9)` for floating-point comparisons in
canonical math (the canon-exactness suite uses `rel=1e-9`).

## 4. Integration tests

Integration tests run a full pipeline end-to-end on a **minimal** config.

- `tests/integration/test_e0_pipeline.py` - runs the complete E0
  experiment (environment, conditions, analysis, decision) on a minimal
  config (`num_train_steps 200`, `num_test_steps 50`, `num_latent_states 3`,
  `observation_dim 4`). It exercises
  `run_single_seed`, `DEFAULT_CONFIG`, `analyze_conditions`,
  `compute_held_out_log_likelihood`, `compute_emergence_statistic`, and
  `E0Decider`.
- `backend/tests/` includes a live-fire harness for the C8 consolidation
  pipeline (100 rapid consecutive read/write operations across KGs,
  episodic memory, memory-graph, consolidator, and vector backend).

Mark genuinely long integration tests with `@pytest.mark.integration` and
slow ones with `@pytest.mark.slow` so the default gate stays fast.

## 5. Scientific validation tests

`tests/unit/test_core_canonical.py` is the **canon-exactness** suite. It
verifies four things:

1. `lambda_model = k*b + n*log2(N)` is the canonical formula and is
   **non-configurable** (computed, never read from JSON/config).
2. `E[M | H0] approx 0` on shuffled input (the null-referenced emergence
   statistic).
3. The log score matches a reference to `1e-9`.
4. No **banned symbol** (`free_energy`, `belief`, etc.) appears in
   `core/` - a structural guard against reintroducing `[REJECTED]`
   constructs.

`tests/EXP1/` guards the EXP-1 protocol: calibration computation
(`test_exp1_calibration.py`), the decision/kill criteria
(`test_exp1_decision.py`), run orchestration (`test_exp1_run.py`), and
readiness/manifest integrity (`test_exp1_readiness.py` - asserts the
Program A callable adapter has a stable identity and that the execution
manifest rejects a missing adapter identity).

## 6. Determinism tests

Determinism is asserted, not assumed.

- `test_replay_engine_vitals_r3c.py` - the replay identity tests (see
  `replay.md`): online equals replay within `1e-10`; a no-op proposal is
  a fixed point (S and A unchanged); replay never mutates the live
  engine; two replays of the same snapshot produce byte-identical S. The
  protocol demands a halt on identity failure.
- `research/tests/test_read_only_nonmutation.py` - the **deepcopy safety
  spike**: `ReadOnlyEvaluator` scores a probe stream on a `deepcopy` of the
  monitor and leaves the live model **bit-identical** before and after.
  It proves (1) the fingerprint is sensitive (a single direct
  `monitor.tick` mutates it) and (2) read-only evaluation does not mutate
  (the fingerprint is unchanged). Floats are round-tripped via `repr` to
  keep identity exact; an id-keyed memo breaks reference cycles.
- Canonical predictors take an explicit `rng_seed`/`seed` and use
  `numpy.random.RandomState`; `state_dict`/`load_state_dict` make runs
  reproducible.

## 7. Regression tests

`validation/regression.py` defines `RegressionGate` - the enforcement
point for the project's **Freeze Rule**.

- Given baseline and candidate metric scores, the gate decides whether
  the candidate may ship. If any **critical** metric (e.g.
  `PredictionError`, `FalsePositives`) degrades by more than a fixed
  tolerance versus the baseline, the gate fails.
- `assert_no_regression` turns a failure into a hard `AssertionError` so a
  CI step, pre-commit hook, or PR check can block the change.
- **Directionality:** every metric in `validation.metrics` (Entropy,
  Surprise, Active Load, Cognitive Energy, and the error/false-positive
  metrics) is **lower-is-better** by convention; a metric is "degraded"
  when its value goes up. Higher-is-better metrics (accuracy, recall) are
  registered via `higher_is_better` so the gate flips the sign.
- `DEFAULT_TOLERANCE = 0.05` (5%): a critical metric must degrade by
  more than 5% of its baseline before the gate trips.
- `RegressionGate` implements `validation.interfaces.Regression`:
  `is_improvement() -> bool` (ABC); `evaluate() -> RegressionResult` (the
  itemised verdict - which metrics improved, which regressed, plus a
  human-readable summary).

`validation/runner.py` defines `BenchmarkRunner` - the execution harness
that sits between a `Dataset` (tick-by-tick sensory vectors) and a
duck-typed monitor (`tick(vector) -> dict`). It drives the loop and
collects a structured `output_log` (a Python list, not a DB), with
bounded memory (`max_log_size` trims oldest entries), deterministic
replay, and graceful degradation (a `None` monitor or a failed tick is
logged, not raised).

## 8. Review workflow (summary)

The full PASS/FAIL workflow lives in `validation.md`. In short: a change
passes the test gate when `pytest tests/ -m "not slow"` is green on the
pinned commit, the `RegressionGate` reports no critical regression, and
the relevant specialist (Reviewer, ScientificAuditor where the science
path is touched, Documentation) returns PASS.

## 9. Test isolation rules

- Run the suite under `VELYNX_TEST_MODE=1` so every database is
  redirected to `backend/tests/data/_isolated/` and live `.velynx_data/`
  stores are never touched (see `sqlite.md`).
- Inject mutable/duck-typed sources for telemetry and monitors so tests
  do not depend on live subsystem state (see `telemetry.md`,
  `replay.md`).
- Use minimal configs for integration tests (the E0 integration test
  shrinks `num_train_steps` to 200) so the gate stays fast.
- Do not assert on floating equality; use `pytest.approx` with an
  explicit tolerance (`1e-9` for canonical math, `1e-10` for replay
  identity).

## 10. What is not present

- There is no dedicated performance/benchmark test suite in `tests/`;
  `benchmark.py` and `benchmarks/` are run separately
  (`reproducibility.yaml`: `python benchmark.py`).
- There is no snapshot-test or golden-file framework for scientific
  outputs; reproducibility is enforced via pinned commits, seeds, and
  the regression gate, not frozen output files.
- `tests/fixtures/` currently holds only the package marker; there is no
  shared fixture library. Add fixtures next to the tests that use them.