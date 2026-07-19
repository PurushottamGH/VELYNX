# SCIENTIFIC VALIDATION MATRIX

**[FACT]** This matrix provides the unbroken chain of logic from foundational hypothesis to ultimate publication claim.

| Phase | H* (Error-Gated Structure) | H1 (Calibration) | H2 (Affective Indexing) |
| :--- | :--- | :--- | :--- |
| **Hypothesis** | Error-gated structure acquisition yields non-injected latent structure that improves prediction. | Confidence tiers rigorously bound empirical retrieval accuracy. | Affective framing indexes superior problem-solving schemas. |
| **Observable** | Held-out prediction; Learned latent partition vs. Ground truth latent. | Correctness probability per predicted confidence tier. | Objective task success score (e.g., debugging fixes). |
| **Metric** | Log-Likelihood (LL); Emergence Statistic $M$ (NMI diff). | Expected Calibration Error (ECE). | Mean Success Rate. |
| **Statistical Test** | Paired t-test ($p < 0.01$). | Chi-square independence test; ECE calculation. | Independent samples t-test / Mann-Whitney U ($p < 0.05$). |
| **Decision Rule** | Is T > C1 AND T > C2 on LL? Is $M$ > margin? | Is ECE < 0.10? | Is Mean(Framed) > Mean(Unframed)? |
| **Kill Criterion** | LL indistinguishable from controls OR $M$ statistic $\approx 0$. | ECE $\geq$ 0.10 or accuracy is tier-independent. | Framed success $\leq$ Unframed baseline. |
| **Publication Claim** | **If pass:** Rigorous proof of emergent representation. <br>**If killed:** Methodology paper exposing designer-injection in prior emergent models. | **If pass:** Program A is an honest retrieval product. <br>**If killed:** Claim of "honest uncertainty" is falsified. | **If pass:** Affect acts as a measurable prior for search space constraint. <br>**If killed:** Affective concepts are inert designer artifacts. |

---

## Observability Completeness Audit

* **Rule:** No hypothesis may lack an observable.
  * **H*:** Observable is held-out LL and learned partition. (Verified)
  * **H1:** Observable is empirical accuracy vs. predicted tier. (Verified)
  * **H2:** Observable is objective task success. (Verified)
* **Rule:** No observable may lack a metric.
  * **H*:** Metrics are LL and $M$ statistic. (Verified)
  * **H1:** Metric is ECE. (Verified)
  * **H2:** Metric is Success Rate / Score. (Verified)
