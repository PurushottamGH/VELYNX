# Program C: Safe Removal Order

## Dependency-Topological Sequence

Each step removes a subsystem only after all its dependents have already been removed (or were never depended upon). At each step, the remaining experiment set is verified.

**Status categories:**
- `→ ARCHIVE` = remove from active tree, preserve in archive/
- `→ DELETE` = remove permanently
- `KEEP` = irreducible, must remain

---

## Phase 1: No-Brainer Removals (zero dependencies from experiment code)

These subsystems have no incoming dependencies from any experiment or production code path that experiments exercise.

| Step | Subsystem | Action | Rationale |
|------|-----------|--------|-----------|
| 1 | `searxng/` | → DELETE | Third-party Docker service. Not imported by Python code. Experiments use fallback chain if SearXNG unavailable. |
| 2 | `kiro-gateway/` | → DELETE | Third-party gateway. Not imported by any experiment. |
| 3 | `node_modules/` | → DELETE | JS dependencies. Not imported by any experiment. |
| 4 | `frontend/` | → ARCHIVE | React UI. No experiment reads or imports frontend/ code. All experiments run headlessly via CLI or pytest. |
| 5 | `experiments/` | → ARCHIVE | calculator.py, generated_tool.py, test_calc.py are toy/placeholder code. Not referenced by any experiment. |
| 6 | `docs/` | → ARCHIVE | Documentation files. No experiment reads them. |
| 7 | `scripts/` | → ARCHIVE | Operational utilities (start-frontend.ps1, test-api.ps1, etc.). No experiment imports them. |
| 8 | Root `.md` files (README, ablation_report, VELYNX_*.md, etc.) | → ARCHIVE | Documentation/benchmark prompts. Not imported by any experiment. Not executed. |
| 9 | `src/` (TypeScript) + `dist/` | → DELETE | TypeScript entry point. Not used by any experiment. |
| 10 | `tsconfig.json`, `package.json` (root) | → DELETE | TypeScript/Node config. Not used by any experiment. |

## Phase 2: Root Diagnostic Scripts (nothing depends on them)

| Step | Subsystem | Action | Rationale |
|------|-----------|--------|-----------|
| 11 | `find_ghosts.py` | → ARCHIVE | Debug utility. No experiment imports it. |
| 12 | `inspect_db.py`, `inspect_module.py`, `inspect_triple.py` | → ARCHIVE | Debug utilities. No experiment imports them. |
| 13 | `peek_code.py` | → ARCHIVE | Debug utility. No experiment imports it. |
| 14 | `find_the_truth.py` | → ARCHIVE | Debug utility. No experiment imports it. |
| 15 | `ghost_hunt.py` | → ARCHIVE | Debug utility. No experiment imports it. |
| 16 | `hunt_sqlite.py` | → ARCHIVE | Debug utility. |
| 17 | `debug_triage.py`, `diagnose_john_smith.py` | → ARCHIVE | Debug utilities. |
| 18 | `bootstrap_db.py` | → ARCHIVE | DB bootstrapping. Not needed after initial setup. |
| 19 | `candidate_audit.py` | → ARCHIVE | Debug audit. |
| 20 | `verify_installation.py` | → ARCHIVE | Install verification. Not an experiment. |
| 21 | `verify_recall_topology.py` | → ARCHIVE | Verification script. |
| 22 | `get_schema.py`, `generate_graph.py` | → ARCHIVE | Utilities. |
| 23 | `migrate_phase64.py` | → ARCHIVE | Migration script. |
| 24 | `_probe.py`, `_probe2.py`, `_probe3.py` | → ARCHIVE | Diagnostic probes. |

## Phase 3: Dead Code (no imports from any code path)

| Step | Subsystem | Action | Rationale |
|------|-----------|--------|-----------|
| 25 | `backend/agents/` | → ARCHIVE | `agent_coordinator.py` — stub with no detectable imports. Zero experiment impact. |
| 26 | `backend/tools/` | → ARCHIVE | `dedupe_directions.py`, `visualize_graph.py` — standalone utilities. Not imported by any experiment. |
| 27 | `backend/testing/` | → ARCHIVE | `diagnostic_test.py`, `life_simulator.py` — helper scripts. Not imported by any experiment. |
| 28 | `backend/contracts/` | → ARCHIVE | `predictive_core_spec.py` — spec file. Only imported by orchestration/validator.py which is not on any experiment critical path. |

## Phase 4: Decorative / Aesthetic (no scientific function)

| Step | Subsystem | Action | Rationale |
|------|-----------|--------|-----------|
| 29 | `backend/audio/` | → ARCHIVE | `vocal_tract.py` — TTS for REPL. Not imported by any experiment. No experiment depends on audio output. |

## Phase 5: Legacy / Superseded (newer implementation exists)

| Step | Subsystem | Action | Rationale |
|------|-----------|--------|-----------|
| 30 | `backend/cli.py` | → ARCHIVE | CLI entry point. Uses orchestrator.py. Not invoked by any experiment. |
| 31 | `backend/cli_ui.py` | → ARCHIVE | CLI UI helpers. Used by cli.py. Not invoked by any experiment. |
| 32 | `backend/chat.py` | → ARCHIVE | Chat interface. Not imported by any experiment. |
| 33 | `backend/orchestrator.py` | → ARCHIVE | Pre-FastAPI synchronous orchestrator. Superseded by `backend/app/pipeline.py`. Not imported by any experiment (only cli.py, which is also removed). |
| 34 | `backend/brain.py` | → ARCHIVE | VelynxBrain.think() — unified brain abstraction. No imports detected from any experiment or production file on the experiment path. Superseded by app/pipeline.py. |
| 35 | `backend/self_coder.py` | → ARCHIVE | Self-coding engine. Only imported by brain.py (also being removed). Superseded by agency/code_writer.py. |
| 36 | `cognitive_core.py` | → ARCHIVE | Self-contained C1-C3/C6 cognitive core. Standalone, not imported by any experiment. |
| 37 | `cognitive_health.py` | → ARCHIVE | Proxy to validation/ — all logic migrated to validation/{metrics,report}. Not imported by any experiment. |
| 38 | `concept_birth.py` | → ARCHIVE | Debug script. |
| 39 | `latent_cause_engine.py` | → ARCHIVE | Standalone experiment. Not a formal Program C experiment. |
| 40 | `night_learner.py` | → ARCHIVE | Wrapper around backend/learning/night_learner.py. Redundant. |
| 41 | `velynx_soul.py` | → ARCHIVE | Soul test script. Redundant with pytest test_soul_graph.py. |
| 42 | `environment.py` | → ARCHIVE | Environment test script. |
| 43 | `teach.py` | → ARCHIVE | Interactive teaching tool. Not used by any experiment. |

## Phase 6: Duplicated Functionality

| Step | Subsystem | Action | Rationale |
|------|-----------|--------|-----------|
| 44 | `velynx_core/` | → ARCHIVE | Standalone v2 core with memory/brain/learner/self_coder. All functionality duplicated and extended by `backend/{cognition,memory,learning,agency}`. Only experiment that breaks: EXP-0 (`test_velynx_core.py`). Decision: **ARCHIVE**. EXP-0 is an integration smoke test for the duplicated implementation. |

## Phase 7: Optional Infrastructure (no experiment strictly requires)

| Step | Subsystem | Action | Rationale |
|------|-----------|--------|-----------|
| 45 | `configs/` | → ARCHIVE | Configuration JSON files. benchmark.py provides defaults and CLI flags. |
| 46 | `data/` (except essential JSON schemas) | KEEP | Some data files are required by subsystems at runtime. Need per-file analysis. |
| 47 | `backend/wipe_db.py` | → ARCHIVE | DB utility. Not imported by any experiment. |
| 48 | `backend/diagnose_db.py` | → ARCHIVE | DB utility. Not imported by any experiment. |

## Phase 8: Supporting Subsystems (single-test dependencies)

These subsystems are required by the PYTEST experiment suite, but only by 1-2 test files each. If PYTEST is retained as an experiment, these must stay. Each removal breaks exactly one test.

| Step | Subsystem | Action | Rationale |
|------|-----------|--------|-----------|
| 49 | `backend/self_model/` | KEEP | Breaks `test_self_model.py` in PYTEST. Single-test dependency. |
| 50 | `backend/simulation/` | KEEP | Breaks `test_simulation_engine.py` in PYTEST. Single-test dependency. |
| 51 | `backend/nlp/` | KEEP | Breaks `test_temporal_parser.py` in PYTEST. Single-test dependency. |
| 52 | `backend/ops/` | KEEP | Breaks `test_ops.py` in PYTEST + models/llm_client.py circuit breaker import. |
| 53 | `backend/runtime/` | KEEP | Breaks `test_event_system.py` in PYTEST + evaluation/ trial_runner/session_replay imports. |

## Phase 9: Core (irreducible)

These subsystems form Minimal Program C. They cannot be removed without breaking experiments.

| Step | Subsystem | Action | Rationale |
|------|-----------|--------|-----------|
| 54 | `backend/__init__.py` | KEEP | Makes backend a Python package. ALL imports fail without it. |
| 55 | `backend/cognition/` | KEEP | Core reasoning engine. Required by ALL formal experiments. |
| 56 | `backend/memory/` | KEEP | Three-tier memory. Required by ALL experiments. |
| 57 | `backend/pipeline/` | KEEP | Inference wiring. Required by LF, COG-S, PYTEST. |
| 58 | `backend/knowledge/` | KEEP | Knowledge graph. Required by LF, COG-S, PYTEST. |
| 59 | `backend/learning/` | KEEP | Learning loops. Required by LF, COG-S, PYTEST. |
| 60 | `backend/agency/` | KEEP | Curiosity/goal generation. Required by LF, COG-S, PYTEST. |
| 61 | `backend/reflection/` | KEEP | Reasoning audit. Required by LF, PYTEST. |
| 62 | `backend/conversation/` | KEEP | Dialogue management. Required by LF, COG-S, PYTEST. |
| 63 | `backend/retrieval/` | KEEP | External search. Required by LF, PYTEST. |
| 64 | `backend/app/` | KEEP | FastAPI + answer_question. Required by LF, COG-S, PYTEST. |
| 65 | `backend/models/` | KEEP | Data models. Required by LF, PYTEST. |
| 66 | `backend/database/` | KEEP | Persistence. Required by LF, PYTEST. |
| 67 | `backend/abstraction/` | KEEP | Belief formation. Required transitively via cognition. |
| 68 | `backend/soul/` | KEEP | Soul graph. Required by B-V2, LF, PYTEST. |
| 69 | `backend/metacognition/` | KEEP | Meta-monitoring. Required by PYTEST. |
| 70 | `backend/evaluation/` | KEEP | Benchmark infrastructure. Required by PYTEST. |
| 71 | `velynx/` | KEEP | Brain stem. Required by LF, COG-S, PYTEST. |
| 72 | `validation/` | KEEP | Experiment harness. Required by R1, R2A, R3, C8, R3C, B-PROD. |
| 73 | `research/` | KEEP | Research infrastructure. Required by R1, R2A, R3, R3E, R3F. |
| 74 | `curriculum/` | KEEP | Content files. Required transitively by learning subsystem. |

---

## Removal Sequence Summary

```
Phase 1  (10 steps): searxng/, kiro-gateway/, node_modules/, frontend/,
          experiments/, docs/, scripts/, root .md files, src/dist/, tsconfig/package
Phase 2  (14 steps): Root diagnostic scripts (find_ghosts, inspect_*, probe, etc.)
Phase 3  (4 steps):  backend/agents/, backend/tools/, backend/testing/,
          backend/contracts/
Phase 4  (1 step):   backend/audio/
Phase 5  (14 steps): cli.py, cli_ui.py, chat.py, orchestrator.py, brain.py,
          self_coder.py, cognitive_core.py, cognitive_health.py, concept_birth.py,
          latent_cause_engine.py, night_learner.py, velynx_soul.py, environment.py,
          teach.py
Phase 6  (1 step):   velynx_core/ (breaks EXP-0 only)
Phase 7  (3 steps):  configs/, data/ (per-file), wipe_db.py, diagnose_db.py
Phase 8  (5 steps):  self_model/, simulation/, nlp/, ops/, runtime/
                     → KEEP (single-test breakage deemed acceptable)
Phase 9  (21 steps): All core subsystems → KEEP (irreducible)
```

**Total ARCHIVE/DELETE: ~47 subsystems/packages**
**Total KEEP: ~21 subsystems (Minimal Program C)**
**Steps until first core break: 48 removals before any experiment is affected**
