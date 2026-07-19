# Program D — Migration Plan

## Purpose
Define the migration path from the current architecture (dual-core: `velynx_core/` + `backend/`) to a unified architecture with clear layer boundaries.

---

## CURRENT STATE

```
┌─────────────────────────────────────────────────────────┐
│                    Root Scripts                         │
│  cognitive_core.py  night_learner.py  benchmark.py ...  │
├─────────────────────────────────────────────────────────┤
│                    velynxs_core/                        │
│  velynx.py  brain.py  memory.py  learner.py  selfcoder  │
├─────────────────────────────────────────────────────────┤
│                     backend/                            │
│  brain.py  orchetrator.py  cli*.py  selfcoder.py       │
│  ├── cognition/  ├── memory/  ├── knowledge/           │
│  ├── pipeline/   ├── agency/   ├── learning/           │
│  ├── retrieval/  ├── app/      ├── reflection/         │
│  ├── database/   ├── soul/     ├── models/             │
│  └── ...                                               │
├─────────────────────────────────────────────────────────┤
│                   validation/                           │
│  metrics.py  report.py  runner.py  regression.py  ...  │
├─────────────────────────────────────────────────────────┤
│                   research/                             │
│  runner.py  stats.py  artifacts.py  policies/  eval/   │
└─────────────────────────────────────────────────────────┘
```

## TARGET STATE

```
┌─────────────────────────────────────────────────────────┐
│                    entry_points/                        │
│  velynx.py → backend.app.main                           │
│  cognitive_core.py → backend.cognition.cognitive_engine │
│  benchmark.py → validation.runner                       │
├─────────────────────────────────────────────────────────┤
│                    velynxs_api/                         │
│  VelynxSystem → backend.orchestrator                    │
│  VelynxBrain → backend.brain                            │
│  VelynxMemory → backend.memory                          │
│  VelynxLearner → backend.learning                       │
│  VelynxSelfCoder → backend.self_coder                   │
├─────────────────────────────────────────────────────────┤
│                    backend/                              │
│  └── (consolidated, no duplicates)                      │
├─────────────────────────────────────────────────────────┤
│                    validation/                           │
│  └── (unchanged — already clean)                        │
├─────────────────────────────────────────────────────────┤
│                    research/                             │
│  └── (unchanged — already clean)                        │
└─────────────────────────────────────────────────────────┘
```

---

## MIGRATION STEPS

### Step 1: Consolidate Core API (Session 1 — 4h)
**Goal**: Merge `velynx_core/` into `backend/` with backwards-compatible re-exports

**Actions**:
1. Create `velynx_core/__init__.py` → re-export from `backend/` equivalents
2. Move `VelynxSystem` logic from `velynx_core/velynx.py` into `backend/orchestrator.py`
3. Keep old `velynx_core/velynx.py` as thin CLI shim that imports from `backend/`

**Validation**: All `from velynxs_core import *` calls work identically

### Step 2: Merge Knowledge Graphs (Session 2 — 4h)
**Goal**: Single `KnowledgeGraph` class

**Actions**:
1. Create `backend/knowledge/knowledge_graph.py` as canonical implementation
2. Merge features from `backend/memory/knowledge_graph.py` (episodic, state tracking)
3. Create `backend/memory/knowledge_graph.py` as re-export module
4. Update all `from backend.memory.knowledge_graph import KnowledgeGraph` → `backend.knowledge.knowledge_graph`

**Validation**: `test_knowledge.py` passes, `test_probe.py` passes

### Step 3: Merge Brains (Session 3 — 4h)
**Goal**: Single `VelynxBrain` class with async+sync interfaces

**Actions**:
1. `backend/brain.py` becomes canonical (async, intent routing)
2. Add sync wrapper methods to `backend/brain.py` for legacy callers
3. `velynx_core/brain.py` becomes thin re-export

**Validation**: Both CLI and web interface work identically

### Step 4: Merge Self-Coders (Session 4 — 2h)
**Goal**: Single `SelfCoder` with all features

**Actions**:
1. Add `scan_codebase()`, `generate_fix()`, `SandboxExecutor` features to `backend/self_coder.py`
2. Keep LLM-free memory-only mode as fallback
3. Archive `velynx_core/self_coder.py`

**Validation**: `python -c "from backend.self_coder import SelfCoder; print(SelfCoder()._list_backend_files()[:3])"`

### Step 5: Break Circular Dependencies (Session 5 — 3h)
**Goal**: Clean import graph

**Actions**:
1. Create `backend/cognition/types.py` with shared data structures
2. Move `ReasoningStep`, `VelynxAnswer`, `Contradiction`, etc. to types module
3. Update all imports

**Validation**: `python -c "from backend.cognition.scenario_engine import parse_scenario"` and `from backend.cognition.metacog import reflect` work without ImportError

### Step 6: Centralize Configuration (Session 6 — 2h)
**Goal**: Single source of truth for paths, constants, parameters

**Actions**:
1. Create `backend/config/` package
2. Add `paths.py` (all file paths), `constants.py` (free-energy coefficients, thresholds)
3. Update all hardcoded paths and constants

**Validation**: System boots from any working directory

### Step 7: Archive Redundancies (Session 7 — 1h)
**Goal**: Remove dead code

**Actions**:
1. Move all files identified in reduction plan to `research_artifacts/archive/`
2. Add deprecation warnings to re-export modules
3. Run full test suite

**Validation**: `pytest backend/tests/` passes

---

## ROLLBACK PLAN

Every migration step produces a `velynx_core/velynx.py.bak` or equivalent before modification.
Rollback = restore `.bak` file and remove new code.

## EXPERIMENTS AFFECTED

| Experiment | Migration Impact |
|-----------|-----------------|
| benchmark.py | Imports from `validation/` — unaffected |
| run_benchmark_v2.py | Imports `scenario_engine` — affected by Step 5 |
| research_benchmark.py | Imports `research/` — unaffected |
| stability_audit.py | Imports `backend.orchestration` — archive (dead) |

## TESTING STRATEGY

1. **Unit tests**: Run after each step
2. **Integration**: Run `python -c "from backend.orchestrator import velynx_respond; print(velynx_respond('test'))"`
3. **Regression**: Run `pytest backend/tests/ -x`

## CONFIDENCE

| Step | Confidence | Reason |
|------|-----------|--------|
| 1: Core API | 0.85 | Backwards-compatible re-exports well-understood |
| 2: KG Merge | 0.65 | Two implementations with unknown behavioral differences |
| 3: Brains | 0.60 | Different APIs (sync/async, answer structures) |
| 4: Self-Coders | 0.75 | Feature sets partially overlap; no behavioral tests |
| 5: Cycle Break | 0.80 | Lazy imports already work; formalizing them is safe |
| 6: Config | 0.90 | Mechanical transformation; easy to verify |
| 7: Archive | 0.95 | No callers; trivial to restore |

## TIMELINE

| Step | Duration | Dependencies | Parallelizable? |
|------|----------|-------------|----------------|
| 1 | 4h | None | Yes (with 2) |
| 2 | 4h | None | Yes (with 1) |
| 3 | 4h | Step 1 | No |
| 4 | 2h | Steps 1, 3 | No |
| 5 | 3h | Steps 1-4 | No |
| 6 | 2h | Steps 1-5 | No |
| 7 | 1h | Steps 1-6 | No |

**Total critical path**: ~12h (Steps 1, 3, 4, 5, 6, 7 sequential)
**Total effort**: ~20h (with parallel Steps 1+2)
