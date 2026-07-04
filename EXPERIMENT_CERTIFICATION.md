# EXPERIMENT_CERTIFICATION

**Auditor:** Scientific Validation Lead, Program D
**Date:** 2026-07-04
**Scope:** Controls, baselines, experimental validity, and reproducibility of all four pre-registered experiments
**Reference:** `PROGRAM_D_CANONICAL.md §7`; `SCIENTIFIC_CERTIFICATION.md`

---

## Verdict: **WARNING**

Sprint 1 implements and tests **E0** to a high standard. EXP-0 is implemented as a harness but **not runnable** (dataset missing). EXP-1 and EXP-2 are **not implemented** (only empty package directories). The prior `EXPERIMENT_CERTIFICATION.md` marked E0 as "Scientifically invalid"; that assessment is now stale — E0 is valid but the verdict (H\* pass/kill) has not been produced.

---

## 1. EXP-0 — Paraphrase Precondition

### Status: **READY BUT NOT EXECUTABLE**

### Controls
- **Original 32 queries**: 32 "What is X?" paired with the 32 seeded concept names. **Valid** as a positive control.
- **Paraphrase queries**: Designed to be keyword-free, but **the `paraphrases.json` file is missing from the repository**. The `dataset.py` loader will raise `DatasetIntegrityError` or `FileNotFoundError` on import.

### Baselines
- **Random baseline**: Referenced in the prior `EXPERIMENT_CERTIFICATION.md`; not present in the current EXP-0 code path. The current implementation relies on within-subject paired comparison (original vs paraphrase per concept), not a random baseline per concept.
- **Tier 2 (legacy lexical)**: Acts as a control for Tier 1 (V2 semantic). Both run on the same 64 (item, condition) pairs, so a collapse on Tier 1 with no collapse on Tier 2 would isolate the semantic layer.

### State isolation
- **Wipe mechanism**: `scripts/wipe_db.py` is called before every Tier 1 and Tier 3 trial. This is the **same reset path** used by `backend/tests/live_fire_harness.py`, so the two will not diverge.
- **Interleaved trial order**: `_trial_order` in `run_exp0.py:87-96` shuffles (item_index, condition) pairs using `random.Random(seed)`, ensuring originals and paraphrases are interleaved rather than blocked. This bounds within-run state drift.

### Leakage checks
- **Substring check**: `leakage_check.py:84-86` uses `concept_lower in query_lower` — matches `soul_lookup_legacy`'s production fast path.
- **Porter-stem check**: `leakage_check.py:89-100` re-implements the exact stemming behavior of `soul_router.py:_stem_match`, including the byte-for-byte reproduction of the multi-word concept stemming (`stem("market collapse") == "market collaps"`). This was the subject of a prior review and is now correct.
- **Original-query sanity**: `leakage_check.py:140-144` confirms the original query does contain its own concept (so the control condition is valid).

### Statistical validity
- **McNemar exact test**: `analysis.py:41-61` — two-sided, binomial on discordant pairs, no continuity correction. Correct for n=32.
- **Paired bootstrap CI**: `analysis.py:64-87` — 10,000 iterations, resamples item indices with replacement (paired), seed=0 for determinism.
- **Holm-Bonferroni**: `analysis.py:90-104` — step-down correction across the two primary tiers.

### Dataset integrity
- **SHA-256 hash**: `dataset.py:50-60` checks `paraphrases.json`'s recorded `source_file_sha256` against the live `concepts.json` hash. A drift raises `DatasetIntegrityError`.
- **Concept set match**: `dataset.py:62-70` verifies the paraphrase item set exactly matches the concept set.

### Gaps
- **`paraphrases.json` is missing**: the EXP-0 dataset is **not in the repository**. The runner will fail immediately.
- **EXP-0 has never been run**: no `artifacts/` directory with `exp0_report.md` or `exp0_summary.json` exists.
- **Random baseline missing**: the prior certification noted a random baseline; the current implementation does not include one.
- **No Tier 3 artifact**: Tier 3 (full pipeline) requires LLM API access and has never been tested in EXP-0.

### Decision
**Block on dataset.** Commit `paraphrases.json`, run EXP-0, then re-certify.

---

## 2. EXP-1 — Program A Calibration Gate (H1)

### Status: **NOT IMPLEMENTED**

### Controls
- **BM25/TF-IDF retrieval with randomly assigned confidence**: **Missing.**
- **Constant-confidence baseline**: **Missing.**

### Baselines
- **≥200 mixed queries (facts, ambiguous, hallucinations)**: **Missing.** No query set in the repository.
- **Reliability diagram**: Not generated anywhere in the codebase.
- **ECE computation**: `core/measurement/proper_scoring.py:42-72` implements `expected_calibration_error` correctly, but it is not wired to any experiment.

### Experimental validity
- **Unverifiable.** The `experiments/EXP1/` directory contains only an empty `__init__.py`.
- The prior `EXPERIMENT_CERTIFICATION.md` from a prior audit correctly states: "Status: Blocked." This is still true.

### Goodhart guard
- **Bin-boundary hacking detection**: Not implemented. The `expected_calibration_error` function uses fixed equal-width binning, which is a standard but not bin-boundary-attack-resistant choice.

### Decision
**Block.** EXP-1 is a required deliverable (canon §3 deliverable #1, priority 1) and is not built.

---

## 3. EXP-2 — Affective Indexing (H2)

### Status: **NOT IMPLEMENTED**

### Controls
- **Unframed (neutral) prompt**: **Missing.** No prompt templates exist.
- **Third-party task set**: **Missing.** The circularity guard (canon §6-H2, §10 Issue-6) forbids the 32 authored soul concepts, but no alternative task battery has been assembled.

### Baselines
- **Framed vs unframed success rates**: Not measurable — no task set, no scorer.
- **Pre-registered significance test**: Not configured.

### Experimental validity
- **Unverifiable.** The `experiments/EXP2/` directory contains only an empty `__init__.py`.
- The prior `EXPERIMENT_CERTIFICATION.md` correctly states: "Status: Blocked." This is still true.

### Circularity guard
- The `experiments/E0/` code does **not** import `program_b` or `concepts.json` — verified by reading the E0 module imports (`core.predictors.dirichlet_markov`, `core.mdl.mdl_growth`, `core.measurement.proper_scoring`, `core.emergence.emergence_statistic`, `experiments.E0.*`). This is the correct posture for E0 but does not address EXP-2's circularity requirement.

### Decision
**Block.** EXP-2 is a required deliverable (canon §3 deliverable #2) and is not built.

---

## 4. E0 — H\* Decider

### Status: **IMPLEMENTED, TESTED, NOT EXECUTED AT FULL SCALE**

### Controls (all four present)

| Condition | Implementation | Test coverage | Validity |
|---|---|---|---|
| **T** (error-gated growth) | `run_treatment` in `run.py:180-288` | 5 condition-runner tests + 4 growth-ordering tests | **Valid** |
| **C1** (fixed capacity) | `run_fixed_capacity` in `run.py:291-339` | 2 tests | **Valid** |
| **C2** (capacity-matched random growth) | `apply_growth_at_random_times` in `run.py:342-415` | 4 capacity-matched tests | **Valid** |
| **C3** (shuffled input) | `run_shuffled_input` in `run.py:418-503` | 2 tests | **Valid** |

### C2 capacity-matching (the C2 fix)
- **Same growth count as T**: `run.py:549-588` runs T first, then passes `t_growth_count` to C2. Verified by `test_c2_has_same_growth_count_as_t`.
- **Same final capacity**: `test_c2_has_same_final_capacity_as_t` passes.
- **Random timing, not error-correlated**: `test_c2_growth_timing_is_random` verifies that C2 growth event indices are uniform across the run and differ from T's.

### Baselines
- **Linear predictive baseline**: `experiments/E0/leakage_check.py:23-98` verifies that a multinomial logistic regression cannot recover the latent from observations (addresses assumption I3 and failure mode F1). The `is_nonlinear` flag is True if accuracy < chance + 0.1.

### DV-a: Held-out predictive log-likelihood
- **Metric**: mean log P_θ on the last 20% of the training sequence.
- **Computation**: `core/measurement/proper_scoring.py:75-107` → `predictive_log_likelihood` (correct proper scoring rule per Bernardo 1979).
- **Test**: `test_log_loss_monotonic` confirms lower loss for better predictions.

### DV-b: Null-referenced emergence statistic
- **Definition**: `M = NMI(learned, true) − NMI(learned, shuffled)`.
- **Null reference**: C3's inferred latent states (the shuffled-input control). This is the correct construction per canon §5.5.
- **Margin**: `M_STATISTIC_MARGIN = 0.05` (pre-registered, hardcoded).
- **Test**: `test_null_referenced_centering` verifies |M| < 0.3 for random data; `test_emergence_statistic_positive_for_correlated` verifies M > 0 when learned correlates with true.

### Statistical test for DV-a
- **Paired one-sided t-test** (scipy.stats.ttest_rel, converted to one-sided) for ≥2 seeds.
- **Bootstrap permutation** for <2 seeds.
- **p<0.01 threshold** matches canon §6-H\*.

### Kill criteria
- **H\* falsified if**: T fails to beat BOTH C1 and C2 on DV-a at p<0.01 across ≥5 seeds, **OR** DV-b within noise of shuffled control — after two honest attempts.
- **Wired**: `E0Decider.should_falsify` returns `(True, reason)` after two non-pass attempts. `INCONCLUSIVE` (insufficient seeds) does not count as a pass.

### Reproducibility
- **Seed registry**: `SeedRegistry` separates env seed from agent seed per condition.
- **Determinism**: `test_seeded_reproducibility` verifies identical seeds produce identical log-likelihood sequences.
- **Environment determinism**: `test_environment_deterministic_with_seed` and `test_environment_different_seeds_different` pass.

### Gaps
- **Full 5-seed run with default config not executed**: No `aggregated_results.json` artifact exists. The sprint's tests run at much smaller scale (n_train_steps=100–500, not the 10,000 in the default).
- **No H\* verdict produced**: The pass/kill decision has never been emitted for a full-scale run.
- **M margin is hardcoded**: 0.05 is not derived from the null distribution. A data-derived margin (e.g., `mean(M_shuffled) + 2·std(M_shuffled)`) would be more defensible.
- **Held-out split from same trajectory**: `compute_held_out_log_likelihood` uses the last 20% of train, not a fresh environment instance. The dataset's `generate_train_test_sequences` method exists but is **not called** by any runner.

### Decision
**Valid implementation, but no experimental result.** E0 is the strongest deliverable in Sprint 1. It must be run end-to-end at scale before the H\* verdict is meaningful.

---

## 5. Summary

| Experiment | Implementation | Test coverage | Executed at scale | Verdict |
|---|---|---|---|---|
| **EXP-0** | Complete harness | N/A (no tests) | **No** (dataset missing) | **Block** |
| **EXP-1** | **Not implemented** | None | N/A | **Block** |
| **EXP-2** | **Not implemented** | None | N/A | **Block** |
| **E0** | Complete, canon-exact | 60+ tests, all pass | **No** (small-scale only) | **Valid implementation, no result** |

### Overall: **WARNING**

Sprint 1 delivers a scientifically sound E0 implementation with strong test coverage. But only one of four pre-registered experiments is built, and none has been executed at production scale. The "100 tests pass" claim is true but covers **E0/components only**, not the full experiment suite.

---

**Experiment Certification Verdict: WARNING**
