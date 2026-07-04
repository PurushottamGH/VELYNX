# C3 Instrumentation Report — Sprint 1.2

## 1. Code Change

**File:** `experiments/E0/run.py` — `run_shuffled_input()` (C3 condition)

**Added:** `per_step_log: List[Dict]` initialization (line 455), `per_step_log.append(...)` block after each MDL check (lines 508–517), and `"per_step_log"` key in the return dict (line 543).

**Format is identical to `run_treatment()`:**
```
step, capacity_before, capacity_after, entropy_before, entropy_after,
lambda_model, gain, grew
```

**No other code was modified.** Growth logic, DV-a, DV-b, controls, statistics, and the experiment mathematical core are untouched.

---

## 2. MDL Check Counts — Pre-Fix (20-seed run, evidence copy)

| Condition | Seeds | Per-Step Log Entries | Growth Events |
|-----------|-------|---------------------|---------------|
| T (Treatment) | 8 (seeds 42–49) | **144** (18/seed) | 0 |
| C3 (Shuffled-input) | 8 (seeds 42–49) | **0** | 0 |

**Gap confirmed:** C3 ran the identical `should_grow()` MDL logic but never persisted the
diagnostic trace. `growth_diagnostics.py` could read T data but produced an
empty C3 column.

---

## 3. Post-Fix Expectation

After the next experiment run, C3 will populate `per_step_log` with entries
identical in structure to T. Counts are expected to be equal
(within rounding) since both conditions evaluate at the same
`warmup_steps`/`evaluate_every` cadence.

The `growth_events` list is only appended when `predictor.grow()` is
called — neither the condition's count nor the DV-a/DV-b verdict paths
are affected by this change.

---

## 4. Integration Review #002

**Not found in INTEGRATION_LEDGER.md.** The ledger ends at Review #001
(line 82: *"Awaiting next engineering delivery."*). The T==C1
exact-equality question was discussed during Review #001 (F1 findings)
but Review #002 was never drafted. The fix for F1 has been delivered
but not yet submitted for formal review — hence no Review #002 entry exists.

---

## 5. Verification Checklist

- [x] `run_shuffled_input()` now initializes `per_step_log`
- [x] `per_step_log.append(...)` fires on every MDL-check tick (same as Treatment)
- [x] Return dict includes `"per_step_log"` key
- [x] Growth logic (line 504–506) unchanged
- [x] DV-a / DV-b measurement paths untouched
- [x] Treatment comparison path untouched
- [x] Pre-fix gap confirmed via `growth_diagnostics.py` (T=144, C3=0)
