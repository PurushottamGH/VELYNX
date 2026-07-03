# EXP-0 — Paraphrase Invariance of Soul Concept Detection

## Experiment ID

**EXP-0** (from `docs/VELYNX_v2_PI_Review.md` Phase 4, line 109)

---

## Research Question

Does the Soul Graph's concept-detection cascade (`backend/pipeline/soul_router.py`, Tiers 1–2; `backend/app/pipeline.py`, Tier 3) depend on the literal presence of a seeded concept keyword, such that detection collapses when the keyword is removed but the query's meaning is preserved?

---

## Hypothesis

**H₁**: For at least one detector tier, the concept-detection hit rate on paraphrased queries (keyword removed, meaning preserved) is significantly lower than the hit rate on the matched original queries (keyword present).

**Rationale**: `soul_lookup_legacy` matches by exact substring or Porter stem against 32 fixed strings — a mechanism that is definitionally blind to any phrasing that doesn't share a lexical root with the concept name. `soul_lookup` (Tier 1) instead uses sentence-embedding similarity, which is not defined by keyword overlap and may or may not degrade under paraphrase — this is the part of H₁ that is a genuine, undecided empirical question rather than a restatement of known code behavior.

---

## Null Hypothesis

**H₀**: For a given tier, the paraphrase condition's hit rate is not distinguishable from the original condition's hit rate beyond what paired sampling noise at N=32 would produce (McNemar exact test, two-sided, p > α). Any apparent drop is attributable to chance discordance between two conditions with genuinely equal underlying detection probability.

---

## Independent Variables

| Variable | Levels | Description |
|----------|--------|-------------|
| Wording condition | original, paraphrase | Within-subject (same concept, paired). "Original" = `"What is {concept}?"`. "Paraphrase" = a scenario query built per `EXP0_PROTOCOL.md` §4–5 that is validated to contain no substring or Porter-stem match for any of the 32 seeded concepts. |
| Detector tier | Tier 1 (V2/semantic), Tier 2 (legacy/lexical), Tier 3 (full pipeline) | Which concrete code path is measured. Tiers 1 and 2 are primary/pre-registered; Tier 3 is secondary/exploratory (see Controls). |

---

## Dependent Variables

| Variable | Description | Range |
|----------|-------------|-------|
| DV-1 (primary) | Tier 2 hit: `concept in soul_lookup_legacy(query)["concepts"]` | {0,1} per trial |
| DV-2 (primary) | Tier 1 hit: `concept in soul_lookup(query)["concepts"]` | {0,1} per trial |
| DV-3 (secondary) | Tier 3 hit: `concept in answer_question(query).resonance_scores` | {0,1} per trial |
| Hit-rate difference | `hit_rate(original) − hit_rate(paraphrase)`, per tier | [−1, 1] |
| Latency | `DetectorResult.latency_seconds`, per trial | [0, ∞) seconds (engineering telemetry only, not a hypothesis test) |

All three DVs are read from a structured field (`result["concepts"]` or `resp.resonance_scores`) populated by the code under test, never from free-text answer parsing or an LLM judge — this removes researcher degrees of freedom in scoring (`foundation/program_d_scientific_foundation_v0.1.md` Phase 6, failure mode F3).

---

## Controls

| Control | Purpose |
|---------|---------|
| Full population (N=32, all seeded concepts) | No sampling bias from concept selection — see `EXP0_STATISTICAL_ANALYSIS.md` §1 for why this is adequately powered without needing N≈100. |
| `derivation` stratification (mechanical / mechanical-adjusted / hand-authored) | Lets the collapse-or-not finding be re-checked on the 19 items requiring no experimenter authorship, isolating any concern that hand-authored paraphrases are systematically different in difficulty. |
| Tier 2 as a lexical-only reference arm | A pure substring/stem detector with a *known* mechanism — establishes what "total collapse" looks like in this system, calibrating the interpretation of Tier 1's result. |
| Interleaved trial order + per-trial state reset (Tier 1 / Tier 3) | Bounds cross-trial contamination from Hebbian plasticity writes (`apply_plasticity`) that share state with the detector under test (`resonate()`'s `living_edges` read) — see `EXP0_PROTOCOL.md` §6. |
| Frozen dataset content hash (`concepts.json`, `paraphrases.json`) | `dataset.py` refuses to run if either file has changed since the pre-registration was written — "freeze the code" is enforced, not just asserted. |
| Leakage validator re-run at every invocation | `run_exp0.py` calls `leakage_check.py` before scoring anything and aborts on failure — the benchmark cannot silently drift into a keyword-leaking state between authoring and running. |

---

## Dataset

- **Name**: `paraphrases.json` (32 items), cross-validated against `backend/soul/concepts.json`
- **Concepts source hash**: `sha256=55b54f281a894cdd808e9eae4fa1db374719c3b21842b09a31001d004065dc87` (commit `5dc8da9`)
- **N**: 32 concepts × 2 conditions = 64 queries per tier
- **Derivation breakdown**: 15 mechanical, 4 mechanical-adjusted, 13 hand-authored (see `EXP0_PROTOCOL.md` §4)
- **Detector tiers scored**: 1, 2 (primary); 3 (secondary, opt-in via `--tier 3`)

---

## Random Seed

- Trial-order shuffle seed: **1** (`run_exp0.py --seed`, default)
- Bootstrap CI seed: **0** (`analysis.py:paired_bootstrap_ci`, fixed, not CLI-configurable — the bootstrap is a property of the analysis, not the data collection, so it does not need to vary with the run seed)

---

## Success Criterion

**Collapse confirmed** (the PI review's prediction holds for a given tier): hit_rate(paraphrase) is significantly lower than hit_rate(original) —

- McNemar exact test p ≤ 0.01 (survives Holm-Bonferroni correction across the two primary tiers), **and**
- Observed hit-rate drop ≥ 0.40 (40 percentage points) — chosen because it is well above the ≈14-percentage-point noise floor a coin-flip-level McNemar test could produce at N=32 (see Statistical Tests / power analysis) and is consistent with the magnitude the PI review predicts (100% → ≈40% or lower, by analogy to the 4.0/10 honest-test score).

---

## Failure Criterion

**No collapse** for a given tier: McNemar p > 0.01 after correction, **or** p ≤ 0.01 but the observed drop is < 0.40 (statistically detectable but not the scale of collapse the PI review predicts — reported as a smaller, real effect, not claimed as confirmation).

---

## Statistical Tests

| Test | Purpose |
|------|---------|
| McNemar's exact test (binomial on discordant pairs) | Primary significance test for paired binary hit/miss data at N=32; exact (not chi-square-approximated) because expected discordant-pair counts can be small. |
| Paired bootstrap 95% CI (10,000 resamples of item-index, seed=0) | Effect-size interval on the hit-rate difference, in the same reporting style as `research/stats.py`'s `BootstrapMeanDifferenceTest` used for the R1 ablation, for cross-experiment comparability. |
| Holm-Bonferroni step-down correction | Applied across the two **primary** pre-registered tests (Tier 1, Tier 2). Tier 3 is exploratory and is reported uncorrected and clearly labeled as such. |
| Minimum-detectable-effect (power) calculation at N=32, α=0.01 | Reported once in `EXP0_STATISTICAL_ANALYSIS.md` §1, not re-computed per run — a property of the fixed sample size. |

---

## Decision Matrix

| Outcome | Tier 1 (V2/semantic) | Tier 2 (legacy/lexical) | Interpretation | Next task |
|---|---|---|---|---|
| A | Collapses | Collapses | PI review's prediction holds for the entire current production cascade. Programs B/C's "understanding exceeds lookup table" claim is falsified at the concept-detection layer. | Report negative result; proceed to EXP-1 (calibration) per the existing roadmap. |
| B | Does **not** collapse | Collapses | The legacy fallback is a confirmed lookup table, but the production-first-tried V2 embedding path generalizes past-keyword. A genuinely informative result the PI review did not anticipate (it predates the embedding upgrade). | Investigate whether Tier 2 is ever actually reached in practice (i.e., does Tier 1 fire often enough that Tier 2's lookup-table behavior is mostly moot?) — a follow-up measurement, not a new subsystem. |
| C | Collapses | Does **not** collapse | Implausible given Tier 2's known mechanism, but reported if observed — likely indicates a dataset or harness defect; treat as a correctness bug in EXP-0 itself before drawing any scientific conclusion. |
| D | Neither collapses | Neither collapses | PI review's prediction is falsified for the current system. Report as a genuine negative result against the *audit's* prediction, not as evidence "understanding" is validated — a passing paraphrase test is necessary, not sufficient, for that stronger claim. |

---

## Threats to Validity

1. **State contamination (Tier 1 / Tier 3).** `resonate()` reads `living_edges`, which `apply_plasticity()` writes after high-confidence soul hits. Per-trial `wipe_db.py` resets mitigate but may not perfectly eliminate residual effects (e.g., in-RAM singletons outside the wipe's reach — see `live_fire_harness.py`'s own documented caveats on this exact issue).
2. **Semantic-preservation is a human judgment call, not machine-checked** (`EXP0_PROTOCOL.md` §5, rule 3). A different author might judge 1–2 of the 32 paraphrases differently. Mitigated by full transparency (`derivation` + `authoring_note` fields let a reviewer re-judge every item) but not eliminated.
3. **Single dataset, single query template per concept.** Each concept has exactly one original phrasing and one paraphrase — a single paraphrase failing to trigger detection is not distinguishable from "this particular paraphrase happened to be worded unluckily" versus "the concept is not detectable under any paraphrase." A future EXP-0b with k>1 paraphrase variants per concept would address this (noted, not built, per Program D's rule against unrequired complexity).
4. **`soul_lookup_legacy`'s missing `"scores"` key** is worked around by reading `result["concepts"]` directly rather than `resonance_scores` (see `EXP0_PROTOCOL.md` §3) — if a future code change alters what `soul_lookup`/`soul_lookup_legacy` return, `detectors.py` must be re-verified against the new return shape before trusting a re-run.
5. **Undeclared dependency.** `nltk` is imported by `backend/pipeline/soul_router.py` but is not listed in `requirements.txt`. If the run environment does not already have it installed (as this design environment happened to), Tier 2 will fail at import. Documented as a setup prerequisite in `EXP0_RUNBOOK.md`, not fixed here (fixing production dependency manifests is out of scope for an experiment framework).
6. **Working-tree cleanliness.** "Freeze the code" presumes a clean `git status` at run time. This repository had uncommitted changes at design time; `EXP0_RUNBOOK.md` makes verifying (or recording) this state step 1, not an afterthought.

---

## Freeze Date

This document is frozen before any code is executed against the VELYNX cognitive pipeline (`backend.pipeline.soul_router`, `backend.app.pipeline`). `dataset.py` and `leakage_check.py` have been executed against the two static JSON files only (`backend/soul/concepts.json`, `paraphrases.json`) as a materials-validation step, producing zero VELYNX cognition results.

All subsequent changes are tracked by Git and referenced to this experiment ID.
