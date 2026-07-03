"""EXP-0 — the one command.

    python run_exp0.py --tier 1 2               (primary, pre-registered)
    python run_exp0.py --tier 1 2 3 --seed 1     (add the exploratory full-pipeline tier)
    python run_exp0.py --dry-run                 (validate everything, call nothing)

Freezes nothing itself -- EXP0_RUNBOOK.md's step 1 (verify `git status` is
clean, or record the diff) is the researcher's responsibility before
invoking this script. What this script DOES do, every run:

  1. Load + integrity-check the dataset (dataset.py).
  2. Re-run the leakage validator (leakage_check.py) and refuse to proceed
     on failure -- a run must never score a benchmark it hasn't verified.
  3. Determine trial order via random.Random(seed) (see EXP0_PROTOCOL.md
     section 5 -- interleaved, not blocked by condition, to avoid an
     order confound from within-run state accumulation).
  4. For every requested tier, reset cognitive state (scripts/wipe_db.py)
     before EVERY trial that touches Tier 1 or Tier 3 (Tier 2 is a pure
     function and is never reset).
  5. Call the detector, record a DetectorResult per trial.
  6. Write seven artifacts to a fresh, immutable run directory (see
     EXP0_DIRECTORY_STRUCTURE.md): manifest, raw JSONL, per-tier summaries,
     and the rendered report.

This script never modifies backend/soul/concepts.json, paraphrases.json, or
any production source file.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
# Only _REPO_ROOT is needed: detectors.py imports exclusively via the
# "backend."-prefixed form (backend.pipeline.soul_router, backend.app.pipeline).
# Do NOT also add _REPO_ROOT/"backend" the way backend/tests/live_fire_harness.py
# does -- that harness needs it because pipeline.py mixes "backend.X" with
# BARE "app.X"/"conversation.X" imports; detectors.py has no bare imports, so
# adding backend/ here would only create a same-named-module shadowing risk
# with no compensating benefit.
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import dataset as exp0_dataset          # noqa: E402
import detectors                        # noqa: E402
import leakage_check                    # noqa: E402
import analysis                         # noqa: E402

DEFAULT_SEED = 1  # matches research/'s DEFAULT_SEEDS[0] convention
DEFAULT_ALPHA = 0.01  # matches foundation/program_d_scientific_foundation_v0.1.md Phase 6's p<0.01


def _reset_state(verbose: bool = True) -> bool:
    """Reuse backend/tests/live_fire_harness.py's exact wipe mechanism so
    EXP-0 does not reimplement (and risk diverging from) the one already-
    validated reset path in this repo."""
    import importlib.util
    wipe_path = _REPO_ROOT / "scripts" / "wipe_db.py"
    if not wipe_path.exists():
        if verbose:
            print(f"  [reset] {wipe_path} not found -- skipping reset.")
        return False
    spec = importlib.util.spec_from_file_location("wipe_db", str(wipe_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.run_wipe(dry=False, verbose=verbose, strict=True)
    return True


def _allocate_run_dir(seed: int, tiers: list[int]) -> Path:
    tier_tag = "".join(str(t) for t in tiers)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = _HERE / "artifacts" / f"run_{stamp}_seed{seed}_tier{tier_tag}"
    if run_dir.exists():
        raise FileExistsError(f"{run_dir} already exists -- refusing to overwrite an artifact dir.")
    run_dir.mkdir(parents=True)
    return run_dir


def _trial_order(items, seed: int) -> list[tuple[int, str]]:
    """(item_index, condition) pairs in randomized, interleaved order.
    Interleaving originals and paraphrases (rather than running all 32
    originals, then all 32 paraphrases) bounds how much within-run state
    drift (Tier-1/Tier-3 Hebbian plasticity) can differ systematically
    between the two conditions."""
    pairs = [(i, "original") for i in range(len(items))] + \
            [(i, "paraphrase") for i in range(len(items))]
    random.Random(seed).shuffle(pairs)
    return pairs


def run_tier2(items) -> dict:
    """Pure-function tier. No reset needed between trials."""
    raw = []
    for item in items:
        for cond, query in (("original", item.original_query),
                             ("paraphrase", item.paraphrase_query)):
            result = detectors.tier2_legacy(query)
            raw.append({"concept": item.concept, "condition": cond, **asdict(result)})
    return {"tier": "tier2_legacy", "raw": raw}


def run_tier1(items, seed: int, verbose: bool) -> dict:
    order = _trial_order(items, seed)
    by_key: dict[tuple[str, str], object] = {}
    raw = []
    for idx, cond in order:
        item = items[idx]
        query = item.original_query if cond == "original" else item.paraphrase_query
        _reset_state(verbose=verbose)
        result = detectors.tier1_v2(query)
        raw.append({"concept": item.concept, "condition": cond, **asdict(result)})
        by_key[(item.concept, cond)] = result
    return {"tier": "tier1_v2", "raw": raw}


async def run_tier3(items, seed: int, verbose: bool) -> dict:
    order = _trial_order(items, seed)
    raw = []
    for trial_num, (idx, cond) in enumerate(order):
        item = items[idx]
        query = item.original_query if cond == "original" else item.paraphrase_query
        _reset_state(verbose=verbose)
        session_id = f"exp0-{item.concept}-{cond}-{trial_num}"
        result = await detectors.tier3_full(query, session_id=session_id)
        raw.append({"concept": item.concept, "condition": cond, **asdict(result)})
    return {"tier": "tier3_full", "raw": raw}


def _hits_by_concept(raw: list[dict], items) -> tuple[list[bool], list[bool]]:
    by_key = {(r["concept"], r["condition"]): r for r in raw}
    hits_original, hits_paraphrase = [], []
    for item in items:
        o = by_key[(item.concept, "original")]
        p = by_key[(item.concept, "paraphrase")]
        hits_original.append(item.concept in o["concepts_detected"])
        hits_paraphrase.append(item.concept in p["concepts_detected"])
    return hits_original, hits_paraphrase


def analyze_tier(tier_result: dict, items, alpha: float) -> dict:
    hits_o, hits_p = _hits_by_concept(tier_result["raw"], items)
    m = analysis.mcnemar_exact(hits_o, hits_p)
    b = analysis.paired_bootstrap_ci(hits_o, hits_p, seed=0)
    report_text = analysis.render_report(
        tier_name=tier_result["tier"], concepts=[i.concept for i in items],
        hits_original=hits_o, hits_paraphrase=hits_p,
        mcnemar=m, bootstrap=b, alpha_used=alpha,
    )
    return {
        "tier": tier_result["tier"],
        "hit_rate_original": analysis.hit_rate(hits_o),
        "hit_rate_paraphrase": analysis.hit_rate(hits_p),
        "mcnemar": {"n01": m.n01, "n10": m.n10, "n_concordant": m.n_concordant,
                    "n_discordant": m.n_discordant, "p_value": m.p_value,
                    "direction": m.direction},
        "bootstrap_ci": b,
        "significant_at_alpha": m.p_value <= alpha,
        "report_text": report_text,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="EXP-0: paraphrase-invariance test")
    parser.add_argument("--tier", type=int, nargs="+", default=[1, 2], choices=[1, 2, 3],
                        help="Which detector tier(s) to run. 1+2 are the pre-registered "
                             "primary tiers; 3 is exploratory/secondary (heaviest deps).")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help="RNG seed for trial-order randomization (default: %(default)s)")
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA,
                        help="Significance threshold before Holm correction (default: %(default)s)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate dataset + leakage + imports; call no detector.")
    parser.add_argument("--quiet", action="store_true", help="Suppress reset-step logging.")
    args = parser.parse_args(argv)

    print("EXP-0 -- loading and validating dataset...")
    items = exp0_dataset.load_items()
    print(f"  {len(items)} items loaded, integrity check passed.")

    print("EXP-0 -- re-running leakage validator...")
    if leakage_check.main() != 0:
        print("REFUSING TO RUN: leakage validator failed. Fix paraphrases.json first.")
        return 1

    if args.dry_run:
        for tier in args.tier:
            if tier == 1:
                from backend.pipeline.soul_router import soul_lookup  # noqa: F401
            elif tier == 2:
                from backend.pipeline.soul_router import soul_lookup_legacy  # noqa: F401
            elif tier == 3:
                from backend.app.pipeline import answer_question  # noqa: F401
        print("DRY RUN OK -- dataset valid, leakage-free, all requested tier imports resolve. "
              "No detector was called; no artifacts were written.")
        return 0

    run_dir = _allocate_run_dir(args.seed, args.tier)
    print(f"EXP-0 -- writing artifacts to {run_dir}")

    tier_results = {}
    try:
        if 2 in args.tier:
            print("Running Tier 2 (legacy/lexical, no reset needed)...")
            tier_results[2] = run_tier2(items)
        if 1 in args.tier:
            print("Running Tier 1 (V2/semantic, resetting state before every trial)...")
            tier_results[1] = run_tier1(items, args.seed, verbose=not args.quiet)
        if 3 in args.tier:
            print("Running Tier 3 (full pipeline, resetting state before every trial)...")
            tier_results[3] = asyncio.run(run_tier3(items, args.seed, verbose=not args.quiet))
    except Exception as exc:
        # The run directory was already created (artifact-immutability requires
        # allocating it before we know trial counts). A crash mid-tier must not
        # leave an empty directory that looks like a valid-but-trivial result --
        # mark it unambiguously as failed instead.
        import traceback
        (run_dir / "_FAILED.txt").write_text(
            f"EXP-0 run crashed before completing.\n"
            f"Tiers completed before failure: {sorted(tier_results.keys())}\n"
            f"Tiers requested: {args.tier}\n\n{traceback.format_exc()}",
            encoding="utf-8",
        )
        print(f"RUN FAILED -- see {run_dir / '_FAILED.txt'}")
        raise

    (run_dir / "exp0_raw_results.jsonl").write_text(
        "\n".join(json.dumps(rec) for tr in tier_results.values() for rec in tr["raw"]) + "\n",
        encoding="utf-8",
    )

    primary_p_values = {}
    analyzed = {}
    for tier_num, tr in tier_results.items():
        a = analyze_tier(tr, items, args.alpha)
        analyzed[tr["tier"]] = a
        if tier_num in (1, 2):
            primary_p_values[tr["tier"]] = a["mcnemar"]["p_value"]

    holm = analysis.holm_bonferroni(primary_p_values, alpha=args.alpha) if primary_p_values else {}

    manifest = {
        "schema_version": "exp0.1",
        "dataset": exp0_dataset.dataset_manifest(),
        "seed": args.seed,
        "alpha_before_correction": args.alpha,
        "tiers_run": args.tier,
        "run_dir": str(run_dir),
    }
    (run_dir / "exp0_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    summary = {"per_tier": analyzed, "holm_bonferroni_primary": holm}
    (run_dir / "exp0_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8",
    )

    report_lines = ["# EXP-0 Report", "", f"Seed: {args.seed}  |  Tiers run: {args.tier}", ""]
    for tier_name, a in analyzed.items():
        report_lines.append(a["report_text"])
    if holm:
        report_lines.append("### Holm-Bonferroni correction across primary tiers (1, 2)")
        for name, r in holm.items():
            report_lines.append(f"- {name}: p={r['p_value']:.5f}, threshold={r['threshold']:.5f}, "
                                 f"significant after correction: {r['significant_after_correction']}")
    report_text = "\n".join(report_lines) + "\n"
    (run_dir / "exp0_report.md").write_text(report_text, encoding="utf-8")

    print(report_text)
    print(f"Artifacts written to {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
