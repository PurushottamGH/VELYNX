# Program D — Duplicated Logic Detection

## Purpose
Catalog all cases where functionally identical or near-identical logic exists in multiple locations.

---

## 1. DUPLICATE MODULES (same name, different packages)

| # | Path A | Path B | Overlap | Risk |
|---|--------|--------|---------|------|
| 1 | `velynx_core/brain.py` (371 lines) | `backend/brain.py` (211 lines) | Both define `VelynxBrain` class with reasoning logic | HIGH |
| 2 | `velynx_core/memory.py` (365 lines) | `backend/memory/*.py` (~6000 lines) | Both manage concept storage, SQLite, embeddings | HIGH |
| 3 | `velynx_core/learner.py` (501 lines) | `backend/learning/*.py` (~4000 lines) | Both learn from web sources, extract concepts | HIGH |
| 4 | `velynx_core/self_coder.py` (617 lines) | `backend/self_coder.py` (145 lines) | Both modify own source code | HIGH |
| 5 | `backend/memory/knowledge_graph.py` | `backend/knowledge/knowledge_graph.py` | Both define `KnowledgeGraph` class | HIGH |

## 2. DUPLICATE LOGIC BLOCKS

### 2.1 Concept Extraction
| Location | Pattern | Duplicate In |
|----------|---------|--------------|
| `velynx_core/learner.py:141-227` | `extract_concept_from_source()` | `backend/learning/online_learner.py` |
| `velynx_core/brain.py:73-93` | `extract_concepts()` | `backend/cognition/scenario_engine.py:28-30` |

### 2.2 SQLite Connection Management
| Location | Pattern | Duplicate In |
|----------|---------|--------------|
| `velynx_core/memory.py:123-136` | `_conn()` context manager with WAL | `backend/memory/_sqlite.py:connect()` |
| `backend/cognition/predictive_core.py:29-32` | `_get_conn()` | `backend/memory/_sqlite.py` |

### 2.3 ANSI Terminal Colors
| Location | Pattern | Duplicate In |
|----------|---------|--------------|
| `velynx_core/velynx.py:42-51` | Color constants (CYAN, GREEN, RED, etc.) | `backend/cli_ui.py:40-49` |
| `velynx_core/velynx.py:53` | `c(text, color)` function | `backend/cli_ui.py:60-65` |

### 2.4 Contradiction Resolution
| Location | Pattern | Duplicate In |
|----------|---------|--------------|
| `backend/cognition/reasoning_engine.py:815-955` | Full symbolic contradiction resolver | `backend/cognition/advanced_cognition.py:136-204` (simple text-based) |

### 2.5 Stopwords / Emotion Words
| Location | Pattern | Duplicate In |
|----------|---------|--------------|
| `velynx_core/brain.py:68-71` | STOPWORDS set | `backend/cognition/metacog.py:14-28` (expanded set) |

### 2.6 Free-Energy Coefficients
| Location | Pattern | Duplicate In |
|----------|---------|--------------|
| `backend/cognition/decision_policy.py:79-81` | `DEFAULT_LAMBDA=1.0, MU=2.0, NU=0.5` | `validation/metrics.py:29-31` |

## 3. DUPLICATE DATA FILES
| # | File A | File B | Notes |
|---|--------|--------|-------|
| 1 | `velynx_identity.db` | `backend/data/*.db` | Multiple SQLite DBs with overlapping schemas |
| 2 | `velynx_state.db` | `backend/data/knowledge_graph.db` | State vs knowledge graph overlap |
| 3 | `backend/soul/concepts.json` | `data/soul_concepts.json` | Duplicate soul concept definitions |

## Experiments Affected
- All experiments using `backend/cognition/reasoning_engine.py` or `velynx_core/brain.py`
- Benchmarks may produce different results depending on which duplicate is exercised

## Removal Risk
- **HIGH**: The `velynx_core` and `backend` duplicates represent two parallel implementations. Removing one requires ensuring the other handles all call sites.
- **MEDIUM**: Duplicate constants risk drift (if one set of coefficients is updated but not the other).

## Regression Tests
- `test_replay_engine_vitals_r3c.py`
- `test_shared_metrics_v1.py`
- `test_agency.py`
- All validity depends on which code path executes

## Confidence
- 0.95 for module-name duplicates (confirmed by file listing)
- 0.80 for logic-block duplicates (confirmed by code reading)
- 0.60 for data-file duplicates (runtime state may differ)
