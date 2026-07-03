# EXP-0 — Directory Structure

## Location

`experiments/EXP0/`, alongside `experiments/program_d_experiment_coverage_matrix.csv` (the existing Program D experiment tracker referenced in the repo README). This directory is separate from `research/experiments/` (which holds pre-registrations for the `research/` package's `RunConfig`/`ResearchRunner` sweeps, e.g. R1, R3F.1 — a different kind of experiment, operating on the synthetic C7 sensor environment rather than the live NLP pipeline). EXP-0 does not use `research/runner.py`/`research/artifacts.py` because its unit of measurement (a query → detector → hit/miss) has no `RunConfig` fields in common with a consolidation-policy sweep; it defines its own, smaller artifact schema (§3) instead of forcing an unrelated one to fit.

## Layout as of the frozen design (no artifacts/ yet — nothing has run)

```
experiments/
├── program_d_experiment_coverage_matrix.csv      (pre-existing, unrelated to EXP-0)
├── calculator.py, generated_tool.py, test_calc.py (pre-existing self-coder-sandbox
│                                                    toy files, marked DELETE in
│                                                    archive/program_c_archive_manifest.md
│                                                    — not touched by this experiment)
└── EXP0/
    ├── EXP0_PROTOCOL.md              # mission, target mechanism, dataset & paraphrase
    │                                  # protocol, randomization procedure, non-goals
    ├── EXP0_PREREGISTRATION.md       # hypotheses, IV/DV, controls, success/failure criteria
    ├── EXP0_DIRECTORY_STRUCTURE.md   # this file
    ├── EXP0_IMPLEMENTATION_PLAN.md   # module-by-module code spec
    ├── EXP0_STATISTICAL_ANALYSIS.md  # test derivations, power analysis, worked example
    ├── EXP0_RUNBOOK.md               # step-by-step operating instructions
    │
    ├── __init__.py                   # package docstring only; no exports
    ├── dataset.py                    # loads + integrity-checks paraphrases.json vs
    │                                  # concepts.json; BenchmarkItem dataclass
    ├── paraphrases.json              # FROZEN: the 32 (original, paraphrase) pairs
    ├── leakage_check.py              # re-derived (not imported) copy of soul_router.py's
    │                                  # substring/stem rules; validates paraphrases.json
    ├── detectors.py                  # tier1_v2 / tier2_legacy / tier3_full wrappers;
    │                                  # DetectorResult dataclass
    ├── analysis.py                   # mcnemar_exact, paired_bootstrap_ci,
    │                                  # holm_bonferroni, render_report
    ├── run_exp0.py                   # CLI orchestrator — "the one command"
    │
    └── artifacts/                    # created on first run; does not exist yet
        └── run_<UTCSTAMP>_seed<N>_tier<T>/    # one immutable directory per invocation
            ├── exp0_manifest.json     # dataset hashes, seed, alpha, tiers run
            ├── exp0_raw_results.jsonl # one JSON object per (concept, condition, tier) trial
            ├── exp0_summary.json      # per-tier hit rates, McNemar/bootstrap results, Holm correction
            └── exp0_report.md         # rendered Markdown, human-readable
```

## Why no `data/` subfolder

The "dataset" (`paraphrases.json`) is small enough (32 items) and permanently tied to one source file (`backend/soul/concepts.json`) that a separate `data/` directory would only add navigation overhead. It lives at the top of `EXP0/` next to the code that loads it, matching how `research/policies/__init__.py` keeps its registry next to its implementations rather than in a nested `data/` folder.

## Artifact immutability

`run_exp0.py:_allocate_run_dir()` raises `FileExistsError` if the target `run_<...>` directory already exists — mirroring `research/artifacts.py:allocate_experiment_dir()`'s convention — so a run can never silently overwrite a previous one's results. Each directory name encodes its own seed and tier selection, so two runs with different parameters never collide, and two runs with identical parameters will collide (by design) rather than one silently clobbering the other.

## Artifact schema (per run directory)

| File | Contents | Written by |
|---|---|---|
| `exp0_manifest.json` | `{schema_version, dataset: {concepts_json_sha256, paraphrases_json_sha256, item_count}, seed, alpha_before_correction, tiers_run, run_dir}` | `run_exp0.py:main()` |
| `exp0_raw_results.jsonl` | One line per trial: `{concept, condition, tier, query, concepts_detected, confidence, answer_text, latency_seconds, error}` (the last four are `null` for tiers where they don't apply) | `run_exp0.py:run_tier1/2/3()` |
| `exp0_summary.json` | `{per_tier: {<tier_name>: {hit_rate_original, hit_rate_paraphrase, mcnemar: {...}, bootstrap_ci: {...}, significant_at_alpha, report_text}}, holm_bonferroni_primary: {...}}` | `run_exp0.py:analyze_tier()` via `analysis.py` |
| `exp0_report.md` | Human-readable concatenation of each tier's `report_text` plus the Holm-Bonferroni table | `run_exp0.py:main()` |
| `_FAILED.txt` (only present on a crashed run) | Traceback + which tiers completed before failure. The run directory is allocated before any tier starts (to keep the immutability check in one place), so a mid-run crash must leave an unambiguous failure marker rather than a directory that merely looks empty. If this file is present, none of the other four files should be trusted even if some happen to exist from a partially-written state. | `run_exp0.py:main()`'s exception handler |

No file in `artifacts/` is ever read by production code — this is strictly an output sink, one-directional.

## What is version-controlled vs. generated

- **Version-controlled (part of this deliverable):** everything directly under `experiments/EXP0/` except `artifacts/`.
- **Generated, not committed:** `experiments/EXP0/artifacts/**` (add `experiments/EXP0/artifacts/` to `.gitignore` if repeated local runs should not be tracked; left as a decision for whoever runs the first real invocation, since whether raw experimental output belongs in version control is a data-management policy call, not an experiment-design one).
