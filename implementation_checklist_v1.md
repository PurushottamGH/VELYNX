# VELYNX Repository v2 — Implementation Checklist v1

**Date:** 2026-07-03
**Executor:** Single engineer
**Strategy:** Dual-import shim. Every moved file leaves a forwarding shim at the old path so `from backend.*` imports continue to resolve. All tests pass at every commit. Shims are removed in the final phase.

---

## Phase 0: Directory Skeleton

### Commit 0.1 — Create target directory tree

Create all empty target directories with `__init__.py` files so Python recognizes them as packages.

```
foundation/hypothesis/  foundation/assumptions/  foundation/kill_criteria/
foundation/mathematics/ foundation/architecture/ foundation/novelty/
core/predictors/  core/emergence/  core/mdl/  core/measurement/  core/controls/
experiments/E0/  experiments/R1/  experiments/R3F/
experiments/EXP1/  experiments/EXP2/  experiments/EXP3/  experiments/EXP4/
experiments/coverage/
benchmarks/evaluation/  benchmarks/cognition/  benchmarks/reflection/
benchmarks/monitoring/  benchmarks/hallucination/  benchmarks/failure/
program_a/retrieval/  program_a/nlp/
program_b/soul_graph/  program_b/concepts/
program_c/cognition/  program_c/memory/  program_c/learning/  program_c/knowledge/
program_c/metacognition/  program_c/reflection/  program_c/pipeline/
program_c/abstraction/  program_c/self_model/  program_c/simulation/
program_c/agency/  program_c/conversation/  program_c/models/
infra/app/  infra/database/alembic/versions/  infra/runtime/
infra/ops/  infra/constitution/  infra/config/  infra/data/  infra/frontend/
docs/research/  docs/architecture/  docs/audits/  docs/requirements/
docs/reviews/  docs/literature/  docs/plans/
archive/code/  archive/experiments/  archive/documents/  archive/data/
artifacts/benchmarks/  artifacts/experiments/  artifacts/output/
tests/unit/  tests/integration/  tests/fixtures/
```

**Files touched:** 0 code files. Only `mkdir -p` + blank `__init__.py` files.
**Verification:** `git status` shows only empty dirs. Tests pass unchanged.
**Difficulty:** Trivial
**Risk:** None
**Rollback:** `git clean -fd` or `git revert`
**Time:** 5 min

---

## Phase 1: Foundation Documents

### Commit 1.1 — Write hypothesis documents in `foundation/hypothesis/`

Create `central_hypothesis.md`, `H1_calibration.md`, `H2_affective_indexing.md`, `H3_emergent_development.md` — distilled from `PROGRAM_D_RESEARCH_STATE_v0.1.md` §6 and `VELYNX_v2_PI_Review.md`.

**Files touched:** 4 new files.
**Verification:** Markdown only; no code. Tests pass unchanged.
**Difficulty:** Easy
**Risk:** None
**Rollback:** `git revert`
**Time:** 1–2 hr

### Commit 1.2 — Write assumption, kill-criterion, mathematics, architecture, novelty documents in `foundation/`

Create 14 new files in `foundation/assumptions/`, `foundation/kill_criteria/`, `foundation/mathematics/`, `foundation/architecture/`, `foundation/novelty/`. Distilled from existing sources; the old files remain in place.

**Files touched:** 14 new files.
**Verification:** Markdown only; no code. Tests pass unchanged.
**Difficulty:** Easy
**Risk:** None
**Rollback:** `git revert`
**Time:** 2–3 hr

---

## Phase 3: Infrastructure Moves (load-bearing code starts here)

**Shim pattern used from this point forward:**
```
# Move:  git mv backend/ops/circuit_breakers.py infra/ops/circuit_breakers.py
# Edit:  update infra/ops/circuit_breakers.py import paths from backend. → infra.
# Shim:  write backend/ops/circuit_breakers.py:
#            from infra.ops.circuit_breakers import *   # noqa: F401, F403
# Test:  from backend.ops.circuit_breakers import X  still resolves → tests pass
```

### Commit 3.1 — Move `infra/config/` and `infra/constitution/`

- `git mv configs/* infra/config/`
- `git mv backend/constitution/* infra/constitution/`
- No import shims needed (these are JSON/markdown, not Python modules)
- Update `backend/data/` references if any configs were there

**Files touched:** ~10 files (moves only).
**Verification:** No import changes. `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Easy
**Risk:** Low — configs and markdown have no import dependencies
**Rollback:** `git revert`
**Time:** 15 min

### Commit 3.2 — Move `infra/ops/`

- `git mv backend/ops/* infra/ops/` (9 Python files + `__init__.py`)
- Edit `infra/ops/` files: change `from backend.` → `from infra.` in their *internal* imports
- Write forwarding shims in `backend/ops/`
- Update `backend/ops/__init__.py` to re-export from `infra.ops`

**Files touched:** ~9 new location files (edited) + 10 shim files written.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Medium
**Risk:** Low — ops is a leaf package (few internal cross-imports)
**Rollback:** `git revert`; if shim bugs, restore old `backend/ops/` from previous commit
**Time:** 45 min

### Commit 3.3 — Move `infra/runtime/`

- `git mv backend/runtime/* infra/runtime/` (5 Python files)
- Edit internal imports: `from backend.` → `from infra.`
- Write forwarding shims in `backend/runtime/`

**Files touched:** ~5 new location files + 5 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Medium
**Risk:** Low–Medium — runtime may import `backend.database.*` (will get shim-resolved)
**Rollback:** `git revert`
**Time:** 30 min

### Commit 3.4 — Move `infra/database/`

- `git mv backend/database/* infra/database/` (engine, models, repositories, alembic, redis_cache, runtime_state)
- Update `alembic/env.py` migration paths if they reference `backend.database`
- Write forwarding shims in `backend/database/`

**Files touched:** ~8 new location files + 6 shims + 1 alembic config edit.
**Verification:** `pytest backend/tests/ -m "not slow"` passes. `alembic history` works.
**Difficulty:** Medium
**Risk:** Medium — database models are widely imported; shim coverage is critical
**Rollback:** `git revert`; verify DB migrations still resolve
**Time:** 1 hr

### Commit 3.5 — Move `infra/app/`

- `git mv backend/app/* infra/app/` (main, routes_*, streaming, lifespan, pipeline)
- `git mv backend/main.py infra/app/` (root entry point)
- Edit internal imports: `from backend.` → `from infra.`
- Write forwarding shims in `backend/app/`
- Update any `sys.path` / entry-point scripts that reference `backend.app`

**Files touched:** ~10 new location files + 8 shims + entry-point updates.
**Verification:** `pytest backend/tests/ -m "not slow"` passes. `python -c "from infra.app.main import app"` works.
**Difficulty:** Medium
**Risk:** Medium — app routes are import-heavy; test carefully
**Rollback:** `git revert`; if app fails to start, restore `backend/app/` from prior commit
**Time:** 1 hr

---

## Phase 4: Program A, B, C Moves

### Commit 4.1 — Move Program A (retrieval + NLP)

- `git mv backend/retrieval/* program_a/retrieval/`
- `git mv backend/nlp/* program_a/nlp/`
- Edit internal imports in both directories: `from backend.` → `from program_a.`
- Write forwarding shims in `backend/retrieval/` and `backend/nlp/`

**Files touched:** ~10 new location files + 10 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Medium
**Risk:** Low — retrieval is a leaf package (imports from infra, not vice versa)
**Rollback:** `git revert`
**Time:** 45 min

### Commit 4.2 — Move Program B (soul graph)

- `git mv backend/soul/* program_b/soul_graph/`
- Edit internal imports
- Write forwarding shims in `backend/soul/`
- Move `concepts.json` if it's separate

**Files touched:** ~3 new location files + 2 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Easy
**Risk:** Low — 2 Python files only
**Rollback:** `git revert`
**Time:** 15 min

### Commit 4.3 — Move Program C: `cognition/`

Largest directory (18 files). Move as a whole.

- `git mv backend/cognition/* program_c/cognition/`
- Edit internal imports in each file: `from backend.` → `from program_c.`
- Write forwarding shims in `backend/cognition/`

**Files touched:** 18 new location files (edited) + 18 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Hard
**Risk:** High — `backend.cognition` is the most-imported package in the codebase. Every shim must re-export exactly. Check for cross-references within cognition (e.g., `predictive_core.py` imports from `vector_prediction_core.py` — they both moved together, so internal imports use new paths).
**Rollback:** `git revert`. If shims are incomplete, tests will reveal immediately.
**Time:** 2 hr

### Commit 4.4 — Move Program C: `memory/`

- `git mv backend/memory/* program_c/memory/` (18 files)
- Same pattern as cognition

**Files touched:** 18 new location files + 18 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Hard
**Risk:** High — memory is widely imported
**Rollback:** `git revert`
**Time:** 1.5 hr

### Commit 4.5 — Move Program C: `learning/`

- `git mv backend/learning/* program_c/learning/` (15 files)

**Files touched:** 15 new location files + 15 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Medium–Hard
**Risk:** Medium–High — learning imports from memory and cognition
**Rollback:** `git revert`
**Time:** 1 hr

### Commit 4.6 — Move Program C: `knowledge/`

- `git mv backend/knowledge/* program_c/knowledge/` (14 files)

**Files touched:** 14 new location files + 14 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Medium–Hard
**Risk:** Medium — knowledge imports from memory
**Rollback:** `git revert`
**Time:** 1 hr

### Commit 4.7 — Move Program C: `pipeline/`

- `git mv backend/pipeline/* program_c/pipeline/` (19 files)

**Files touched:** 19 new location files + 19 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Hard
**Risk:** High — pipeline is the integration layer, imports from everything
**Rollback:** `git revert`
**Time:** 2 hr

### Commit 4.8 — Move Program C: remaining subpackages

Move the remaining smaller packages together (safe to batch since each is independent):

- `git mv backend/metacognition/* program_c/metacognition/`
- `git mv backend/reflection/* program_c/reflection/`
- `git mv backend/abstraction/* program_c/abstraction/`
- `git mv backend/self_model/* program_c/self_model/`
- `git mv backend/simulation/* program_c/simulation/`
- `git mv backend/agency/* program_c/agency/`
- `git mv backend/conversation/* program_c/conversation/`
- `git mv backend/models/* program_c/models/`
- `git mv backend/brain.py program_c/`
- `git mv backend/cli.py program_c/`
- `git mv backend/cli_ui.py program_c/`

Write shims for all.

**Files touched:** ~60+ files.
**Verification:** `pytest backend/tests/ -m "not slow"` passes.
**Difficulty:** Hard
**Risk:** Medium — each package is smaller and more focused, but batching increases blast radius
**Rollback:** `git revert`. If partial failure, revert whole commit.
**Time:** 3 hr

---

## Phase 5: Benchmark Consolidation

### Commit 5.1 — Move `benchmarks/evaluation/` from `backend/evaluation/`

- `git mv backend/evaluation/* benchmarks/evaluation/` (16 files — benchmark_runner, scenario_loader, trial_runner, adversarial_tests, etc.)
- Edit internal imports: `from backend.` → `from benchmarks.`
- Write forwarding shims in `backend/evaluation/`

**Files touched:** 16 new location files + 16 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes. `pytest research/tests/ -m "not slow"` passes.
**Difficulty:** Medium
**Risk:** Medium — evaluation imports from backend packages; shims handle it
**Rollback:** `git revert`
**Time:** 1 hr

### Commit 5.2 — Move `validation/` to `benchmarks/evaluation/`

- `git mv validation/* benchmarks/evaluation/` (9 files: interfaces, runner, report, metrics, datasets, artifact, monitor, regression, shared_metrics_v1)
- Edit internal imports: `from validation.` → `from benchmarks.evaluation.`
- Write forwarding shims in `validation/`

Note: `validation/metrics.py` and `validation/shared_metrics_v1.py` are marked in migration_plan.md for potential `core/measurement/` — defer that decision. For now, move all to `benchmarks/evaluation/`; the core extraction in Phase 2 will identify what belongs in `core/`.

**Files touched:** ~9 new location files + 9 shims.
**Verification:** `pytest backend/tests/ -m "not slow"` passes. `pytest research/tests/` passes.
**Difficulty:** Medium
**Risk:** Medium — validation is imported by backend tests; shims handle backward compat
**Rollback:** `git revert`
**Time:** 45 min

### Commit 5.3 — Move `research/evaluation/` to `benchmarks/evaluation/`

- Move `research/evaluation/*` → `benchmarks/evaluation/`
- Write forwarding shims in `research/evaluation/`

**Files touched:** ~5 files.
**Verification:** `pytest research/tests/` passes.
**Difficulty:** Easy
**Risk:** Low — small directory
**Rollback:** `git revert`
**Time:** 15 min

---

## Phase 2: Core Primitives Extraction

### Commit 2.1 — Create `core/predictors/` + `core/measurement/`

Extract the Dirichlet–Markov conjugate predictor from `backend/cognition/predictive_core.py` and `backend/cognition/vector_prediction_core.py`:
- Write `core/predictors/base.py` — predictor interface
- Write `core/predictors/dirichlet_markov.py` — extracted predictor class
- Write `core/measurement/proper_scoring.py` — log-loss scorer extracted from `backend/cognition/decision_policy.py`
- Write `core/measurement/metrics.py` — consolidated from `validation/metrics.py` and `validation/shared_metrics_v1.py`
- Refactor original locations to import from `core/` (thin wrappers)

**Files touched:** 4 new files + edits to 3 existing source files.
**Verification:** `pytest backend/tests/ -m "not slow"` passes. `python -c "from core.predictors.dirichlet_markov import DirichletMarkovPredictor"` works.
**Difficulty:** Hard
**Risk:** High — this is the first code *extraction* (not pure move). Must preserve exact behavior.
**Rollback:** `git revert`; if extraction bugs found, revert and re-extract with corrected logic
**Time:** 3 hr

### Commit 2.2 — Create `core/emergence/` + `core/mdl/` + `core/controls/`

- Write `core/emergence/emergence_statistic.py` — NMI estimator extracted from `validation/metrics.py`
- Write `core/emergence/null_referenced_test.py` — null-referenced construction
- Write `core/mdl/mdl_growth.py` — MDL description-length from `backend/cognition/concept_birth.py`
- Write `core/mdl/concept_birth_ledger.py` — concept-birth ledger
- Write `core/measurement/observability.py` — new instrumentation
- Write `core/controls/fixed_capacity.py` — from `research/policies/null.py`
- Write `core/controls/random_growth.py` — from `research/policies/random_policy.py`
- Write `core/controls/shuffled_input.py` — new control
- Refactor original locations to import from `core/`

**Files touched:** 8 new files + edits to 4+ existing source files.
**Verification:** `pytest backend/tests/ -m "not slow"` passes. `pytest research/tests/` passes.
**Difficulty:** Hard
**Risk:** High — extraction of scientific primitives must preserve exact mathematical semantics
**Rollback:** `git revert`
**Time:** 4 hr

---

## Phase 6: Experiment Reorganization

### Commit 6.1 — Rename `experiments/EXP0/` to `experiments/E0/` and add per-experiment dirs

- `git mv experiments/EXP0 experiments/E0`
- Create `experiments/R1/`, `experiments/R3F/`, `experiments/EXP1/`–`EXP4/` with `preregistration.md`, `protocol.md`, `run.py`, `analysis.py` stubs (or move from `research/experiments/` if they exist)
- Write `experiments/coverage/experiment_coverage_matrix.csv` — derived from `program_d_experiment_coverage_matrix.csv`
- Preserve backward compat: write a `README.md` in `experiments/EXP0/` that says "Moved to experiments/E0/"
- Or: create a `forward` file / git symlink (prefer the former on Windows)

**Files touched:** Rename 1 directory + ~5 new experiment dirs.
**Verification:** `python experiments/E0/run_exp0.py` still runs (update any internal paths). `git log --follow experiments/E0/run.py` shows history.
**Difficulty:** Medium
**Risk:** Medium — experiment reproducibility depends on paths. If any script hardcodes `experiments/EXP0/`, update it.
**Rollback:** `git revert`
**Time:** 1.5 hr

---

## Phase 7: Documentation Consolidation

### Commit 7.1 — Move root + scattered docs to `docs/` subdirectories

- `git mv PROGRAM_D_RESEARCH_STATE_v0.1.md docs/research/`
- `git mv "VELYNX_v2_PI_Review.md" docs/research/`
- `git mv ARCHITECTURE.md docs/architecture/` (if it exists at root)
- `git mv VELYNX_AUDIT_2026-06-01.md docs/audits/`
- `git mv docs/requirements.md docs/requirements/`
- `git mv docs/requirements_raw.txt docs/requirements/`
- `git mv reviews/* docs/reviews/`
- `git mv literature/* docs/literature/`
- `git mv reduction/* docs/plans/`
- `git mv VELYNX_PHASE36_AUDIT.md docs/audits/`
- `git mv phase57_agentic_loop_architecture.md docs/architecture/`
- `git mv phase60_self_model_architecture.md docs/architecture/`

**Files touched:** ~20 file moves.
**Verification:** No code changes. Tests pass.
**Difficulty:** Easy
**Risk:** Low — markdown files only
**Rollback:** `git revert`
**Time:** 30 min

---

## Phase 8: Archive Superseded Code

### Commit 8.1 — Archive dead/duplicated code

- `git mv velynx_core/ archive/code/velynx_core/`
- `git mv backend/agents/ archive/code/agents/`
- `git mv backend/audio/ archive/code/audio/`
- `git mv backend/testing/ archive/code/testing/`
- `git mv backend/tools/ archive/code/tools/`
- `git mv backend/contracts/ archive/code/contracts/`
- `git mv backend/integration/ archive/code/integration/`
- `git mv backend/self_coder.py archive/code/`
- `git mv backend/orchestrator.py archive/code/`
- `git mv experiments/calculator.py archive/experiments/`
- `git mv experiments/test_calc.py archive/experiments/`
- `git mv experiments/generated_tool.py archive/experiments/`
- `git mv experiments/EXP0/artifacts/ archive/experiments/` (if experiment artifacts not needed at root)

**Important:** Do NOT archive anything still imported. Verify each deletion has zero imports elsewhere.

**Files touched:** 10+ directories moved.
**Verification:** `grep -r` on all deleted paths returns nothing. `pytest backend/tests/` passes.
**Difficulty:** Medium
**Risk:** Medium — must verify no remaining references before moving. Run a grep first.
**Rollback:** `git revert`. If something breaks, `git mv` back from archive.
**Time:** 1 hr

---

## Phase 9: Import Path Rewrite — Remove All Shims

### Commit 9.1 — Bulk import rewrite codemod

Write `scripts/_fix_imports_v2.py` that applies the import mapping table:

| Old prefix | New prefix |
|-----------|-----------|
| `backend.app.` | `infra.app.` |
| `backend.database.` | `infra.database.` |
| `backend.runtime.` | `infra.runtime.` |
| `backend.ops.` | `infra.ops.` |
| `backend.evaluation.` | `benchmarks.evaluation.` |
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
| `validation.` | `benchmarks.evaluation.` |
| `research.evaluation.` | `benchmarks.evaluation.` |
| `research.attribution.` | `program_c.agency.` |
| `research.policies.` | `core.controls.` |
| `research.proposals.` | `core.mdl.` |

Run the script against all `.py` files in `program_c/`, `program_a/`, `program_b/`, `infra/`, `benchmarks/`, `experiments/`, `core/`, `tests/`, and remaining root-level files.

Then **delete all shim files** from `backend/`, `validation/`, `research/evaluation/`, `research/policies/`, `research/proposals/`.

**Files touched:** ~250+ Python files (bulk regex replacement) + ~100 shim files deleted.
**Verification:** `python -c "from backend.cognition.reasoning_engine import ReasoningEngine"` must fail. `python -c "from program_c.cognition.reasoning_engine import ReasoningEngine"` must succeed. Full `pytest` suite passes.
**Difficulty:** Very Hard
**Risk:** Very High — every import in the codebase changes. Miss one replacement and the code breaks.
**Rollback:** `git revert`. Before running, commit so you have a clean checkpoint. Run the codemod as a separate commit.
**Time:** 4 hr (1 hr to write/test script, 3 hr to fix edge cases)

---

## Phase 10: Test Infrastructure

### Commit 10.1 — Consolidate tests into `tests/`

- `git mv backend/tests/* tests/`
- `git mv research/tests/* tests/`
- `git mv root-level test_*.py tests/` (archive diagnostics that don't belong)
- Create forwarding shims or symlinks from `backend/tests/` to `tests/` for any CI scripts that reference old paths
- Update conftest markers, CI config, pytest invocation paths

**Files touched:** 60+ test files moved + conftest updates + CI config.
**Verification:** `pytest tests/ -m "not slow"` passes identically to previous `pytest backend/tests/`.
**Difficulty:** Medium
**Risk:** Medium — test discovery paths change. Verify `__init__.py` and conftest location.
**Rollback:** `git revert`
**Time:** 1 hr

---

## Phase 11: Build & Configuration

### Commit 11.1 — Create `pyproject.toml`

Write `pyproject.toml` that:
- Declares Python build system (setuptools)
- Declares package metadata
- Merges `backend/requirements.txt` + `root/requirements.txt` into `[project.dependencies]`
- Moves test dependencies to `[project.optional-dependencies] test`
- Configures `[tool.pytest.ini_options]` so `pytest` works from the repo root
- Configures `[tool.coverage]` if desired

**Files touched:** 1 new file + remove `backend/requirements.txt` + `root/requirements.txt` (or keep as compat).
**Verification:** `pip install -e .` installs the package. `pytest tests/` discovers tests. `python -c "import program_c.cognition"` works without `sys.path` hacks.
**Difficulty:** Medium
**Risk:** Medium — first time the project has a proper packaging config. May expose import issues.
**Rollback:** `git revert`; project continues to work via sys.path as before
**Time:** 2 hr

### Commit 11.2 — Final cleanup

- Update `.gitignore` for new structure (add `infra/data/` contents, `artifacts/`, `archive/`, `.venv*`, `.pytest_cache/`, `__pycache__/`)
- Remove any remaining shim directories that are now empty (`backend/agents/`, `backend/tools/`, etc.)
- Update `docker-compose.yml` volume mounts to point to new paths
- Update `.env.example` if paths changed
- Update `README.md` to reflect v2 structure (keep minimal; point to `docs/`)

**Files touched:** `.gitignore`, `docker-compose.yml`, `.env.example`, `README.md`.
**Verification:** `git status` shows clean. `pytest tests/` passes.
**Difficulty:** Easy
**Risk:** Low
**Rollback:** `git revert`
**Time:** 30 min

---

## Migration Roadmap Summary

| # | Commit | Phase | Files Touched | Difficulty | Risk | Time |
|---|--------|-------|---------------|------------|------|------|
| 1 | 0.1 | Create directories | 0 code files | Trivial | None | 5 min |
| 2 | 1.1 | Hypothesis docs | 4 new | Easy | None | 1–2 hr |
| 3 | 1.2 | Foundation docs | 14 new | Easy | None | 2–3 hr |
| 4 | 3.1 | infra/config + constitution | ~10 moves | Easy | Low | 15 min |
| 5 | 3.2 | infra/ops | ~19 files (9+10 shims) | Medium | Low | 45 min |
| 6 | 3.3 | infra/runtime | ~10 files | Medium | Low–Med | 30 min |
| 7 | 3.4 | infra/database | ~14 files | Medium | Medium | 1 hr |
| 8 | 3.5 | infra/app | ~18 files | Medium | Medium | 1 hr |
| 9 | 4.1 | Program A | ~20 files | Medium | Low | 45 min |
| 10 | 4.2 | Program B | ~5 files | Easy | Low | 15 min |
| 11 | 4.3 | Program C: cognition | 36 files | Hard | High | 2 hr |
| 12 | 4.4 | Program C: memory | 36 files | Hard | High | 1.5 hr |
| 13 | 4.5 | Program C: learning | 30 files | Med–Hard | Med–High | 1 hr |
| 14 | 4.6 | Program C: knowledge | 28 files | Med–Hard | Medium | 1 hr |
| 15 | 4.7 | Program C: pipeline | 38 files | Hard | High | 2 hr |
| 16 | 4.8 | Program C: remaining | ~60+ files | Hard | Medium | 3 hr |
| 17 | 5.1 | benchmarks/evaluation | 32 files | Medium | Medium | 1 hr |
| 18 | 5.2 | validation→benchmarks | ~18 files | Medium | Medium | 45 min |
| 19 | 5.3 | research/evaluation→benchmarks | ~5 files | Easy | Low | 15 min |
| 20 | 2.1 | core predictors + measurement | ~7 files | Hard | High | 3 hr |
| 21 | 2.2 | core emergence + MDL + controls | ~12 files | Hard | High | 4 hr |
| 22 | 6.1 | Experiment reorg | ~1 dir rename + 5 new | Medium | Medium | 1.5 hr |
| 23 | 7.1 | Docs consolidation | ~20 moves | Easy | Low | 30 min |
| 24 | 8.1 | Archive dead code | ~10 dirs moved | Medium | Medium | 1 hr |
| 25 | 9.1 | Bulk import rewrite | ~350 files | Very Hard | Very High | 4 hr |
| 26 | 10.1 | Test consolidation | ~60+ moves | Medium | Medium | 1 hr |
| 27 | 11.1 | pyproject.toml | 1 new + 2 deleted | Medium | Medium | 2 hr |
| 28 | 11.2 | Final cleanup | 4 files | Easy | Low | 30 min |

**Total estimated time:** 34–40 hours (1 engineer, 1 work week)

---

## Risk Management

### Rollback strategy by severity:

| Risk Level | Action |
|-----------|--------|
| **None** | No rollback needed. |
| **Low** | `git revert <commit>` — no side effects. |
| **Medium** | `git revert <commit>` then verify tests pass. If shim-related failure, restore files from previous commit manually. |
| **High/Very High** | Before commit, ensure the working tree is clean. After commit, run full test suite. If failures, `git revert` immediately. If the commit is large (e.g., 9.1), consider splitting into sub-commits by module. |

### Before-and-after hooks for high-risk commits:

- **Commit 9.1 (bulk import rewrite):** Run a pre-commit script that counts `from backend.` imports. After the commit, assert the count drops to zero (except shim files if any remain). Keep the script in `scripts/` for verification.

### Preserving experiment reproducibility:
- Each experiment's `run.py` and `analysis.py` are kept functionally identical. The ONLY change is import paths.
- After Phase 9, run `python experiments/E0/run_exp0.py` and verify it produces the same output structure as the pre-migration version.
- EXP0 artifacts are archived before migration, so a pre-migration checkout always works.

### Preserving git history:
- Use `git mv` exclusively — never delete + recreate files.
- `git log --follow <new-path>` will trace back to the original file in `backend/`.
- The migration itself is committed linearly on `main`. No rebasing or squashing of existing history.

---

## Pre-requisite: Seed `backend/__init__.py`

Before ANY code moves, add a module docstring to `backend/__init__.py` (it is currently empty). This ensures Python treats `backend` as a namespace package consistently. Without this, some moves could silently break package resolution.

**Action:** Write to `backend/__init__.py`:
```python
"""VELYNX backend package — compatibility shim during v2 migration."""
```

This is a best practice and will be replaced with a deprecation warning closer to Phase 9.

---

## Execution Order (Day-by-Day)

| Day | Commits | Focus |
|-----|---------|-------|
| Mon AM | 0.1, 1.1, 1.2, 3.1, 3.2, 3.3 | Foundation + infra start |
| Mon PM | 3.4, 3.5, 4.1, 4.2, 5.3 | Infra + Program A/B + small benchmark |
| Tue AM | 4.3, 4.4 | Program C: cognition + memory (hard) |
| Tue PM | 4.5, 4.6, 5.1 | Program C: learning + knowledge + benchmarks |
| Wed AM | 4.7, 4.8 | Program C: pipeline + remaining packages |
| Wed PM | 5.2, 7.1, 8.1 | Validation move, docs, archive |
| Thu AM | 2.1, 2.2 | Core extraction (hard — may push to Thu PM) |
| Thu PM | 6.1, 10.1 | Experiment reorg + test consolidation |
| Fri AM | 9.1 | Bulk import rewrite (prepare codemod Thu PM) |
| Fri PM | 11.1, 11.2 | Build config + final cleanup + full test suite |
