# SCIENTIFIC COMPLIANCE MATRIX

This matrix maps the implementation components to their governing scientific framework, enforcing the strict audit-and-falsification protocol.

| Component / Subsystem | Hypothesis | Primary Metric (Observable) | Governing Experiment | Kill Criterion | Publication Claim if Passed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Error-Gated Capacity Growth** (`core/mdl/`, `core/emergence/`) | **H\*** (Error-Gated Structure Acquisition) | Held-out log-likelihood ($L = -\log P_\theta$) & null-referenced Emergence Statistic ($M$) | **E0** | T fails to beat C1 & C2 on LL at $p<0.01$ (≥5 seeds) OR $M$ within noise of shuffled C3. | Rigorous negative result + null-referenced emergence discrimination methodology. |
| **Program A** (Live-truth Retrieval Engine) | **H1** (Retrieval Uncertainty Calibration) | Expected Calibration Error (ECE) | **EXP-1** | $ECE \geq 0.10$ or evaluation accuracy is statistically independent of the predicted tier. | Honest uncertainty (bounded calibration) in autonomous search. |
| **Program B** (Affective Indexing / "Soul Graph") | **H2** (Affective Dimensionality Reduction) | Objective task success rate | **EXP-2** | No significant difference in task outcomes compared to unframed prompt. | Affective framing indexes problem-solving schemas effectively. |
| **Old Deployed Concept System** (`backend/pipeline/soul_router.py`) | **N/A** (Precondition Test) | Concept detection accuracy (%) | **EXP-0** | Concept detection collapses to noise ($\approx 1/32$) on paraphrase queries. | Falsification of legacy "semantic understanding" claim. |

## Notes on Compliance:
- The legacy **H3** is **[REJECTED]** (subsumed by H\*).
- The legacy `E = λH + μS + νA` (free energy) is **[REJECTED]** and cannot map to any valid claim. Its existence in the implementation breaks compliance.
- Any subsystem not mapped above (e.g., self-models, dream states) must be archived as per the prime directive: "No subsystem without a pre-registered experiment that requires it."
