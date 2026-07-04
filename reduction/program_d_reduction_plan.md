# Program D — Reduction Plan

## Purpose
Systematic reduction of technical debt, dead code, and duplicated logic while preserving all system capabilities.

---

## PHASE 1: ARCHIVAL (IMMEDIATE — SAFE)

### 1.1 Archive Dead Debug Scripts
**Files:**
- `peek_code.py` (5 lines)
- `find_the_truth.py` (10 lines)
- `find_ghosts.py` (24 lines)
- `ghost_hunt.py` (27 lines)
- `stability_audit.py` (61 lines) — recreate when needed
- `verify_recall_topology.py` (85 lines) — recreate when needed

**Action**: Move to `research_artifacts/` or `scripts/archive/`
**Risk**: LOW — zero callers
**Tests**: None affected
**Confidence**: 0.95

### 1.2 Archive Dead Experiment Stubs
**Files:**
- `experiments/test_calc.py` (2 lines)
- `experiments/calculator.py` (17 lines) — note: `benchmark.py` generates equivalent tools
- `experiments/generated_tool.py` (11 lines)

**Action**: Archive to `experiments/archive/`
**Risk**: LOW
**Tests**: None affected
**Confidence**: 0.95

---

## PHASE 2: PROXY ELIMINATION (LOW RISK)

### 2.1 Migrate `cognitive_health.py` Proxy
**File**: `cognitive_health.py` (78 lines)
**Status**: All logic migrated to `validation/metrics.py` and `validation/report.py`

**Action**:
1. Replace all `import cognitive_health` with direct imports from `validation.metrics` and `validation.report`
2. Update `cognitive_core.py` import
3. Archive `cognitive_health.py`

**Risk**: LOW
**Tests**: `test_stem.py`, `cognitive_core` tests
**Confidence**: 0.90

---

## PHASE 3: DUPLICATE CONSOLIDATION (HIGH IMPACT)

### 3.1 Unify `knowledge_graph.py`
**Files**: `backend/memory/knowledge_graph.py` and `backend/knowledge/knowledge_graph.py`
**Problem**: Two classes named `KnowledgeGraph` with overlapping responsibilities

**Action**:
1. Audit all imports of both modules
2. Merge into single `KnowledgeGraph` class in `backend/knowledge/knowledge_graph.py`
3. Create facade import in `backend/memory/knowledge_graph.py` that re-exports
4. Archive facade after all callers updated

**Risk**: HIGH — 20+ files import one or both versions
**Experiments Affected**: All experiments using KG
**Tests**: `test_probe.py`, `test_knowledge.py`, `test_agency.py`
**Confidence**: 0.70

### 3.2 Unify `brain.py`
**Files**: `velynx_core/brain.py` and `backend/brain.py`
**Problem**: Two `VelynxBrain` classes with different APIs

**Action**:
1. `backend/brain.py` is the newer, richer version (async, intent routing, sim, improve)
2. `velynx_core/brain.py` is legacy but may have users
3. Create adapter import so `velynx_core.brain.VelynxBrain` delegates to `backend.brain.VelynxBrain`
4. Archive `velynx_core/brain.py`

**Risk**: HIGH — the APIs differ (sync vs async, different answer structures)
**Experiments Affected**: Any code using `velynx_core.brain`
**Tests**: `test_probe.py`, `test_velynx_core.py`
**Confidence**: 0.60

### 3.3 Unify `self_coder.py`
**Files**: `velynx_core/self_coder.py` (617 lines, full LLM-based) and `backend/self_coder.py` (145 lines, LLM-free MEMORY-ONLY)

**Action**:
1. `backend/self_coder.py` is the active version (used by `brain.py`)
2. `velynx_core/self_coder.py` is more feature-rich (scan_codebase, generate_fix, SandboxExecutor)
3. Merge features: keep `backend/self_coder.py` as base, add `velynx_core` features
4. Archive `velynx_core/self_coder.py`

**Risk**: MEDIUM — feature sets partially overlap
**Experiments Affected**: Self-coder experiments
**Tests**: `test_probe.py`
**Confidence**: 0.75

### 3.4 Unify Free-Energy Coefficients
**Files**: `decision_policy.py:79-81` and `validation/metrics.py:29-31`
**Problem**: Duplicated constants `DEFAULT_LAMBDA=1.0, MU=2.0, NU=0.5`

**Action**:
1. Import from `validation/metrics.py` in `decision_policy.py`
2. Remove duplicate definitions

**Risk**: LOW
**Tests**: `test_replay_engine_vitals_r3c.py`, `test_shared_metrics_v1.py`
**Confidence**: 0.95

---

## PHASE 4: CIRCULAR DEPENDENCY RESOLUTION (MEDIUM RISK)

### 4.1 Break `scenario_engine.py` ↔ `metacog.py` Cycle
**Problem**: Circular imports between these two modules

**Action**:
1. Extract shared types (concept structures, arc types) to `backend/cognition/shared_types.py`
2. Remove redundant `from backend.cognition.metacog import reflect` at `scenario_engine.py:49`
3. Keep lazy import in `metacog.py:145` but restructure to remove conditional

**Risk**: MEDIUM — lazy import currently works, but restructuring may break edge cases
**Tests**: `python -c "from backend.cognition.scenario_engine import parse_scenario"`
**Confidence**: 0.80

### 4.2 Break `cognitive_core.py` ↔ `concept_birth.py` Cycle
**Action**:
1. Extract `InternalModelView` into shared types module (e.g., `cognitive_types.py`)
2. Remove defensive imports in both files
3. Replace with direct imports from shared module

**Risk**: MEDIUM
**Tests**: `python -c "from cognitive_core import CognitiveEngine"`
**Confidence**: 0.80

---

## PHASE 5: HIDDEN COUPLING REMEDIATION (LOW-MEDIUM RISK)

### 5.1 Centralize File Paths
**Problem**: 6+ modules hardcode file paths relative to their location

**Action**:
1. Create `backend/config/paths.py` with all canonical paths
2. Update all modules to use path constants
3. Add `VELYNX_DATA_DIR` to all path resolutions (not just some)

**Risk**: LOW
**Tests**: Run full pipeline
**Confidence**: 0.85

### 5.2 Document Database Schema Dependencies
**Problem**: Multiple modules depend on DB schemas defined elsewhere

**Action**:
1. Create `backend/database/schemas.py` documenting all table schemas
2. Add schema versioning to avoid silent breakage
3. Add migration path for `brain_stem.db` → `predictive.db` schema alignment

**Risk**: LOW
**Tests**: DB diagnostic tools
**Confidence**: 0.85

---

## SUMMARY

| Phase | Items | Risk | Effort | Confidence |
|-------|-------|------|--------|------------|
| P1: Archival | 8 files | LOW | 1h | 0.95 |
| P2: Proxy | 1 file | LOW | 1h | 0.90 |
| P3: Duplicates | 4 groups | HIGH | 8h | 0.60-0.95 |
| P4: Cycles | 2 groups | MEDIUM | 4h | 0.80 |
| P5: Coupling | 2 groups | LOW-MEDIUM | 3h | 0.85 |

**Total**: ~17h engineering time

## Never Delete — Always Archive
All removed files move to `research_artifacts/archive/` with a README explaining why they were archived and how to restore.
