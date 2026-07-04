# SCIENTIFIC EXECUTION SPECIFICATION

**[FACT]** This document is the definitive implementation-ready scientific execution specification for Program D, derived directly from `PROGRAM_D_CANONICAL.md`.

---

## EXP-0: Benchmark Paraphrase (Precondition Test)

**Purpose:** Stop claiming the legacy headline result. Verify if the deployed system's concept detection collapses to noise under semantic-preserving paraphrases.
**Hypothesis:** N/A (Precondition audit of the old deployed system; not a formal research hypothesis).
**Null hypothesis:** Concept detection accuracy on paraphrases is statistically indistinguishable from exact-keyword queries.
**Variables:** Direct query (exact keyword) vs. Paraphrase query (semantic equivalent, keyword removed).
**Inputs:** 64 interleaved queries (32 original "What is X?" with exact keywords, 32 keyword-free paraphrases).
**Outputs:** Concept detection success (binary 1/0) for Tier 1 (embedding) and Tier 2 (lexical).
**Controls:** Exact keyword queries (the original 32 benchmark queries).
**Baselines:** Random baseline for 32 concepts ($\approx 1/32$ accuracy).
**Metrics:** Concept detection accuracy (%).
**Statistics:** McNemar's test for paired nominal data (original vs. paraphrase success).
**Sample size:** $N=64$ queries (32 pairs).
**Power assumptions:** 32 pairs is sufficient to detect a catastrophic collapse from $\approx 100\%$ to near noise ($\approx 3\%$).
**Failure conditions:** Keyword leakage into the paraphrase; Porter-stem collision between paraphrase and target; Hebbian weight leakage across trials.
**Kill criteria:** Concept detection collapses to noise on the paraphrase set.
**Success criteria:** Execution completes under strict state isolation, empirically verifying the collapse.
**Expected artifacts:** `exp0_results.json`, `exp0_audit_report.md`.
**Expected plots:** Bar chart comparing exact-keyword vs. paraphrase detection accuracy.
**Expected tables:** 32x2 contingency table of detection success per concept.
**Required reproducibility information:** Explicit query text corpus (all 64 queries) committed to version control; fixed seeds. *Mandatory requirement: The semantic graph and episodic memory must be hard-reset before every trial.*

---

## EXP-1: Calibration Curve (Program A Product Gate)

**Purpose:** Evaluate if Program A's confidence tiers represent empirical "honest uncertainty."
**Hypothesis:** H1 — Symbolic confidence tiers (CERTAIN, PROBABLE, DEBATED, UNKNOWN) strictly bound empirical accuracy.
**Null hypothesis:** Evaluation accuracy is statistically independent of the predicted confidence tier.
**Variables:** Predicted confidence tier (independent variable); empirical correctness (dependent variable).
**Inputs:** $\geq 200$ mixed queries covering known facts, ambiguous questions, and hallucinated concepts.
**Outputs:** Predicted confidence tier, binary correctness of the retrieval/answer.
**Controls:** TF-IDF/BM25 retrieval paired with randomly assigned confidence outputs.
**Baselines:** Constant-confidence baseline (e.g., a system that always predicts the modal tier).
**Metrics:** Expected Calibration Error (ECE); Accuracy per tier.
**Statistics:** ECE calculation; Chi-square test for independence between predicted tier and actual correctness.
**Sample size:** $N \geq 200$ queries.
**Power assumptions:** $N=200$ is sufficient to estimate ECE with narrow confidence intervals.
**Failure conditions:** The system emits `CERTAIN` on hallucinated content; bin-boundary hacking is employed to artificially lower ECE without signal improvement.
**Kill criteria:** $ECE \geq 0.10$ OR accuracy is statistically independent of the tier over the query set.
**Success criteria:** $ECE < 0.10$ measured without threshold hacking.
**Expected artifacts:** `exp1_ece_metrics.csv`, `exp1_calibration_report.md`.
**Expected plots:** Reliability diagram (calibration curve) showing predicted confidence vs. empirical accuracy.
**Expected tables:** Table mapping each Tier to its Mean Predicted Confidence, Empirical Accuracy, and Query Count.
**Required reproducibility information:** Frozen confidence mapping code; exact evaluation query set and ground-truth labels committed to the repository.

---

## EXP-2: Affective Bridge (Program B Claim Audit)

**Purpose:** Test if emotional framing acts as an effective retrieval index for problem-solving schemas.
**Hypothesis:** H2 — A learned affective-framing $\rightarrow$ problem-solving-schema mapping improves objective task outcomes over an unframed baseline.
**Null hypothesis:** Objective task scores using the affective frame are $\leq$ the scores of the unframed baseline.
**Variables:** Affective frame present in prompt vs. neutral prompt (absent).
**Inputs:** Isolated, third-party objective task set (e.g., coding debugging fixes, discrete planning paths). Prompt templates.
**Outputs:** Objective task success score (binary completion or continuous normalized score).
**Controls:** Neutral (unframed) prompt describing the identical task.
**Baselines:** Unframed prompt performance.
**Metrics:** Objective task success rate.
**Statistics:** Independent samples t-test (for continuous scores) or Mann-Whitney U test, $p < 0.05$.
**Sample size:** Pre-registered target (e.g., $N=100$ tasks per condition).
**Power assumptions:** Sized to detect a moderate effect ($d = 0.5$) with 80% power.
**Failure conditions:** Tasks are sourced from or implicitly dependent on the 32 authored soul concepts (circularity).
**Kill criteria:** No statistically significant task-outcome difference, OR the schemas require manual re-authoring per task (proving injection, not emergence).
**Success criteria:** Framed condition outperforms the unframed condition at pre-registered significance.
**Expected artifacts:** `exp2_task_scores.csv`, `exp2_schema_report.md`.
**Expected plots:** Box plots of task scores comparing the framed vs. unframed conditions.
**Expected tables:** Summary statistics (Mean, SD, N) and test statistics (t-value, p-value, effect size).
**Required reproducibility information:** Frozen third-party task set; exact prompt text templates; LLM temperature rigidly fixed to 0.

---

## E0: Emergence-vs-Injection Discrimination (Program C Central Test)

**Purpose:** Operationalize assumption I2 to test if an error-gated capacity model acquires genuine emergent structure rather than injected statistics.
**Hypothesis:** H* — Error-gated structure acquisition yields structure that improves held-out prediction beyond controls and is statistically irreducible to the shuffled baseline.
**Null hypothesis:** Predictive log-likelihood is indistinguishable from C1 and C2, and the emergence statistic $M$ is within the noise margin of C3.
**Variables:** Error-gated capacity-growth operator (ON vs. OFF vs. Decoupled).
**Inputs:** Synthetic sequence generated from a known hidden Markov model with $K$ latent states and nonlinear observation mixing.
**Outputs:** Predicted probabilities $P_\theta(x_{t+1} | x_{\leq t})$, learned partition $\theta_k$.
**Controls:**
- **C1:** Fixed capacity (no growth).
- **C2:** Capacity-matched growth at random times (decoupled from error).
- **C3:** Shuffled-input control (destroys temporal structure but preserves marginals).
**Baselines:** Linear predictive baseline (to verify the environment is strictly non-linear and requires structural capacity).
**Metrics:** 
- **DV-a:** Held-out predictive log-likelihood.
- **DV-b:** Emergence statistic $M = \mathrm{NMI}(\text{learned}, \text{true}) - \mathrm{NMI}(\text{learned}, \text{shuffled})$.
**Statistics:** Paired t-tests for DV-a (T vs. C1, T vs. C2) requiring $p < 0.01$.
**Sample size:** $\geq 5$ random seeds.
**Power assumptions:** 5 seeds provide strict discrimination if the acquisition mechanism is deterministically robust.
**Failure conditions:** Environment is linearly separable; MDL threshold $\lambda$ is tuned by hand rather than derived.
**Kill criteria:** Treatment (T) fails to beat BOTH C1 and C2 on DV-a at $p < 0.01$ across $\geq 5$ seeds, OR DV-b is within the noise margin of C3, evaluated after two honest attempts.
**Success criteria:** T > C1 and T > C2 on DV-a ($p < 0.01$), and DV-b strictly exceeds pre-registered margin.
**Expected artifacts:** `e0_loglikelihoods.csv`, `e0_m_statistic_results.csv`, `e0_falsification_report.md`.
**Expected plots:** Learning curves plotting predictive log-likelihood over time for T, C1, and C2.
**Expected tables:** Final LL means and standard deviations; NMI computation breakdown table.
**Required reproducibility information:** Hardcoded MDL ledger formula $\lambda_{model} = k \cdot b + n \cdot \log_2 N$; precise synthetic environment generator parameters; array of fixed seeds explicitly registered.
