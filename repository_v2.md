# VELYNX Repository v2 — Canonical Future Structure

**Design principle:** Research-first organization. Every directory has exactly one responsibility. No duplication. One source of truth. The layout reflects the scientific hierarchy of the program, not the engineering convenience of the build.

**Program taxonomy (unchanged):**
- **Program A** — Calibrated live-truth retrieval (honest product path)
- **Program B** — Soul Graph (affective concept graph, authored artifact)
- **Program C** — Symbolic cognitive stack (engineering-retained to run experiments)
- **Program D** — Falsifiable experimental restatement (audit/reduction program)

---

## Foundation

The irreducible scientific substrate. Nothing here is decorative — every document is either a hypothesis statement, a kill criterion, or a formal ontology.

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `foundation/hypothesis/` | Central hypothesis (H\*), sub-hypotheses H1/H2/H3, and their falsifiable restatements | `central_hypothesis.md`, `H1_calibration.md`, `H2_affective_indexing.md`, `H3_emergent_development.md` |
| `foundation/assumptions/` | All load-bearing assumptions, reduced to the three irreducible (I1/I2/I3). Assumption ledger, coverage matrix, parameter atlas | `assumption_ledger.md`, `assumption_coverage_matrix.csv`, `parameter_atlas.md` |
| `foundation/kill_criteria/` | Kill criteria K1–K10 (each wired, not decorative). Program-level kill criterion | `kill_criteria.md`, `kill_criteria_validation_report.md` |
| `foundation/mathematics/` | The reduced mathematical substrate (5 primitives). Mathematical provenance of every formula. Variable dependency graph | `mathematical_foundation.md`, `variable_provenance.md`, `variable_dependency_graph.graphml`, `variable_dependency_matrix.csv` |
| `foundation/architecture/` | System architecture description, layer boundaries, module dependency graphs | `architecture.md`, `dependency_graph.graphml`, `dependency_matrix.csv`, `layer_diagram.mmd` |
| `foundation/novelty/` | Novelty analysis against 11 reference fields. Publication test | `novelty_analysis.md`, `publication_test.md` |

**Owner:** Principal Investigator (Program D)
**Scientific role:** Defines what is true, what is assumed, what is killable
**Engineering role:** None (pure research documentation)
**Dependent experiments:** All experiments (they test these hypotheses)
**Would be cited by:** Every paper derived from this program (H\* paper, H2 paper, negative-results paper)
**Category:** Foundation

---

## Core

The reusable scientific machinery — primitives and measurement infrastructure that all experiments share. One implementation of each primitive, no duplication.

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `core/predictors/` | Growable predictor class implementations (Dirichlet–Markov conjugate predictor, etc.) | `dirichlet_markov.py`, `base.py`, `__init__.py` |
| `core/emergence/` | Emergence statistics: NMI estimator, null-referenced construction, held-out split logic | `emergence_statistic.py`, `null_referenced_test.py` |
| `core/mdl/` | MDL growth operator: description-length calculation, concept-birth ledger | `mdl_growth.py`, `concept_birth_ledger.py` |
| `core/measurement/` | Proper scoring rules (log-loss), metrics, observability instrumentation | `proper_scoring.py`, `metrics.py`, `observability.py` |
| `core/controls/` | Null/baseline model implementations: fixed-capacity predictor, capacity-matched random-growth, shuffled-input control | `fixed_capacity.py`, `random_growth.py`, `shuffled_input.py` |

**Owner:** Research Engineering Lead
**Scientific role:** Implements the five primitives from the mathematical foundation (I1–I3, log-loss, MDL trigger, emergence statistic)
**Engineering role:** Single source of truth for predictive machinery; all experiments import from here
**Dependent experiments:** E0, R1–R3F, EXP-0–EXP-4 (all experimental measurement)
**Would be cited by:** Methodology section of every experimental paper
**Category:** Core

---

## Experiments

Each experiment is self-contained. It imports from `core/` and writes results to `artifacts/`. No shared mutable state between experiments.

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `experiments/E0/` | Emergence-vs-injection discrimination on nonlinear-latent stream (the central experiment that decides H\*) | `preregistration.md`, `protocol.md`, `run.py`, `analysis.py`, `detectors.py`, `dataset.py`, `leakage_check.py`, `paraphrases.json` |
| `experiments/R1/` | Free-energy consolidation policy ablation (72 experiments, already run) | `preregistration.md`, `protocol.md`, `run.py`, `analysis.py` |
| `experiments/R2/` | (Reserved for R2 family) | — |
| `experiments/R3F/` | R3F1 formal benchmark suite | `preregistration.md`, `protocol.md`, `run.py`, `analysis.py` |
| `experiments/EXP1/` | Calibration curve (H1 — ECE < 0.1) | `preregistration.md`, `protocol.md`, `run.py`, `analysis.py` |
| `experiments/EXP2/` | Affective indexing test (H2 — framed vs unframed) | `preregistration.md`, `protocol.md`, `run.py`, `analysis.py` |
| `experiments/EXP3/` | Minimal predictive organism (H3) | `preregistration.md`, `protocol.md`, `run.py`, `analysis.py` |
| `experiments/EXP4/` | Cycle bootstrapping (gated behind EXP-3) | `preregistration.md`, `protocol.md`, `run.py`, `analysis.py` |
| `experiments/coverage/` | Experiment-to-component coverage matrix | `experiment_coverage_matrix.csv` |

**Owner:** PI + Research Engineering Lead (joint)
**Scientific role:** Each experiment tests exactly one falsifiable hypothesis; produces one data artifact
**Engineering role:** Run scripts + analysis scripts, each scoped to one experiment
**Dependent experiments:** None (independent by construction)
**Would be cited by:** The specific experimental paper (E0→H\* paper, EXP1→calibration paper, etc.)
**Category:** Experiments

---

## Benchmarks

Evaluation harnesses and benchmark suites shared across experiments.

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `benchmarks/evaluation/` | Benchmark runner, scenario loader, trial runner, adversarial tests | `benchmark_runner.py`, `scenario_loader.py`, `trial_runner.py`, `adversarial_tests.py` |
| `benchmarks/cognition/` | Cognition-specific benchmarks (cognition_benchmarks.py, drift monitor, memory retrieval tests, planning evaluator) | `cognition_benchmarks.py`, `cognition_drift_monitor.py`, `memory_retrieval_tests.py`, `planning_evaluator.py` |
| `benchmarks/reflection/` | Reflection quality evaluation, reality checks | `reflection_evaluator.py`, `reality_checks.py` |
| `benchmarks/monitoring/` | Runtime profiler, stability monitor, session replay | `runtime_profiler.py`, `stability_monitor.py`, `session_replay.py` |
| `benchmarks/hallucination/` | Hallucination detection | `hallucination_detector.py` |
| `benchmarks/failure/` | Failure analysis | `failure_analysis.py` |

**Owner:** Research Engineering Lead
**Scientific role:** Ensures every claimed capability has a measurable test
**Engineering role:** CI-integrated benchmark harnesses
**Dependent experiments:** R1–R3F, EXP-0–EXP-4 (share benchmark infrastructure)
**Would be cited by:** Methods section of experimental papers
**Category:** Benchmarks

---

## Infrastructure

Operational systems, databases, configuration, API surface, and deployment.

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `infra/app/` | FastAPI application entry point, routes, middleware, streaming | `main.py`, `lifespan.py`, `routes_eval.py`, `routes_ops.py`, `routes_query.py`, `streaming.py`, `pipeline.py` |
| `infra/database/` | Database engine, models, repositories, migrations (Alembic), Redis cache, runtime state | `engine.py`, `models.py`, `repositories.py`, `redis_cache.py`, `runtime_state.py`, `alembic/` |
| `infra/runtime/` | Event bus, event handlers, event models, runtime monitoring, tracing | `event_bus.py`, `event_handlers.py`, `event_models.py`, `runtime_monitor.py`, `tracing.py` |
| `infra/ops/` | Operations: circuit breakers, failure recovery, health monitoring, load shedding, observability, resource management, snapshots, supervisor, token budget | `circuit_breakers.py`, `failure_recovery.py`, `health_monitor.py`, `load_shedding.py`, `observability.py`, `resource_manager.py`, `runtime_snapshots.py`, `runtime_supervisor.py`, `token_budget_manager.py` |
| `infra/constitution/` | Constitution markdown documents (epistemology, logic, science, uncertainty, communication, curiosity) | `epistemology.md`, `logic.md`, `science.md`, `uncertainty.md`, `communication.md`, `curiosity.md` |
| `infra/config/` | Configuration schemas, defaults, environment-specific overrides | `baseline.json`, `noisy.json`, `simple.json` |
| `infra/data/` | Runtime data store (databases, JSON state files, vector indices). Not in version control for experiments; bind-mounted or generated at startup | `chroma_db/`, vector indices, JSON state |
| `infra/frontend/` | Vite/JS frontend | `src/`, `dist/`, `index.html`, `package.json` |

**Owner:** Engineering Lead
**Scientific role:** None (pure operations)
**Engineering role:** Running the system, serving the API, persisting state, monitoring health
**Dependent experiments:** None directly (experiments run independently)
**Would be cited by:** None
**Category:** Infrastructure

---

## Program A — Live-Truth Retrieval

The honest product path. Separated from the research stack because it ships independently.

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `program_a/retrieval/` | Unified retriever (Arxiv, Brave, DuckDuckGo, SearXNG, Tavily, Wikipedia), browser | `unified_retriever.py`, `arxiv_client.py`, `brave_client.py`, `browser.py`, `duckduckgo_client.py`, `searxng_client.py`, `tavily_client.py`, `wiki_client.py`, `video_learner.py` |
| `program_a/nlp/` | Temporal parser, NLP utilities | `temporal_parser.py` |
| `program_a/routes/` | (If separate deployment from infra) | — |

**Owner:** Product Engineering Lead
**Scientific role:** H1 (calibration) is tested here; otherwise pure engineering
**Engineering role:** RAG pipeline, credibility scoring, uncertainty tiering
**Dependent experiments:** EXP-1 (calibration curve)
**Would be cited by:** H1/calibration paper
**Category:** Program A (product track)

---

## Program B — Soul Graph

Authored affective concept graph. Engineering-retained to run experiments that depend on it (EXP-2, R3F).

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `program_b/soul_graph/` | Soul graph implementation (nodes, edges, Hebbian plasticity, sleep cycle, BFS) | `soul_graph.py`, `soul_store.py` |
| `program_b/concepts/` | Authored concept definitions (concepts.json) | `concepts.json` |

**Owner:** PI (scientific) + Engineering Lead (maintenance)
**Scientific role:** H2 (affective indexing) tests whether the affective→strategic bridge does measurable work
**Engineering role:** Maintains the soul graph runtime; no new features unless H2 survives EXP-2
**Dependent experiments:** EXP-2 (H2), R3F (if it uses soul concepts)
**Would be cited by:** H2 paper (if signal found); otherwise archived
**Category:** Program B (experimental)

---

## Program C — Cognitive Stack

The symbolic-AGI subsystems. Engineering-retained to run current experiments. No development beyond bug fixes unless an experiment demands it.

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `program_c/cognition/` | Perception, reasoning engine, scenario engine, attention modulation, priority routing, decision policy, concept birth, dream state, replay engine, sim engine, viz engine, predictive core | `perception.py`, `reasoning_engine.py`, `scenario_engine.py`, `attention_modulator.py`, `priority_router.py`, `decision_policy.py`, `concept_birth.py`, `dream_state.py`, `replay_engine.py`, `sim_engine.py`, `sim_detector.py`, `viz_engine.py`, `viz_detector.py`, `predictive_core.py`, `predictive_engine.py`, `vector_prediction_core.py`, `unified_pipeline.py` |
| `program_c/memory/` | All memory subsystems: knowledge graph, memory graph, episodic memory, working memory, vector store, embedding service, concept engine, memory manager, retriever, crawler index, state delta, session, recall logger | `knowledge_graph.py`, `memory_graph.py`, `episodic_memory.py`, `episodic.py`, `working_memory.py`, `vector_store.py`, `vector_backend.py`, `embedding_service.py`, `gpu_embedder.py`, `concept_engine.py`, `memory_manager.py`, `memory_retriever.py`, `memory_store.py`, `memory_schemas.py`, `crawler_index.py`, `state_delta.py`, `session.py`, `recall_logger.py` |
| `program_c/learning/` | Continuous learner, deep learner, online learner, night learner, curriculum, feedback loop, gap tracker, knowledge tutor, living constitution, permanence, source trust, strategy optimizer, rule deriver, proactive cognition, failure diagnosis | `continuous_learner.py`, `deep_learner.py`, `online_learner.py`, `night_learner.py`, `curriculum.py`, `feedback_loop.py`, `gap_tracker.py`, `knowledge_tutor.py`, `living_constitution.py`, `permanence.py`, `source_trust.py`, `strategy_optimizer.py`, `rule_deriver.py`, `proactive_cognition.py`, `failure_diagnosis.py` |
| `program_c/knowledge/` | Knowledge engine, consolidator, epistemic manager, fact extractor, normalizer, ontology loader, predicate resolver, schema gatekeeper, temporal filter, entity bridge, bridge, voice engine, world model context/schema | `knowledge_engine.py`, `consolidator.py`, `epistemic_manager.py`, `fact_extractor.py`, `normalizer.py`, `ontology_loader.py`, `predicate_resolver.py`, `schema_gatekeeper.py`, `temporal_filter.py`, `entity_bridge.py`, `bridge.py`, `voice_engine.py`, `world_model_context.py`, `world_model_schema.py` |
| `program_c/metacognition/` | Meta-monitoring, adaptation engine, cognition metrics, confidence calibration, pattern analysis, strategy analysis | `meta_monitor.py`, `adaptation_engine.py`, `cognition_metrics.py`, `confidence_calibrator.py`, `pattern_analyzer.py`, `strategy_analyzer.py` |
| `program_c/reflection/` | Reflection engine, advanced reflection, confidence estimation, improvement engine, reasoning audit | `reflection_engine.py`, `advanced_reflection.py`, `confidence_estimator.py`, `improvement_engine.py`, `reasoning_audit.py` |
| `program_c/pipeline/` | Agentic loop, inference pipeline, reasoning core/wiring, context builder, intent engine, query rewriter, knowledge router, retrieval mesh, synthesizer, truth filter, contradiction detection, resonance, reflex, constitution loader, seed knowledge, persistence, self-router, soul router, reflection router | All pipeline files |
| `program_c/abstraction/` | Belief generator, belief models, belief store, consolidation runner, cross-seed validator | `belief_generator.py`, `belief_models.py`, `belief_store.py`, `consolidation_runner.py`, `cross_seed_validator.py` |
| `program_c/self_model/` | Self-model, identity store, health monitor, baseline tracker, self-audit | `self_model.py`, `identity_store.py`, `health_monitor.py`, `baseline_tracker.py`, `self_audit.py` |
| `program_c/simulation/` | Simulation interface, causal evaluator, logger, memory context | `interface.py`, `causal_evaluator.py`, `logger.py`, `simulation_memory_context.py` |
| `program_c/agency/` | Action log, code writer, curiosity executor, dependency manager, health sentinel, quality assurance, system bridge, auto-fixer, context reconstruction | `action_log.py`, `code_writer.py`, `curiosity.py`, `curiosity_executor.py`, `dependency_manager.py`, `health_sentinel.py`, `quality_assurance.py`, `system_bridge.py`, `auto_fixer.py`, `context_recon.py` |
| `program_c/conversation/` | Dialogue manager, monologue, context compressor, beliefs, working memory, reasoning modes | `dialogue_manager.py`, `monologue.py`, `context_compressor.py`, `beliefs.py`, `working_memory.py`, `reasoning_modes.py` |
| `program_c/models/` | Data models (Pydantic): answer, source, query, predictive, LLM client | `answer.py`, `source.py`, `query.py`, `predictive.py`, `llm_client.py` |

**Owner:** Engineering Lead (maintenance mode)
**Scientific role:** Provides the machinery that current experiments run on; no scientific validity asserted
**Engineering role:** Fix bugs, prevent rot, keep experiment suite passing
**Dependent experiments:** R1–R3F, EXP-0 (all run on Program C machinery)
**Would be cited by:** None (engineering appendix in experimental papers)
**Category:** Program C (engineering-retained)

---

## Documentation

Research documentation, architecture docs, requirements, PI reviews, session artifacts.

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `docs/research/` | PI Review (VELYNX_v2_PI_Review), research state (PROGRAM_D_RESEARCH_STATE), scientific foundation | All master research documents |
| `docs/architecture/` | Architecture doc, phase architecture documents | `ARCHITECTURE.md`, `phase57_agentic_loop_architecture.md`, `phase60_self_model_architecture.md` |
| `docs/audits/` | VELYNX audit reports, phase audit documents | `VELYNX_AUDIT_2026-06-01.md`, `VELYNX_PHASE36_AUDIT.md` |
| `docs/requirements/` | Requirements documents | `requirements.md`, `requirements_raw.txt` |
| `docs/reviews/` | Code health reviews (circular dependencies, dead code, duplicated logic, hidden coupling) | `program_d_circular_dependencies.md`, `program_d_dead_code_analysis.md`, `program_d_duplicated_logic.md`, `program_d_hidden_coupling.md` |
| `docs/literature/` | Literature-facing documentation (mathematical provenance) | `program_d_mathematical_provenance.md` |
| `docs/plans/` | Reduction plans, migration plans, archive manifests | `program_d_reduction_plan.md`, `program_d_migration_plan.md`, `program_c_reduction_plan.md`, `program_c_safe_removal_order.md`, `program_c_archive_manifest.md` |

**Owner:** PI + Engineering Lead (joint)
**Scientific role:** Records the reasoning trail; ensures reviewer reproducibility
**Engineering role:** Architecture documentation for maintainers
**Dependent experiments:** None
**Would be cited by:** The "prior work" / "system description" sections of papers
**Category:** Documentation

---

## Archive

Superseded code, deprecated experiments, legacy documents. Never deleted — only moved here.

| Directory | Purpose |
|-----------|---------|
| `archive/code/` | Deprecated/superseded source code (velynx_core/, legacy orchestrator, brain.py duplicates, self_coder.py duplicates, frontend/, configs/, etc.) |
| `archive/experiments/` | Superseded experiment artifacts (calculator, toy scripts) |
| `archive/documents/` | Superseded design documents |
| `archive/data/` | Legacy data files from past experiments (not needed for reproduction) |

**Owner:** Engineering Lead
**Category:** Archive

---

## Research Artifacts

Generated experimental outputs (figures, reports, analysis results). Not under version control; generated on demand.

| Directory | Purpose |
|-----------|---------|
| `artifacts/benchmarks/` | R2A1 policy benchmark, R3F1 report, attribution run outputs, etc. |
| `artifacts/experiments/` | Experiment run data (exp_001..exp_N) |
| `artifacts/output/` | Rendered simulation HTML, charts, plots |

**Owner:** Research Engineering Lead
**Category:** Archive (generated artifacts, excluded from VCS)

---

## Root Files

| File | Purpose |
|------|---------|
| `README.md` | Repository index (kept minimal; points to docs/) |
| `pyproject.toml` | Python project metadata, dependencies, build config |
| `package.json` | JS build config (frontend, if active) |
| `.env.example` | Environment variable template |
| `.gitignore` | VCS exclusion rules |
| `Dockerfile` | Container build |
| `docker-compose.yml` | Multi-service orchestration |

---

## Removed (never existed in v2)

The following directories from v1 are **removed** because they duplicated responsibility or had no scientific role:

| Directory | Reason for removal |
|-----------|--------------------|
| `velynx_core/` | Fully duplicated by `backend/*` → code archived, responsibility merged into `program_c/` |
| `backend/` | Split into `program_a/`, `program_b/`, `program_c/`, `infra/`, `benchmarks/` |
| `src/` | Single stub file with no purpose → deleted |
| `velynx/` | Small package with no identity → merged into `program_c/` |
| `evaluation/` | Split: `validation/` → `benchmarks/`, `research/evaluation/` → `benchmarks/` |
| `validation/` | Renamed/merged into `benchmarks/` |
| `reduction/` | Documents → `docs/plans/` |
| `assumptions/` | Documents → `foundation/assumptions/` |
| `dependency_graphs/` | Documents → `foundation/architecture/` |
| `reviews/` | Documents → `docs/reviews/` |
| `literature/` | Documents → `docs/literature/` |
| `curriculum/` | Data → `program_c/learning/` (runtime content, not standalone) |
| `configs/` | → `infra/config/` |
| `scripts/` | Utilities either archived or inlined into Makefile/pyproject.toml |
| `research/` | Split: `attribution/` → `program_c/agency/` or `core/`, `evaluation/` → `benchmarks/`, `experiments/` → `experiments/`, `policies/` → `core/controls/`, `proposals/` → `core/mdl/`, `tests/` → `tests/` |
| `research_artifacts/` | → `artifacts/` |
| `data/` | → `infra/data/` (runtime data, not VCS-tracked) |
| `models/` | Empty → removed |
| `novelty/` | Empty → removed |
| `artifacts/` | Consolidated under `artifacts/` |
| `.velynx_data/` | → `infra/data/` |
