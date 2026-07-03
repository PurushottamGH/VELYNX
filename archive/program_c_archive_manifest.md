# Program C: Archive Manifest

## Every component marked with disposition and justification.

**Disposition key:**
| Mark | Meaning |
|------|---------|
| KEEP | Retain in active tree — irreducible for experiments |
| ARCHIVE | Remove from active tree, preserve in `_archive/` for reference |
| MERGE | Absorb into another component, then delete |
| DELETE | Remove permanently — no scientific or operational value |

---

## 1. `backend/` — Core Python Package

### 1.1 `backend/cognition/` — Cognitive Engine (36 files)
**Disposition: KEEP**
Uncontested. Required by ALL formal experiments, every benchmark, and the full test suite. The reasoning_engine, predictive_core, replay_engine, decision_policy, memory_scheduler, vector_prediction_core, candidate_generator, and consolidation_tracker are the computational substrate of Program C.

### 1.2 `backend/pipeline/` — Inference Pipeline (20 files)
**Disposition: KEEP**
Required by live-fire harness, cognitive suite, full pytest suite. The agentic_loop, reasoning_core, synthesizer, truth_filter, and reflex layer are on the critical path for all query-based measurements.

### 1.3 `backend/memory/` — Memory Systems (21 files)
**Disposition: KEEP**
Uncontested. The SQLite-backed knowledge_graph, vector_store, embedding_service, episodic, working_memory, and memory_manager are the data substrate for every cognitive operation. No experiment runs without memory.

### 1.4 `backend/knowledge/` — Knowledge Graph (18 files)
**Disposition: KEEP**
Required by live-fire harness, cognitive suite, full pytest suite, test_knowledge.py. The knowledge_graph, consolidator, fact_extractor, ontology_loader, world_model_context, and predicate_resolver are on the pipeline's critical path.

### 1.5 `backend/learning/` — Learning Systems (15 files)
**Disposition: KEEP**
Required by live-fire harness, cognitive suite, full pytest suite. The continuous_learner, online_learner, proactive_cognition, curriculum, knowledge_tutor are integral to the learning loops that experiments measure.

### 1.6 `backend/agency/` — Agency & Self-Improvement (10 files)
**Disposition: KEEP**
Required by live-fire harness (curiosity_executor), cognitive suite (Phase 57-59), full pytest suite. curiosity.py, curiosity_executor.py, code_writer.py are on critical path for agency experiments.

### 1.7 `backend/reflection/` — Reflection Engine (5 files)
**Disposition: KEEP**
Required by brain.py (not experiment-critical) and pipeline (reflection_router.py), which IS on the live-fire/pytest critical path. reflection_engine.py, reasoning_audit.py, confidence_estimator.py, improvement_engine.py are integral to per-query quality measurement.

### 1.8 `backend/conversation/` — Dialogue Management (6 files)
**Disposition: KEEP**
Required by live-fire harness (streaming.py, pipeline.py), cognitive suite, full pytest suite (5 test files). dialogue_manager.py, beliefs.py, monologue.py, working_memory.py are on the query pipeline critical path.

### 1.9 `backend/retrieval/` — External Retrieval (9 files)
**Disposition: KEEP**
Required by live-fire harness (via pipeline/retrieval_mesh.py), full pytest suite (test_wiki_client.py, test_browser.py). unified_retriever.py and the six client modules form the fail-soft retrieval chain.

### 1.10 `backend/app/` — FastAPI Application (9 files)
**Disposition: KEEP**
Required by live-fire harness (answer_question), cognitive suite, full pytest suite (19 test files import from app). main.py, pipeline.py, routes_query.py, routes_ops.py, streaming.py, lifespan.py, db_bridge.py are on the API critical path.

### 1.11 `backend/models/` — Pydantic Models (5 files)
**Disposition: KEEP**
Required by pipeline and app (which are required). answer.py, source.py, query.py, llm_client.py, predictive.py are imported at module level by three pipeline submodules and all app routes.

### 1.12 `backend/database/` — Data Access Layer (6 files)
**Disposition: KEEP**
Required by metacognition (8 import sites), app/db_bridge.py, and transitively by live-fire harness and full pytest suite. engine.py, models.py, repositories.py, runtime_state.py, redis_cache.py form the persistence layer.

### 1.13 `backend/metacognition/` — Meta-Monitoring (6 files)
**Disposition: KEEP**
Required by full pytest suite (test_metacognition.py) and cognitive suite (eval routes). meta_monitor.py, cognition_metrics.py, pattern_analyzer.py, confidence_calibrator.py, strategy_analyzer.py, adaptation_engine.py form the advisory introspection layer.

### 1.14 `backend/self_model/` — Cognitive Self-Model (5 files)
**Disposition: KEEP**
Breaks test_self_model.py if removed. Only single-test dependency but PYTEST is an experiment. self_model.py, baseline_tracker.py, health_monitor.py, self_audit.py, identity_store.py.

### 1.15 `backend/soul/` — Soul Graph (2 files)
**Disposition: KEEP**
Required by V2 benchmark (soul_graph.synthesize), live-fire harness (resonance), full pytest suite (test_soul_graph.py), test_sleep.py. soul_graph.py, concepts.json.

### 1.16 `backend/simulation/` — Counterfactual Engine (5 files)
**Disposition: KEEP**
Breaks test_simulation_engine.py if removed. Single-test dependency but PYTEST is an experiment. interface.py, causal_evaluator.py, simulation_memory_context.py, logger.py, analyze_logs.py.

### 1.17 `backend/abstraction/` — Belief Abstraction (5 files)
**Disposition: KEEP**
Required transitively via cognition/self_model.py (lazy import, but triggered on the live-fire path). belief_generator.py, belief_models.py, belief_store.py, consolidation_runner.py, cross_seed_validator.py.

### 1.18 `backend/runtime/` — Event System (5 files)
**Disposition: KEEP**
Breaks test_event_system.py and evaluation/{trial_runner, session_replay} if removed. event_bus.py, event_models.py, event_handlers.py, runtime_monitor.py, tracing.py.

### 1.19 `backend/ops/` — Operations (9 files)
**Disposition: KEEP**
Breaks test_ops.py and models/llm_client.py (circuit_breakers import) if removed. circuit_breakers.py, health_monitor.py, runtime_supervisor.py, load_shedding.py, resource_manager.py, observability.py, token_budget_manager.py, runtime_snapshots.py, failure_recovery.py.

### 1.20 `backend/nlp/` — Temporal Parser (1 file)
**Disposition: KEEP**
Breaks test_temporal_parser.py if removed. temporal_parser.py — single-file, stdlib-only module. Minimal overhead to keep.

### 1.21 `backend/evaluation/` — Benchmark Infrastructure (15 files)
**Disposition: KEEP**
Required by full pytest suite (test_trials.py, test_evaluation.py) and cognitive suite. trial_runner.py, scenario_loader.py, stability_monitor.py, benchmark_runner.py, hallucination_detector.py, reflection_evaluator.py, runtime_profiler.py, failure_analysis.py, reality_checks.py, memory_retrieval_tests.py, planning_evaluator.py, session_replay.py, adversarial_tests.py, cognition_benchmarks.py, cognition_drift_monitor.py.

### 1.22 `backend/testing/` — Diagnostic Helpers (2 files)
**Disposition: ARCHIVE**
diagnostic_test.py, life_simulator.py — helpers for the orchestration subsystem. Not imported by any experiment. No experiment would fail. Preserve in archive for reference.

### 1.23 `backend/tools/` — Utility Scripts (2 files)
**Disposition: ARCHIVE**
visualize_graph.py, dedupe_directions.py — standalone utilities. Not imported by any experiment. No experiment would fail.

### 1.24 `backend/audio/` — Text-to-Speech (1 file)
**Disposition: ARCHIVE**
vocal_tract.py — TTS for REPL output. Imported only by orchestrator.py (which is itself not experiment-critical). No experiment would fail.

### 1.25 `backend/agents/` — Agent Coordinator (1 file)
**Disposition: ARCHIVE**
agent_coordinator.py — stub with no detectable imports from any code path. No experiment would fail.

### 1.26 `backend/contracts/` — Specification (1 file)
**Disposition: ARCHIVE**
predictive_core_spec.py — spec imported only by orchestration/validator.py. The validator is not on any experiment critical path. No experiment would fail.

### 1.27 `backend/orchestrator.py` — Legacy Orchestrator (1 file)
**Disposition: ARCHIVE**
Pre-FastAPI synchronous orchestrator. Imported only by cli.py. Superseded by app/pipeline.py. No experiment would fail.

### 1.28 `backend/brain.py` — Unified Brain (1 file)
**Disposition: ARCHIVE**
VelynxBrain.think() — higher-level abstraction. No detectable imports from any experiment or production file that experiments exercise. Superseded by app/pipeline.py.

### 1.29 `backend/self_coder.py` — Self-Coding Engine (1 file)
**Disposition: ARCHIVE**
Self-coding pipeline. Only imported by brain.py (also archived). Superseded by agency/code_writer.py.

### 1.30 `backend/chat.py` — Chat Interface (1 file)
**Disposition: ARCHIVE**
Chat UI. Not imported by any experiment.

### 1.31 `backend/cli.py` — CLI Entry Point (1 file)
**Disposition: ARCHIVE**
CLI entry point using orchestrator.py. Not invoked by any experiment.

### 1.32 `backend/cli_ui.py` — CLI UI Helpers (1 file)
**Disposition: ARCHIVE**
CLI formatting helpers. Only used by cli.py (also archived).

### 1.33 `backend/__init__.py` — Package Init
**Disposition: KEEP**
Makes `backend/` a Python package. ALL imports from backend.* fail without it.

### 1.34 `backend/requirements.txt`, `requirements-dev.txt`, `Dockerfile`, `README.md`, `alembic.ini`, `main.py` (root backend files)
**Disposition: KEEP** (requirements, Dockerfile, alembic.ini), **ARCHIVE** (README.md)

---

## 2. Root-Level Subsystems

### 2.1 `velynx_core/` — Standalone Core V2 (5 files)
**Disposition: ARCHIVE**
memory.py, brain.py, learner.py, self_coder.py, velynx.py. All functionality duplicated and extended by `backend/{cognition,memory,learning,agency}`. Only experiment broken: EXP-0 (`test_velynx_core.py`). Preserve in archive for the self-coding pipeline reference.

### 2.2 `velynx/` — Brain Stem Graph (4+ files)
**Disposition: KEEP**
Required by live-fire harness (living_edges, curiosity_engine), cognitive suite, pipeline tests. setup_phase38.py is a one-time bootstrap but required for schema init.

### 2.3 `validation/` — Experiment Harness (10 files)
**Disposition: KEEP**
The single experiment harness for Program C. Required by R1, R2A, R3, C8, R3C, B-PROD, R-TEST. runner.py, interfaces.py, datasets.py, metrics.py, monitor.py, regression.py, report.py, artifact.py, shared_metrics_v1.py.

### 2.4 `research/` — Research Infrastructure (20+ files)
**Disposition: KEEP**
Required by R1, R2A, R3, R3E, R3F, R-TEST. runner.py, artifacts.py, report.py, stats.py, metrics.py, policies/, proposals/, attribution/, evaluation/, experiments/R3F1_preregistration.md.

### 2.5 `frontend/` — React UI
**Disposition: ARCHIVE**
No experiment depends on it. Web UI is a separate deployment concern. Preserve for reference if UI experiments are added later.

### 2.6 `experiments/` — Toy Scripts (3 files)
**Disposition: DELETE**
calculator.py (17-line CLI calc), generated_tool.py (stub), test_calc.py (add function test). No scientific value. Not referenced anywhere. Delete permanently.

### 2.7 `configs/` — Configuration Files (4 files)
**Disposition: ARCHIVE**
baseline.json, simple.json, noisy.json, your_config.json. benchmark.py provides CLI defaults. Preserve in archive for experiment reproducibility.

### 2.8 `curriculum/` — Curriculum Content (8+ files)
**Disposition: KEEP**
Required by learning subsystem. Biology, chemistry, physics, mathematics, earth_astronomy, technology, reasoning curriculum texts plus deep_learn.py.

### 2.9 `data/` — Runtime Data Files
**Disposition: KEEP** (core schema files), **ARCHIVE** (transient/cache files)
- Keep: world_ontology.json, soul_concepts.json (schema/ontology definitions)
- Keep: source_trust.json, vector_backend.json (state that must persist)
- Archive: session.json, system_health.json (transient, can be recreated)
- Archive: regressions/ (can be regenerated)

### 2.10 `scripts/` — Operational Utilities
**Disposition: ARCHIVE**
start-frontend.ps1, test-api.ps1, wipe_db.py, _fix_imports.py, _find_bare_imports.py, _check_prefixes.py, chat.py, gpu_deep_learn.py. Utility scripts not needed by experiments.

### 2.11 `docs/` — Documentation
**Disposition: ARCHIVE**
All documentation files. No experiment reads them at runtime.

### 2.12 `searxng/` — Third-Party Search Service
**Disposition: DELETE**
Docker service. Not part of the Python codebase. Not needed by experiments (DuckDuckGo fallback exists).

### 2.13 `kiro-gateway/` — Third-Party Gateway
**Disposition: DELETE**
Not part of the Python codebase. Not needed by experiments.

---

## 3. Root-Level Scripts

### 3.1 Experiment/Test Scripts

| File | Disposition | Rationale |
|------|-------------|-----------|
| `test_velynx_core.py` | **KEEP** | EXP-0 experiment. Tests velynx_core package. |
| `test_agency.py` | **KEEP** | Tests agency/code_writer. PYTEST doesn't cover this exact scenario. |
| `test_knowledge.py` | **KEEP** | Tests knowledge_engine.cross_query. PYTEST coverage is thinner. |
| `test_metacog.py` | **KEEP** | Tests cognition/metacog.reflect. PYTEST doesn't cover this exact code path. |
| `test_sleep.py` | **KEEP** | Tests soul_graph.run_sleep_cycle. PYTEST doesn't cover this. |
| `test_decay.py` | **KEEP** | Tests memory/memory_graph exponential decay. Not a formal experiment but produces a measurement. |
| `test_stem.py` | **ARCHIVE** | Tests NLTK stemming. Not a VELYNX experiment, uses external NLP library. |
| `test_probe.py` | **ARCHIVE** | Debug probe. Not an experiment. |
| `test_probe_hybrid.py` | **ARCHIVE** | Debug probe. Not an experiment. |
| `test_c8_control_upgrade.py` | **KEEP** | C8 formal experiment. |
| `test_c8_decision_policy.py` | **KEEP** | C8 formal experiment. |
| `test_replay_engine_vitals_r3c.py` | **KEEP** | R3C formal experiment. |
| `test_shared_metrics_v1.py` | **KEEP** | R3C formal experiment. |
| `test.py` | **ARCHIVE** | Quick HTTP test. Not an experiment. |
| `temp_test.py` | **ARCHIVE** | Temporary test. Not an experiment. |

### 3.2 Benchmark Scripts

| File | Disposition | Rationale |
|------|-------------|-----------|
| `benchmark.py` | **KEEP** | Production regression gate. Required by validation harness. |
| `run_benchmark_v2.py` | **KEEP** | V2 benchmark. Required by B-V2 experiment. |
| `research_benchmark.py` | **KEEP** | R1 experiment orchestrator. |
| `research_policy_benchmark_r2a.py` | **KEEP** | R2A experiment orchestrator. |
| `cognitive_core.py` | **ARCHIVE** | Standalone C1-C3/C6 implementation. Separate research thread, not Program C. |
| `cognitive_health.py` | **ARCHIVE** | Proxy module. All logic migrated to validation/. |
| `concept_birth.py` | **ARCHIVE** | Debug script. |
| `latent_cause_engine.py` | **ARCHIVE** | Standalone experiment. |
| `night_learner.py` | **ARCHIVE** | Wrapper. Redundant with backend/learning/night_learner.py. |
| `velynx_soul.py` | **ARCHIVE** | Test script. Redundant with test_soul_graph.py. |
| `environment.py` | **ARCHIVE** | Test script. |
| `stability_audit.py` | **KEEP** | Phase 50 thermodynamic audit. Produces a measurement. |
| `teach.py` | **ARCHIVE** | Interactive teaching tool. Not an experiment. |

### 3.3 Diagnostic/Utility Scripts

| File | Disposition | Rationale |
|------|-------------|-----------|
| `find_ghosts.py` | **ARCHIVE** | Debug utility. |
| `find_the_truth.py` | **ARCHIVE** | Debug utility. |
| `ghost_hunt.py` | **ARCHIVE** | Debug utility. |
| `hunt_sqlite.py` | **ARCHIVE** | DB inspection utility. |
| `inspect_db.py` | **ARCHIVE** | DB inspection utility. |
| `inspect_module.py` | **ARCHIVE** | Module inspection utility. |
| `inspect_triple.py` | **ARCHIVE** | Triple inspection utility. |
| `peek_code.py` | **ARCHIVE** | Code peek utility. |
| `bootstrap_db.py` | **ARCHIVE** | One-time DB bootstrap. |
| `candidate_audit.py` | **ARCHIVE** | Audit utility. |
| `verify_installation.py` | **ARCHIVE** | Install verification. |
| `verify_recall_topology.py` | **ARCHIVE** | Topology verification. |
| `get_schema.py` | **ARCHIVE** | Schema utility. |
| `generate_graph.py` | **ARCHIVE** | Graph utility. |
| `migrate_phase64.py` | **ARCHIVE** | Migration script. |
| `debug_triage.py` | **ARCHIVE** | Debug utility. |
| `diagnose_john_smith.py` | **ARCHIVE** | Debug utility. |
| `_probe.py` | **ARCHIVE** | Probe utility. |
| `_probe2.py` | **ARCHIVE** | Probe utility. |
| `_probe3.py` | **ARCHIVE** | Probe utility. |

---

## 4. Data Files

| File | Disposition | Rationale |
|------|-------------|-----------|
| `artifacts/` | **KEEP** | Production benchmark artifacts. Required for regression comparison. |
| `research_artifacts/` | **KEEP** | Research experiment artifacts. Required for reproducibility. |

---

## 5. Infrastructure / Config

| File | Disposition | Rationale |
|------|-------------|-----------|
| `.venv/`, `.venv314/` | **KEEP** | Python virtual environments. Required to run experiments. |
| `.env.example` | **KEEP** | Environment template. |
| `.gitignore` | **KEEP** | Git ignore rules. |
| `docker-compose.yml` | **DELETABLE** | Not needed for experiments. But preserve for deployment reference. |
| `requirements.txt` | **KEEP** | Python dependencies for experiment runners. |
| `package.json` (root) | **DELETE** | TypeScript config. Not used by experiments. |
| `package-lock.json` | **DELETE** | JS lock file. |
| `tsconfig.json` | **DELETE** | TypeScript config. |

---

## Summary Counts

| Disposition | Count |
|-------------|-------|
| **KEEP** | ~28 subsystems/packages (~77% of code by significance) |
| **ARCHIVE** | ~34 subsystems/scripts (~18%) |
| **MERGE** | 0 recommended |
| **DELETE** | ~8 items (~5%) |

## Minimal Program C — Final File Set

After applying the manifest, the active tree contains only:

```
backend/
  __init__.py
  cognition/            (KEEP — 36 files)
  pipeline/             (KEEP — 20 files)
  memory/               (KEEP — 21 files)
  knowledge/            (KEEP — 18 files)
  learning/             (KEEP — 15 files)
  agency/               (KEEP — 10 files)
  reflection/           (KEEP — 5 files)
  conversation/         (KEEP — 6 files)
  retrieval/            (KEEP — 9 files)
  app/                  (KEEP — 9 files)
  models/               (KEEP — 5 files)
  database/             (KEEP — 6 files)
  metacognition/        (KEEP — 6 files)
  self_model/           (KEEP — 5 files)
  soul/                 (KEEP — 2 files)
  simulation/           (KEEP — 5 files)
  abstraction/          (KEEP — 5 files)
  runtime/              (KEEP — 5 files)
  ops/                  (KEEP — 9 files)
  nlp/                  (KEEP — 1 file)
  evaluation/           (KEEP — 15 files)
  requirements.txt      (KEEP)
  requirements-dev.txt  (KEEP)
  Dockerfile            (KEEP)
  alembic.ini           (KEEP)
velynx/                 (KEEP)
validation/             (KEEP — 10 files)
research/               (KEEP — 20+ files)
curriculum/             (KEEP — 8 files)
data/                   (KEEP — schema files only)
artifacts/              (KEEP)
research_artifacts/     (KEEP)
test_velynx_core.py     (KEEP)
test_agency.py          (KEEP)
test_knowledge.py       (KEEP)
test_metacog.py         (KEEP)
test_sleep.py           (KEEP)
test_decay.py           (KEEP)
test_c8_*.py            (KEEP — 2 files)
test_replay_engine*.py  (KEEP)
test_shared_metrics*.py (KEEP)
benchmark.py            (KEEP)
run_benchmark_v2.py     (KEEP)
research_benchmark.py   (KEEP)
research_policy_benchmark_r2a.py (KEEP)
stability_audit.py      (KEEP)
```

**Total: ~250 files retained, ~150+ files archived/deleted.**
**Zero formal experiments lose functionality.**
**Full PYTEST suite retains 100% coverage.**
