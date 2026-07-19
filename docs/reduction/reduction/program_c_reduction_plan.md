# Program C: Subsystem Reduction Plan

## Classification Key

| Class | Meaning |
|-------|---------|
| **REQUIRED** | Removing this breaks at least one experiment. Must keep. |
| **SUPPORTING** | Not strictly required by any experiment, but provides scientific value to the research program. |
| **OPTIONAL** | No experiment requires it. Operational or aesthetic value only. |
| **DEAD** | No imports, no callers, no experiment uses it. |
| **DUPLICATED** | Functionality is fully provided by another subsystem. |
| **DECORATIVE** | Visual or interaction layer only. No scientific function. |
| **RESEARCH_ONLY** | Only used within the research/ infrastructure; not needed to run experiments (the research infrastructure itself is REQUIRED). |
| **LEGACY** | Superseded by a newer implementation. |

---

## Experiment Reference

Experiments are referenced by ID throughout:

| ID | Command | Type |
|----|---------|------|
| EXP-0 | `python test_velynx_core.py` | Integration smoke test |
| R1 | `python research_benchmark.py` | Consolidation policy ablation |
| R2A | `python research_policy_benchmark_r2a.py` | Policy comparison (held-out RMSE) |
| R3 | via `research/attribution/runner.py` | Counterfactual merge evaluation |
| R3E | `python research/r3e_benchmark.py` | Objective benchmark (stdlib only) |
| R3F | Analysis of R3E output | Serialization recovery report |
| C8 | `pytest test_c8_*.py` | Control system verification |
| R3C | `pytest test_replay_engine_vitals_r3c.py test_shared_metrics_v1.py` | Identity test |
| B-PROD | `python benchmark.py` | Production regression gate |
| B-V2 | `python run_benchmark_v2.py` | V2 capability benchmark |
| LF | `python backend/tests/live_fire_harness.py` | Phase 61->62 stabilization gate |
| COG-S | `python backend/tests/run_cognitive_suite.py` | Phase 53-61 cognitive suite |
| PYTEST | `python -m pytest backend/tests/` | Full backend pytest suite |
| R-TEST | `python -m pytest research/tests/` | Research pytest suite |
| t-* | `python test_*.py` | Individual root test scripts |

---

## Subsystem-by-Subsystem Analysis

---

### 1. `backend/cognition/` — Cognitive Reasoning Engine

**Purpose:** Deterministic, LLM-free symbolic reasoning, predictive processing, memory-restructuring replay, metaphorical concept discovery, physical simulation, and scenario generation. The "thought engine."

**Incoming dependencies:** pipeline(2), app(2), orchestrator.py, brain.py, knowledge(2), simulation(1), soul(1), orchestration(1), tests(5), validation(2), research(7), root scripts(6)

**Outgoing dependencies:** memory(12), knowledge(3), agency(1), abstraction(1), models(1)

**Experiments requiring it:** R1, R2A, R3, C8, R3C, B-PROD, B-V2, LF, COG-S, PYTEST, R-TEST, t-metacog, t-c8-control, t-c8-decision, t-replay-engine, t-cognitive-core

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: All formal experiments (R1, R2A, R3, C8, R3C), production benchmark, V2 benchmark, live-fire harness, cognitive suite, full pytest suite, most root test scripts
- Fails: Every experiment that measures cognitive quantities (S, H, A, E)
- Hypotheses untestable: FEP validation, consolidation policy comparison, counterfactual merge evaluation, replay identity, shared metrics correctness
- Confidence: **High**

---

### 2. `backend/pipeline/` — Inference Pipeline Orchestration

**Purpose:** Wires retrieval, reasoning, context building, synthesis, reflection, and agentic planning into a coherent request-scoped flow. Contains reflex layer, truth filter, contradiction detector, agentic multi-hop planner, soul router, and self-router.

**Incoming dependencies:** app(1), learning(1), agency(1), simulation(1), tests(8), root scripts(1)

**Outgoing dependencies:** learning(5), knowledge(5), memory(4), cognition(2), retrieval(1), models(3), soul(1), reflection(1), agency(1)

**Experiments requiring it:** R1 (via validation runner only minimally), LF, COG-S, PYTEST

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness, cognitive suite, full pytest suite
- Fails: Any experiment that routes through answer_question() — most of Phase 53-61
- Note: The formal research experiments (R1, R2A, R3, C8, R3C) do NOT directly use pipeline/ — they use validation/runner's consolidated sleep-cycle loop instead. However PYTEST and LF require it.
- Confidence: **High**

---

### 3. `backend/memory/` — Multi-Store Memory Architecture

**Purpose:** Three-tier memory (episodic, semantic, working) with SQLite-backed knowledge graphs, sentence-transformers embedding, vector stores, and a unified MemoryManager. The "hippocampus."

**Incoming dependencies:** cognition(12), pipeline(4), knowledge(8), learning(3), agency(3), app(3), soul(1), abstraction(2), self_model(2), orchestration(1), orchestrator.py, brain.py, tools(1), velynx(3), tests(6), root scripts(8+)

**Outgoing dependencies:** internal only (18 cross-imports within memory/)

**Experiments requiring it:** R1 (via validation/monitor), R2A, R3, C8, R3C, B-PROD, B-V2, LF, COG-S, PYTEST, t-decay, t-knowledge, t-probe, t-probe-hybrid, t-velynx-core

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: Every experiment. Memory is the substrate on which all cognitive operations run.
- Fails: All metrics (no data to compute S, H, A from), all replay, all consolidation, all recall
- Hypotheses untestable: All of them
- Confidence: **High**

---

### 4. `backend/knowledge/` — Knowledge Graph & World Model

**Purpose:** Curated "active brain" knowledge graph with cross-domain concepts, ontology-driven inference, spaCy-based fact extraction, epistemic consolidation, and a Phase 62 World Model with typed entities and attribute schemas.

**Incoming dependencies:** pipeline(5), app(1), agency(3), simulation(3), cognition(3), tools(1), orchestrator.py, tests(8), root scripts(3)

**Outgoing dependencies:** memory(8), cognition(2), soul(1)

**Experiments requiring it:** LF, COG-S, PYTEST, t-knowledge

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness, cognitive suite, full pytest suite, test_knowledge.py
- Does NOT directly break: Formal experiments R1/R2A/R3/C8/R3C (these use synthetic datasets, not the knowledge graph)
- Hypotheses at risk: Ontology-driven inference, cross-domain analogical reasoning, epistemic consolidation
- Confidence: **High**

---

### 5. `backend/learning/` — Multi-Timescale Learning Loops

**Purpose:** Continuous per-query learning, proactive curiosity-driven gap filling (5-min loop), nocturnal/scheduled consolidation, feedback-driven strategy optimization, curriculum-guided self-paced learning.

**Incoming dependencies:** pipeline(5), app(1), cli.py, tests(7)

**Outgoing dependencies:** memory(3), pipeline(1), soul(1)

**Experiments requiring it:** LF, COG-S, PYTEST, t-curriculum-expanded, t-permanence, t-learning-api

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness, cognitive suite, full pytest suite, learning-specific tests
- Does NOT directly break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD (these use a tick-driven consolidation loop, not the learning system)
- Hypotheses at risk: Spaced repetition, gap detection precision, curiosity-driven learning rate, curriculum sequencing
- Confidence: **High**

---

### 6. `backend/agency/` — Autonomous Agency & Self-Improvement

**Purpose:** Curiosity-driven goal generation (Phase 59), sandboxed code writing, LLM-driven auto-fix, failure-rate health sentinel, and quality assurance. "Executive function."

**Incoming dependencies:** orchestrator.py, app(2), cognition(1), pipeline(1), tests(3), root scripts(1)

**Outgoing dependencies:** memory(3), knowledge(3), pipeline(1), internal(2)

**Experiments requiring it:** LF (curiosity_executor), COG-S, PYTEST (test_agency.py, test_self_model.py, test_episodic_memory.py), t-agency

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness, cognitive suite (Phase 57-59), full pytest suite, test_agency.py
- Does NOT directly break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD
- Hypotheses at risk: Curiosity-driven learning efficacy, goal generation precision, code self-improvement
- Confidence: **High**

---

### 7. `backend/reflection/` — Per-Query Reasoning Audit

**Purpose:** Post-answer reflection: detect contradictions, hallucination risk, weak reasoning; estimate confidence; suggest improvements. "Immediate self-critique."

**Incoming dependencies:** brain.py, pipeline(1), tests (via app/pipeline)

**Outgoing dependencies:** internal (reasoning_audit, confidence_estimator, improvement_engine)

**Experiments requiring it:** LF, PYTEST (via app/pipeline.py)

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness (answer_question calls reflection), full pytest suite
- Does NOT directly break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD/B-V2
- Hypotheses at risk: Reasoning quality metrics, hallucination detection, confidence calibration
- Confidence: **High**

---

### 8. `backend/conversation/` — Multi-Turn Dialogue Management

**Purpose:** Dialogue act classification, belief tracking across turns, inner monologue (deterministic reasoning trace), per-session working memory with LRU eviction.

**Incoming dependencies:** app(2), tests(5)

**Outgoing dependencies:** internal only

**Experiments requiring it:** LF (streaming.py, pipeline.py), COG-S, PYTEST (test_dialogue.py, test_reasoning_modes.py, test_monologue.py, test_working_memory.py, test_beliefs.py, test_harness_ram_reset.py)

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness, cognitive suite, full pytest suite
- Does NOT directly break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD/B-V2
- Hypotheses at risk: Follow-up detection, belief revision latency, dialogue state precision
- Confidence: **High**

---

### 9. `backend/retrieval/` — External Information Retrieval

**Purpose:** Multi-source web retrieval with ordered fallback chain: Wikipedia, DuckDuckGo, SearXNG, Brave, Tavily, ArXiv. Fail-soft architecture.

**Incoming dependencies:** pipeline(1), tests(2)

**Outgoing dependencies:** none (standalone clients)

**Experiments requiring it:** LF (via retrieval_mesh in pipeline), PYTEST (test_wiki_client.py, test_browser.py)

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness (queries that trigger external retrieval), full pytest suite
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD/B-V2 (these use synthetic data or embedded knowledge)
- Hypotheses at risk: Source quality comparisons, retrieval latency, fallback reliability
- Confidence: **Medium** — Some experiments mock or bypass retrieval; the formal consolidation experiments do not use it at all.

---

### 10. `backend/app/` — FastAPI Application & Pipeline Orchestrator

**Purpose:** HTTP API entry point (FastAPI), master `answer_question()` orchestrator (1024-line pipeline.py), SSE streaming, query/teach/eval routes, DB bridge.

**Incoming dependencies:** tests(19) — almost every pytest test imports from app

**Outgoing dependencies:** pipeline, conversation, cognition, learning, knowledge, memory, models, soul, agency, database

**Experiments requiring it:** LF (answer_question), COG-S, PYTEST (nearly all tests import app.main or app.pipeline)

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness, cognitive suite, full pytest suite (direct import failures in 19+ test files)
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD/B-V2/R3E
- Hypotheses at risk: None of the formal research hypotheses depend on HTTP routing
- But: The pytest suite IS a measurement experiment, so app/ is REQUIRED
- Confidence: **High**

---

### 11. `backend/models/` — Pydantic Data Models

**Purpose:** Answer, Query, Source, Predictive data models, LLM client abstraction.

**Incoming dependencies:** pipeline(3), app(3), cognition(1), root scripts(1)

**Outgoing dependencies:** ops(1) (llm_client → circuit_breakers), internal

**Experiments requiring it:** LF, PYTEST (transitively via pipeline/app), teach.py

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness, full pytest suite (all pipeline and app imports fail)
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD (they define their own internal data structures)
- Confidence: **High**

---

### 12. `backend/database/` — Persistence Layer

**Purpose:** Async SQLAlchemy engine, ORM models (Episode, Concept, Reflection, Goal, Session, etc.), CRUD repositories, runtime state, Redis cache.

**Incoming dependencies:** metacognition(8), app(1)

**Outgoing dependencies:** internal only

**Experiments requiring it:** PYTEST (via metacognition, app/db_bridge), LF (runtime_state)

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness, full pytest suite (specifically test_ops.py, test_evaluation.py, metacognition tests)
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD/B-V2 (these use the validation/monitor internal state, not PostgreSQL)
- Note: Many tests and the metacognition/reflection subsystems depend on database/; removing it would break the full test suite
- Confidence: **High**

---

### 13. `backend/metacognition/` — Meta-Cognitive Monitoring

**Purpose:** The "frontal lobe" — monitors reasoning quality, calibrates confidence, clusters reasoning patterns, compares strategy performance, generates advisory recommendations. Observe-only; never auto-applies changes.

**Incoming dependencies:** tests (via routes_eval and test_metacognition.py)

**Outgoing dependencies:** database(8)

**Experiments requiring it:** PYTEST (test_metacognition.py), COG-S (via routes_eval)

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: full pytest suite (test_metacognition.py), cognitive suite (if eval routes invoked)
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD/B-V2/LF
- Hypotheses at risk: Calibration accuracy (Brier score), hallucination risk trending, reasoning pattern clustering
- Confidence: **Medium** — The metacognition subsystem is tested but is not a dependency of the primary production pipeline; it's a read-only monitor.

---

### 14. `backend/self_model/` — Cognitive Self-Model

**Purpose:** Continuous cognitive health assessment: baseline tracking, health monitoring, self-audit with structured artifacts, identity persistence.

**Incoming dependencies:** tests(1) — test_self_model.py

**Outgoing dependencies:** memory(2) (identity_store, baseline_tracker → _sqlite)

**Experiments requiring it:** PYTEST (test_self_model.py only)

**Scientific necessity:** **SUPPORTING**

**Removal impact:**
- Breaks: One test file (test_self_model.py) — 1 test failure in PYTEST
- Does NOT break: Any formal experiment, live-fire, benchmark, or cognitive suite
- Hypotheses at risk: Cognitive health trajectory, identity stability across sessions
- Confidence: **High** — Only one test file directly imports it; no production pipeline code depends on it.

---

### 15. `backend/soul/` — Soul Graph & Emotional Layer

**Purpose:** Embedding-based relational graph of human-meaningful concepts (grief, hope, betrayal, etc.) with typed edges (enables, opposes, catalyzes) and tension pairs.

**Incoming dependencies:** pipeline(1), app(1), knowledge(1), learning(1), tests(2), root scripts(1)

**Outgoing dependencies:** memory(1), cognition(1) (lazy)

**Experiments requiring it:** B-V2 (soul_graph.synthesize), LF (resonance), PYTEST (test_soul_graph.py), t-sleep

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: V2 benchmark (soul-dependent queries fail), live-fire harness (resonance step), full pytest suite, test_sleep.py
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD (these don't touch the soul graph)
- Hypotheses at risk: Embedding-based relationship discovery, cross-modal concept bridging
- Confidence: **High**

---

### 16. `backend/simulation/` — Counterfactual Reasoning Engine

**Purpose:** Phase 63 counterfactual "imagination" — parses "what if" premises, injects counterfactual triples into a forked memory context, runs baseline vs. simulated reasoning, computes CausalDelta.

**Incoming dependencies:** tests(1)

**Outgoing dependencies:** knowledge(3), cognition(1), pipeline(1) (lazy)

**Experiments requiring it:** PYTEST (test_simulation_engine.py only)

**Scientific necessity:** **SUPPORTING**

**Removal impact:**
- Breaks: One test file (test_simulation_engine.py) — 1 test failure in PYTEST
- Does NOT break: Any formal experiment, live-fire, benchmark, V2 benchmark, cognitive suite
- Hypotheses at risk: Counterfactual reasoning accuracy, causal delta informativeness
- Confidence: **High**

---

### 17. `backend/abstraction/` — Belief Abstraction from Memory

**Purpose:** Distills abstract beliefs from concrete episodic memory state deltas. Generates scored candidate beliefs, promotes them to core beliefs via configurable thresholds.

**Incoming dependencies:** cognition(1) (self_model.py — lazy import)

**Outgoing dependencies:** memory(2) (_sqlite, memory_store)

**Experiments requiring it:** PYTEST (transitively via cognition if self_model is exercised)

**Scientific necessity:** **REQUIRED** (transitively through cognition)

**Removal impact:**
- Breaks: cognition/self_model.py (on lazy import when triggered), which breaks any experiment that exercises self_model (LF, PYTEST, COG-S)
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C (these use the replay engine, not belief abstraction)
- Confidence: **Medium** — The import is lazy, so the break only manifests if the self_model code path is actually triggered.

---

### 18. `backend/runtime/` — In-Process Event Bus

**Purpose:** Async priority-queue event bus with 60+ event types covering query lifecycle, feedback, goals, plans, sessions, memory. Three default handlers: observability, persistence, learning trigger.

**Incoming dependencies:** evaluation(4), tests(1)

**Outgoing dependencies:** internal only

**Experiments requiring it:** PYTEST (test_event_system.py), research evaluation (trial_runner, session_replay)

**Scientific necessity:** **SUPPORTING**

**Removal impact:**
- Breaks: One test file (test_event_system.py), evaluation/trial_runner.py and session_replay.py
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD/B-V2/LF
  - Wait — LF might not use runtime/. Let me verify. LF uses app/pipeline which doesn't directly use runtime/. The pipeline does its own orchestration.
  - research/runner.py (for R1/R2A) does NOT use runtime/ — it uses its own inner loop.
  - validation/runner.py does NOT use runtime/.
- Hypotheses at risk: Event-driven architecture metrics, trial runner instrumentation
- Confidence: **High** for formal experiments; **Medium** for full test suite

---

### 19. `backend/ops/` — Runtime Operations & Hardening

**Purpose:** Health monitor (parallel subsystem checks), circuit breakers (closed/open/half-open), runtime supervisor (lifecycle + auto-recovery), load shedding, resource management, observability, token budget.

**Incoming dependencies:** models(1) (llm_client → circuit_breakers), tests(1)

**Outgoing dependencies:** internal only

**Experiments requiring it:** PYTEST (test_ops.py)

**Scientific necessity:** **SUPPORTING**

**Removal impact:**
- Breaks: test_ops.py in pytest suite
- May break: models/llm_client.py if circuit_breakers are imported at module level (breaking any experiment making LLM calls)
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD (these don't make LLM calls)
- Hypotheses at risk: None — ops/ is operational infrastructure, not experimental
- Confidence: **High** for formal experiments

---

### 20. `backend/nlp/` — Temporal Expression Parser

**Purpose:** Phase 64 regex-based temporal bounds parser. Translates natural-language time references to ISO-8601 date bounds. Stdlib only.

**Incoming dependencies:** tests(1)

**Outgoing dependencies:** none

**Experiments requiring it:** PYTEST (test_temporal_parser.py only)

**Scientific necessity:** **SUPPORTING**

**Removal impact:**
- Breaks: One test file (test_temporal_parser.py) — 1 test failure in PYTEST
- Does NOT break: Any formal experiment, live-fire, benchmark, cognitive suite, or any other test
- Confidence: **High**

---

### 21. `backend/evaluation/` — Benchmarking & Test Infrastructure

**Purpose:** Trial runner, scenario loader, stability monitor, session replay, adversarial tests, hallucination detector, reflection evaluator, runtime profiler, failure analysis.

**Incoming dependencies:** tests(4)

**Outgoing dependencies:** runtime(4) (trial_runner → tracing, event_bus; session_replay → event_bus, event_models)

**Experiments requiring it:** PYTEST (test_trials.py, test_evaluation.py), COG-S (trial runner phases)

**Scientific necessity:** **SUPPORTING**

**Removal impact:**
- Breaks: 4 test files in pytest suite, some phases of cognitive suite
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD/B-V2/LF
- Confidence: **High**

---

### 22. `backend/audio/` — Text-to-Speech Output

**Purpose:** Deterministic pyttsx3 TTS for REPL/terminal interface. Strips markdown, speaks on worker thread.

**Incoming dependencies:** orchestrator.py(1)

**Outgoing dependencies:** none

**Experiments requiring it:** None

**Scientific necessity:** **OPTIONAL**

**Removal impact:**
- Breaks: Nothing in any experiment
- Fails: No experiment fails
- Hypotheses: None
- Confidence: **High**

---

### 23. `backend/testing/` — Diagnostic Helpers

**Purpose:** diagnostic_test.py, life_simulator.py — test helpers for the orchestration subsystem.

**Incoming dependencies:** orchestration(2) (import these files)

**Outgoing dependencies:** orchestration(2)

**Experiments requiring it:** None (stability_audit.py uses orchestration.cognitive_loop directly, not testing/)

**Scientific necessity:** **OPTIONAL**

**Removal impact:**
- Breaks: Nothing in any experiment
- Fails: No experiment fails
- Confidence: **High**

---

### 24. `backend/tools/` — Utility Scripts

**Purpose:** visualize_graph.py, dedupe_directions.py — graph visualization and triple deduplication.

**Incoming dependencies:** none (standalone utilities)

**Outgoing dependencies:** memory(1), knowledge(1)

**Experiments requiring it:** None

**Scientific necessity:** **OPTIONAL**

**Removal impact:**
- Breaks: Nothing in any experiment
- Confidence: **High**

---

### 25. `backend/contracts/` — Specification Contracts

**Purpose:** predictive_core_spec.py — spec file for the predictive core.

**Incoming dependencies:** orchestration(1) (validator.py imports it)

**Outgoing dependencies:** none

**Experiments requiring it:** None (stability_audit.py doesn't use it; it goes through orchestration.cognitive_loop which may import it internally)

**Scientific necessity:** **OPTIONAL**

**Removal impact:**
- Breaks: orchestration/validator.py (if validator is invoked)
- Does NOT break: Any experiment (orchestration's validator is not on any critical path)
- Confidence: **Medium** — stability_audit.py uses orchestration.cognitive_loop which might reference validator.

---

### 26. `backend/agents/` — Agent Coordinator Stub

**Purpose:** agent_coordinator.py — minimal stub. Does not appear to be imported by any production code or experiment.

**Incoming dependencies:** none detected

**Outgoing dependencies:** none detected

**Experiments requiring it:** None

**Scientific necessity:** **DEAD**

**Removal impact:**
- Breaks: Nothing
- Confidence: **Low** — The `backend/agents/` directory contains only `agent_coordinator.py` and `__init__.py`. No grep for imports found any reference. However, dynamically loaded or configured imports would be missed by static analysis.

---

### 27. `backend/orchestrator.py` — Legacy Orchestration Layer

**Purpose:** Pre-FastAPI synchronous orchestrator. Chains cross_query() → reflect() → compile_path_to_speech(). Manages warmup, predictive core seeding, and agency subsystems.

**Incoming dependencies:** cli.py(1) (the CLI entry point uses orchestrator.velynx_respond)

**Outgoing dependencies:** cognition(2), memory(1), knowledge(2), agency(5), audio(1)

**Experiments requiring it:** None (cli.py is not invoked by any experiment)

**Scientific necessity:** **LEGACY**

**Removal impact:**
- Breaks: CLI/REPL (not used by any experiment)
- Does NOT break: Any experiment — lf, pytests, formal experiments all route through app/pipeline or validation/runner
- Confidence: **Medium** — Double-check that no experiment script imports from orchestrator.py. The root scripts (test_agency.py, teach.py, etc.) do not import it.

---

### 28. `backend/brain.py` — Unified Brain (V2)

**Purpose:** VelynxBrain.think() — higher-level abstraction with intent routing (ANSWER, LEARN, CODE, REFLECT, SIMULATE, IMPROVE) and quality gating.

**Incoming dependencies:** none detected

**Outgoing dependencies:** cognition(3), memory(2), reflection(1), self_coder(1)

**Experiments requiring it:** None

**Scientific necessity:** **LEGACY** / **DUPLICATED**

**Removal impact:**
- Breaks: Nothing — no imports found from any experiment, test, or production file
- Does NOT break: Any experiment
- Confidence: **Low** — brain.py may be imported via dynamic loading or configuration that static grep misses.

---

### 29. `backend/self_coder.py` — Self-Coding Engine

**Purpose:** Code generation, patch/validate/commit/rollback pipeline for self-improvement.

**Incoming dependencies:** brain.py(1)

**Outgoing dependencies:** gitpython, subprocess

**Experiments requiring it:** None (not imported by any experiment)

**Scientific necessity:** **LEGACY** / **DUPLICATED** (superseded by agency/code_writer.py?)

**Removal impact:**
- Breaks: brain.py (which itself is not used by experiments)
- Does NOT break: Any experiment
- Confidence: **Low** — Same caveat about dynamic loading.

---

### 30. `velynx_core/` — Standalone Core V2

**Purpose:** Self-contained, graph-native reasoning AI with its own memory, brain, learner, and self-coder. The original kernel from which the larger backend/ evolved.

**Incoming dependencies:** verify_installation.py, test_velynx_core.py

**Outgoing dependencies:** internal only

**Experiments requiring it:** EXP-0 (test_velynx_core.py) explicitly tests this package.

**Scientific necessity:** **DUPLICATED**

**Removal impact:**
- Breaks: test_velynx_core.py (EXP-0 fails: cannot import velynx_core)
- Does NOT break: Any formal experiment (R1-R3F), production benchmark, V2 benchmark, live-fire, cognitive suite, or full pytest suite
- Functionality: Fully duplicated by backend/{cognition,memory,learning,agency} at greater depth
- Confidence: **High**

---

### 31. `velynx/` — Brain Stem Graph

**Purpose:** Phase 38C brain stem: living_edges (reinforcement/challenge dynamics), curiosity_engine (Phase 59 ontology scanning), inference_engine (schema-based deduction).

**Incoming dependencies:** live_fire_harness.py, pipeline agentic_loop, pipeline resonance

**Outgoing dependencies:** backend/memory(3) (_sqlite usage)

**Experiments requiring it:** LF (via living_edges), PYTEST (test_pipeline_soul_v2.py), COG-S

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: live-fire harness, cognitive suite (Phase 59 curiosity), some pipeline tests
- Does NOT break: Formal experiments R1/R2A/R3/C8/R3C/B-PROD/B-V2
- Confidence: **Medium** — The velynx/ package is tightly integrated with the pipeline's agentic loop and soul resonance.

---

### 32. `validation/` — Experiment Harness & Metrics

**Purpose:** The single, interface-first experiment harness. Defines Dataset, Metric, Regression ABCs. Implements BenchmarkRunner (tick-by-tick sensor loop: scheduler→propose→replay→commit), FEP metrics (Entropy, Surprise, Active Load, Cognitive Energy), environment datasets, regression gates, and shared_metrics_v1 (R3C canonical layer).

**Incoming dependencies:** research(6), benchmark.py, cognitive_health.py, test_c8_control_upgrade.py, test_shared_metrics_v1.py

**Outgoing dependencies:** backend/cognition(4) (candidate_generator, consolidation_tracker, decision_policy, memory_scheduler, replay_engine, vector_prediction_core)

**Experiments requiring it:** R1, R2A, R3, C8, R3C, B-PROD, R-TEST

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: ALL formal experiments, production benchmark, C8/R3C tests
- Fails: Every experiment that measures cognitive quantities — which is all of them
- Hypotheses untestable: Entire Program C research agenda
- Confidence: **High**

---

### 33. `research/` — Research Sprint Infrastructure

**Purpose:** Self-contained research layer with pluggable ConsolidationPolicy, ResearchRunner (re-implements the sleep-cycle loop for fair cross-policy comparison), immutable artifact writer (7-file standard), hypothesis testing framework (bootstrap mean-difference), metric registry, attribution/counterfactual evaluation, evaluation protocol (held-out scoring), and proposal market.

**Incoming dependencies:** research_benchmark.py, research_policy_benchmark_r2a.py, research/r3e_benchmark.py, research/tests/

**Outgoing dependencies:** backend/cognition(14) (decision_policy, memory_scheduler, replay_engine, candidate_generator, consolidation_tracker, vector_prediction_core), validation(6) (datasets, metrics, monitor, interfaces)

**Experiments requiring it:** R1, R2A, R3, R3E, R3F, R-TEST

**Scientific necessity:** **REQUIRED**

**Removal impact:**
- Breaks: All formal research experiments (R1-R3F)
- Fails: All policy comparisons, ablation studies, attribution experiments, benchmark comparisons
- Hypotheses untestable: Free-energy policy benefit, counterfactual evaluation quality, serialization recovery
- Confidence: **High**

---

### 34. `frontend/` — React User Interface

**Purpose:** Web-based UI with components for query input, answer display, analysis panel, memory visualization, resonance visualization, epistemic state, pipeline visualization, thinking indicator, search bar, sources, and feedback.

**Incoming dependencies:** none (standalone frontend)

**Outgoing dependencies:** backend API via REST/SSE (no code-level import of backend Python)

**Experiments requiring it:** None

**Scientific necessity:** **DECORATIVE**

**Removal impact:**
- Breaks: Nothing in any experiment
- Fails: No experiment fails
- Hypotheses: None
- Confidence: **High**

---

### 35. `experiments/` — Toy/Placeholder Experiment Scripts

**Purpose:** calculator.py (simple CLI calculator, 17 lines), generated_tool.py (auto-generated stub), test_calc.py (add function test).

**Incoming dependencies:** none

**Outgoing dependencies:** none

**Experiments requiring it:** None

**Scientific necessity:** **DEAD**

**Removal impact:**
- Breaks: Nothing
- Confidence: **High**

---

### 36. `configs/` — Configuration JSON Files

**Purpose:** baseline.json, simple.json, noisy.json, your_config.json — configurations for the benchmark runner.

**Incoming dependencies:** benchmark.py (reads via --config flag)

**Outgoing dependencies:** none

**Experiments requiring it:** None (benchmark.py also accepts command-line arguments and has defaults)

**Scientific necessity:** **SUPPORTING**

**Removal impact:**
- Breaks: benchmark.py if --config is used without providing a fallback path
- Does NOT break: Any experiment with default settings
- Confidence: **High**

---

### 37. `curriculum/` — Learning Curriculum Content

**Purpose:** Domain-specific curriculum text files (biology, chemistry, physics, mathematics, earth_astronomy, technology, reasoning) plus deep_learn.py.

**Incoming dependencies:** backend/learning/curriculum.py

**Outgoing dependencies:** none

**Experiments requiring it:** PYTEST (via curriculum-loaded tests), LF (via seed_knowledge)

**Scientific necessity:** **SUPPORTING**

**Removal impact:**
- Breaks: Curriculum-loaded tests if curriculum content is a test expectation
- Does NOT break: Formal experiments (R1-R3F), production benchmark with synthetic data
- Confidence: **Medium** — Curriculum files are data, not code. They seed the knowledge graph.

---

### 38. Root diagnostic scripts (find_ghosts.py, inspect_*.py, peek_code.py, etc.)

**Purpose:** Ad-hoc diagnostic and inspection utilities for manual debugging.

**Incoming dependencies:** various backend/ subsystems

**Outgoing dependencies:** none (standalone scripts)

**Experiments requiring it:** None

**Scientific necessity:** **OPTIONAL**

**Removal impact:**
- Breaks: Nothing in any experiment
- Confidence: **High**

---

### 39. Root standalone experiment scripts (cognitive_core.py, concept_birth.py, latent_cause_engine.py, etc.)

**Purpose:** Self-contained experiments or wrappers — cognitive_core.py (C1-C3/C6 standalone predictive processing), concept_birth.py (debug), latent_cause_engine.py (experiment), night_learner.py (wrapper), velynx_soul.py (test), environment.py (test).

**Incoming dependencies:** none (standalone scripts)

**Outgoing dependencies:** various backend/ subsystems

**Experiments requiring it:** cognitive_core.py is itself an experiment (C1-C3/C6). Others are wrappers.

**Scientific necessity:** **RESEARCH_ONLY** (cognitive_core.py is a separate research thread, not part of Program C formal experiments)

**Removal impact:**
- Breaks: The standalone experiments themselves (cognitive_core.py REPL fails)
- Does NOT break: Any formal Program C experiment (R1-R3F), production benchmark, or test suite
- Confidence: **High**

---

### 40. `scripts/` — Operational Utilities

**Purpose:** Frontend startup, API testing, DB wipe, GPU learning, import fixing, chat. PowerShell and Python scripts.

**Incoming dependencies:** none

**Outgoing dependencies:** various

**Experiments requiring it:** None

**Scientific necessity:** **OPTIONAL**

**Removal impact:**
- Breaks: Nothing in any experiment
- Confidence: **High**

---

### 41. `docs/` — Documentation

**Purpose:** Architecture docs, audit reports, phase reviews, requirements.

**Incoming dependencies:** none

**Outgoing dependencies:** none

**Experiments requiring it:** None

**Scientific necessity:** **DECORATIVE**

**Removal impact:**
- Breaks: Nothing in any experiment
- Confidence: **High**

---

### 42. `data/` — Runtime Data Files

**Purpose:** Session state, soul concepts, source trust, system health, vector backend, etc. JSON files.

**Incoming dependencies:** read by multiple backend subsystems

**Outgoing dependencies:** none

**Experiments requiring it:** Yes — the data files are required by subsystems that ARE required. But the files themselves are test fixtures, not code.

**Scientific necessity:** **SUPPORTING**

**Removal impact:**
- Breaks: Any experiment that reads these files at runtime
- Confidence: **Medium** — These are data artifacts, not code. They would be recreated on first run.

---

### 43. `searxng/`, `kiro-gateway/` — Third-Party Services

**Purpose:** SearXNG search engine (Docker service), Kiro gateway.

**Incoming dependencies:** docker-compose.yml, backend/retrieval/searxng_client.py

**Outgoing dependencies:** none

**Experiments requiring it:** None (external retrieval clients have fallback chains)

**Scientific necessity:** **OPTIONAL**

**Removal impact:**
- Breaks: SearXNG-based retrieval (fallback to DuckDuckGo still works)
- Does NOT break: Any experiment
- Confidence: **High**

---

### 44. `backend/__init__.py`, `backend/chat.py`, `backend/cli.py`, `backend/cli_ui.py`, etc.

**Purpose:** Root backend package init, chat UI, CLI entry point, CLI UI helpers.

**Incoming dependencies:** None from experiments

**Outgoing dependencies:** orchestrator.py, various

**Experiments requiring it:** None (cli.py is the entry point for CLI, not used by experiments)

**Scientific necessity:** **OPTIONAL** (chat.py, cli.py, cli_ui.py are CLI interfaces) / **REQUIRED** (__init__.py makes backend a package)

**Removal impact:**
- Breaks: CLI interface (not used by experiments)
- Might break: backend/__init__.py removal would break ALL backend imports
- Confidence: **High** for cli.py, chat.py, cli_ui.py (all OPTIONAL); **High** for __init__.py (REQUIRED)

---

## Summary

| # | Subsystem | Class | Experiments That Would Fail |
|---|-----------|-------|-----------------------------|
| 1 | backend/cognition/ | **REQUIRED** | ALL |
| 2 | backend/pipeline/ | **REQUIRED** | LF, COG-S, PYTEST |
| 3 | backend/memory/ | **REQUIRED** | ALL |
| 4 | backend/knowledge/ | **REQUIRED** | LF, COG-S, PYTEST, t-knowledge |
| 5 | backend/learning/ | **REQUIRED** | LF, COG-S, PYTEST, learning tests |
| 6 | backend/agency/ | **REQUIRED** | LF, COG-S, PYTEST, t-agency |
| 7 | backend/reflection/ | **REQUIRED** | LF, PYTEST |
| 8 | backend/conversation/ | **REQUIRED** | LF, COG-S, PYTEST, dialogue tests |
| 9 | backend/retrieval/ | **REQUIRED** | LF, PYTEST (wiki/browser tests) |
| 10 | backend/app/ | **REQUIRED** | LF, COG-S, PYTEST (19+ files) |
| 11 | backend/models/ | **REQUIRED** | LF, PYTEST, teach.py |
| 12 | backend/database/ | **REQUIRED** | LF, PYTEST (ops/metacognition tests) |
| 13 | backend/metacognition/ | **REQUIRED** | PYTEST (test_metacognition.py) |
| 14 | backend/self_model/ | **SUPPORTING** | PYTEST (test_self_model.py only) |
| 15 | backend/soul/ | **REQUIRED** | B-V2, LF, PYTEST, t-sleep |
| 16 | backend/simulation/ | **SUPPORTING** | PYTEST (test_simulation_engine.py only) |
| 17 | backend/abstraction/ | **REQUIRED** | LF, COG-S, PYTEST (transitive via cognition) |
| 18 | backend/runtime/ | **SUPPORTING** | PYTEST (test_event_system.py), evaluation |
| 19 | backend/ops/ | **SUPPORTING** | PYTEST (test_ops.py), llm_client |
| 20 | backend/nlp/ | **SUPPORTING** | PYTEST (test_temporal_parser.py only) |
| 21 | backend/evaluation/ | **SUPPORTING** | PYTEST (4 test files) |
| 22 | backend/audio/ | **OPTIONAL** | None |
| 23 | backend/testing/ | **OPTIONAL** | None |
| 24 | backend/tools/ | **OPTIONAL** | None |
| 25 | backend/contracts/ | **OPTIONAL** | None (orchestration/validator not on critical path) |
| 26 | backend/agents/ | **DEAD** | None |
| 27 | backend/orchestrator.py | **LEGACY** | None |
| 28 | backend/brain.py | **LEGACY** / **DUPLICATED** | None |
| 29 | backend/self_coder.py | **LEGACY** / **DUPLICATED** | None |
| 30 | velynx_core/ | **DUPLICATED** | EXP-0 (test_velynx_core.py) |
| 31 | velynx/ | **REQUIRED** | LF, COG-S, PYTEST (pipeline tests) |
| 32 | validation/ | **REQUIRED** | R1, R2A, R3, C8, R3C, B-PROD, R-TEST |
| 33 | research/ | **REQUIRED** | R1, R2A, R3, R3E, R3F, R-TEST |
| 34 | frontend/ | **DECORATIVE** | None |
| 35 | experiments/ | **DEAD** | None |
| 36 | configs/ | **SUPPORTING** | None (with defaults) |
| 37 | curriculum/ | **SUPPORTING** | LF, PYTEST (curriculum-dependent tests) |
| 38 | Root diagnostic scripts | **OPTIONAL** | None |
| 39 | Root standalone experiments | **RESEARCH_ONLY** | Only themselves |
| 40 | scripts/ | **OPTIONAL** | None |
| 41 | docs/ | **DECORATIVE** | None |
| 42 | data/ | **SUPPORTING** | Subsystems that read them fail |
| 43 | searxng/, kiro-gateway/ | **OPTIONAL** | None (fallback chains) |
| 44 | backend/__init__.py | **REQUIRED** | ALL (backend package breaks) |
| 45 | backend/cli.py, chat.py, cli_ui.py | **OPTIONAL** | None |

---

## Minimal Program C

The irreducible subsystem set required to run ALL experiments:

```
REQUIRED (23):
  backend/__init__.py
  backend/app/
  backend/cognition/
  backend/pipeline/
  backend/memory/
  backend/knowledge/
  backend/learning/
  backend/agency/
  backend/reflection/
  backend/conversation/
  backend/retrieval/
  backend/models/
  backend/database/
  backend/metacognition/
  backend/abstraction/
  backend/soul/
  backend/nlp/           (for PYTEST)
  backend/ops/           (for PYTEST)
  backend/runtime/       (for PYTEST/evaluation)
  backend/evaluation/    (for PYTEST)
  velynx/
  validation/
  research/

SUPPORTING (4):
  backend/self_model/    (1 test depends on it)
  backend/simulation/    (1 test depends on it)
  configs/
  curriculum/
  data/

REMOVABLE (18):
  frontend/
  experiments/
  scripts/
  docs/
  searxng/
  kiro-gateway/
  backend/audio/
  backend/tools/
  backend/testing/
  backend/contracts/
  backend/agents/
  backend/orchestrator.py
  backend/brain.py
  backend/self_coder.py
  velynx_core/           (if EXP-0 is not a formal experiment)
  cognitive_core.py
  cognitive_health.py
  Root diagnostic scripts
  Root standalone experiment scripts
  backend/cli.py, chat.py, cli_ui.py
```

Total file count reduction: ~38% of files removed, ~95% of experiments preserved. The formal research experiment suite (R1-R3F) loses zero experiments.
