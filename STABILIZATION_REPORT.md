# Stabilization Report

**Date:** 2026-07-03  
**Commit:** `a41b5c4` (Phase 62.3)  
**Repository:** VELYNX — Predictive Processing Cognitive Architecture

---

## 1. Experiment Execution

| Experiment | Status | Result | Notes |
|-----------|--------|--------|-------|
| **E0** | `running` | ✅ PASS | 5000 ticks, mean FE=2.40, no kill criteria. Artifacts verified. |
| **EXP-0** | `running` | ✅ PASS | Dry-run validates dataset, leakage, and imports. Full run requires `--tier` flag. |
| **EXP-1** | `planned` | ⏭️ SKIP | No run.py — preregistration planned. |
| **EXP-2** | `planned` | ⏭️ SKIP | No run.py — preregistration planned. |
| **EXP-3** | `planned` | ⏭️ SKIP | Gated behind EXP-2. |
| **EXP-4** | `gated` | ⏭️ SKIP | Gated behind EXP-3. |
| **R1** | `archived` | ⏭️ SKIP | 72 experiments completed externally via research/runner.py. |
| **R3F** | `planned` | ⏭️ SKIP | Formal benchmark suite — preregistration in progress. |

## 2. Reproducibility Audit

| Check | Result |
|-------|--------|
| Experiment registry | ✅ 7 experiments registered, all paths valid |
| Parameter registry | ✅ 4 parameter groups, all file references valid |
| Config files | ✅ All 3 configs exist (baseline.json, noisy.json, simple.json) |
| Requirements | ✅ requirements.txt + pyproject.toml present |
| .env template | ✅ .env.example present |
| Seed control | ✅ BENCHMARK_SEED env var, default 42 |
| Git versioning | ✅ reproducibility.yaml tracks HEAD commit |
| Hardware spec | ✅ Documented in reproducibility.yaml |
| Known issues | ✅ Documented (LLM variance, Hebbian order-dependence, web search) |

### Artifact Integrity

| Experiment | Integrity |
|-----------|-----------|
| E0 runs | ✅ All 3 runs verified (SHA-256 hashes match) |
| EXP-1/2 failed runs | ⚠️ Expected — these are failed manifests from un-implemented experiments |
| EXP-0 artifacts | ✅ Verified via dry-run dataset integrity check |

## 3. Static Analysis

### Compilation

| Scope | Result |
|-------|--------|
| Infrastructure (`core/`, `experiments/`, `benchmarks/`, `scripts/`, `validation/`) | ✅ All files compile clean |
| Pre-existing backend code | ⚠️ 4 files fail (all pre-existing, not part of new infrastructure): `archive/code/diagnostics/velynx_soul.py`, `backend/abstraction/belief_generator.py`, `backend/abstraction/belief_store.py`, `backend/self_model/baseline_tracker.py` |

### Linting (flake8 E9/F63/F7/F82)

| Scope | Errors |
|-------|--------|
| Infrastructure packages | ✅ 0 errors |
| Pre-existing scripts | ⚠️ 3 errors in `scripts/gpu_deep_learn.py` (undefined `checkpoint`) |

## 4. Dependency Analysis

| Check | Result |
|-------|--------|
| Circular imports | ✅ None detected between infrastructure packages |
| Duplicated imports | ✅ None in infrastructure packages (3 duplicates in legacy `scripts/gpu_deep_learn.py`) |
| Import chain | ✅ Clean: core → stdlib only. experiments → core + stdlib. benchmarks → experiments + stdlib. |

## 5. Configuration Drift

| Check | Result |
|-------|--------|
| Parameter registry locations | ✅ All file references exist |
| Experiment component references | ✅ All existing component paths valid |
| Config files referenced in reproducibility.yaml | ✅ All 3 exist |
| Drift between parameter_registry.yaml and code constants | ⚠️ LAMBDA/MU/NU mirrored in 3 locations (intentional — see §7) |

## 6. CI Workflow Verification

| Workflow | Status | Notes |
|----------|--------|-------|
| `ci.yml` lint job | ✅ | flake8 + black + mypy |
| `ci.yml` test job | ✅ | pytest + coverage |
| `ci.yml` reproducibility job | ✅ | verify_reproducibility.py |
| `ci.yml` experiment-validation job | ✅ | validate_experiment_registry.py + validate_parameter_registry.py |
| `ci.yml` benchmark job | ✅ | smoke_benchmark.py |
| `ci.yml` kill-criteria job | ✅ | check_kill_criteria.py |
| `ci.yml` artifact-integrity job | ✅ | verify_artifact_integrity.py |

## 7. Known Issues (Non-Blocking)

| Issue | Severity | Plan |
|-------|----------|------|
| LAMBDA/MU/NU mirrored in 3 files | Low | Phase 2 of migration will consolidate into `core/measurement/metrics.py` as single source of truth |
| 4 pre-existing backend files fail compilation | Low | Backend migration (Phase 3-4) will resolve these |
| `scripts/gpu_deep_learn.py` has undefined name | Low | Pre-existing script, not part of experiment infrastructure |
| R1 registered as "archived" but has no artifact data | Low | R1 artifacts exist in `research/` directory — documented |

---

**Stabilization verdict: PASS** — All infrastructure checks pass. Known issues are pre-existing in legacy code or are intentional design decisions documented in the migration plan.
