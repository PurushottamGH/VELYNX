# Program D — Experiment Protocols

**[FACT]** All experiments must be pre-registered and run against frozen code. No experiment may be used to tune hyperparameters dynamically.

---

## E0: Emergence-vs-Injection Discrimination
**[FACT]** Tests H* (Error-Gated Structure Acquisition).

* **Protocol Summary:** Expose a minimal predictive organism (no seeded concepts, no ontology) to a synthetic sequence from a known generator with K latent states and nonlinear observation mixing. Compare error-gated growth against fixed-capacity and random-growth controls.
* **Environment:** Nonlinear latent mixing (must be verified offline so a linear predictor cannot recover the latent).
* **Treatment (T):** Error-gated growth ON.
* **Control 1 (C1):** Fixed capacity (no growth).
* **Control 2 (C2):** Capacity-matched growth at random times (decoupled from error).
* **Control 3 (C3):** Shuffled-input (destroys temporal structure, preserves marginals).
* **Measurements:** 
  * DV-a: Held-out predictive log-likelihood.
  * DV-b: NMI(learned partition, true latent) - NMI(learned partition, C3-shuffled).
* **Criteria:** T must beat C1 and C2 on DV-a at p<0.01. DV-b must exceed pre-registered margin.

---

## EXP-0: Benchmark Paraphrase
**[FACT]** Tests whether Program B/C concept detection collapses under semantic-preserving paraphrases. (Precondition test of the current deployed system, not H*).

* **Protocol Summary:** Freeze code. Take the 32 seeded concepts. Generate an original direct query ("What is X?") and a paraphrase query (scenario without the keyword or its stem). Re-score concept detection across Tier 1 (embedding) and Tier 2 (lexical).
* **Data:** 64 interleaved trials (32 original, 32 paraphrase).
* **Constraints:** No keyword leakage. No Porter-stem collision. 
* **State Reset:** Wipe semantic graph and episodic memory before every trial to prevent Hebbian weight leakage across conditions.
* **Criteria:** If concept detection collapses to noise on paraphrases, the claim of semantic "understanding" over a keyword lookup table is falsified.

---

## EXP-1: Calibration Curve
**[FACT]** Tests H1 (Calibration).

* **Protocol Summary:** Present the retrieval engine (Program A) with ≥200 mixed queries (including known facts, ambiguous questions, and hallucinations). Plot the claimed uncertainty tier against empirical correctness.
* **Measurement:** Expected Calibration Error (ECE) / reliability diagram.
* **Criteria:** ECE must be < 0.1 for the system to claim "honest uncertainty." 

---

## EXP-2: Affective Bridge
**[FACT]** Tests H2 (Affective Indexing).

* **Protocol Summary:** Test the hypothesis that emotional framing retrieves superior problem-solving schemas. Assign objective tasks (e.g., debugging fixes, planning) using prompts that invoke affective frames vs. neutral baselines.
* **Treatment:** Prompt includes affective state mapping (e.g., shame -> failure -> debugging schema).
* **Control:** Prompt includes only the neutral task description.
* **Measurement:** Objective task success rate.
* **Criteria:** Treatment must show statistically significant improvement over control.

---

## EXP-3: Minimal Predictive Organism
**[FACT]** Tests H3 (Emergent Development).

* **Protocol Summary:** The precursor protocol to E0. Deploy the minimal organism into an environment requiring structure acquisition.
* **Measurement:** Transfer of emergent structure to a held-out prediction task.
* **Criteria:** The structure acquired must exceed what is trivially given by initialization and input statistics. (Effectively subsumed and made rigorous by E0).
