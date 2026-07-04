# Program D — Hidden Coupling Detection

## Purpose
Identify implicit, non-obvious dependencies between modules that are not expressed through explicit imports.

---

## 1. FILE SYSTEM COUPLING

| # | Module | Coupled To | Mechanism | Risk |
|---|--------|-----------|-----------|------|
| 1 | `backend/cognition/metacog.py:30` | Filesystem at `data/gap_log.jsonl` | Writes directly to repo-relative path | HIGH |
| 2 | `backend/cognition/metacog.py:31` | Filesystem at `backend/soul/concepts.json` | Reads soul concepts from hardcoded path | HIGH |
| 3 | `backend/cognition/unified_pipeline.py:22` | Filesystem at `velynx_data/improvement/` | `_DATA_DIR` derived from `VELYNX_DATA_DIR` env or `.` | MEDIUM |
| 4 | `backend/cognition/advanced_cognition.py:23` | Filesystem at `velynx_data/cognition/` | Same pattern as above | MEDIUM |
| 5 | `velynx_core/self_coder.py:543-544` | Filesystem — `.py.velynx_backup` suffix | Backup convention coupled to restore logic | MEDIUM |
| 6 | `velynx_core/velynx.py:32` | Filesystem at `velynx_core/velynx.log` | Hardcoded log path | LOW |
| 7 | `backend/orchestrator.py:27` | Filesystem — `sys.path` manipulation | Mutates `sys.path` as side effect | MEDIUM |

## 2. ENVIRONMENT VARIABLE COUPLING

| # | Variable | Read By | Effect | Risk |
|---|----------|---------|--------|------|
| 1 | `VELYNX_VERBOSE` | `velynx_core/velynx.py:237` | Shows reasoning chain | LOW |
| 2 | `VELYNX_SANDBOX` | `backend/self_coder.py:253` | Passed to subprocess env | MEDIUM |
| 3 | `VELYNX_DATA_DIR` | `backend/cognition/unified_pipeline.py:22` | Controls data directory | MEDIUM |
| 4 | `VELYNX_TEST_MODE` | `ghost_hunt.py:13` | Enables test mode | LOW |

## 3. DATABASE SCHEMA COUPLING

| # | DB File | Read By | Schema Assumption | Risk |
|---|---------|---------|-------------------|------|
| 1 | `brain_stem.db` | `backend/cognition/predictive_core.py:371-383` | Assumes `living_edges` table with `source, target, weight_alpha, weight_beta, confidence` | HIGH |
| 2 | `velynx_state.db` | `verify_recall_topology.py` | Assumes `recall_events` table | MEDIUM |
| 3 | `*.db` (generic) | `backend/wipe_db.py`, `backend/diagnose_db.py` | Assumes `episodes`, `relationships`, `concepts` tables | MEDIUM |

## 4. IMPLICIT ORDERING COUPLING

| # | Module | Depends On | Why |
|---|--------|-----------|-----|
| 1 | `backend/orchestrator.py:warmup_system()` | `seed_concept_states_from_soul()` before `velynx_respond()` | Predictive tables must be seeded before first query |
| 2 | `backend/brain.py:think()` | `boot()` called first | Loads KG + VS before reasoning |
| 3 | `validation/runner.py` | C8 pipeline order: MemoryScheduler → CandidateGenerator → ReplayEngine → DecisionPolicy | Sequence enforced by pipelined design |

## 5. SHARED MUTABLE STATE COUPLING

| # | Module | Global State | Accessed By | Risk |
|---|--------|-------------|-------------|------|
| 1 | `backend/orchestrator.py` | `MEMORY`, `_code_writer`, `_vocal_tract`, `_bridge`, `_warmed_up` | Module-level singletons | MEDIUM |
| 2 | `cognitive_core.py` | `CognitiveEngine` instance state | Tick-by-tick mutation | MEDIUM |
| 3 | `backend/cognition/advanced_cognition.py` | `curiosity_engine`, `contradiction_resolver`, `cognition_coordinator` | Module-level singletons | MEDIUM |
| 4 | `backend/cognition/metacog.py` | `_load_soul_concepts()` result (not cached) | Called on every `evaluate_output()` | LOW |

## Experiments Affected
- All experiments that write `gap_log.jsonl` will fail if `data/gap_log.jsonl` is missing
- Predictive core tests fail if `brain_stem.db` schema changes
- File system-dependent experiments may be non-reproducible across machines

## Removal Risk
- **HIGH**: Database schema coupling means DB migration breaks predictive core
- **MEDIUM**: File path coupling breaks if working directory changes
- **LOW**: Environment variable coupling is easily documented

## Regression Tests
- Add test for `gap_log.jsonl` write permissions
- Add test for `VELYNX_DATA_DIR` resolution
- Add schema migration tests for `brain_stem.db`

## Confidence
- 0.90 for file system coupling (confirmed by code reading)
- 0.80 for DB schema coupling (confirmed by tracing column usage)
- 0.70 for env var coupling (some may be undocumented)
