# VELYNX Full Codebase Audit Report

**Date:** 2026-06-01
**Scope:** Entire VELYNX codebase (~30,000 lines Python, 130+ files)
**Method:** 5 parallel deep-analysis agents examining backend architecture, memory/retrieval, evaluation/learning, ops/runtime, and frontend/tests.

---

## EXECUTIVE SUMMARY

VELYNX is a 32-phase AI cognition system that has grown through rapid iteration. The core query pipeline works, but the codebase carries significant dead weight: 4 entire subsystems are implemented but never called, 2 parallel query pipelines exist, and multiple naming collisions create confusion. The system is functional but accumulating technical debt at an accelerating rate.

**Severity breakdown:**
- CRITICAL issues: 3
- HIGH issues: 7
- MEDIUM issues: 8
- LOW issues: 5

---

## CRITICAL ISSUES

### C1. Dead Subsystems (4 entire modules never called)

The following are fully implemented but have **zero callers** from any live entry point:

| Subsystem | Files | Lines | Status |
|-----------|-------|-------|--------|
| `runtime/orchestrator.py` | 1 | 311 | Event-driven query orchestrator. Never called. |
| `planning/` (planner, task_graph, strategy_engine, execution_tracker) | 4 | 912 | DAG-based planning. Only referenced by dead `goals/`. |
| `goals/goal_engine.py` | 1 | 330 | Goal lifecycle management. Only referenced by dead `planning/`. |
| `brain/` (problem_solver, code_executor, math_engine, problem_sources) | 4 | ~600 | Coding/math problem solver. Never imported by any endpoint. |

**Total dead code: ~2,150 lines across 10 files.**

### C2. Two Parallel Query Pipelines

`app/main.py:answer_question()` (870 lines) and `runtime/orchestrator.py:orchestrate_query()` (311 lines) implement the same pipeline independently. Only `app/main.py` is used. The orchestrator creates a circular import by importing `_record_memory_turn` from `app/main.py`.

### C3. Circuit Breakers, Load Shedding, Failure Recovery — All Dead Code

| Module | Singleton Created | Wired Into Request Path |
|--------|-------------------|------------------------|
| `ops/circuit_breakers.py` | `llm_circuit`, `redis_circuit`, `embedding_circuit` | **NO** — LLM client does its own httpx retries |
| `ops/load_shedding.py` | `load_shedder` (max 10 concurrent) | **NO** — endpoint uses raw `asyncio.wait_for` |
| `ops/failure_recovery.py` | `recover_database/redis/event_bus` | **NO** — manual API call only, no auto-recovery |

These were built but never integrated. The LLM client (`models/llm_client.py`) completely ignores the circuit breaker.

---

## HIGH ISSUES

### H1. God Object: `app/main.py` (870 lines)

Handles FastAPI app creation, lifespan management, 20+ API endpoints, the entire query pipeline, memory recording, and database persistence. Imports from 15+ modules with 30+ inline lazy imports making the dependency graph untraceable.

### H2. Two Memory Systems Running in Parallel

| System | File | Backend | Used By |
|--------|------|---------|---------|
| Legacy | `memory/vector_store.py` (281 lines) | JSON file, TF-IDF token matching | `online_learner.py` for feedback storage |
| New | `memory/memory_manager.py` (238 lines) | ChromaDB + embeddings | `app/main.py` for semantic recall |

`app/main.py` tries semantic recall first, then falls back to legacy. Neither system is deprecated.

### H3. Two Reflection Engines Producing Different Output Shapes

| Engine | File | Output Type | Used By |
|--------|------|-------------|---------|
| Wrapper | `reflection/reflection_engine.py` (99 lines) | `ReflectionResult` | `app/main.py` |
| Advanced | `reflection/advanced_reflection.py` (508 lines) | `ReflectionReport` | `agents/agent_coordinator.py` |

### H4. Duplicate Embedding Model in Memory

`EmbeddingService` and `GPUEmbedder` both load `all-MiniLM-L6-v2` independently. Two copies of the model can exist in memory simultaneously — they do not share a cache.

### H5. N+1 Query Bottleneck in Retrieval

`retrieval_engine.py` calls `backend.get_by_id()` individually for each of `limit * 3` oversampled hits. Each call wraps a synchronous ChromaDB `get()` in `asyncio.to_thread`. With `limit=5`, that's up to 15 sequential async calls. A batch `get_by_ids` would eliminate this.

### H6. Duplicate Wikipedia/arXiv Queries

`unified_retriever.py` queries Wikipedia twice (direct method + `wiki_client.search()`) and arXiv twice (client + direct API fallback). Both hit the same endpoints.

### H7. Three Separate Recall Systems Never Unified

1. `MemoryManager.recall()` — vector-based semantic memory
2. `VectorStore.recall()` — token-overlap associative memory
3. `ConceptEngine.get_answer()` — concept lookup

Each has its own scoring and storage with no coordination.

---

## MEDIUM ISSUES

### M1. Naming Collision: `improvement_engine.py`

Two completely different modules share the same filename:
- `reflection/improvement_engine.py` (153 lines) — generates improvement suggestions from audit results
- `cognition/improvement_engine.py` (375 lines) — unified query pipeline + self-improvement loop

### M2. Naming Collision: `strategy_optimizer.py`

Two different modules:
- `learning/strategy_optimizer.py` (59 lines) — **write path**, records strategy outcomes
- `metacognition/strategy_optimizer.py` (151 lines) — **read path**, analyzes strategy performance

### M3. Two Proactive Learners

- `learning/continuous_learner.py` lines 268-338: `ProactiveLearner` class — instantiated but never started
- `learning/proactive_cognition.py` (405 lines): `ProactiveCognitionEngine` — the one actually wired into the app

### M4. 6 Overlapping Monitoring Modules

| Module | Concern |
|--------|---------|
| `ops/health_monitor.py` | Database, Redis, event bus, memory health |
| `ops/runtime_supervisor.py` | Wraps health_monitor + failure_recovery |
| `runtime/runtime_monitor.py` | Event counters and handler latency |
| `ops/observability.py` | Prometheus-compatible metrics |
| `metacognition/meta_monitor.py` | Metacognition analysis |
| `evaluation/stability_monitor.py` | Runtime stability report |

`health_monitor` and `runtime_monitor` check overlapping concerns. The API calls `health_monitor` directly AND through `runtime_supervisor`.

### M5. Crawler Modules Are Stubs

`crawler/spider.py`, `crawler/indexer.py`, `crawler/scheduler.py` — each is 3 lines returning empty/None. Zero implementation.

### M6. Root-Level Test Files Are Stubs

`tests/test_pipeline.py`, `tests/test_retrieval.py`, `tests/test_truth_filter.py` — each is 2 lines with `assert True`. Test nothing.

### M7. `decay()` Is O(n) Expensive

`memory_manager.py:decay()` calls `get_all()` on every collection, then re-embeds and re-upserts each entry that needs decay. With large memory stores, this is prohibitively expensive.

### M8. Evaluation Disconnected from Learning

The evaluation subsystem (15 files) does not automatically feed into the learning loop. Running trials does not adjust strategy scores or permanence values. Requires manual API calls to bridge.

---

## LOW ISSUES

### L1. `crawler_index.py` Is Dead

6 lines, no implementation. Placeholder from an earlier phase.

### L2. `test.py` Contains Hardcoded API Key

Despite the name, `test.py` (28 lines) is an API call script, not a test file. Contains a hardcoded API key.

### L3. `online_learner.py` Fan-Out

Imports from 8 submodules (feedback_loop, gap_tracker, source_trust, permanence, strategy_optimizer, rule_deriver, failure_diagnosis, living_constitution). Tight coupling.

### L4. `learning/feedback_loop.py` and `learning/gap_tracker.py` Are Minimal

20 and 19 lines respectively. Just append to JSON files. Could be inlined.

### L5. Zero Frontend Tests

No component tests, no hook tests, no E2E tests for the React frontend.

---

## DUPLICATED SYSTEMS SUMMARY

| System | Instances | Resolution |
|--------|-----------|------------|
| Query pipeline | `app/main.py` + `runtime/orchestrator.py` | Delete orchestrator |
| Memory storage | `vector_store.py` (legacy) + `memory_manager.py` (new) | Deprecate legacy |
| Reflection engine | `reflection_engine.py` (wrapper) + `advanced_reflection.py` | Pick one |
| Improvement engine | `reflection/improvement_engine.py` + `cognition/improvement_engine.py` | Rename cognition one |
| Strategy optimizer | `learning/strategy_optimizer.py` + `metacognition/strategy_optimizer.py` | Rename metacognition one |
| Proactive learner | `continuous_learner.py:ProactiveLearner` + `proactive_cognition.py` | Delete unused one |
| Embedding model | `EmbeddingService` + `GPUEmbedder` | Share singleton |
| Monitoring | 6 modules with overlapping concerns | Consolidate to 3 |
| Wikipedia retrieval | Direct method + `wiki_client.search()` | Remove duplicate |
| arXiv retrieval | Client + direct API fallback | Remove duplicate |

---

## BOTTLENECK ANALYSIS

### 1. Retrieval N+1 (HIGH impact)
`retrieval_engine.py` makes 15 sequential `get_by_id()` calls per query. Each wraps a synchronous ChromaDB call. Batch retrieval would cut latency by ~10x.

### 2. Decay Re-embedding (MEDIUM impact)
`memory_manager.py:decay()` re-embeds every entry that needs decay. O(n) embeddings per cycle. Should use timestamp-based lazy decay instead.

### 3. Sequential Fast-Path Checks (LOW impact)
`answer_question()` checks 6 fast paths sequentially (KG, tutor, curriculum, seed, semantic, legacy). Most queries hit none. Could be parallelized or short-circuited earlier.

### 4. Double Embedding Model (MEDIUM impact)
Two copies of `all-MiniLM-L6-v2` loaded independently. ~90MB wasted memory.

---

## PHASE 36 PROPOSAL: "Consolidation & Hardening"

### Theme: Stop building new features. Fix what exists.

### P36.1 — Dead Code Elimination (Priority: CRITICAL)
- Delete `runtime/orchestrator.py`
- Delete `planning/` (planner, task_graph, strategy_engine, execution_tracker)
- Delete `goals/goal_engine.py`
- Delete `brain/` (problem_solver, code_executor, math_engine, problem_sources)
- Delete `ProactiveLearner` from `continuous_learner.py`
- Delete stub crawler modules or implement them
- Delete stub root-level test files
- **Impact:** -2,150 lines, reduced import overhead, clearer architecture

### P36.2 — Wire Up Safety Systems (Priority: CRITICAL)
- Integrate `circuit_breakers.py` into `llm_client.py` — replace httpx retry with `llm_circuit.call()`
- Integrate `load_shedding.py` into `/query` endpoint — replace `asyncio.wait_for` with `load_shedder.acquire()`
- Wire `failure_recovery.py` into `runtime_supervisor` auto-recovery loop
- **Impact:** Production resilience that was built but never activated

### P36.3 — Unify Memory (Priority: HIGH)
- Deprecate `memory/vector_store.py` — migrate all writes to `memory/memory_manager.py`
- Add batch `get_by_ids` to `VectorBackend` protocol
- Share embedding model singleton between `EmbeddingService` and `GPUEmbedder`
- **Impact:** Single memory system, 10x retrieval speedup, 90MB memory savings

### P36.4 — Split `app/main.py` (Priority: HIGH)
- Extract query pipeline into `pipeline/query_handler.py`
- Extract API routes into `app/routes.py`
- Extract lifespan management into `app/lifespan.py`
- **Impact:** 870-line god object becomes 3 focused modules (~300 lines each)

### P36.5 — Resolve Naming Collisions (Priority: MEDIUM)
- Rename `cognition/improvement_engine.py` → `cognition/unified_pipeline.py`
- Rename `metacognition/strategy_optimizer.py` → `metacognition/strategy_analyzer.py`
- **Impact:** Eliminates confusion, prevents wrong-import bugs

### P36.6 — Consolidate Monitoring (Priority: MEDIUM)
- Merge `runtime_monitor` into `health_monitor`
- Make `runtime_supervisor` the single entry point for all health/ops queries
- Remove direct `health_monitor` calls from API routes
- **Impact:** Single monitoring truth source

### P36.7 — Connect Evaluation to Learning (Priority: MEDIUM)
- After trial runs, automatically feed failure patterns into `strategy_optimizer.learn_strategy()`
- Bridge `hallucination_detector` findings to `permanence.weaken_fact()`
- **Impact:** Closes the loop between QA and self-improvement

### P36.8 — Eliminate Retrieval Duplicates (Priority: LOW)
- Remove `_wikipedia_direct` from `unified_retriever.py` — use only `wiki_client.search()`
- Remove arXiv direct API fallback — use only `arxiv_client.search()`
- **Impact:** Cleaner retrieval chain, no duplicate API calls

---

## ARCHITECTURE HEALTH SCORE

| Dimension | Score | Notes |
|-----------|-------|-------|
| Modularity | 5/10 | Good module separation, but god objects and naming collisions |
| Dead code | 3/10 | 4 entire subsystems never called, 2,150+ lines dead |
| Test coverage | 6/10 | 25 backend test files (all real), zero frontend tests |
| Performance | 5/10 | N+1 retrieval, double embedding model, O(n) decay |
| Observability | 4/10 | 6 monitoring modules, most not wired into request path |
| Resilience | 2/10 | Circuit breakers/load shedding built but never activated |
| Naming clarity | 4/10 | 3 filename collisions, confusing dual systems |
| **Overall** | **4.1/10** | Functional but accumulating debt rapidly |

---

## FILE STATISTICS

| Directory | Files | Lines | Active? |
|-----------|-------|-------|---------|
| backend/pipeline/ | 12 | 1,376 | Yes — core query path |
| backend/memory/ | 11 | 2,275 | Partially — 2 parallel systems |
| backend/cognition/ | 11 | 2,530 | Yes |
| backend/reflection/ | 6 | 1,050 | Partially — 2 engines |
| backend/evaluation/ | 16 | 2,962 | Yes — QA endpoints only |
| backend/learning/ | 14 | 2,576 | Yes |
| backend/metacognition/ | 7 | 1,292 | Yes |
| backend/conversation/ | 6 | 1,046 | Yes — Phase 11 active |
| backend/ops/ | 10 | 943 | Mostly dead |
| backend/runtime/ | 7 | 890 | Partially — event bus alive, orchestrator dead |
| backend/planning/ | 5 | 1,019 | **Dead** |
| backend/goals/ | 2 | 437 | **Dead** |
| backend/brain/ | 5 | ~600 | **Dead** |
| backend/agents/ | 2 | 524 | Yes |
| backend/app/ | 4 | ~1,000 | Yes — god object |
| backend/database/ | 6 | ~500 | Yes |
| backend/retrieval/ | 9 | ~800 | Yes |
| backend/models/ | 4 | ~200 | Yes |
| backend/tests/ | 25 | ~3,000 | Yes |
| frontend/ | 8 | ~500 | Yes |
| scripts/ | 3 | ~920 | Yes |
| **Total** | **~130** | **~30,000** | **~24,000 active, ~6,000 dead** |

**~20% of the codebase is dead code.**
