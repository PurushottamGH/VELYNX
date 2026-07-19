# REFERENCE DATA SPECIFICATION

**[FACT]** This document defines the exact datasets, splits, and formats required for execution.

## 1. EXP-0: Paraphrase Benchmark
- **Required dataset:** `exp0_queries.json`
- **Expected format:** JSON list of objects containing `query_id`, `exact_keyword_query`, `paraphrase_query`, `ground_truth_concept`.
- **Ground truth:** 32 specific concepts.
- **Seed policy:** Fixed query order.
- **Hash requirements:** SHA-256 hash of the dataset must match the registered benchmark hash prior to execution.

## 2. EXP-1: Calibration Query Set
- **Required dataset:** `exp1_queries.json`
- **Expected format:** JSON list of 200+ queries.
- **Split:** 40% known facts, 30% ambiguous edge-cases, 30% known hallucination triggers.
- **Ground truth:** Expert-annotated binary truth labels (1 = correct/verifiable, 0 = incorrect/hallucination/unverifiable).
- **Dataset versioning:** v1.0, strictly frozen.

## 3. EXP-2: Third-Party Objective Tasks
- **Required dataset:** `exp2_tasks.json`
- **Expected format:** 100+ tasks from standard evaluation suites (e.g., HumanEval, MBPP for coding, or standardized planning domains).
- **Ground truth:** Executable test suites or verified solution strings.
- **Validation split:** None required (zero-shot evaluation).
- **Hash requirements:** Sourced from immutable public repositories, SHA-256 verified.

## 4. E0: Synthetic HMM Environment
- **Synthetic generation requirements:** 
  - Must generate sequences from a discrete Hidden Markov Model.
  - Number of true latent states $K = 10$.
  - Transition matrix must be dense but non-uniform (ergodic but structured).
  - Observation emission must be non-linear (e.g., XOR rules over latent dimensions) to defeat linear capacity baselines.
- **Sequence Length:** 50,000 steps training, 10,000 steps hold-out test.
- **Seed policy:** The generator must use a completely separate seed sequence (e.g., 100, 101, 102...) distinct from the agent's PRNG.
- **Validation:** Ensure linear baseline achieves exactly random-chance prediction on the test split.
