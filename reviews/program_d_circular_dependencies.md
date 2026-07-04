# Program D — Circular Dependency Detection

## Purpose
Identify all circular import chains that may cause runtime errors, initialization deadlocks, or design fragility.

---

## 1. CONFIRMED CIRCULAR IMPORTS (risk: HIGH)

### C1: `scenario_engine.py` ↔ `metacog.py`

**Path:**
```
backend/cognition/scenario_engine.py:15   import backend.cognition.metacog  → reflect
backend/cognition/scenario_engine.py:49   from backend.cognition.metacog import reflect  (re-import)
backend/cognition/metacog.py:145          from cognition.scenario_engine import parse_scenario
```

**Mechanism:**
- `metacog.reflect()` conditionally imports `parse_scenario` inside the function body (lazy import)
- `scenario_engine.parse_scenario()` calls `metacog.reflect()` (though reflect conditionally imports)
- `scenario_engine` also redundantly re-imports `reflect` at line 49

**Resolution:**
- The lazy import in `metacog.py:145` (`from cognition.scenario_engine import parse_scenario`) avoids the import-time crash
- But the redundant import at `scenario_engine.py:49` creates a latent cycle risk

---

## 2. POTENTIAL CIRCULAR CHAINS (risk: MEDIUM)

### C2: `backend/brain.py` → `backend/self_coder.py` → `backend/memory/` → `backend/brain.py`

**Path:**
```
backend/brain.py:12-17   imports backend.memory.knowledge_graph, backend.cognition.reasoning_engine,
                          backend.self_coder, backend.reflection.reflection_engine
backend/self_coder.py:   imports backend.memory (via runtime validation paths)
backend/memory/*.py:     MAY import backend.brain (not confirmed, but pattern exists in velynxs_core)
```

**Risk: LOW** — no confirmed import of `brain.py` from `memory/` in backend.

### C3: `cognitive_core.py` → `concept_birth.py` → `cognitive_core.py`

**Path:**
```
cognitive_core.py:        imports concept_birth.evaluate_concept_birth (defensive)
concept_birth.py:206      from cognitive_core import InternalModelView (defensive)
```

**Mechanism:**
- `cognitive_core.py` has `try: from concept_birth import *` (lines 20-23)
- `concept_birth.py` has `try: from cognitive_core import InternalModelView` (line 18)
- Both are lazy/defensive imports using try/except, so import-time crash is avoided
- But the cycle exists logically — neither module can be imported before the other

**Resolution:**
- Extract `InternalModelView` into a shared types module
- Both modules already handle ImportError gracefully

### C4: `cognitive_core.py` → `cognitive_health.py` → `validation/metrics.py` → `cognitive_core.py` (indirect)

**Path:**
```
cognitive_core.py → cognitive_health.py (proxy)
cognitive_health.py → validation/metrics.py, validation/report.py
validation/ → backend/cognition/ → cognitive_core.py (through runner)
```

**Risk: LOW** — the chain is indirect and all imports are runtime-safe.

---

## 3. IMPORT GRAPH SUMMARY

```
       scenario_engine.py
          ↕        (circular via lazy import)
         metacog.py

       cognitive_core.py
          ↕        (circular via defensive import)
       concept_birth.py
```

## Experiments Affected
- `run_benchmark_v2.py` imports `scenario_engine` → may trigger circular import
- `run_benchmark_v2.py` may also trigger `metacog.reflect()` path

## Removal Risk
- **HIGH for C1**: Breaking either lazy import will crash the pipeline at import time
- **MEDIUM for C3**: Both defensive imports already handle failure, but design is fragile
- **LOW for C2, C4**: No confirmed direct cycles

## Regression Tests
- `python -c "from backend.cognition.scenario_engine import parse_scenario"`
- `python -c "from backend.cognition.metacog import reflect"`
- `python -c "from cognitive_core import CognitiveEngine"`
- These should all pass without ImportError

## Confidence
- 0.95 for C1 (confirmed by reading both files)
- 0.90 for C3 (confirmed by reading defensive import blocks)
- 0.70 for C2, C4 (potential chains not fully traced)
