# EXP-0 — Protocol

**Status:** Frozen design. No code has been executed against the VELYNX cognitive pipeline. No results exist yet.
**Author role:** Lead Research Engineer, Program D.
**Mission:** Falsify the strongest remaining claim of Program C — that the system's "understanding" exceeds a lookup table — by measuring whether concept detection collapses under semantic-preserving paraphrases that remove designer-injected keywords.
**Non-goal:** This document does not propose a fix, a redesign, or a new subsystem. It defines a measurement.

---

## 1. Origin and scope

This experiment is EXP-0 from `docs/VELYNX_v2_PI_Review.md` Phase 4 (line 109):

> "Freeze the code. Take the 100/100 benchmark. Paraphrase every query so no seeded concept keyword appears as a substring ('forgave' not 'forgiveness'; 'everything I built is gone' not 'loss/grief'). Re-score. Prediction: collapse to ≈ the 4.0/10 of the honest test."

EXP-0 is a **precondition**, not the Program D redesign's central experiment (`E0`, in `foundation/program_d_scientific_foundation_v0.1.md` Phase 6, which concerns a *new* minimal predictive organism and is explicitly out of scope here). EXP-0 tests the **existing, currently-deployed** system as-is.

---

## 2. Finding F0 — the "100/100 benchmark" does not exist as a single artifact

Before a benchmark can be frozen and paraphrased, it must be identified. Investigation of the repository turned up **two distinct artifacts**, both invoked loosely as "100/100" in the source documents, that are not the same benchmark:

| Artifact | File | N | Query style | What "100/100" refers to |
|---|---|---|---|---|
| Live-Fire stabilization harness | `backend/tests/live_fire_harness.py` | 100 (5 base + 95 randomized) | Mundane personal facts (favorite color/city/animal…) taught and recalled within the **same run**, using freshly-randomized nonsense entity names every run specifically so no pre-seeded vocabulary is involved | Git commits `b7f1c9c`, `6126a7e`: "100/100 Live-Fire Pass" |
| Soul-concept capability benchmarks | `VELYNX_Benchmark_Prompt.md` → `benchmark_v2_results.json` (10 queries); `soul_test_report.md` (6 queries, scored 4.0/10) | 10 and 6 | Scenario/definitional queries built directly on the 32 hand-authored Soul Graph concepts (`grief`, `betrayal`, `forgiveness`, …) | `docs/VELYNX_v2_PI_Review.md` Phase 1, assumption E1: "curated queries chosen to hit seeded concepts" |

The PI review's own worked examples ("forgave" not "forgiveness"; loss/grief) are drawn **verbatim** from `soul_test_report.md`'s root-cause findings (Q5, Q6) — i.e., from the second artifact, which has 6 queries, not 100. The live-fire harness's 100 queries never mention a soul concept at all (its whole design goal is to avoid pre-seeded vocabulary via fresh random entities). **No single existing file has ~100 queries built on the 32 seeded concepts.**

**Resolution (a deviation from the PI review's literal prose, preserving its intent):** EXP-0 targets the mechanism the PI review's examples unambiguously identify — the Soul Graph concept-detection cascade (§3) — and defines its own frozen benchmark as the **full population** of the 32 seeded concepts in `backend/soul/concepts.json`, not a sample and not a forced-fit to "100." Testing the full population is stronger than sampling from it: there is no concept-selection bias to defend. See `EXP0_STATISTICAL_ANALYSIS.md` §1 for why N=32 is adequately powered without needing 100 trials.

This finding is itself a Program D artifact: it demonstrates that "100/100" has been used as a rhetorical stand-in for "the passing benchmark" across at least two source documents without anyone checking which file that phrase denotes. Record it as a minor addition to the existing risk list (`PROGRAM_D_RESEARCH_STATE_v0.1.md` §7, R-1..R-12) as **R-13 — benchmark-identity ambiguity**, closed by this document.

---

## 3. Target mechanism

The live pipeline (`backend/app/pipeline.py:527-529`) tries concept detection in this fixed order:

```
soul_answer = soul_lookup(text)              # Tier 1 (V2 / semantic)
if not soul_answer:
    soul_answer = soul_lookup_legacy(text)   # Tier 2 (legacy / lexical)
# soul_answer (or its absence) feeds resonance_context, which is injected
# into the downstream retrieval + LLM synthesis (Tier 3, full pipeline).
```

- **Tier 1 — `backend/pipeline/soul_router.py:soul_lookup()`.** Calls `backend/cognition/scenario_engine.py:parse_scenario()`, which calls `backend/soul/soul_graph.py:resonate()`: encodes the query with a sentence-transformer, computes cosine similarity against a prebuilt embedding index of the 32 concepts, and reads a `living_edges` SQLite table for structural weighting. Fires if `max(concept_scores) > 0.35`. **No LLM call** (`scenario_engine.py` docstring: "Pure local inference."). This is a genuinely more sophisticated mechanism than a keyword lookup, and whether it is paraphrase-robust is an **open empirical question**, not a foregone conclusion — the codebase has evolved substantially since `soul_test_report.md` (4.0/10) was written (that report predates the `nltk` stem-matching fallback added in commit `b7f1c9c`, and its "0.01s" latencies are inconsistent with a live embedding encode + DB read, suggesting it predates Tier 1 entirely).
- **Tier 2 — `backend/pipeline/soul_router.py:soul_lookup_legacy()`.** Exact substring match (`concept_name in query.lower()`) OR Porter-stem match on individual query words (`_stem_match`, `>=4`-char-prefix fallback) against the 32 concept names in `backend/soul/concepts.json`. Pure function: no DB, no model, no network. This is the literal mechanism the PI review's "forgave"/"forgiveness" example describes.
- **Tier 3 — `backend/app/pipeline.py:answer_question()`.** The full, end-to-end entry point used by `chat.py`, the FastAPI route, and `live_fire_harness.py`. Tries Tier 1 then Tier 2 internally; on a double miss it falls through to retrieval + LLM synthesis. Exposes `resonance_scores` (dict keyed by detected concept name) directly on `AnswerResponse`.

EXP-0 measures all three tiers, in the same order production tries them, so a result at Tier 1 or Tier 2 is directly attributable to a named, frozen function rather than to the opaque end-to-end system.

**Known implementation detail affecting Tier 1 measurement:** `soul_lookup_legacy`'s return dict has no `"scores"` key, so if legacy is the one that matched, `build_resonance_context()` (`backend/pipeline/resonance.py`) returns empty `resonance_scores` even though a concept *was* detected. EXP-0 does not rely on `resonance_scores` for Tier 1/Tier 2 — it calls `soul_lookup`/`soul_lookup_legacy` directly and reads `result["concepts"]`, which is populated by both code paths. `resonance_scores` is used only for Tier 3, where it is the field actually exposed on the response a real caller would see.

---

## 4. Dataset construction

Population: all 32 concept keys in `backend/soul/concepts.json` (frozen file, `sha256=55b54f2…`, commit `5dc8da9`). One paired item per concept — see `paraphrases.json`.

- **Original (control) query** — mechanically generated for every concept: `"What is {concept}?"` (`"What are {concept}?"` for the one grammatically-plural concept, `uncontrollable forces`). This guarantees verbatim presence of the concept's own keyword and matches the exact phrasing of `soul_test_report.md` Q1/Q2 ("What is grief?", "What is betrayal?").
- **Paraphrase query** — a one-sentence third/second-person scenario, wrapped in a fixed question template (`"{situation}. What is the person in this situation most likely feeling or wrestling with, and why?"`), constructed as follows:
  - **15/32 concepts ("mechanical")** — the scenario is `backend/soul/concepts.json[concept].real_situations[0].situation`, used verbatim. This field is designer-authored content that predates and is independent of this experiment, which removes any experimenter-degrees-of-freedom concern for these items.
  - **4/32 concepts ("mechanical-adjusted")** — same source, but the situation string itself contained a seeded keyword (its own, or a *different* concept's) and required a minimal edit. Every edit is logged verbatim in `paraphrases.json`'s `authoring_note` field (e.g., `love`: "You love someone…" → "You care deeply about someone…").
  - **13/32 concepts ("hand-authored")** — `real_situations` was empty for these concepts in `concepts.json`. A new one-sentence scenario was authored, matching the length, register, and concreteness of the other 19, and validated identically.

Every item's `derivation` tag is preserved in `paraphrases.json` so the analysis can, if desired, be re-run restricted to the 19 "mechanical(-adjusted)" items alone as a robustness check against any concern that hand-authored items are systematically easier or harder.

---

## 5. Paraphrase protocol

Every paraphrase in `paraphrases.json` is required to satisfy all six rules below. Compliance with rules 4–6 is machine-checked by `leakage_check.py`, which every run of `run_exp0.py` re-executes and refuses to proceed past on failure — the benchmark cannot be scored in a state that has not just been re-verified clean.

1. **Lexical substitution.** No word in the paraphrase may share a surface form with the target concept's name. (Subsumed by rule 4's stronger stem check.)
2. **Syntactic restructuring.** The paraphrase is not a clausal rewrite of the original definitional question — it is a different *speech act* (a scenario + open question, versus "What is X?"). This is a stronger transformation than a synonym swap: it also changes the query from `query_type="direct"` to `query_type="scenario"` at the `parse_scenario()` classification layer (see §3), so the paraphrase condition exercises a different internal code path, not merely different words on the same path.
3. **Semantic preservation.** Each paraphrase must remain identifiably about its target concept to a competent adult reader with no access to the concept label — this is a human-judgment gate applied once at authoring time (documented, not re-litigated per run). It is *not* mechanically checked, and is recorded as a limitation in `EXP0_STATISTICAL_ANALYSIS.md` §4 (Threats to Validity).
4. **Keyword removal.** No substring match: `concept_name.lower() not in paraphrase_query.lower()`, checked against **all 32** concept names, not just the target's own (a paraphrase that accidentally names a *different* seeded concept is still a confound).
5. **Adversarial phrasing (unseen vocabulary relative to the keyword).** No Porter-stem collision on any content word, replicating `soul_router.py`'s own `_stem_match` rule (equality or shared 4-character prefix) — this is the exact rule that makes "forgave"/"forgiveness" collide in production, so a valid paraphrase must be adversarial with respect to *that specific rule*, not just avoid the literal word.
6. **Unseen vocabulary.** Where the source `real_situations` text already used ordinary descriptive language, no additional synonym-list or thesaurus substitution was applied — over-engineering the paraphrase (e.g., swapping every word for a rare synonym) would trade one confound (keyword leakage) for another (unnatural phrasing that changes the item's difficulty independent of the paraphrase manipulation). The rule is: change only what's needed to break the seeded-keyword path; leave the rest of the sentence as plain and natural as the source material.

`leakage_check.py find_leaks()` implements rules 4 and 5 exactly as re-derived (not imported) copies of `soul_router.py`'s matching code, so the validator cannot silently drift out of sync with — or be fooled by future changes to — the production detector.

---

## 6. Randomization procedure

- **Trial order:** For Tier 1 and Tier 3 (the two tiers with mutable, cross-trial state — see §7), the 64 trials (32 concepts × 2 conditions) are **interleaved**, not blocked (i.e., not "all 32 originals, then all 32 paraphrases"). Order is `random.Random(seed).shuffle()` over the 64 (concept, condition) pairs — deterministic given `--seed` (default `1`, matching `research/`'s `DEFAULT_SEEDS` convention).
- **Tier 2** has no state and is run in a fixed, deterministic order (dataset order) since there is nothing for order to confound.
- **Why interleaving matters here specifically:** `backend/soul/soul_graph.py:apply_plasticity()` is invoked by the pipeline after any CERTAIN/PROBABLE soul-concept hit (`backend/app/pipeline.py:948-951`), applying Hebbian weight updates to `living_edges` — the same table Tier 1's `resonate()` reads for its "concept gravity" structural term. Running all originals first (high hit rate expected) before all paraphrases (low hit rate expected) would let the first block systematically strengthen edges the second block then benefits or suffers from, in a way correlated with condition. Interleaving does not eliminate this state-coupling (see Threats to Validity), but it prevents it from being perfectly confounded with the original/paraphrase manipulation.
- **State reset:** before every Tier 1 and Tier 3 trial, `scripts/wipe_db.py:run_wipe(dry=False, strict=True)` is invoked (the exact function `backend/tests/live_fire_harness.py` already uses and validates) to clear the semantic graph and episodic memory. This is the single largest engineering cost of EXP-0 (64 wipes × up-to-2 tiers) — see `EXP0_RUNBOOK.md` for expected wall-clock impact.
- **Tier 3 session isolation:** every trial uses a unique `session_id` (`exp0-{concept}-{condition}-{trial_number}`) so `answer_question`'s working-memory/pronoun-resolution buffer cannot inject a prior trial's concepts into the current one.

---

## 7. Non-goals and explicit exclusions

- EXP-0 does **not** modify `backend/soul/concepts.json`, `backend/pipeline/soul_router.py`, `backend/soul/soul_graph.py`, or any other production file.
- EXP-0 does **not** re-run or depend on the outcome of `backend/tests/live_fire_harness.py` — that harness's 100/100 stabilization metric is a different claim (engineering robustness on freshly-taught facts) and is not addressed here (see Finding F0).
- EXP-0 does **not** attempt to fix morphological blindness, retune the `0.35` resonance threshold, or otherwise improve detection. A finding of collapse is a result to report, not a bug to patch under this experiment.
- EXP-0 does **not** execute against the live system as part of producing this design. Every number in `EXP0_STATISTICAL_ANALYSIS.md`'s worked example is synthetic and labeled as such.
- Tier 3 (full pipeline) is explicitly **secondary/exploratory**: it depends on LLM API access, network retrieval, and the full DB stack, none of which are prerequisites for the pre-registered primary comparison (Tiers 1 and 2). Running Tier 3 is optional and does not gate a decision on the primary hypothesis.

---

## 8. Cross-references

- Pre-registration (hypotheses, IVs/DVs, success/failure criteria): `EXP0_PREREGISTRATION.md`
- Directory layout and artifact schema: `EXP0_DIRECTORY_STRUCTURE.md`
- Module-level implementation notes: `EXP0_IMPLEMENTATION_PLAN.md`
- Statistical tests, power analysis, worked synthetic example: `EXP0_STATISTICAL_ANALYSIS.md`
- How to actually run it: `EXP0_RUNBOOK.md`
