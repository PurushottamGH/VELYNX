# Program D — Hypothesis Register

**[FACT]** Never invent new hypotheses. Only refine existing ones.

---

## H* (Central Hypothesis: Error-Gated Structure Acquisition)
**[HYPOTHESIS]** An agent whose only learning signal is sensorimotor prediction error, and which adds representational capacity only when prediction error persists, will acquire internal structure that (i) is absent at initialization, (ii) improves prediction on held-out data beyond a fixed-capacity control and a capacity-matched control whose growth is decoupled from error, and (iii) is not reducible to the statistics injected by the designer.

* **Purpose:** To determine if emergent structure is operationally distinguishable from injected/statistically-trivial structure.
* **Variables:** 
  * Independent Variable: Presence/identity of the error-gated capacity-growth operator (ON vs. OFF/decoupled).
* **Observables:** 
  * (a) Held-out predictive log-likelihood. 
  * (b) Emergence statistic: Normalized mutual information (NMI) between the learned latent partition and the true latent generator, minus the same quantity under a shuffled-input control.
* **Mathematics:** 
  * Proper scoring loss: `L = −log P_θ(x_{t+1} | x_{≤t})`
  * MDL-derived growth operator triggered iff `G = H_before − H_after − λ_model > 0`
  * Emergence statistic `M(θ_k)` such that `E[M | H₀] = 0`
* **Failure conditions:** 
  * (F1) Environment is too easy. 
  * (F2) Growth is uncoupled in practice. 
  * (F3) Emergence statistic has researcher degrees of freedom. 
  * (F4) Observability gap (metrics unmeasurable).
* **Kill criteria:** 
  * Fails to beat fixed-capacity (C1) and error-decoupled (C2) controls on held-out LL at p<0.01 across ≥5 seeds, OR learned-latent MI does not exceed the shuffled-input control by the pre-registered margin, after two honest attempts.
* **Experimental protocol:** E0 (Emergence-vs-injection discrimination on a nonlinear-latent stream).
* **Expected positive result:** T > C1 and T > C2 at p<0.01. DV-b exceeds pre-registered margin.
* **Expected negative result:** Held-out predictive LL is indistinguishable from fixed-capacity/error-decoupled controls, and learned-latent MI is within noise of shuffled-input control.

---

## H1 (Calibration)
**[HYPOTHESIS]** A retrieval agent can report uncertainty tiers whose empirical correctness matches the tier.

* **Purpose:** To evaluate if the system's confidence tiers represent honest uncertainty.
* **Variables:** 
  * Independent Variable: Presence of calibration.
* **Observables:** 
  * Expected Calibration Error (ECE).
* **Mathematics:** 
  * `ECE < 0.1`
* **Failure conditions:** 
  * The system emits `CERTAIN` on hallucinated content.
* **Kill criteria:** 
  * Calibration is no better than a constant-confidence baseline.
* **Experimental protocol:** EXP-1 (Calibration curve over ≥200 mixed queries).
* **Expected positive result:** Empirical correctness aligns with confidence tiers (ECE < 0.1).
* **Expected negative result:** Calibration is no better than a constant-confidence baseline, invalidating the "honest uncertainty" claim.

---

## H2 (Affective Indexing)
**[HYPOTHESIS]** A learned affective-framing to problem-solving-schema mapping improves objective task outcomes over an unframed baseline.

* **Purpose:** To test if emotional framing acts as an effective retrieval key into problem-solving schemas.
* **Variables:** 
  * Independent Variable: Affective frame present vs. absent.
* **Observables:** 
  * Objective task score (e.g., debugging fixes / planning success).
* **Mathematics:** 
  * Mean objective task score (Framed) > Mean objective task score (Unframed).
* **Failure conditions:** 
  * Affective frame yields no significant task-outcome difference.
* **Kill criteria:** 
  * Task outcome is not significantly different, or schemas must be re-authored per task.
* **Experimental protocol:** EXP-2.
* **Expected positive result:** Framed tasks outperform unframed baseline on objective scores.
* **Expected negative result:** No significant difference in task outcomes between framed and unframed baselines.

---

## H3 (Emergent Development) — [REJECTED] / SUBSUMED BY H*
**[REJECTED]** Retained only as an archived cross-reference (PROGRAM_D_CANONICAL.md §10 Issue-1). This is H* with the emergent-vs-injected clause (iii)/I2 removed; its content lives inside H* and its protocol is subsumed and made rigorous by E0. Do not treat as a live hypothesis or build EXP-3/EXP-4 for it.
