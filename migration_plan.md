# VELYNX Repository v2 — Migration Plan

**Rule:** Do NOT move files in this plan. This is a logical migration blueprint. Physical moves happen in a separate execution phase.

**Principle:** Every migration step is reversable. Never delete — always archive. Execute in dependency order: documentation first (foundation can be written without touching code), then core, then infra, then programs, then experiments.

---

## Phase 0: Create Directories

Create the empty target directories (no files moved yet).

```
foundation/hypothesis/
foundation/assumptions/
foundation/kill_criteria/
foundation/mathematics/
foundation/architecture/
foundation/novelty/

core/predictors/
core/emergence/
core/mdl/
core/measurement/
core/controls/

experiments/E0/
experiments/R1/
experiments/R3F/
experiments/EXP1/
experiments/EXP2/
experiments/EXP3/
experiments/EXP4/
experiments/coverage/

benchmarks/evaluation/
benchmarks/cognition/
benchmarks/reflection/
benchmarks/monitoring/
benchmarks/hallucination/
benchmarks/failure/

program_a/retrieval/
program_a/nlp/

program_b/soul_graph/
program_b/concepts/

program_c/cognition/
program_c/memory/
program_c/learning/
program_c/knowledge/
program_c/metacognition/
program_c/reflection/
program_c/pipeline/
program_c/abstraction/
program_c/self_model/
program_c/simulation/
program_c/agency/
program_c/conversation/
program_c/models/

infra/app/
infra/app/soul/
infra/database/
infra/database/alembic/versions/
infra/runtime/
infra/ops/
infra/constitution/
infra/config/
infra/data/
infra/frontend/

docs/research/
docs/architecture/
docs/audits/
docs/requirements/
docs/reviews/
docs/literature/
docs/plans/

archive/code/
archive/experiments/
archive/documents/
archive/data/

artifacts/benchmarks/
artifacts/experiments/
artifacts/output/

tests/unit/
tests/integration/
tests/fixtures/
```

---

## Phase 1: Foundation (Documentation Only — No Code Moves)

Write new documents in `foundation/`. These are distilled from existing documents, not moved.

| New file | Source material |
|----------|----------------|
| `foundation/hypothesis/central_hypothesis.md` | Synthesized from `PROGRAM_D_RESEARCH_STATE_v0.1.md` §6 and `program_d_scientific_foundation_v0.1.md` Phase 1 |
| `foundation/hypothesis/H1_calibration.md` | Extracted from `VELYNX_v2_PI_Review.md` Phase 5 H1 |
| `foundation/hypothesis/H2_affective_indexing.md` | Extracted from `VELYNX_v2_PI_Review.md` Phase 5 H2 |
| `foundation/hypothesis/H3_emergent_development.md` | Extracted from `VELYNX_v2_PI_Review.md` Phase 5 H3 |
| `foundation/assumptions/assumption_ledger.md` | Reduced from `research/program_c_assumption_ledger.md` — keep only I1/I2/I3 |
| `foundation/assumptions/assumption_coverage_matrix.csv` | Simplified from `assumptions/program_d_assumption_coverage_matrix.csv` |
| `foundation/assumptions/parameter_atlas.md` | Relocated from `assumptions/program_d_parameter_atlas.md` |
| `foundation/kill_criteria/kill_criteria.md` | Rewritten from `foundation/kill_criteria_validation.md` with all criteria wired |
| `foundation/kill_criteria/kill_criteria_validation_report.md` | Relocated from `foundation/kill_criteria_validation.md` |
| `foundation/mathematics/mathematical_foundation.md` | Distilled from `program_d_scientific_foundation_v0.1.md` Phase 3 |
| `foundation/mathematics/variable_provenance.md` | Relocated from `research/program_c_variable_provenance.md` |
| `foundation/mathematics/variable_dependency_graph.graphml` | Relocated from `research/program_c_variable_dependency_graph.md` (or generated from code) |
| `foundation/mathematics/variable_dependency_matrix.csv` | New (extracted from provenance) |
| `foundation/architecture/architecture.md` | Relocated from `docs/ARCHITECTURE.md` |
| `foundation/architecture/dependency_graph.graphml` | Relocated from `dependency_graphs/program_d_dependency_graph.graphml` |
| `foundation/architecture/dependency_matrix.csv` | Relocated from `dependency_graphs/program_d_dependency_matrix.csv` |
| `foundation/architecture/layer_diagram.mmd` | Relocated from `dependency_graphs/program_d_diagram.mmd` |
| `foundation/novelty/novelty_analysis.md` | Distilled from `program_d_scientific_foundation_v0.1.md` Phase 4 |
| `foundation/novelty/publication_test.md` | Distilled from `program_d_scientific_foundation_v0.1.md` Phase 7 |

**After Phase 1:** Documents in `foundation/` are authoritative. Old locations are symlinked or archived. The following old paths are deprecated:

- `foundation/kill_criteria_validation.md` → archived
- `assumptions/` entire directory → archived
- `dependency_graphs/` entire directory → archived
- `research/program_c_*` → archived (contents moved to foundation)

---

## Phase 2: Core (Extract Reusable Scientific Machinery)

Identify all code that implements the five primitives (log-loss, MDL growth, Dirichlet–Markov predictor, emergence statistics, null controls). These exist today buried inside `backend/` and `research/`. Extract copies into `core/` — the canonical source. Old code is refactored to import from `core/`.

| Target | Source(s) | Action |
|--------|-----------|--------|
| `core/predictors/dirichlet_markov.py` | `backend/cognition/predictive_core.py`, `backend/cognition/vector_prediction_core.py` | Extract Dirichlet–Markov conjugate prior predictor |
| `core/predictors/base.py` | New | Define predictor interface |
| `core/emergence/emergence_statistic.py` | `validation/metrics.py` (NMI), `research/attribution/metrics.py` | Extract NMI estimator, held-out LL |
| `core/emergence/null_referenced_test.py` | New | Null-referenced construction: `M(θ_k) - E[M \| H₀]` |
| `core/mdl/mdl_growth.py` | `backend/cognition/concept_birth.py` | Extract MDL description-length calculation |
| `core/mdl/concept_birth_ledger.py` | `backend/cognition/concept_birth.py` | Extract concept-birth ledger (G = H_before − H_after − λ_model) |
| `core/measurement/proper_scoring.py` | `backend/cognition/decision_policy.py` (log-loss component) | Extract log-loss scorer |
| `core/measurement/metrics.py` | `validation/metrics.py`, `validation/shared_metrics_v1.py` | Consolidate to single source |
| `core/measurement/observability.py` | New | Instrumentation for currently-unmeasurable metrics |
| `core/controls/fixed_capacity.py` | `research/policies/null.py` | Extract fixed-capacity control |
| `core/controls/random_growth.py` | `research/policies/random_policy.py` | Extract capacity-matched random-growth control |
| `core/controls/shuffled_input.py` | New | Shuffle input marginals while preserving temporal structure |

**After Phase 2:** `core/` is the single source of truth for all scientific primitives. Old implementations in `backend/` and `research/` are changed to:

```python
# Old code becomes a thin wrapper:
from core.predictors import DirichletMarkovPredictor
from core.measurement import log_loss
from core.mdl import mdl_growth_trigger
```

No duplicated logic — if two modules need the same predictor, they both import from `core/`.

---

## Phase 3: Infrastructure (Separate Operations from Science)

Move operational code into `infra/`. This is a pure engineering reorganization — no scientific content.

| Source → Target | Reason |
|----------------|--------|
| `backend/app/` → `infra/app/` | FastAPI entry point, routes, middleware — pure infrastructure |
| `backend/database/` → `infra/database/` | DB engine, models, migrations |
| `backend/runtime/` → `infra/runtime/` | Event bus, monitoring, tracing |
| `backend/ops/` → `infra/ops/` | Circuit breakers, health, load shedding, supervisor |
| `backend/constitution/` → `infra/constitution/` | Constitution markdown documents |
| `configs/` → `infra/config/` | JSON configuration files |
| `backend/velynx_data/` → `infra/data/` | Runtime data (bind-mounted or generated) |
| `data/` → `infra/data/` | Runtime databases, JSON state, vector indices |
| `frontend/` → `infra/frontend/` | Vite/JS UI |

**Update import paths:** All `backend.app.*` → `infra.app.*`, `backend.database.*` → `infra.database.*`, etc.

---

## Phase 4: Program A, B, C (Separate Concerns)

Code currently lives in `backend/` in a flat structure mixing product, research, and operations. Split into three programs plus the non-program `program_c/` engineering-retained stack.

### Program A — Retrieval

| Source → Target | Reason |
|----------------|--------|
| `backend/retrieval/` → `program_a/retrieval/` | Retrieval clients are Program A's core |
| `backend/nlp/temporal_parser.py` → `program_a/nlp/` | NLP utility for retrieval |
| `backend/models/llm_client.py` → `program_a/retrieval/` (or kept in models) | LLM client used by retrieval |

### Program B — Soul Graph

| Source → Target | Reason |
|----------------|--------|
| `backend/soul/soul_graph.py` → `program_b/soul_graph/` | Soul graph implementation |
| `backend/app/soul/soul_store.py` → `program_b/soul_graph/` | Soul store (authored concepts persist) |
| `backend/soul/concepts.json` → `program_b/concepts/` | Authored concept definitions |

### Program C — Engineering-Retained Stack

Every subdirectory under `backend/` that is not already moved to `program_a/`, `program_b/`, `infra/`, `benchmarks/`, or `core/` goes to `program_c/`:

| Source → Target |
|----------------|
| `backend/cognition/` → `program_c/cognition/` |
| `backend/memory/` → `program_c/memory/` |
| `backend/learning/` → `program_c/learning/` |
| `backend/knowledge/` → `program_c/knowledge/` |
| `backend/metacognition/` → `program_c/metacognition/` |
| `backend/reflection/` → `program_c/reflection/` |
| `backend/pipeline/` → `program_c/pipeline/` |
| `backend/abstraction/` → `program_c/abstraction/` |
| `backend/self_model/` → `program_c/self_model/` |
| `backend/simulation/` → `program_c/simulation/` |
| `backend/agency/` → `program_c/agency/` |
| `backend/conversation/` → `program_c/conversation/` |
| `backend/models/` (remaining) → `program_c/models/` |
| `backend/cli.py`, `backend/cli_ui.py` → `program_c/` (CLI for cognitive stack) |
| `backend/brain.py` → `program_c/` (orchestrator) |

**No code changes** — pure file moves plus import path updates.

---

## Phase 5: Benchmarks (Consolidate Evaluation)

Currently evaluation code is scattered across `backend/evaluation/`, `validation/`, and `research/evaluation/`. Consolidate into `benchmarks/`.

| Source → Target | Reason |
|----------------|--------|
| `backend/evaluation/` → `benchmarks/evaluation/` (benchmark_runner, scenario_loader, trial_runner, adversarial_tests) | Evaluation harness |
| `backend/evaluation/cognition_benchmarks.py` → `benchmarks/cognition/` | Cognition benchmarks |
| `backend/evaluation/cognition_drift_monitor.py` → `benchmarks/cognition/` | Drift monitoring |
| `backend/evaluation/memory_retrieval_tests.py` → `benchmarks/cognition/` | Memory tests |
| `backend/evaluation/planning_evaluator.py` → `benchmarks/cognition/` | Planning eval |
| `backend/evaluation/reflection_evaluator.py` → `benchmarks/reflection/` | Reflection eval |
| `backend/evaluation/reality_checks.py` → `benchmarks/reflection/` | Reality checks |
| `backend/evaluation/runtime_profiler.py` → `benchmarks/monitoring/` | Profiler |
| `backend/evaluation/stability_monitor.py` → `benchmarks/monitoring/` | Stability |
| `backend/evaluation/session_replay.py` → `benchmarks/monitoring/` | Session replay |
| `backend/evaluation/hallucination_detector.py` → `benchmarks/hallucination/` | Hallucination |
| `backend/evaluation/failure_analysis.py` → `benchmarks/failure/` | Failure analysis |
| `validation/interfaces.py` → `benchmarks/evaluation/` | Benchmark interfaces |
| `validation/runner.py` → `benchmarks/evaluation/` | Benchmark runner |
| `validation/report.py` → `benchmarks/evaluation/` | Report generation |
| `validation/regression.py` → `benchmarks/monitoring/` | Regression detection |
| `validation/monitor.py` → `benchmarks/monitoring/` | Monitoring |
| `validation/metrics.py` → `benchmarks/evaluation/` (or `core/measurement/`) | Metrics |
| `validation/datasets.py` → `benchmarks/evaluation/` | Dataset loaders |
| `validation/artifact.py` → `benchmarks/evaluation/` | Artifact tracking |
| `research/evaluation/` → `benchmarks/evaluation/` | Protocol, split, read-only checks |

---

## Phase 6: Experiments (Self-Contained Directories)

Each experiment is already self-contained (`experiments/EXP0/`). Keep that pattern.

| Source → Target | Reason |
|----------------|--------|
| `experiments/EXP0/` → `experiments/E0/` | Rename to E0 (matches foundation naming) |
| `research/experiments/R3F1_preregistration.md` → `experiments/R3F/` | R3F benchmark |
| `backend/evaluation/benchmark_runner.py` → `experiments/R1/` (copied reference) or kept in `benchmarks/` | Shared by all experiments |
| `research/policies/` → `core/controls/` | These ARE the controls, not experiments |
| `research/runner.py` → `experiments/` (shared runner) or `benchmarks/` | Shared experiment runner |

New experiments are created as:
- `experiments/E0/run.py` — already exists as `experiments/EXP0/run_exp0.py`
- `experiments/E0/analysis.py` — already exists as `experiments/EXP0/analysis.py`
- `experiments/E0/preregistration.md` — already exists as `experiments/EXP0/EXP0_PREREGISTRATION.md`

---

## Phase 7: Documentation (Consolidate)

| Source → Target | Reason |
|----------------|--------|
| `PROGRAM_D_RESEARCH_STATE_v0.1.md` → `docs/research/` | Master research state document |
| `docs/VELYNX_v2_PI_Review.md` → `docs/research/` | PI Review |
| `docs/ARCHITECTURE.md` → `docs/architecture/` | Architecture doc |
| `docs/phase57_agentic_loop_architecture.md` → `docs/architecture/` | Phase architecture |
| `docs/phase60_self_model_architecture.md` → `docs/architecture/` | Phase architecture |
| `docs/VELYNX_AUDIT_2026-06-01.md` → `docs/audits/` | Audit report |
| `docs/requirements.md` → `docs/requirements/` | Requirements |
| `docs/requirements_raw.txt` → `docs/requirements/` | Raw requirements |
| `reviews/` → `docs/reviews/` | Code health reviews |
| `literature/program_d_mathematical_provenance.md` → `docs/literature/` | Literature |
| `reduction/` → `docs/plans/` | Migration/reduction plans |
| `archive/program_c_archive_manifest.md` → `docs/plans/` | Archive manifest |

---

## Phase 8: Archive (Move Superseded Code)

Move files that are dead, duplicated, or superseded into `archive/`.

| Source → Archive Path | Reason |
|----------------------|--------|
| `velynx_core/` → `archive/code/velynx_core/` | Fully duplicated by `program_c/` |
| `backend/agents/` → `archive/code/agents/` | Dead stubs |
| `backend/audio/` → `archive/code/audio/` | Not in current experimental scope |
| `backend/testing/` → `archive/code/testing/` | Dedicated test infra moved to `tests/` |
| `backend/tools/` → `archive/code/tools/` | One-off utilities |
| `backend/contracts/` → `archive/code/contracts/` | Single file, not maintained |
| `backend/integration/` → `archive/code/integration/` | Empty directory |
| `backend/self_coder.py` → `archive/code/` | Duplicate (also in `velynx_core/`) |
| `backend/orchestrator.py` → `archive/code/` | Superseded by `program_c/pipeline/agentic_loop.py` |
| `experiments/calculator.py` → `archive/experiments/` | Toy scripts |
| `experiments/test_calc.py` → `archive/experiments/` | Toy tests |
| `experiments/generated_tool.py` → `archive/experiments/` | Generated tool stub |
| Root diagnostic probes (`_probe.py`, `cognitive_core.py`, `find_ghosts.py`, etc.) → `archive/code/` | Debugging scripts, not load-bearing |
| `searxng/` → **delete** (third-party cloned repo) | Not part of the repository |
| `kiro-gateway/` → **delete** (third-party) | Not part of the repository |
| `node_modules/` → **delete** | Build artifact |
| `dist/` → **delete** | Build artifact |

---

## Phase 9: Import Path Updates

Every Python file in the repository must be updated to reflect the new directory structure. This is the most mechanical and error-prone phase.

**Strategy:**
1. Write a codemod script (`scripts/_fix_imports_v2.py`) that batch-replaces import paths.
2. Run the script, then run `pytest` to verify nothing broke.
3. If tests fail, manually fix remaining broken imports.

**Import mapping table (partial):**

| Old prefix | New prefix |
|-----------|-----------|
| `backend.app.` | `infra.app.` |
| `backend.database.` | `infra.database.` |
| `backend.runtime.` | `infra.runtime.` |
| `backend.ops.` | `infra.ops.` |
| `backend.evaluation.` | `benchmarks.` |
| `backend.retrieval.` | `program_a.retrieval.` |
| `backend.soul.` | `program_b.soul_graph.` |
| `backend.cognition.` | `program_c.cognition.` |
| `backend.memory.` | `program_c.memory.` |
| `backend.learning.` | `program_c.learning.` |
| `backend.knowledge.` | `program_c.knowledge.` |
| `backend.metacognition.` | `program_c.metacognition.` |
| `backend.reflection.` | `program_c.reflection.` |
| `backend.pipeline.` | `program_c.pipeline.` |
| `backend.abstraction.` | `program_c.abstraction.` |
| `backend.self_model.` | `program_c.self_model.` |
| `backend.simulation.` | `program_c.simulation.` |
| `backend.agency.` | `program_c.agency.` |
| `backend.conversation.` | `program_c.conversation.` |
| `backend.models.` | `program_c.models.` |
| `backend.nlp.` | `program_a.nlp.` |
| `validation.` | `benchmarks.` |
| `research.evaluation.` | `benchmarks.evaluation.` |
| `research.attribution.` | `program_c.agency.` (or `core.`) |
| `research.policies.` | `core.controls.` |
| `research.proposals.` | `core.mdl.` |
| `research.tests.` | `tests.` |

---

## Phase 10: Test Infrastructure

| Source → Target | Reason |
|----------------|--------|
| `backend/tests/` → `tests/` | Consolidate all tests |
| `research/tests/` → `tests/` | Research tests |
| `validation/*_test.py` → `tests/` | Validation tests |
| Root-level `test_*.py` files → `tests/` | Ad-hoc test scripts |

**Caveat:** Some root-level test files are specific diagnostics (`test_agency.py`, `test_c8_*.py`, etc.). Archive these; their functionality should be subsumed by the experiment/permanence test suites.

---

## Phase 11: Configuration & Build Files

| Source → Target | Reason |
|----------------|--------|
| `backend/requirements.txt` → `requirements.txt` (merged) | Consolidated dependencies |
| `backend/requirements-dev.txt` → `requirements-dev.txt` | Dev dependencies |
| `Dockerfile` → `infra/Dockerfile` | Container build |
| `docker-compose.yml` → root (keep) | Multi-service orchestration |
| `pyproject.toml` → root (create) | Modern Python packaging |
| Root `configs/` → `infra/config/` | JSON config |

---

## Migration Order (Topological Sort)

```
Phase 0:  Create directories           (0 dependencies)
Phase 1:  Foundation documents         (0 dependencies — pure writing)
Phase 2:  Core primitives              (foundation/hypothesis defines what is core)
Phase 3:  Infrastructure               (0 dependencies — pure file moves)
Phase 4:  Programs A/B/C               (infra must exist first for import paths)
Phase 5:  Benchmarks                   (program_c must exist for test imports)
Phase 6:  Experiments                  (core + benchmarks must exist)
Phase 7:  Documentation                (0 dependencies)
Phase 8:  Archive                      (all other phases complete)
Phase 9:  Import path updates          (all file moves complete)
Phase 10: Test infrastructure          (imports updated)
Phase 11: Config & build files         (last — integration)
```

---

## What Does NOT Change

- All Python code stays functionally identical. No rewrites, no refactoring, no behavior changes.
- `pyproject.toml` replaces `requirements.txt` + `setup.py` but declares the same dependencies.
- Scientific hypotheses remain exactly as stated in `program_d_scientific_foundation_v0.1.md`.
- Experiment preregistrations remain unchanged.
- The README is updated to reflect the new structure but retains the same project identity.
