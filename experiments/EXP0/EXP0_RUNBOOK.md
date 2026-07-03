# EXP-0 — Runbook

Follow these steps in order. Steps 1–4 are verification/setup and touch no VELYNX cognition code. Step 5 is the first point at which the live pipeline is called — nothing before it should be skipped.

---

## Step 0 — What you need

- A Python environment with this repo's existing dependencies installed, **plus `nltk`** (see Step 2 — it is imported by production code at `backend/pipeline/soul_router.py:8` but is missing from `requirements.txt`; this is a pre-existing repo defect, not introduced by EXP-0).
- For **Tier 1** and **Tier 3**: the sentence-transformer embedding model and index that `backend/soul/soul_graph.py:resonate()` depends on, and a working `brain_stem.db` with a `living_edges` table (the same prerequisites `backend/tests/live_fire_harness.py` needs).
- For **Tier 3** only, additionally: whatever LLM API credentials / network access the full `answer_question()` pipeline requires for retrieval + synthesis.
- **Tier 2** alone needs none of the above beyond `nltk` — it is the cheapest, fastest, most-portable tier and the recommended first run.

---

## Step 1 — Freeze verification

"Freeze the code" (`docs/VELYNX_v2_PI_Review.md` EXP-0 definition) requires knowing exactly what code ran. Before anything else:

```bash
git status --short
git rev-parse HEAD
```

- If `git status --short` is **empty**: record the commit hash from `git rev-parse HEAD` in your run notes. That hash is your freeze point.
- If it is **not empty** (as it was at design time for this repository): either (a) commit or stash the pending changes so the tree is clean, or (b) if that's not possible right now, run `git diff > exp0_pre_run_diff_<date>.patch` and keep that patch alongside your results — a run against a dirty tree without a saved diff is not reproducible and should not be reported as a frozen-code result.

---

## Step 2 — Install missing dependency

```bash
pip install nltk
```

No corpus download is required — `backend/pipeline/soul_router.py` only uses `nltk.stem.PorterStemmer`, which is a pure algorithm with no downloaded data files. Verify:

```bash
python -c "from nltk.stem import PorterStemmer; print(PorterStemmer().stem('forgiveness'))"
```

Expected output: `forgiv`.

---

## Step 3 — Validate the materials (no VELYNX code called)

```bash
cd experiments/EXP0
python dataset.py
```

Expected: `Loaded 32 items.` followed by a per-concept derivation listing and a manifest dict. Any `DatasetIntegrityError` here means `backend/soul/concepts.json` has changed since `paraphrases.json` was frozen — stop and resolve before continuing (see `EXP0_IMPLEMENTATION_PLAN.md`, `dataset.py` failure modes).

```bash
python leakage_check.py
```

Expected: `RESULT: PASSED — 32 paraphrase items checked against 32 seeded concepts. No leaks.` Do not proceed past a `FAILED` result — `run_exp0.py` will also refuse to run in that state, but catching it here is faster to debug.

---

## Step 4 — Dry run (validates imports resolve; still calls no detector)

```bash
python run_exp0.py --tier 2 --dry-run
```

This attempts to `import backend.pipeline.soul_router` (Tier 2's dependency) and reports whether it resolves, without calling `soul_lookup_legacy` and without writing any artifact. If you intend to also run Tier 1 or Tier 3, dry-run those too:

```bash
python run_exp0.py --tier 1 --dry-run
python run_exp0.py --tier 3 --dry-run
```

A dry-run import failure here means an environment/dependency problem (missing package, missing model weights, missing DB) — resolve it before Step 5, since a mid-run failure after 40 of 64 trials wastes the state-reset cost already paid.

---

## Step 5 — The one command

**Primary, pre-registered comparison (Tiers 1 and 2):**

```bash
python run_exp0.py --tier 1 2 --seed 1
```

**Tier 2 only** (fastest — recommended as your very first real invocation, since it has no DB/model prerequisites and completes in seconds):

```bash
python run_exp0.py --tier 2 --seed 1
```

**Add the exploratory full-pipeline tier** (heaviest; only after 1+2 have run successfully):

```bash
python run_exp0.py --tier 1 2 3 --seed 1
```

### Expected wall-clock

- Tier 2: sub-second (64 pure-function calls).
- Tier 1: dominated by 64 `scripts/wipe_db.py` resets, each of which is itself dominated by however long that script's DELETE+VACUUM+schema-shell-recreation takes on your machine — estimate from a single manual `python scripts/wipe_db.py` timing before committing to a full run.
- Tier 3: Tier 1's cost plus 64 real `answer_question()` calls, each potentially involving retrieval + an LLM call on a miss — the slowest tier by a wide margin. Budget accordingly; there is no fast-path shortcut without changing what's being measured.

### What you'll see

Console output streams per-tier progress (`Running Tier 2...`, `Running Tier 1 (resetting state before every trial)...`), then the rendered report is printed and also written to disk. On success, the last line names the artifact directory, e.g.:

```
Artifacts written to experiments/EXP0/artifacts/run_20260702T120000Z_seed1_tier12
```

---

## Step 6 — Interpreting `exp0_report.md`

For each tier requested, the report shows:

```
### tier2_legacy

- N (paired items): 32
- Hit rate, original:   <original hit rate>
- Hit rate, paraphrase: <paraphrase hit rate>
- McNemar exact test: n01=<>, n10=<>, discordant=<>, p=<> (<direction>)
- Bootstrap 95% CI on rate difference ...
- Significant at alpha=0.01: <True/False>
- Concepts that collapsed (hit on original, miss on paraphrase): <list>
```

Read this against `EXP0_PREREGISTRATION.md`'s Decision Matrix:

1. Check the `holm_bonferroni` section at the bottom of the report — this is the corrected significance verdict across Tiers 1+2, not the raw per-tier `p` values.
2. Cross both tiers' corrected verdicts against the Decision Matrix's four rows (A–D) to find your interpretation and next task.
3. The per-concept "collapsed" list is worth reading even when the aggregate result is clear — a pattern (e.g., only multi-word or only abstract concepts collapse) is itself informative and should be reported alongside the headline number, not discarded.
4. If Tier 3 was run, treat its numbers as supporting/exploratory context (`EXP0_PREREGISTRATION.md`), never as overriding a Tier 1/Tier 2 verdict.

---

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `DatasetIntegrityError` at Step 3/4 | `concepts.json` edited since freeze | Re-run `leakage_check.py`, bump `paraphrases.json`'s `schema_version`, re-freeze, or revert the edit. |
| `leakage_check.py` reports a leak | Someone hand-edited `paraphrases.json` without re-validating | Fix the flagged item; re-run until `PASSED`. |
| `ModuleNotFoundError: nltk` | Step 2 skipped | `pip install nltk`. |
| Tier 1/3 dry-run import fails | Embedding model/index or DB not set up in this environment | Set up the same prerequisites `backend/tests/live_fire_harness.py` needs, or run Tier 2 only. |
| `FileExistsError` allocating the run directory | Re-ran with identical `--seed`/`--tier` within the same UTC second, or a prior run's directory wasn't cleaned up | Wait a second and re-run, or pass a different `--seed`. Never manually delete a prior run's artifact directory to "fix" this without first checking whether it holds a result you still need. |
| A `run_<...>/` directory exists with only a `_FAILED.txt` file (no `exp0_report.md`) | The run crashed mid-tier (the directory is created before any tier starts, per `EXP0_DIRECTORY_STRUCTURE.md`'s immutability note) | Read `_FAILED.txt` for the traceback and which tiers completed before the crash. This directory holds no valid result — do not cite its absence of files as "0% hit rate." Fix the underlying error and start a fresh run (a different `--seed`, or the same one once the prior failed directory is moved aside). |
| A trial's `error` field is non-null in `exp0_raw_results.jsonl` | The underlying call raised (timeout, transient DB lock, etc.) | Inspect the error; if isolated to one or two trials, note it in your write-up and treat that pair as missing data rather than a miss (a caught exception is not evidence of "no detection"). If systematic, stop and fix the environment before trusting any hit-rate number from that run. |
