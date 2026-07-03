# Technical Debt Report

**Date:** 2026-07-03  
**Commit:** `a41b5c4` (Phase 62.3)

---

## Classification

| Category | Count | Severity |
|----------|-------|----------|
| 🔴 Critical | 1 | Blocks correctness |
| 🟡 Major | 3 | Impacts maintainability |
| 🟢 Minor | 9 | Cosmetic or pre-existing |
| ⚪ Informational | 5 | No action required |

---

## 🔴 Critical Debt

### D1. Parameter Duplication — Free Energy Coefficients

**Location:** `core/measurement/metrics.py`, `experiments/metrics.py`, `validation/metrics.py`, `backend/cognition/decision_policy.py`, `cognitive_core.py`

**Description:** The coefficients `LAMBDA=1.0`, `MU=2.0`, `NU=0.5` are defined in 5 separate locations. Changes require coordinated updates across all files.

**Resolution:** Make `core/measurement/metrics.py` the single canonical source. All other modules import from it:
```python
from core.measurement.metrics import LAMBDA, MU, NU
```
(This is deferred to Phase 2 of the migration plan.)

**Status:** ⏳ Pending backend migration (Phase 2)

---

## 🟡 Major Debt

### D2. 4 Pre-Existing Backend Files Fail Compilation

**Files:**
- `backend/abstraction/belief_generator.py`
- `backend/abstraction/belief_store.py`
- `backend/self_model/baseline_tracker.py`
- `archive/code/diagnostics/velynx_soul.py`

**Error:** These files have syntax or runtime errors that prevent `py_compile` from succeeding.

**Resolution:** These will be resolved during the backend file migration (Phases 3-4) when files are moved into `program_c/`.

**Status:** ⏳ Pending backend migration

### D3. Unreachable Legacy Test Constants

**Files:** `backend/tests/test_agency.py`, `test_belief_revision.py`, `test_cognition.py`, `test_curiosity.py`, `test_dynamic_agency.py`, `test_episodic_memory.py`, `test_self_model.py`, `test_semantic_grounding.py`

**Description:** `CONSOLIDATION_WAIT_SECONDS` varies between 4 and 5 across test files. This discrepancy suggests some tests may have different timing assumptions that aren't documented.

**Resolution:** Audit and unify to a single constant. This is test infrastructure debt.

**Status:** ⏳ Pending test consolidation (Phase 10)

### D4. Benchmark Framework Has No Concrete Benchmarks

**Location:** `benchmarks/`

**Description:** The benchmark framework (`benchmarks/runner.py`, `benchmarks/evaluation/`) is fully functional but has zero registered benchmark implementations. The concrete benchmarks exist in `backend/evaluation/` but haven't been migrated.

**Resolution:** Move benchmarks from `backend/evaluation/` to `benchmarks/` (Phase 5).

**Status:** ⏳ Pending benchmark migration (Phase 5)

---

## 🟢 Minor Debt

### D5. `scripts/gpu_deep_learn.py` — Undefined Name

**File:** `scripts/gpu_deep_learn.py:398`

**Error:** Variable `checkpoint` is used but not defined (linting error F821).

**Severity:** This script is a pre-existing utility for GPU-based deep learning, not part of the experiment infrastructure.

**Resolution:** Either fix the variable reference or archive the script.

### D6. `scripts/gpu_deep_learn.py` — Duplicated Imports

**File:** `scripts/gpu_deep_learn.py`

**Duplicates:** `import sys`, `from memory.knowledge_graph import knowledge_graph`, `import torch` each appear twice.

**Severity:** Cosmetic — no runtime impact.

### D7. R1 Experiment Registry Status Ambiguity

**File:** `experiment_registry.yaml`

**Description:** R1 is marked "archived" (was "completed") but the directory contains no artifacts. Actual R1 results exist in `research/` directory.

**Severity:** Low — now documented in registry.

### D8. Experiment Artifacts from Failed Runs

**Location:** `artifacts/experiments/EXP1/`, `artifacts/experiments/EXP2/`

**Description:** Previous attempts to run EXP-1/EXP-2 created failed manifests. These are harmless but clutter the artifact store.

**Severity:** Cosmetic — only 4 small JSON files.

### D9. Empty `docs/research/`, `docs/architecture/`, etc.

**Description:** Doc subdirectories were created (Phase 0 of migration) but no documents have been moved into them yet.

**Severity:** Low — pending Phase 7 (documentation consolidation).

### D10. Stale `experiments/calculator.py`, `experiments/test_calc.py`, `experiments/generated_tool.py`

**Description:** These are toy utility scripts in the experiments directory that are not part of any experiment.

**Severity:** Low — should be archived.

### D11. No `requirements-locked.txt`

**File:** Referenced in `reproducibility.yaml` as TODO item.

**Description:** Dependencies are not pinned to specific versions.

**Severity:** Low — acceptable for active development.

### D12. `data/epistemic.db-shm` and `data/epistemic.db-wal` Untracked

**Description:** SQLite WAL/SHM files are present in the working directory.

**Severity:** Low — these are ignored by .gitignore's `*.db` pattern. They will be cleaned on next `wipe_db.py` run.

### D13. Duplicate `gcp-key.json.json`

**Description:** A file named `gcp-key.json.json` (double extension) exists at repository root. This is likely a renamed artifact.

**Severity:** Low — should be archived or removed.

---

## ⚪ Informational

### I1. Constant Duplication is Intentional (3 files)

**Files:** `core/measurement/metrics.py`, `experiments/metrics.py`, `validation/metrics.py`

**Context:** `ENERGY_EXHAUSTION`, `ENTROPY_HIGH`, `SURPRISE_HIGH`, `SURPRISE_MILD`, `PRESSURE_HIGH`, `PRESSURE_MILD`, `LAMBDA`, `MU`, `NU` appear in all three files. This is a transitional state — Phase 2 of the migration plan will consolidate into `core/` as single source of truth.

### I2. Test Constants Vary by Design

**Context:** `SESSION_ID`, `TURN1_KNOWLEDGE`, `TURN2_MULTI_HOP_GOAL`, `RECALL_QUESTION` vary across test files. This is expected — each test suite needs unique session IDs and query content.

### I3. 19 Pre-Existing Experiment Artifacts

**Location:** `artifacts/exp_001` through `artifacts/exp_019`

**Context:** These were generated by prior experiment runs and are preserved for audit. They are CSV/JSON data files with version tracking.

### I4. `research/` Directory is Fully Functioning

**Context:** The `research/` package contains the most mature code (Sprint R1/R2A/R3). It will be migrated into the new structure during Phases 2-5 but is currently fully functional and independently testable.

### I5. `validation/` Directory is Live Production Code

**Context:** The `validation/` package is actively imported by `backend/` and must remain in place until the backend migration is complete. It cannot be archived or consolidated until all import references are updated.

---

## Debt Resolution Roadmap

| Debt | Phase | Effort | Priority |
|------|-------|--------|----------|
| D1. Parameter consolidation | Phase 2 | 1 day | High |
| D2. Fix backend compilation | Phase 3-4 | 2 days | High |
| D3. Unify test constants | Phase 10 | 0.5 day | Medium |
| D4. Add concrete benchmarks | Phase 5 | 1 day | Medium |
| D5. Fix/archive gpu_deep_learn.py | Phase 8 | 0.25 day | Low |
| D6. Fix duplicate imports | Phase 8 | 0.1 day | Low |
| D8. Clean failed artifact dirs | Immediate | 0.1 day | Low |
| D10. Archive toy scripts | Phase 8 | 0.1 day | Low |
| D11. Pin dependencies | Phase 11 | 0.5 day | Medium |
| D13. Remove gcp-key.json.json | Immediate | 0.05 day | Low |

---

## Summary

- **Critical items:** 1 (parameter duplication, intentional until Phase 2)
- **Major items:** 3 (all blocked on backend migration)
- **Minor items:** 9 (all low-effort, non-blocking)
- **Total debt:** 13 items, none blocking current stabilization
