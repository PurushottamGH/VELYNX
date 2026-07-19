# METRIC SPECIFICATION

**[FACT]** This document defines the exact mathematical and engineering specification for every load-bearing metric in Program D. 

## 1. Expected Calibration Error (ECE)

* **Name:** Expected Calibration Error (ECE)
* **Purpose:** Quantify the divergence between predicted confidence tiers and empirical correctness (H1 / EXP-1).
* **Mathematical definition:** $ECE = \sum_{m=1}^{M} \frac{|B_m|}{N} | \text{acc}(B_m) - \text{conf}(B_m) |$ where $M$ is the number of confidence bins (4 tiers).
* **Units:** Probability / Proportion (0.0 to 1.0).
* **Input variables:** `predicted_tier` $\in$ {CERTAIN, PROBABLE, DEBATED, UNKNOWN}, `actual_correctness` $\in \{0, 1\}$.
* **Output variables:** `ece_score` (float).
* **Valid range:** $[0.0, 1.0]$.
* **Edge cases:** Zero samples in a bin (ignore bin). 
* **Numerical stability requirements:** Floating point arithmetic (float64) for average calculations.
* **Reference implementation pseudocode:**
  ```python
  def calculate_ece(predictions, labels, tiers={"CERTAIN": 0.95, "PROBABLE": 0.75, "DEBATED": 0.5, "UNKNOWN": 0.25}):
      ece = 0.0
      N = len(predictions)
      for tier, expected_conf in tiers.items():
          bin_mask = (predictions == tier)
          if sum(bin_mask) == 0: continue
          acc = mean(labels[bin_mask])
          weight = sum(bin_mask) / N
          ece += weight * abs(acc - expected_conf)
      return ece
  ```
* **Expected plots:** Reliability diagram (calibration curve) plotting predicted confidence against actual accuracy per bin.
* **Validation procedure:** Check that assigning random tiers yields high ECE, and perfectly calibrated synthetic data yields $ECE \approx 0.0$.

## 2. Concept Detection Accuracy

* **Name:** Concept Detection Accuracy
* **Purpose:** Verify legacy system's vulnerability to paraphrasing (EXP-0).
* **Mathematical definition:** $\text{Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbb{1}[\text{detected\_concept}_i == \text{ground\_truth\_concept}_i]$.
* **Units:** Percentage / Proportion (0.0 to 1.0).
* **Input variables:** `predicted_concept_id` (string), `ground_truth_concept_id` (string).
* **Output variables:** `accuracy` (float).
* **Valid range:** $[0.0, 1.0]$.
* **Edge cases:** Empty predictions (counts as 0 correctness).
* **Numerical stability requirements:** None, strict integer equality matching.
* **Reference implementation pseudocode:**
  ```python
  def calculate_accuracy(predictions, truths):
      return sum(p == t for p, t in zip(predictions, truths)) / len(truths)
  ```
* **Expected plots:** Bar chart (Exact Keyword vs Paraphrase).
* **Validation procedure:** Compare against deterministic matching script.

## 3. Objective Task Success Score

* **Name:** Objective Task Success Score
* **Purpose:** Measure the efficacy of affective indexing on schema retrieval (H2 / EXP-2).
* **Mathematical definition:** Problem-specific grading function $S(y, \hat{y})$ yielding binary completion or normalized score.
* **Units:** Dimensionless score $[0.0, 1.0]$.
* **Input variables:** `predicted_output` (string/code), `ground_truth` (string/execution test).
* **Output variables:** `success_score` (float).
* **Valid range:** $[0.0, 1.0]$.
* **Edge cases:** Syntax errors in generated code yield 0.0.
* **Numerical stability requirements:** Standard float64 normalization.
* **Reference implementation pseudocode:**
  ```python
  def evaluate_task(output, test_suite):
      try:
          return 1.0 if test_suite.run(output).passed else 0.0
      except Exception:
          return 0.0
  ```
* **Expected plots:** Box plot comparing framed vs unframed scores.
* **Validation procedure:** Verified against known ground-truth task solutions.

## 4. Held-out Predictive Log-Likelihood (LL)

* **Name:** Held-out Predictive Log-Likelihood
* **Purpose:** Quantify the primary predictive power of the acquired latent structure (H* / E0).
* **Mathematical definition:** $LL = \frac{1}{N} \sum_{t=1}^N \log P_\theta(x_{t} | x_{<t})$.
* **Units:** Nats or Bits (depending on log base, enforce base 2 or $e$ globally, standardized to base $e$ nats).
* **Input variables:** `predicted_probability_distribution`, `actual_observation`.
* **Output variables:** `mean_log_likelihood` (float).
* **Valid range:** $(-\infty, 0.0]$.
* **Edge cases:** $P_\theta = 0$ resulting in $\log(0) = -\infty$. Must clip probabilities to $\epsilon$ (e.g., $1e-12$).
* **Numerical stability requirements:** Log-sum-exp trick must be used for all internal probability aggregations.
* **Reference implementation pseudocode:**
  ```python
  def calculate_ll(probs, obs_indices, epsilon=1e-12):
      probs = np.clip(probs, epsilon, 1.0)
      probs = probs / np.sum(probs, axis=-1, keepdims=True)
      return np.mean(np.log(probs[np.arange(len(obs_indices)), obs_indices]))
  ```
* **Expected plots:** Learning curves over sequence timesteps.
* **Validation procedure:** Fixed capacity model on stationary data must converge to entropy rate.

## 5. Emergence Statistic (M)

* **Name:** Emergence Statistic (M)
* **Purpose:** Prove structural acquisition is not designer-injected statistics (H* / E0, operationalizes I2).
* **Mathematical definition:** $M = \text{NMI}(\text{learned\_partition}, \text{true\_latent}) - \text{NMI}(\text{learned\_partition}, \text{shuffled\_input})$.
* **Units:** Dimensionless (Difference of Normalized Mutual Information scores).
* **Input variables:** `learned_state_sequence`, `true_latent_sequence`, `shuffled_input_learned_state_sequence`.
* **Output variables:** `m_statistic` (float).
* **Valid range:** $[-1.0, 1.0]$.
* **Edge cases:** State sequences with single uniform state yield undefined NMI (div by 0 entropy). Must handle zero-entropy safely (yields 0 NMI).
* **Numerical stability requirements:** NMI standard scikit-learn implementation.
* **Reference implementation pseudocode:**
  ```python
  from sklearn.metrics import normalized_mutual_info_score as nmi
  def calculate_m_statistic(learned, true, shuffled_learned, true_shuffled):
      return nmi(learned, true) - nmi(shuffled_learned, true_shuffled)
  ```
* **Expected plots:** NMI table comparing true vs shuffled.
* **Validation procedure:** Verify $\mathbb{E}[M | H_0] = 0$ by feeding completely random noise to the growth operator.
