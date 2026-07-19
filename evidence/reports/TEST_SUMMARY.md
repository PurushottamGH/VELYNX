# Test Summary — Sprint 1

**[FACT]** All tests pass. No regressions.

---

## Results

| Suite | File | Tests | Pass | Fail | Skip |
|-------|------|-------|------|------|------|
| Core canonical | `tests/unit/test_core_canonical.py` | 29 | 28 | 0 | 1 |
| E0 components | `tests/unit/test_e0_components.py` | 57 | 57 | 0 | 0 |
| E0 pipeline | `tests/integration/test_e0_pipeline.py` | 15 | 15 | 0 | 0 |
| **Total** | | **101** | **100** | **0** | **1** |

The 1 skipped test (`TestBannedSymbols::test_no_banned_symbols_in_core`) is a pre-existing manual check. Verified separately via grep: no banned symbols in `core/` or `experiments/E0/`.

---

## Test Coverage by Blocker

| Blocker | Test Class | Tests | Status |
|---------|------------|-------|--------|
| Blocker 1 (C2 capacity-matched) | `TestC2CapacityMatched` | 4 | ✅ All pass |
| Blocker 2 (default seeds >= 5) | `TestMultiSeedRunner` | 5 | ✅ All pass |
| Blocker 3 (latent-state correctness) | `TestLatentStateRegression` | 5 | ✅ All pass |
| Blocker 4 (growth ordering) | `TestGrowthOrderingRegression` | 3 | ✅ All pass |
| Blocker 4 (M margin) | `TestGrowthDecision::test_decider_honors_m_static_margin` | 1 | ✅ Pass |

---

## Execution

```bash
# All tests
python -m pytest tests/ -v

# Unit only
python -m pytest tests/unit/ -v

# Integration only
python -m pytest tests/integration/ -v
```

All tests complete in ~17s on reference hardware.

---

## Warnings

3 warnings (all identical): `RuntimeWarning: Precision loss occurred in moment calculation due to catastrophic cancellation` from `scipy.stats.ttest_rel` when data are nearly identical. This is benign — the test verifies the paired t-test correctly rejects when data are indistinguishable.
