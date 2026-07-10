# Architecture

This document describes the VELYNX repository layout, module ownership,
dependency boundaries, and the rules that govern extension. It is the map;
subsystem detail lives in the companion documents. Nothing here is invented -
where a component does not exist as live code, that is stated.

## 1. Repository layout

Top-level directories that carry engineering meaning:

```
VELYNX/
  core/            canonical scientific primitives (research core)
    controls/        fixed_capacity.py, random_growth.py, shuffled_input.py
    emergence/       emergence_statistic.py, null_referenced_test.py
    mdl/             mdl_growth.py
    measurement/     metrics.py, proper_scoring.py
    predictors/       base.py, dirichlet_markov.py
  experiments/     experiment framework
    EXP0/            implemented (preregistration, protocol, run, analysis)
    EXP1/            implemented (calibration gate, H1)
    E0/              implemented (emergence-vs-injection, H*)
    EXP2/ EXP3/ EXP4/ R1/ R3F/   stubs (planned / archived / rejected)
    runner.py metrics.py calculator.py artifacts.py
  validation/      validation framework + regression gate
    runner.py regression.py report.py metrics.py monitor.py
    artifact.py datasets.py interfaces.py shared_metrics_v1.py
  research/         side-effect-free study harness over the backend ReplayEngine
    policies/ runner/ metrics/ stats/ artifacts/ report/ proposals/
  backend/         application/product layer (the second core)
    cognition/  memory/  knowledge/  self_model/  simulation/
    orchestration/  agency/  abstraction/  evaluation/  ops/
    app/  database/  soul/  tools/  pipeline/  models/  nlp/  ...
  tests/           unit/ integration/ EXP1/ fixtures/
  velynx_core/     empty legacy (migrated to core/)
  src/             TypeScript entry (index.ts only)
  configs/ infra/  runtime + reproducibility configuration
  benchmarks/ scripts/ docs/ artifacts/ evidence/ reviews/ literature/
```

## 2. The two cores and the build boundary

VELYNX has a **dual-core** structure (recorded in `repository_v2.md` and
`reduction/program_d_migration_plan.md`):

- **`core/`** - the canonical scientific core. Its `__init__.py` declares it
  the "Single source of truth for all reusable scientific machinery". It is
  minimal: five subpackages implementing the five canonical primitives of
  PROGRAM_D_CANONICAL.md Section 5 (`x_t`, `P_theta`, `L`, `G`, `M`).
- **`backend/`** - the application/product layer. Large, self-contained, and
  explicitly "engineering, not the research center" (canon Section 2). It
  contains the Replay Engine, Ontology, Identity, Telemetry, and SQLite
  persistence subsystems. The canon marks several of these `[REJECTED]` as
  load-bearing *science*; they remain as *engineering* for the Program A
  product.
- **`velynx_core/`** - empty legacy package. The migration unified its
  contents into `core/`. Do not add code here.

The build (`pyproject.toml`) makes the boundary explicit. The setuptools
`packages.find` includes only `core*`, `experiments*`, `validation*`,
`benchmarks*`, `scripts*` and excludes `archive*`, `backend*`, `data*`,
`docs*`. The distributable wheel therefore contains the scientific packages
only; `backend/` is not shipped.

## 3. Module ownership

| Owner (agent)        | Owns                                                                 | Does not own                          |
|----------------------|----------------------------------------------------------------------|---------------------------------------|
| Architect            | `core/` APIs, module boundaries, dependency graph                     | implementation                        |
| Builder              | `core/`, `experiments/`, `validation/`, `research/`, `backend/` code | scientific parameters                 |
| ExperimentEngineer   | `experiments/` execution, manifests, datasets, reports               | hypotheses                             |
| ScientificAuditor    | preregistrations, statistics, calibration, reproducibility           | production code                       |
| Debugger             | telemetry, replay, profiling, SQLite debugging                       | architecture redesign                 |
| Reviewer             | determinism, maintainability, edge cases, security                   | scientific verdicts                   |
| Documentation        | README, architecture docs, API docs                                   | scientific conclusions                 |
| ReleaseManager       | releases, manifests, changelogs, tags, reproducibility reports        | production code                        |

## 4. Dependency boundaries

The dependency direction is layered and one-way. Violations are defects.

```
                    core/   (foundation, no VELYNX-internal deps)
                      ^
                      |
          experiments/  validation/  research/   (depend on core/)
                      ^
                      |
                  backend/   (application; may import core/ for shared math,
                             but core/ never imports backend/)
```

Evidence for the direction:

- `core/predictors/dirichlet_markov.py` imports only
  `core.predictors.base` and third-party `numpy`. `core/` has no upward
  dependencies.
- `core/measurement/proper_scoring.py` is documented as "Extracted from
  `backend/cognition/decision_policy.py`" - the canonical primitive was
  pulled *out* of backend into `core/`. `core/` is now the source; backend
  must not re-assume that role for scientific scoring.
- `core/measurement/metrics.py` is documented as the consolidation of
  `validation/metrics.py`, `validation/shared_metrics_v1.py`, and
  `research/metrics.py`. `core/` is the single source; the others are
  mirrors.
- `research/__init__.py` states it "composes" the backend components
  (DecisionPolicy, ReplayEngine, CandidateGenerator,
  VectorPredictionCore, the `validation` harness, `benchmark.py") behind
  research abstractions and does *not* mutate or monkeypatch them.

Boundary rules:

1. `core/` imports nothing from `experiments/`, `validation/`, `research/`,
   or `backend/`. It depends only on the standard library and `numpy`.
2. `experiments/`, `validation/`, and `research/` may import `core/` and
   third-party packages. They must not import `backend/` production
   machinery except through the documented `research/` composition layer.
3. `backend/` is self-contained and may import `core/` for shared scientific
   math. `backend/memory/_sqlite.py` is the single shared SQLite connection
   helper across all `backend/` subsystems.
4. No circular imports. `reviews/program_d_circular_dependencies.md`
   records prior circular chains as known debt to eliminate, not patterns
   to copy.

## 5. Major subsystems

Brief pointers; full detail is in the companion documents.

- **Predictive processing** (`prediction.md`) - `core/predictors` (Predictor
  ABC + DirichletMarkovPredictor), `core/measurement` (proper scoring, ECE),
  `core/mdl` (MDL growth operator). This is the canonical science.
- **Replay engine** (`replay.md`) - `backend/cognition/replay_engine.py`,
  `decision_policy.py`, `consolidation_tracker.py`; studied through
  `research/policies` and `research/runner`.
- **Ontology** (`ontology.md`) - `backend/knowledge/ontology_loader.py`,
  `schema_gatekeeper.py`, `world_model_schema.py`, data file
  `backend/data/world_ontology.json`.
- **Identity** (`identity.md`) - `backend/self_model/identity_store.py`,
  `baseline_tracker.py`, `health_monitor.py`, `self_model.py`.
- **Telemetry** (`telemetry.md`) - `backend/simulation/logger.py`,
  `backend/memory/recall_logger.py`, `backend/cognition/memory_scheduler.py`,
  `backend/orchestration/cognitive_loop.py`, `backend/ops/`.
- **SQLite persistence** (`sqlite.md`) - `backend/memory/_sqlite.py` and the
  database inventory it governs.
- **Experiments** (`experiments.md`) - `experiments/EXP0`, `EXP1`, `E0`
  (implemented) plus stubs.
- **Validation** (`validation.md`) - the review workflow and
  `validation/regression.py` gate.

## 6. Architectural rules

From PROGRAM_D_CANONICAL.md (binding):

1. **Priority order under trade-off:** scientific correctness > experiment
   reproducibility > code simplicity > performance > features.
2. **No new hypotheses.** Only refine, test, or falsify inherited ones.
3. **No subsystem without a pre-registered experiment that requires it.**
   If nothing in {EXP-0, EXP-1, EXP-2, E0} needs it, it is not built.
4. **Five primitives only.** The mathematical substrate is
   `{ x_t, P_theta over Theta_k, L, G, M }` and nothing else. Do not add a
   sixth.
5. **Epistemic tags are binding.** Every scientific claim is tagged
   `[FACT]`, `[HYPOTHESIS]`, `[SPECULATION]`, or `[REJECTED]`. `[SPECULATION]`
   is prohibited in any load-bearing mechanism. `[REJECTED]` mechanisms must
   not appear in live code.
6. **Permanently removed** (may appear only as archive/delete targets):
   `E = lambda*H + mu*S + nu*A` and its coefficients; CPI and its
   0.40/0.30/0.20/0.10 weights; the Inertia Law; the fracture-ratio 0.85
   trigger; energy-exhaustion 18.0; contradiction-margin 0.9 decay; the 32
   soul concepts; the hand-authored ontology; the self-model; the reasoning
   engine's type-lifting; "resonance / sleep-replay / thermodynamic state".

Engineering invariants (from the code):

7. **Determinism first.** Every randomized path takes an explicit seed
   (`rng_seed` / `seed`) and uses `numpy.random.RandomState` or
   `random.Random`. The default benchmark seed is 42
   (`reproducibility.yaml`).
8. **Telemetry is non-blocking.** A telemetry fault must never crash or
   perturb the system it observes (see `telemetry.md`).
9. **SQLite access is centralized.** All `backend/` SQLite connections go
   through `backend/memory/_sqlite.py` so WAL/busy_timeout/synchronous
   PRAGMAs are consistent (see `sqlite.md`).
10. **Tests are isolated.** `VELYNX_TEST_MODE=1` redirects every database
    into `backend/tests/data/_isolated/` so the suite never touches live
    data (see `sqlite.md`, `testing.md`).

## 7. Extension points

Where new code may be added without architectural review, and where it may
not:

- **New predictor.** Implement `core/predictors/base.py::Predictor` (the
  ABC). Add the class under `core/predictors/`. Do not change the ABC without
  Architect approval.
- **New experiment.** Requires (a) a preregistration document, (b) an entry
  in `experiment_registry.yaml`, (c) a frozen parameter block in
  `parameter_registry.yaml`, and (d) ScientificAuditor sign-off. See
  `experiments.md`.
- **New consolidation policy (research only).** Add a class under
  `research/policies/` implementing the `ConsolidationPolicy` family
  (Null/Random/FIFOAge/Similarity/Utility/FreeEnergy/Oracle). Research code
  must not mutate the production components it wraps.
- **Ontology extension.** Extend `backend/data/world_ontology.json` (data,
  not code). The loader is generic over the JSON. Do not add a hand-authored
  soul-graph ontology - that construct is `[REJECTED]` (see `ontology.md`).
- **New metric.** Add to `core/measurement/`. If it duplicates logic in
  `validation/metrics.py`, `validation/shared_metrics_v1.py`, or
  `research/metrics.py`, those become mirrors and `core/` remains the source
  of truth.
- **Not an extension point.** Scientific constants, thresholds, tier
  mappings, calibration bins, and statistical tests. These are frozen (see
  `experiments.md`).

## 8. What is not present

To avoid fabrication, the following are explicitly absent or empty:

- `velynx_core/` - empty (legacy).
- `experiments/EXP2/`, `experiments/EXP3/`, `experiments/EXP4/`,
  `experiments/R1/`, `experiments/R3F/` - empty stubs. EXP1/EXP2 are
  "planned", R1/R3F are "archived", EXP3/EXP4 are `[REJECTED]`
  (`experiment_registry.yaml`).
- There is no standalone "Ontology Engine" or "Identity Engine" package in
  `core/`. Ontology and Identity live only in `backend/` as application
  subsystems.
- There is no separate "Predictive Processing" package by that name; the
  canonical predictive-processing machinery is `core/predictors` plus
  `core/measurement` and `core/mdl`.