# Coding

Conventions for code contributed to VELYNX. These are derived from
`pyproject.toml`, the existing `core/` and `backend/` modules, and
PROGRAM_D_CANONICAL.md. When this document and the canon disagree on a
scientific matter, the canon wins.

## 1. Language and tooling

- **Python >= 3.11** (`pyproject.toml`, `reproducibility.yaml`). Standard
  library first; `numpy` is the only core numerical dependency.
- **Formatting:** `black`, line-length 100, target `py311`.
- **Lint:** `flake8`, max-line-length 100, `extend-ignore = ["E203", "W503"]`.
- **Tests:** `pytest`. Configured `testpaths` are `tests`, `validation`,
  `research/tests`, `experiments`. Markers: `slow`, `integration`, `smoke`
  (see `testing.md`).
- **Coverage:** `tool.coverage.run` sources are `core`, `experiments`,
  `validation`, `benchmarks`; `*/tests/*` and `*/__pycache__/*` are omitted.
- **TypeScript** lives only in `src/index.ts` and the `frontend/` tree; it is
  not part of the scientific build.

## 2. File and module conventions

- Start every module with a docstring stating its role and, where relevant,
  the canonical section it implements. Example from
  `core/predictors/dirichlet_markov.py`: "Reference: PROGRAM_D_CANONICAL.md
  Section 5.2".
- Use `from __future__ import annotations` at the top of modules that use
  forward references or PEP 604 unions in 3.11-compatible form.
- Prefer absolute package imports (`from core.predictors.base import
  Predictor`), matching the `backend/memory/_sqlite.py` import style noted
  across `backend/tests/`.
- Public package APIs are declared in `__all__` (see `research/__init__.py`).
- Module-level constants are `UPPER_CASE` and documented as either tunable
  hyperparameters or scientific constants (see Section 7).

## 3. Naming

- **Classes:** `PascalCase` (`DirichletMarkovPredictor`,
  `FixedCapacityControl`, `IdentityStore`, `ReplayEngine`).
- **Functions and methods:** `snake_case` (`log_predictive_probability`,
  `should_grow`, `compute_lambda_model_corrected`).
- **Constants:** `UPPER_CASE` (`BITS_PER_PARAMETER`, `LAMBDA`, `MU`, `NU`,
  `ENERGY_EXHAUSTION`, `BUSY_TIMEOUT_MS`, `DEFAULT_TIMEOUT_S`).
- **Private helpers:** leading underscore (`_transition_matrix`,
  `_infer_state`, `_safe_pct`, `_safe_mean`, `_pragma_statements`).
- **Properties** for read-only attributes (`capacity`, `n_observations`,
  `current_state`, `replay_efficiency`, `fill`, `size`).
- **Type aliases** for repeated shapes: `Vector = Sequence[float]`
  (`core/measurement/metrics.py`).

## 4. Typing

- Type-hint all public functions. Use the `typing` module forms already in
  use: `List`, `Optional`, `Tuple`, `Sequence`, `Mapping`, `Dict`, `Any`.
  Match the style of the surrounding module rather than mixing styles.
- Abstract interfaces use `abc.ABC` and `@abstractmethod`. The canonical
  example is `core/predictors/base.py::Predictor` with
  `predict`, `update`, `entropy`, `reset`, `state_dict`, `load_state_dict`.
- Numerical code uses `numpy` (`np.random.RandomState(seed)`). Seed every
  randomized path explicitly; never call unseeded global RNG in code that
  must be reproducible.

## 5. Error handling

- Validate arguments at construction with explicit `ValueError` and a clear
  message. Examples: `initial_capacity must be >= 1`, `alpha must be > 0`,
  `k must be >= 1`, `N must be >= 1`, `b must be > 0`.
- Numerical stability: clamp probabilities with `eps = 1e-15` before taking
  logs (`max(min(p, 1.0 - eps), eps)`, `math.log(max(p, 1e-15))`). Never take
  `log(0)`.
- Defensive division: use `_safe_mean`/`_safe_pct`-style helpers that return
  a defined value (often `0.0`) when the denominator is zero.
- I/O and PRAGMA-style side effects are best-effort: wrap in `try/except`
  and log, never crash the caller. Example: `_sqlite.py` ignores PRAGMA
  failures and `verify_wal` warns rather than raising.
- Copy mutable state on export/restore (`[list(row) for row in ...]`) to
  prevent aliasing across `state_dict`/`load_state_dict`.

## 6. Logging

- Use the standard `logging` module with a `velynx.<subsystem>` logger name:
  `logging.getLogger("velynx.sqlite")`, `logging.getLogger("velynx.ontology_loader")`.
- Log warnings for recoverable degradation (e.g. WAL fallback, missing
  ontology file degrading to "no world model").
- Telemetry and logging paths that observe a live system must be
  non-blocking and fault-tolerant (see `telemetry.md`). A logging fault must
  never perturb the system it records.

## 7. Scientific constants vs hyperparameters

Distinguish these two categories sharply in code and comments:

- **Scientific constants** are derived, not chosen, and are not tunable.
  `BITS_PER_PARAMETER = 1.0` in `core/mdl/mdl_growth.py` is documented as "a
  scientific constant, not a tunable hyperparameter". `lambda_model` is
  derived (`k*b + n*log2(N)`); there is no knob. Do not parameterize them.
- **Hyperparameters** belong in experiment configs (e.g.
  `experiments/E0/config.json`) and are recorded in
  `parameter_registry.yaml` with value, location, and role.
- Tag any constant whose value is load-bearing for a hypothesis. Changing
  one requires ScientificAuditor approval (see `validation.md`).

## 8. Testing expectations

- New `core/` primitives ship with unit tests under `tests/unit/`. Match the
  existing pattern (`test_core_canonical.py`, `test_e0_components.py`,
  `test_fa_trigger_fix.py`).
- Determinism tests assert that replay/online paths produce identical state
  and that no-op proposals leave state unchanged (see the identity tests in
  `test_replay_engine_vitals_r3c.py` and `testing.md`).
- Tests must run under `VELYNX_TEST_MODE=1` without touching live data (see
  `sqlite.md`).
- Prefer `pytest -m "not slow"` for the default gate; mark genuinely slow
  tests with `@pytest.mark.slow`.
- The regression gate is `validation/regression.py`; the suite target is
  100% pass on the pinned commit (`reproducibility.yaml`).

## 9. Refactoring rules

- `core/` is the consolidation target. `core/measurement/metrics.py`
  documents that it "Consolidates from `validation/metrics.py`,
  `validation/shared_metrics_v1.py`, and `research/metrics.py`". When
  consolidating, `core/` becomes the source and the others become mirrors.
- Move files with `git mv` so `git log --follow` preserves history
  (`reproducibility.yaml`: "All code moves use git mv").
- Consult the reduction plans before deleting:
  `reduction/program_d_migration_plan.md`,
  `reduction/program_d_reduction_plan.md`,
  `reduction/program_c_safe_removal_order.md`. Follow the safe removal order
  for subsystem deletions.
- Never reintroduce a `[REJECTED]` construct (Section 10). The dead-code,
  duplication, and hidden-coupling reports under `reviews/` identify
  removal targets, not patterns to copy.
- Preserve backward-compatible shims only when explicitly marked as such
  (e.g. the "Legacy description length" and `compute_lambda_model` shims in
  `core/mdl/mdl_growth.py`), and document them as deprecated.

## 10. Performance guidelines

- SQLite connections use WAL + `synchronous=NORMAL` + `busy_timeout=20000`
  via `backend/memory/_sqlite.py` to reduce lock contention
  (see `sqlite.md`). Do not open raw `sqlite3.connect` calls in `backend/`;
  route through the helper.
- Vectorize numerical work with `numpy` where the surrounding code does.
- The cognitive core runs on CPU; GPU is optional and confined to
  specialist scripts (`reproducibility.yaml`).
- Trade performance for scientific correctness or reproducibility whenever
  the two conflict (canon priority order).

## 11. Forbidden modifications

Without explicit instruction and ScientificAuditor approval, do **not**:

- Modify `PROGRAM_D_CANONICAL.md`, `EXP1_PREREGISTRATION.md`,
  `HYPOTHESIS_REGISTER.md`, `experiments/EXP0/EXP0_PREREGISTRATION.md`,
  `F_A_TRIGGER_FIX_PREREGISTRATION.md`, `SPRINT_1.3_PREREGISTRATION.md`.
- Change experiment thresholds, calibration bins, tier mappings, statistical
  tests, or scientific constants (see `experiments.md`).
- Reintroduce any `[REJECTED]` construct: `E = lambda*H + mu*S + nu*A` and its
  coefficients; CPI and its 0.40/0.30/0.20/0.10 weights; the Inertia Law; the
  fracture-ratio 0.85 trigger; energy-exhaustion 18.0; contradiction-margin
  0.9 decay; the 32 soul concepts; the hand-authored ontology; the self-model
  as a load-bearing mechanism; the reasoning engine's type-lifting;
  "resonance / sleep-replay / thermodynamic state".
- Add a sixth mathematical primitive. The substrate is
  `{ x_t, P_theta, L, G, M }` (canon Section 5).
- Make `core/` import from `experiments/`, `validation/`, `research/`, or
  `backend/`. The dependency direction is one-way (see `architecture.md`).
- Mark a `[SPECULATION]` claim as load-bearing, or use a `[REJECTED]`
  mechanism in live code.
- Bypass the review workflow (see `validation.md`).

## 12. Repository conventions

- Scientific documents use the epistemic tags `[FACT]`, `[HYPOTHESIS]`,
  `[SPECULATION]`, `[REJECTED]` (canon Section 0). Code comments may quote
  these tags when justifying a decision.
- Reference canonical sections by number: "PROGRAM_D_CANONICAL.md Section 5.4".
- Self-check modules may provide a `python -m <module>` entry point (see
  `backend/knowledge/ontology_loader.py`'s self-check). Keep such checks
  side-effect-free.
- Database files (`*.db`, `*.db-shm`, `*.db-wal`) are git-ignored and not in
  VCS (`reproducibility.yaml`). Never commit a database.
- Environment variables used in code: `VELYNX_DATA_DIR` (data root
  override), `VELYNX_TEST_MODE` (test isolation), `VELYNX_ONTOLOGY_PATH`
  (ontology file override), `BENCHMARK_SEED` (default 42), `LOG_LEVEL`.