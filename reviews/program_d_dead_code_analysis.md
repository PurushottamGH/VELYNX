# Program D — Dead Code Analysis

## Purpose
Identify code that is defined but never imported, called, or reachable at runtime. Every flagged item should be archived (not deleted) after verification.

---

## 1. DEAD MODULES (never imported by any other module)

| # | File | Lines | Reason | Removal Risk |
|---|------|-------|--------|-------------|
| 1 | `backend/tools/dedupe_directions.py` | ~50 | No import found | LOW |
| 2 | `backend/tools/visualize_graph.py` | ~50 | No import found | LOW |
| 3 | `backend/conversation/*.py` | ~200 | No import found | MEDIUM |
| 4 | `backend/contracts/*.py` | ~100 | No import found | MEDIUM |
| 5 | `backend/simulation/*.py` | ~200 | No import found | MEDIUM |
| 6 | `backend/nlp/*.py` | ~200 | No import found | MEDIUM |
| 7 | `backend/agents/*.py` | ~200 | No import found | MEDIUM |
| 8 | `experiments/test_calc.py` | 2 | Trivial stub | LOW |
| 9 | `experiments/calculator.py` | 17 | Duplicate of backend tool gen | LOW |
| 10 | `experiments/generated_tool.py` | 11 | Auto-generated stub | LOW |
| 11 | `peek_code.py` | 5 | Debug utility, no callers | LOW |
| 12 | `find_the_truth.py` | 10 | Debug utility, no callers | LOW |
| 13 | `find_ghosts.py` | 24 | Debug utility, no callers | LOW |
| 14 | `ghost_hunt.py` | 27 | Debug utility, no callers | LOW |

## 2. DEAD FUNCTIONS/CLASSES (defined but never called)

| # | Location | Symbol | Notes |
|---|----------|--------|-------|
| 1 | `cognitive_core.py` | `SensoriumVitals.glyph` (property) | Defined but never accessed externally |
| 2 | `backend/cognition/advanced_cognition.py` | `HumanUnderstandingMode._humanize()` | Internal helper, used only internally |
| 3 | `backend/cognition/scenario_engine.py` | `reflect` re-import at bottom | Redundant import (line 49) |
| 4 | `backend/orchestrator.py` | `SYSTEM_PROMPT_CODE_GEN` | Defined but `llm_client` is removed — dead constant |
| 5 | `backend/orchestrator.py` | `_llm_infer_filename()` | Calls `llm_client` which is removed — dead function |
| 6 | `backend/orchestrator.py` | `_llm_generate_code()` | Calls `llm_client` which is removed — dead function |
| 7 | `cognitive_health.py` | Entire module | Proxy — all logic migrated to validation/ |
| 8 | `velynx_core/self_coder.py` | `scan_codebase()` function | Named but never called from outside |

## 3. DEAD IMPORTS (imported but never referenced)

| # | File | Dead Import |
|---|------|-------------|
| 1 | `backend/chat.py` | `asyncio`, `sys`, `os` — partially used |
| 2 | `backend/cli.py` | `__future__.annotations` — only used in type hints |
| 3 | `backend/cognition/scenario_engine.py` | Line 49 re-import of `reflect` |

## 4. UNREACHABLE BRANCHES

| # | File | Branch | Notes |
|---|------|--------|-------|
| 1 | `backend/orchestrator.py` | Lines 168-213, 216-237 | `_llm_generate_code`, `generate_tool_script`, `_infer_filename` all use removed LLM client |

## Dependencies
- Dead module removal requires checking git log for intent
- `cognitive_health.py` removal requires updating `cognitive_core.py` imports

## Experiments Affected
- None directly (dead code is not under test)
- Removing `cognitive_health.py` proxy may break `cognitive_core.py` import chain

## Removal Risk
- LOW: Most items have zero callers
- MEDIUM: `backend/conversation/`, `backend/contracts/` may be needed for Phase 60+ features

## Regression Tests
- `test_probe.py`, `test_sleep.py`, `test_agency.py` may depend on dead modules
- Run full test suite after archival

## Confidence
- 0.90 for items with confirmed zero imports (via grep)
- 0.60 for subpackages where future code may reference them
