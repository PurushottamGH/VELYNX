# SPRINT 1.3 — Preregistration: Forced-Growth Condition (C2f)

**[FACT]** Preregistered before any code is written. No implementation has begun.

---

## 1. Motivation

Sprint 1 (E0) established that H*'s error-gated (MDL-gated) growth mechanism produced **0 growth events across 20 seeds** (42–61) at a true rate unlikely above ≈11%. This leaves a gap: is the MDL gate *necessary*, or would even unconditional forced growth suffice if enough capacity were injected?

Current controls:
- **C1:** Fixed capacity (no growth) — tests whether any growth at all is needed.
- **C2:** Same *count* of growth events as T, at random times — tests whether error-dependent timing matters, but C2's count is zero whenever T grows zero times. In Sprint 1, C2 never grew.

Neither control tests whether *forced capacity injection independent of any MDL check* can improve held-out prediction. C2f fills that gap.

---

## 2. Condition C2f — Forced Growth (Fixed k)

A new condition, independent of T's growth count, in which a fixed number `k` of growth events is injected at random step positions regardless of prediction error or MDL gain.

### 2.1 k-levels

| Level | k (forced growth events) | Rationale |
|-------|--------------------------|-----------|
| k=1   | 1                        | Minimal — does even one extra state help? |
| k=2   | 2                        | Doubling the minimal |
| k=4   | 4                        | Quadrupling — 2 extra states beyond k=2 |
| k=8   | 8                        | Aggressive — potentially overshoots optimum |

k-levels are spaced as powers of 2 to span a wide range economically: from near-minimal (1) to far beyond what T could plausibly produce (8) given that T grew 0 times across 20 seeds.

### 2.2 Growth-position sampling

For each seed and each k-level:
1. Draw `k` random step positions uniformly from `[train_steps//10, train_steps)` (same minimum-step constraint as C2).
2. Inject `predictor.grow()` at those positions regardless of prediction loss or MDL gain.
3. No warmup or evaluate_every gating — growth happens unconditionally at the chosen positions.

### 2.3 Independence from T

This is the critical design constraint. In the current `run_single_seed` (`experiments/E0/run.py:590-634`), C2 receives `t_growth_count` from the treatment condition:

```python
t_growth_count = len(condition_result.get("growth_events", []))
...
condition_result = apply_growth_at_random_times(
    ...
    growth_count=t_growth_count,  # <-- derived from T
    ...
)
```

**C2f must NOT do this.** C2f's `k` is a preregistered constant, not a derived value. Each of the four k-levels runs independently on each seed. The implementation sketch:

```
for each seed:
    for each k in [1, 2, 4, 8]:
        predictor = fresh DirichletMarkovPredictor(initial_capacity=K0)
        inject k growth events at random positions (uniform, no MDL check)
        measure held-out log-likelihood on test sequence
```

The four k-levels share the same environment sequence per seed (same `env_seed`) but use independent predictor instances.

---

## 3. Kill Criteria

### 3.1 Primary question

Does forced growth (any k) help? That is, does C2f(k) beat C1 on held-out predictive log-likelihood (DV-a)?

### 3.2 Preregistered test

| Element | Specification |
|---------|---------------|
| **DV** | Mean held-out log-likelihood (same DV-a as E0) |
| **Comparison** | C2f(k) > C1, one-sided |
| **Test** | Paired t-test across seeds (paired by seed) |
| **Significance threshold** | `alpha = 0.01` per comparison |
| **Multiple comparison correction** | Holm-Bonferroni across all 4 k-levels and the existing T vs C1 comparison (5 tests total) |
| **Net threshold** | FWER = 0.01 across the family |

### 3.3 Decision rule

- **"Forced growth helps" (pass):** At least one C2f(k) shows significantly greater held-out log-likelihood than C1 at FWER ≤ 0.01.
- **"Forced growth doesn't help" (kill):** No C2f(k) significantly beats C1 at FWER ≤ 0.01.

This is deliberately the *same* standard applied to T vs C1 in E0. If forced growth at any intensity fails to beat fixed-capacity at p < 0.01 (corrected), then even unconditional capacity injection is not beneficial, and the hypothesis space shrinks to the necessity of *error-guided* timing.

### 3.4 Ancillary question

If any C2f(k) beats C1, the secondary question is: at what k does T's performance fall relative to C2f? If T (with zero growth events) equals or exceeds the best C2f(k), then the MDL gate is saving capacity relative to forced injection. If C2f(8) outperforms T, then T is *under-growing* and the MDL threshold may be too conservative. This ancillary comparison is **not** a kill criterion — it guides interpretation.

---

## 4. Seed Count (Binomial Power Precheck)

Sprint 1's lesson: defaulting to n=5 gives 44% chance of missing a 15% effect rate. The binomial power method from `evidence/11_power_analysis.md` and `EXP1_PREREGISTRATION.md §7` applies directly:

```
P(miss a seed-level effect across n seeds) = (1 - p)^n
```

Target: P(miss) < 0.10.

### 4.1 What is the relevant seed-level effect?

For C2f, the seed-level binary event is: "C2f(k) beats C1 on held-out log-likelihood at this seed." At k=1 (single forced growth), the effect is weakest — the organism may simply not use the extra capacity. At k=8, the effect should be more reliable. The conservative design targets the weakest k-level (k=1), since if k=1 is detectable, higher k are too.

Expected seed-level effect rate for k=1: approximately 20–40% (a single forced growth is subtle; many seeds may show no net benefit).

### 4.2 Minimum seeds required

| Expected effect rate p (k=1 beats C1) | Minimum seeds for P(miss) < 0.10 | P(miss) at minimum n |
|---:|---:|---:|
| 10% | 22 | 0.0985 |
| 15% | 15 | 0.0874 |
| 20% | 11 | 0.0859 |
| 25% | 9 | 0.0751 |
| 30% | 7 | 0.0824 |
| 40% | 5 | 0.0778 |

### 4.3 Preregistered n

**n = 22 seeds.**

This is the most conservative entry in the table (detecting a 10% per-seed benefit rate). It follows the same target as EXP-1's preregistration and rules out even very weak forced-growth effects that might only help in 10% of seeds. Using fewer than 22 seeds would repeat Sprint 1's original power mistake — for example, n=11 could miss a true 10% benefit rate 31% of the time.

Each of the 22 seeds runs all 4 k-levels (C2f-1, C2f-2, C2f-4, C2f-8) plus the standard T, C1, C2, C3 conditions, all sharing the same environment sequence per seed.

---

## 5. Implementation Rule

- **Do not modify existing C1, C2, C3, or T condition runners.** C2f is a new condition added alongside existing ones.
- **Do not touch `run_single_seed`'s existing `t_growth_count` logic.** C2f's k is sampled from the preregistered list, not from T.
- **All four C2f k-levels use the same environment seed per seed** (same env as T/C1/C2/C3), but **independent predictor instances** (fresh `DirichletMarkovPredictor` per k-level).

---

## 6. Adjudication

- **If C2f(k) beats C1 for any k at FWER ≤ 0.01:** forced growth at some intensity is beneficial. The interesting question shifts to *whether T's zero-growth performance equals or exceeds the best forced-growth level* — assessing the value of the MDL gate.
- **If no C2f(k) beats C1:** even forcing up to 8 growth events at random times does not improve prediction over fixed capacity. This strengthens the conclusion that H*'s lack of growth is not an MDL-threshold artifact but reflects genuine optimality for the environment class tested.
- **If C2f at any k > T and T had zero growth:** the MDL gate is conservative; "even a stopped clock is right twice a day" — forced capacity sometimes helps by chance, but the MDL gate correctly avoids it when it doesn't.

No result can retroactively change these criteria. This preregistration is frozen at creation time, before any implementation or data collection.
