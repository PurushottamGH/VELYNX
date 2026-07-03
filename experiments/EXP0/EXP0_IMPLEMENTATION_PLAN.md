# EXP-0 — Implementation Plan

Each module below is documented against Program D's standing module-design checklist (purpose, inputs, outputs, state, dependencies, failure modes, experiments using it, removal impact). All code described here already exists in `experiments/EXP0/` and has been syntax-checked (`python -m py_compile`) and, where it touches no VELYNX cognition code, unit-verified with synthetic inputs (`dataset.py`, `leakage_check.py`, `analysis.py`). Nothing has called `backend.pipeline.soul_router` or `backend.app.pipeline`.

---

## `dataset.py`

- **Purpose.** Load the frozen 32-item paired benchmark and guarantee it has not silently drifted from its source.
- **Inputs.** `backend/soul/concepts.json` (read-only), `paraphrases.json` (read-only).
- **Outputs.** `load_items() -> list[BenchmarkItem]`; `dataset_manifest() -> dict` (content hashes + item count) for the run manifest.
- **State.** None (no globals mutated; every call re-reads both files from disk — trivially cheap at this size, and it means a mid-session edit to either file is caught on the next call rather than requiring a process restart).
- **Dependencies.** Standard library only (`json`, `hashlib`, `pathlib`, `dataclasses`). No `backend.*` import.
- **Failure modes.** `DatasetIntegrityError` if `concepts.json`'s content hash no longer matches the one recorded in `paraphrases.json` (someone edited the seeded concepts after the benchmark was frozen), or if the two files' concept-name sets disagree (added/removed/renamed a concept). Both are loud, immediate `raise`s — there is no silent-degradation path.
- **Experiments using it.** EXP-0 only.
- **Removal impact.** Total — `run_exp0.py` cannot enumerate trials without it. No other module in the repo imports `dataset.py`.

---

## `paraphrases.json`

- **Purpose.** The frozen experimental material itself (not code) — 32 `{concept, original_query, paraphrase_query, derivation, source_field, authoring_note}` records plus a manifest header (`source_file_sha256`, templates, derivation legend).
- **Inputs.** None at runtime (it *is* an input). Authored once against `backend/soul/concepts.json` per `EXP0_PROTOCOL.md` §4–5.
- **Outputs.** Consumed by `dataset.py` and independently by `leakage_check.py`.
- **State.** Immutable by convention — `dataset.py` treats any drift from its recorded source hash as an integrity error rather than silently re-deriving. Editing this file requires bumping `schema_version` and re-running `leakage_check.py`.
- **Dependencies.** None.
- **Failure modes.** A hand-edit that reintroduces a leaked keyword — caught by `leakage_check.py`, not by this file itself (data files cannot validate themselves).
- **Experiments using it.** EXP-0 only.
- **Removal impact.** Total — this is the benchmark. There is no other copy.

---

## `leakage_check.py`

- **Purpose.** Prove, mechanically, that every paraphrase in `paraphrases.json` is free of the exact keyword-matching signal the experiment is designed to remove — and that every original query correctly retains it.
- **Inputs.** `backend/soul/concepts.json`, `paraphrases.json`.
- **Outputs.** Exit code (0 = clean, 1 = leak found) and a human-readable report to stdout. `main()` is also called programmatically by `run_exp0.py` before any trial runs.
- **State.** None.
- **Dependencies.** `nltk.stem.PorterStemmer` (see Runbook — undeclared in `requirements.txt`). The matching logic (`_stem_match`, substring check) is a **re-derived copy** of `backend/pipeline/soul_router.py`'s rules, not an import of it — a deliberate choice: importing the production module would make the validator inert to a production regression (e.g., if someone changes the 4-char-prefix rule, an *imported* validator would silently start validating against the new rule instead of catching a genuine drift). A copy means the validator has a fixed, auditable definition of "leak" that must be manually kept in sync (see Failure modes).
- **Failure modes.** Because the matching rules are copied rather than imported, this validator can go **out of sync** with `soul_router.py` if that file's matching logic changes and no one updates `leakage_check.py` to match. This is a real, accepted maintenance cost, not an oversight — flagged explicitly here and in `EXP0_RUNBOOK.md` so a future maintainer knows to check both files together.
- **Experiments using it.** EXP-0 only, but the pattern (copy-not-import for a validator) is reusable for any future paraphrase-style experiment.
- **Removal impact.** `run_exp0.py` calls `leakage_check.main()` as a hard gate and refuses to proceed if it's missing/fails — removing this file makes `run_exp0.py` fail its import at the top of the file (`import leakage_check`), which is the intended fail-closed behavior.

---

## `detectors.py`

- **Purpose.** Thin, uniform wrappers around the three production entry points under test, isolating every `backend.*` import so the rest of the framework can be loaded/tested without the VELYNX backend being importable.
- **Inputs.** A query string (`tier1_v2`, `tier2_legacy`), or a query string + session id (`tier3_full`, async).
- **Outputs.** `DetectorResult(tier, query, concepts_detected, confidence, answer_text, latency_seconds, error)`. `.hit(concept)` is the single method every downstream analysis call uses — no other code path reads `concepts_detected` directly, so the definition of "hit" lives in exactly one place.
- **State.** None owned by this module. It reads whatever state `backend.pipeline.soul_router` / `backend.app.pipeline` currently hold (DB connections, loaded embedding index) — resetting that state between trials is `run_exp0.py`'s responsibility (via `_reset_state()`), not this module's, so `detectors.py` stays a pure, independently-testable translation layer.
- **Dependencies.** `backend.pipeline.soul_router` (Tier 1, Tier 2), `backend.app.pipeline` (Tier 3) — all imported lazily inside each function body.
- **Failure modes.** Any exception from the underlying call is caught and recorded in `DetectorResult.error` rather than propagated — a single query erroring (e.g., a timeout, an import failure in a partially-configured environment) must not abort the other 63 trials in the run. `error` is written to the raw JSONL artifact and must be inspected before trusting a tier's hit rate (an item that errored on both conditions would otherwise silently read as "miss, miss" — a concordant, uninformative pair, not a sign of collapse).
- **Experiments using it.** EXP-0 only.
- **Removal impact.** Total for EXP-0. Zero for the rest of the repo — no production code imports from `experiments/`.

---

## `analysis.py`

- **Purpose.** All statistics: McNemar's exact test, paired bootstrap CI, Holm-Bonferroni correction, and Markdown rendering.
- **Inputs.** Two equal-length `list[bool]` (hits per item, original vs. paraphrase condition) per tier.
- **Outputs.** `McNemarResult`, a bootstrap-CI `dict`, a Holm-correction `dict`, and a Markdown string.
- **State.** None. `paired_bootstrap_ci` takes an explicit `seed` (default `0`) and uses a local `random.Random(seed)` instance — never the global `random` module — so repeated calls with the same inputs are bit-for-bit identical.
- **Dependencies.** Standard library only (`math.comb`, `random`) — deliberately no `scipy`, matching `research/stats.py`'s existing no-third-party-stats-library convention in this repo.
- **Failure modes.** `ValueError` on mismatched-length inputs (a caller bug, not a data problem — this should never fire if `run_exp0.py`'s `_hits_by_concept()` is correct, and is a hard stop if it isn't).
- **Experiments using it.** EXP-0 only today; `mcnemar_exact`/`paired_bootstrap_ci`/`holm_bonferroni` are generic enough to be reused by any future paired-binary-outcome experiment without modification (noted for future reuse, not built as a shared library preemptively — Program D's rule against speculative abstraction).
- **Removal impact.** Total for producing `exp0_summary.json`/`exp0_report.md`. The raw JSONL artifact would still be written without it, so a run's primary data is never lost even if the analysis step is broken.

---

## `run_exp0.py`

- **Purpose.** The single command that ties every module above into one reproducible run: validate → determine trial order → reset state per trial where needed → call detectors → write artifacts.
- **Inputs.** CLI args: `--tier {1,2,3}+` (default `1 2`), `--seed` (default `1`), `--alpha` (default `0.01`), `--dry-run`, `--quiet`.
- **Outputs.** A new `artifacts/run_<stamp>_seed<N>_tier<T>/` directory (see `EXP0_DIRECTORY_STRUCTURE.md`), or (in `--dry-run`) nothing but a stdout confirmation.
- **State.** Orchestrates but does not itself hold cross-call state; owns the per-trial `_reset_state()` calls and the run directory's lifetime.
- **Dependencies.** Everything above, plus `scripts/wipe_db.py` (imported the same way `backend/tests/live_fire_harness.py` already does — via `importlib.util`, since `scripts/` is not a package) for Tier 1/Tier 3 state resets.
- **Failure modes.**
  - Refuses to run (`return 1`) if `leakage_check.main()` fails — a hard, unconditional gate.
  - `FileExistsError` if the target artifact directory already exists (immutability, matching `research/artifacts.py`'s convention) — re-running with the same `--seed`/`--tier` twice within the same UTC second is the only realistic way to hit this, and re-running is always safe a second later.
  - Per-trial detector errors do not abort the run (see `detectors.py` above) but DO surface in the raw JSONL and should be checked before trusting `exp0_summary.json`.
  - A crash mid-tier (e.g. `scripts/wipe_db.py`'s `strict=True` mode raising `WipeTargetMissingError`) is caught in `main()`, writes `_FAILED.txt` (traceback + which tiers completed) into the already-allocated run directory, then re-raises — so a partial run is never mistaken for a valid, if uneventful, result (see `EXP0_DIRECTORY_STRUCTURE.md`'s artifact schema and `EXP0_RUNBOOK.md`'s troubleshooting table).
- **Experiments using it.** EXP-0 only.
- **Removal impact.** This IS the experiment's execution entry point — there is no other way to run EXP-0. Its removal has zero impact on any other part of the repository, by construction (no production module imports anything from `experiments/EXP0/`).

---

## Explicitly not built (and why)

- **No LLM-judge scoring.** DVs read structured fields (`concepts_detected`, `resonance_scores`), never free-text answer quality — avoids the unfalsifiable-metric failure mode Program D flagged in `foundation/program_d_scientific_foundation_v0.1.md` Phase 6 (F3: "researcher degrees of freedom").
- **No k>1 paraphrase variants per concept.** Noted as a documented limitation (`EXP0_PREREGISTRATION.md`, Threats to Validity #3) and a candidate follow-up ("EXP-0b"), not built now — Program D's rule is "no subsystem without a preregistered experiment that requires it," and the *first* honest run of EXP-0 does not require replication depth to answer its pre-registered question.
- **No new artifact-writing library.** Reused the existing repo convention (immutable directories, content hashes, JSON artifacts) at a scale appropriate to a 64-trial experiment rather than adopting `research/artifacts.py`'s seven-file `RunConfig` schema, which is shaped for the C7-sensor consolidation-policy sweep and has no equivalent for most of its fields (`replay_horizon`, `noise_sigma`, `policy_params`) in a query-paraphrase experiment.
