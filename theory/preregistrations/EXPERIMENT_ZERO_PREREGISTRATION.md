# Experiment Zero Preregistration: Pipeline Validation Instrument (EXP-Z0)

**Experiment ID:** EXP-Z0
**Deliverable:** 3 (Experiment Zero) of the P1 Experimental Framework
**Purpose:** Validate the **research pipeline itself** — not intelligence — by running the smallest complete experiment that (a) has positive and negative controls, (b) rejects at least one deliberately inadequate explanation, (c) distinguishes at least two competing hypotheses, (d) measures uncertainty, and (e) commits success/failure criteria before execution.
**Phenomenon under instrument:** PH-1, temporal aliasing resolution (`PHENOMENON_REGISTRY.md`).
**Primary contrast:** memory-carrying reading of T-01 vs ALT-0 (memoryless sufficiency), with ALT-L (leakage) as the deliberately-inadequate explanation the design must be able to reject.
**Status:** Preregistered before implementation. No implementation code is fixed here. Author role: Principal Experimental Methodologist.

---

## 0. Why this experiment exists

**[FACT]** Experiment Zero is a **calibration run for the instrument**, in the metrological sense. Its success criterion is not "the system is intelligent" but "the pipeline can tell a real effect from four named impostors and quantify its own uncertainty." A pipeline that cannot pass EXP-Z0 cannot be trusted to run E0, EXP-1, or EXP-2. A pipeline that passes has demonstrated it can:

1. build an environment with a **known ground-truth** aliasing structure the system never sees;
2. compute a **memoryless ceiling** (negative-direction reference) analytically or empirically;
3. run a **positive control** (an oracle that provably has the disambiguating bit) and confirm it wins;
4. run a **negative control** (a system provably denied the bit) and confirm it does *not*;
5. **reject the leakage explanation** by an ablation intervention;
6. report effect sizes with **bootstrap uncertainty** across seeds;
7. apply a **pre-committed decision rule** with no post-hoc freedom.

If any of 1–7 cannot be executed, the finding is that the *pipeline* is inadequate — which is exactly the calibration information EXP-Z0 is designed to surface.

**[FACT]** EXP-Z0 deliberately uses a task where the correct answer is **analytically known**, so a "pass" is checkable against ground truth. This is the positive-control-first discipline: before measuring an unknown, measure a known and confirm the instrument reports it correctly.

---

## 1. Environment (frozen generator)

EXP-Z0 reuses the existing `framework/core/environment.py` regime machinery, restricted to make aliasing exact and analytic.

- **Latent regimes:** Two hidden regimes `R0, R1` with **identical stationary sensor marginals** but different transition consequences. Concretely, `R0` and `R1` map to the *same* attractor for the currently-emitted sensor vector, but differ in which observation is required next. This constructs genuine aliasing: the current sensor vector is by design uninformative about which regime is active.
- **Disambiguating carrier:** A single earlier observation (the "cue", `k` steps back) is the *only* signal that distinguishes `R0` from `R1`. The cue is emitted on the normal sensor channel (not a side channel), then the channel returns to the aliased marginal.
- **Aliased decision set `A`:** The timesteps at which the system must emit the regime-dependent correct output while its current input is in the aliased region. Ground-truth membership of `A` and the true regime are held in an experimenter-only register (never exposed to the system; same discipline as `Environment.ground_truth`).
- **Cue lag `k`:** fixed at `k = 8` steps (see Free Parameter Register). The carrier must be retainable within the stated memory budget; `k=8` is inside every tested budget so absence of PH-1 cannot be excused by infeasibility.

**Non-anticipation:** the generator is causal; no future observation influences a current output. This enforces the T-02 measurement discipline.

## 2. Systems under test and controls

| Role | System | What it establishes |
|---|---|---|
| **Treatment (T)** | A predictor with a bounded memory buffer of the last `m` observations (`m ≥ k`). | Can it use the carrier? The memory-carrying T-01 reading predicts it beats the ceiling. |
| **Negative control (N1) — memoryless** | Same predictor, `m = 0` (current input only). | The analytic **memoryless ceiling**. By construction it *cannot* resolve `A`. If N1 beats the ceiling, the environment leaks — instrument fault. |
| **Negative control (N2) — carrier ablated** | Treatment, but the cue observation is permuted across trials so the bit is destroyed while marginals are preserved. | The **leakage/ALT-L probe**. T must collapse to the N1 ceiling here. If it does not, apparent memory was leakage or a spurious correlate. |
| **Positive control (P1) — oracle** | Treatment handed the true regime label as an extra input on `A`. | Confirms the task is *solvable* and the scoring pipeline credits a system that provably has the bit. Must score near the analytic ceiling-for-oracle. |
| **Positive control (P2) — shuffled sanity** | Treatment on a stream with temporal structure shuffled. | Confirms the effect requires temporal structure; P2 must fall to the memoryless ceiling. |

The two negative and two positive controls are the minimum that make the four impostors (ALT-0, ALT-L, ALT-S, ALT-C) rejectable — see §5.

## 3. Metrics

- **DV-1 (primary): aliased-set loss gap** `Δ = L_ceiling − L_T` on set `A`, where `L` is mean held-out negative log-likelihood (`METRIC_SPECIFICATION.md` §4). `Δ > 0` means T resolves aliasing better than any memoryless policy. Reported in nats.
- **DV-2 (leakage guard): ablation collapse** `C = L_{N2} − L_T` on `A`. The memory-carrying reading requires `C` to be large and positive (removing the carrier hurts T). ALT-L predicts `C ≈ 0`.
- **DV-3 (localization): per-timestep attribution.** Fraction of T's advantage concentrated on timesteps whose cue was within the buffer vs outside. Genuine carrier use predicts concentration on in-buffer cues.
- **Compute/memory budget:** every DV reported jointly with `m`, parameter count, and step count, so ALT-C (capacity) is controlled by construction (N1 and T share all capacity except `m`).

## 4. Uncertainty quantification

- **Seeds:** `S = 22` independent seeds (matching the EXP-1 seed-count discipline; `(1−0.10)^22 = 0.0985 < 0.10` miss probability for a 10%-scale effect).
- **Interval method:** 95% CIs on `Δ`, `C`, and the T-vs-N1 difference via **10,000-iteration bootstrap** over seeds (per `STATISTICAL_ANALYSIS_SPEC.md` §1).
- **Significance:** paired t-test T vs N1 across seeds, `α = 0.01` (matching E0's stricter gate, since this is a deterministic algorithmic contrast). Cohen's `d` reported alongside.
- **Ceiling estimation uncertainty:** the memoryless ceiling is computed both analytically (from the known generator entropy) and empirically (N1 across seeds); the two must agree within the N1 bootstrap CI, else the instrument is miscalibrated (a pipeline failure, reported as such).

## 5. Rejection of the deliberately-inadequate explanation

The brief requires rejecting at least one inadequate explanation. EXP-Z0 targets **ALT-L (leakage)** as the primary inadequate explanation, plus the other three impostors:

| Impostor | Would (wrongly) explain a positive `Δ` as | Rejected by | Rejection rule |
|---|---|---|---|
| **ALT-L leakage** | the bit is still in the current input | N2 ablation (DV-2) | Reject ALT-L iff `C > 0` at `p<0.01`; if `C ≈ 0`, ALT-L is **not** rejected and the pass is void. |
| **ALT-0 memoryless-sufficient** | no memory needed | N1 ceiling (DV-1) | ALT-0 is the null; `Δ>0` rejects it. |
| **ALT-S spurious correlate** | a surface feature, not the cause | N2 preserves marginals; DV-3 localization | Reject iff advantage localizes to in-buffer cues, not surface features. |
| **ALT-C capacity** | more parameters | N1/T share capacity except `m` | Rejected by construction; verified by capacity report. |

**This is the crux calibration:** a pipeline that reports `Δ>0` but *cannot* also show `C>0` has not rejected leakage and therefore has not validated itself. EXP-Z0 is designed so that leakage produces a *detectable* signature (`Δ>0, C≈0`), turning a silent confound into an explicit fail.

## 6. Two-hypothesis discrimination

EXP-Z0 distinguishes **the memory-carrying reading of T-01** from **ALT-0 (memoryless sufficiency)** — two hypotheses that make opposite predictions on `Δ`:

| Hypothesis | Predicts DV-1 `Δ` | Predicts DV-2 `C` |
|---|---|---|
| Memory-carrying T-01 | `Δ > margin > 0` | `C > 0` (ablation hurts) |
| ALT-0 memoryless-sufficient | `Δ ≈ 0` | `C ≈ 0` |

The joint `(Δ, C)` outcome separates them unambiguously: only `(Δ>0, C>0)` supports T-01; `(Δ≈0, ·)` supports ALT-0; `(Δ>0, C≈0)` supports *neither* and indicts the instrument (leakage). This four-way readout is the discriminative payload.

## 7. Preregistered decision rule

EXP-Z0 **validates the pipeline** iff ALL hold across all 22 seeds:

1. **Positive control passes:** P1 (oracle) `Δ` ≥ 90% of the analytic oracle ceiling gap. *(If the oracle can't win, scoring is broken.)*
2. **Analytic/empirical ceiling agreement:** N1 empirical ceiling within the analytic ceiling's bootstrap CI.
3. **Effect present:** T vs N1 paired t-test `p < 0.01`, `Δ > margin` with margin = `0.05` nats (pre-set), 95% CI excludes 0.
4. **Leakage rejected:** `C > 0` at `p < 0.01` (removing the carrier significantly hurts T).
5. **Localized:** ≥ 70% of T's advantage on in-buffer-cue timesteps (DV-3).
6. **Structure required:** P2 (shuffled) `Δ` within N1 ceiling CI (effect vanishes without temporal structure).
7. **No post-hoc changes:** environment params, `k`, `m`, margin, seed count, and rule unchanged after any output is seen.

**Failure taxonomy (each is useful calibration information, not just "fail"):**

| Pattern | Diagnosis |
|---|---|
| P1 fails (rule 1) | Scoring pipeline cannot credit a known-correct system → **fix pipeline before any real experiment.** |
| Rule 2 fails | Ceiling miscalibrated → environment/entropy computation is wrong. |
| `Δ>0` but rule 4 fails | **Leakage** — the headline effect is an artifact; instrument would have produced a false positive on E0. |
| Rule 5 fails | Effect real but non-localized → possible spurious correlate; tighten environment. |
| Rule 6 fails | Effect present without temporal structure → environment does not actually require memory. |
| All pass | **Pipeline validated.** Cleared to run E0/EXP-1/EXP-2. |

A "pass" licenses only the claim: *the pipeline can detect a known temporal-aliasing effect and reject its four named impostors with quantified uncertainty.* It licenses **no** claim about intelligence, generality, or any protected hypothesis.

## 8. Free Parameter Register

No unexplained constants. Every knob is listed and classified (`derived` = forced by task/canon; `preregistered` = operational default fixed before runs).

| Parameter | Value | Class | Justification |
|---|---:|---|---|
| Hidden regimes | 2 (`R0,R1`) with identical sensor marginals | Derived | Minimal aliasing needs exactly two colliding-marginal causes. |
| Cue lag `k` | 8 | Preregistered | Inside every tested memory budget; removes "infeasible to carry" excuse. |
| Treatment memory `m` | 16 (`≥ k`) | Preregistered | Comfortably spans the carrier; not tuned to outcome. |
| Negative memoryless `m` | 0 | Derived | Defines the analytic memoryless ceiling. |
| Aliased-set size `\|A\|` per seed | ≥ 200 decisions | Derived | Matches the `N≥200` resolution floor used across P1. |
| Seeds `S` | 22 | Preregistered | `(1−0.10)^22 < 0.10` miss probability (EXP-1 rule). |
| Effect margin | 0.05 nats | Preregistered | Mirrors the emergence-margin scale `M=0.05` in `RESEARCH_PROTOCOL.md`; pre-set, not fitted. |
| Significance `α` | 0.01 | Derived | Deterministic algorithmic contrast → E0-strength gate. |
| Bootstrap iterations | 10,000 | Derived | `STATISTICAL_ANALYSIS_SPEC.md` §1. |
| Localization threshold | 0.70 | Preregistered | Advantage must be majority-attributable to in-buffer cues; conservative default. |
| Oracle pass fraction | 0.90 | Preregistered | Positive control must recover ≥90% of the analytic oracle gap. |
| Loss metric | mean held-out NLL (nats) | Derived | `METRIC_SPECIFICATION.md` §4. |
| Seed registry | separate env seed and agent seed | Derived | `EXPERIMENT_INTERFACE_SPEC.md` §5. |

## 9. Reproducibility requirements

- Frozen generator parameters, all 22 seeds, `k`, `m`, margin committed to version control before execution.
- Every metric line traceable to a git commit hash and config hash (`EXPERIMENT_INTERFACE_SPEC.md` §4).
- State snapshot serialized before evaluation; N2 ablation applied by a logged, deterministic permutation seeded from the registry.
- Analytic ceiling derivation committed as a checkable script, not a hardcoded number.
- No `core/` commits during the run (`EXPERIMENT_INTERFACE_SPEC.md` §6); no hyperparameter sweeps.

## 10. What EXP-Z0 does not do (scope guard)

- It does **not** test H\*, H1, H2, T-01, or T-02 as scientific claims. It tests whether the *instrument* that will test them behaves correctly on a case with a known answer.
- It does **not** locate where memory is stored (behavior underdetermines mechanism; `HYPOTHESIS_DISCRIMINATION_MATRIX.md` §4.2).
- It does **not** license generalization beyond the two-regime aliasing environment.
- A pass is necessary, not sufficient, for trusting downstream experiments; it clears the pipeline, nothing more.
