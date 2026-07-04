# Program D Certification Ledger

This ledger records the scientific certification status of engineering milestones against the immutable `PROGRAM_D_CANONICAL.md` specification.

## 1. Experiment E0 Implementation (H* Falsification)
**Verdict: FAIL**

* **Deviation 1: Invalid C2 Control**
  * **File:** `experiments/E0/run.py`
  * **Requirement:** `PROGRAM_D_CANONICAL.md §7 (E0)`: `C2 (capacity-matched growth at random times)`
  * **Deviation:** Condition C2 implements growth with a hardcoded 30% probability at each evaluation interval (`if rng.rand() < 0.3: predictor.grow()`). This is decoupled random growth, but it is not *capacity-matched* to the Treatment (T) condition. Because T's capacity is determined dynamically by the MDL trigger, C2's final capacity will arbitrarily diverge from T's, invalidating it as a capacity-matched control.
  * **Minimal Correction:** Run condition T first. Count the exact number of growth events $E$ that occurred in T. In condition C2, uniformly sample exactly $E$ evaluation intervals (from the available intervals after `warmup_steps`) and trigger growth exactly at those intervals to guarantee identical final capacity.

* **Deviation 2: Insufficient Seeds Configured**
  * **File:** `experiments/E0/run.py`
  * **Requirement:** `PROGRAM_D_CANONICAL.md §6 (H*)`: `T fails to beat BOTH C1 and C2 on DV-a at p<0.01 across ≥5 seeds`
  * **Deviation:** The `DEFAULT_CONFIG` dictates `"num_seeds": 3`. Although the decider module correctly checks for a minimum of 5 seeds, the runner defaults to 3, meaning default runs will fail to generate conclusive results.
  * **Minimal Correction:** Change `"num_seeds": 3` to `"num_seeds": 5` in the `DEFAULT_CONFIG` dictionary.

## 2. Specification Re-alignment (Gemini Layer)
**Verdict: FAIL**

* **Deviation 3: H2 Retains Rejected Form**
  * **File:** `PROGRAM_D_SPECIFICATION.md`
  * **Requirement:** `PROGRAM_D_CANONICAL.md §9`: `Rewrite H2 to the §6 indexing/task-score form (delete "dimensionality reduction / compression ratio / search-steps / dense-embedding control").`
  * **Deviation:** The specification still defines H2 as "Affective Dimensionality Reduction" and specifies measuring "search steps-to-convergence" against a "dense embedding cosine-similarity search" control. It failed to apply the mandated update to match the canonical task-score form.
  * **Minimal Correction:** Rewrite H2 in `PROGRAM_D_SPECIFICATION.md` to exactly match `PROGRAM_D_CANONICAL.md §6`: Name: Affective Indexing. Hypothesis: Affective-framing -> problem-solving-schema mapping improves objective task outcomes. Observable: objective task success rate. Control: identical task, neutral (unframed) prompt.

## 3. Engineering Re-alignment (DeepSeek Layer)
**Verdict: FAIL**

* **Deviation 4: Live Tree Contains Archived Components**
  * **File:** `repository_v2.md`
  * **Requirement:** `PROGRAM_D_CANONICAL.md §9`: `Move to archive/ (not the live tree): program_c/self_model/, reasoning_engine, ontology_loader, and the free-energy/R1 experiment as closed evidence; drop EXP3/, EXP4/, R3F/ from the live experiment set.`
  * **Deviation:** `repository_v2.md` still lists `program_c/self_model/`, `reasoning_engine.py` (under `program_c/cognition/`), and `ontology_loader.py` (under `program_c/knowledge/`) in the live tree. It also lists `EXP3`, `EXP4`, `R1`, and `R3F` under the live `experiments/` directory instead of archiving them.
  * **Minimal Correction:** Update the tables in `repository_v2.md` to move these specific components and experiments out of the live `program_c/` and `experiments/` directories, adding them to the `archive/` tracking tables instead.

* **Deviation 5: EXP-0 Missing From Repository Index**
  * **File:** `repository_v2.md`
  * **Requirement:** `PROGRAM_D_CANONICAL.md §9`: `Add experiments/EXP-0/ (paraphrase precondition) — currently missing.`
  * **Deviation:** `EXP-0` (or `EXP0`) is completely omitted from the `experiments/` layout table.
  * **Minimal Correction:** Add the `experiments/EXP0/` directory to the Experiments table in `repository_v2.md`.

## 4. Publication Re-alignment (Nemotron Layer)
**Verdict: FAIL**

* **Deviation 6: Retained Novelty Inflation and Missing Prior Art**
  * **File:** `RELATED_WORK.md`
  * **Requirement:** `PROGRAM_D_CANONICAL.md §9`: `Delete every "Novel/First" tag on E, Inertia Law, three-pressure scoring, "catastrophic-forgetting cure"... Add the owning prior art to RELATED_WORK.md: Oudeyer & Kaplan 2007, Weng 2001, Pathak et al. 2017 (ICM), Burda et al. 2018 (RND)...`
  * **Deviation:** The file continues to assert "✅ Novel" claims for the Inertia Law, Free Energy (E), three-pressure scoring, and the catastrophic-forgetting cure. It completely omits the mandated citations (Oudeyer & Kaplan, Weng, Pathak, Burda) and retains the falsified developmental thesis rather than pivoting to the negative-result path.
  * **Minimal Correction:** Delete sections asserting novelty over rejected claims. Introduce the required prior art (Oudeyer & Kaplan 2007, Weng 2001, Pathak 2017, Burda 2018) for H*. Re-target the document to support the negative-result findings (R1 null, paraphrase-collapse, calibration failure).

## 5. Experiment EXP-0 Implementation (Paraphrase Precondition)
**Verdict: PASS**
* The implementation at `experiments/EXP0/run_exp0.py` accurately configures the dataset, interleaves conditions, and correctly provisions DB wipes between trials to enforce the absence of Hebbian leakage, adhering to the canonical precondition.
