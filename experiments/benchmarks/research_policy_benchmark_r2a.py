"""
research_policy_benchmark_r2a.py
================================

Sprint **R2A.1** policy-comparison driver.

Scientific question
--------------------
Does the ``FreeEnergyPolicy`` provide a measurable *predictive* benefit over
simpler consolidation heuristics, measured by **HeldOutPredictiveRMSE** on a
held-out, seed-disjoint probe stream?

Why this file exists (and what it is NOT)
-----------------------------------------
The R2A implementation is frozen. This driver adds **no** evaluation
infrastructure and **no** cognitive feature: it only *composes* the existing,
frozen public API —

  * ``research.runner.run_single`` / ``RunConfig``         (the runner)
  * ``research.evaluation.EvaluationProtocol``             (held-out scoring)
  * ``research.metrics`` (HeldOutPredictiveRMSE extractor) (the metric registry)
  * ``research.stats.SummaryStatistics`` / bootstrap test  (the statistics)

It does not import or modify ``benchmark.py``, ``research_benchmark.py``, any
``backend.cognition.*`` module, the objective functions, or the evaluation
scripts. It is a read-only experiment orchestrator.

The reason it is needed at all: ``research_benchmark.py`` (the R1 orchestrator)
never attaches an ``EvaluationProtocol`` to its ``RunConfig``s, so it reports
HeldOutPredictiveRMSE as ``n=0`` (not measured). R2A added the protocol exactly
to make this metric obtainable; this driver wires it in at the experiment level.

Configuration (fixed by the sprint)
-----------------------------------
* Policies     : null, random, similarity, free_energy
* Environments : simple (noise_sigma=0.01), noisy (noise_sigma=0.15)
                 -- taken verbatim from configs/simple.json + configs/noisy.json
* Seeds        : 1..5 (five seeds)
* Held constant across EVERY run (the comparability guarantee):
    - replay_horizon      = 200  (production DEFAULT_REPLAY_HORIZON)
    - proximity_threshold = 0.28 (configs/*.json)
    - max_clusters        = 50   (runner default)
    - num_ticks           = 5000 (configs/*.json)
    - merge budget        = 3    (MAX_MERGES_PER_CYCLE, fixed in the runner)
    - scheduler           = MemoryScheduler default (fixed in the runner)
    - held-out probe      = 200 ticks, seed-disjoint, same noise as training

Standard library only. Run from the repository root.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List

from research.evaluation.protocol import EvaluationProtocol, HELD_OUT_RMSE_KEY
from research.metrics import METRICS_BY_NAME
from research.runner import DEFAULT_REPLAY_HORIZON, RunConfig, run_single
from research.stats import BootstrapMeanDifferenceTest, SummaryStatistics

# -- the fixed experiment matrix -------------------------------------------
POLICIES: List[str] = ["null", "random", "similarity", "free_energy"]
ENVIRONMENTS: Dict[str, float] = {"simple": 0.01, "noisy": 0.15}
SEEDS: List[int] = [1, 2, 3, 4, 5]
TREATMENT = "free_energy"

# -- invariants held identical across every run ----------------------------
REPLAY_HORIZON = DEFAULT_REPLAY_HORIZON  # 200
PROXIMITY_THRESHOLD = 0.28
MAX_CLUSTERS = 50
NUM_TICKS = 5000
PROBE_TICKS = 200
DATASET = "environment"

METRIC_KEY = HELD_OUT_RMSE_KEY            # "held_out_predictive_rmse"
METRIC_NAME = "HeldOutPredictiveRMSE"     # registry name (primary, lower-is-better)


def run_matrix(*, verbose: bool = True) -> List[Dict[str, Any]]:
    """Execute policy x environment x seed and collect HeldOutPredictiveRMSE.

    Returns one record per run. The single behavioural axis is ``policy``;
    every other knob is pinned to the module-level invariants above, so any
    difference in HeldOutPredictiveRMSE is attributable to the policy alone.
    """
    extract = METRICS_BY_NAME[METRIC_NAME].extract
    records: List[Dict[str, Any]] = []
    combos = [(p, e, s) for p in POLICIES for e in ENVIRONMENTS for s in SEEDS]
    total = len(combos)

    if verbose:
        print(f"[r2a.1] running {total} experiments "
              f"({len(POLICIES)} policies x {len(ENVIRONMENTS)} envs x {len(SEEDS)} seeds)")
        print(f"[r2a.1] fixed: horizon={REPLAY_HORIZON} ticks={NUM_TICKS} "
              f"proximity={PROXIMITY_THRESHOLD} max_clusters={MAX_CLUSTERS} "
              f"probe_ticks={PROBE_TICKS}")

    for idx, (policy, env_name, seed) in enumerate(combos, start=1):
        noise = ENVIRONMENTS[env_name]
        # Held-out probe: same dataset + same noise as training, but a
        # provably seed-disjoint stream (probe_seed maps seed -> high band).
        protocol = EvaluationProtocol(
            train_seed=seed,
            dataset_name=DATASET,
            noise_sigma=noise,
            num_probe_ticks=PROBE_TICKS,
        )
        cfg = RunConfig(
            policy=policy,
            replay_horizon=REPLAY_HORIZON,
            noise_sigma=noise,
            seed=seed,
            num_ticks=NUM_TICKS,
            dataset_name=DATASET,
            proximity_threshold=PROXIMITY_THRESHOLD,
            max_clusters=MAX_CLUSTERS,
            evaluation_protocol=protocol,
        )
        t0 = time.perf_counter()
        result = run_single(cfg)
        dt = time.perf_counter() - t0

        held_out = extract(result.measurements)
        records.append({
            "policy": policy,
            "environment": env_name,
            "noise_sigma": noise,
            "seed": seed,
            "held_out_seed": protocol.held_out_seed(),
            METRIC_KEY: held_out,
            "in_sample_rmse": result.measurements.get("prediction_rmse"),
            "runtime_seconds": dt,
        })
        if verbose:
            print(f"  [{idx:>2}/{total}] {policy:<11} {env_name:<6} seed={seed} "
                  f"HeldOutRMSE={held_out:.6f}  ({dt:.1f}s)")
    return records


def _samples(records, policy, env=None):
    """HeldOutPredictiveRMSE samples for a policy (optionally one environment)."""
    return [
        r[METRIC_KEY] for r in records
        if r["policy"] == policy
        and (env is None or r["environment"] == env)
        and r[METRIC_KEY] is not None
    ]


def aggregate(records) -> Dict[str, Any]:
    """Per-policy SummaryStatistics (overall + per environment) for the metric."""
    out: Dict[str, Any] = {"overall": {}, "by_environment": {}}
    for policy in POLICIES:
        out["overall"][policy] = SummaryStatistics.from_samples(
            _samples(records, policy)
        ).as_dict()
    for env in ENVIRONMENTS:
        out["by_environment"][env] = {
            policy: SummaryStatistics.from_samples(
                _samples(records, policy, env)
            ).as_dict()
            for policy in POLICIES
        }
    return out


def inference(records) -> Dict[str, Any]:
    """Bootstrap mean-difference test: FreeEnergy vs each baseline heuristic.

    Effect = mean(FreeEnergy) - mean(baseline). HeldOutPredictiveRMSE is
    lower-is-better, so a *negative* effect with a CI excluding zero means
    FreeEnergy predicts measurably better than that baseline.
    """
    test = BootstrapMeanDifferenceTest(iterations=10_000, seed=0)
    treat_overall = _samples(records, TREATMENT)
    result: Dict[str, Any] = {"overall": {}, "by_environment": {}}

    for baseline in POLICIES:
        if baseline == TREATMENT:
            continue
        tr = test.compare(_samples(records, baseline), treat_overall)
        result["overall"][baseline] = {
            "effect": tr.effect, "p_value": tr.p_value,
            "diff_ci95_low": tr.details.get("diff_ci95_low"),
            "diff_ci95_high": tr.details.get("diff_ci95_high"),
            "n_baseline": tr.n_baseline, "n_treatment": tr.n_treatment,
        }

    for env in ENVIRONMENTS:
        treat_env = _samples(records, TREATMENT, env)
        result["by_environment"][env] = {}
        for baseline in POLICIES:
            if baseline == TREATMENT:
                continue
            tr = test.compare(_samples(records, baseline, env), treat_env)
            result["by_environment"][env][baseline] = {
                "effect": tr.effect, "p_value": tr.p_value,
                "diff_ci95_low": tr.details.get("diff_ci95_low"),
                "diff_ci95_high": tr.details.get("diff_ci95_high"),
            }
    return result


def _fmt(x, nd=6):
    return "  n/a " if x is None else f"{x:.{nd}f}"


def _stat_table(title, stats_by_policy) -> str:
    """Render a Mean / Std / 95% CI table for HeldOutPredictiveRMSE."""
    lines = [
        title,
        f"{'Policy':<13}{'n':>3}  {'Mean':>10}  {'Std':>10}  "
        f"{'95% CI low':>11}  {'95% CI high':>11}",
        "-" * 65,
    ]
    # rank by mean (lower is better); None means unmeasured -> sort last
    order = sorted(
        POLICIES,
        key=lambda p: (stats_by_policy[p]["mean"] is None,
                       stats_by_policy[p]["mean"] if stats_by_policy[p]["mean"] is not None else 0.0),
    )
    for p in order:
        s = stats_by_policy[p]
        lines.append(
            f"{p:<13}{s['n']:>3}  {_fmt(s['mean']):>10}  {_fmt(s['std']):>10}  "
            f"{_fmt(s['ci95_low']):>11}  {_fmt(s['ci95_high']):>11}"
        )
    return "\n".join(lines)


def _inference_table(title, infer_block) -> str:
    lines = [
        title,
        f"{'FE vs baseline':<16}{'effect(FE-base)':>16}  {'95% CI of diff':>24}  "
        f"{'p':>7}  verdict",
        "-" * 86,
    ]
    for baseline, t in infer_block.items():
        eff = t["effect"]
        lo, hi = t.get("diff_ci95_low"), t.get("diff_ci95_high")
        p = t["p_value"]
        if eff is None or lo is None or hi is None:
            verdict = "n/a"
        elif hi < 0:
            verdict = "FE BETTER (CI<0)"
        elif lo > 0:
            verdict = "FE WORSE (CI>0)"
        else:
            verdict = "no sig. difference"
        ci = f"[{_fmt(lo,5)}, {_fmt(hi,5)}]"
        lines.append(
            f"{baseline:<16}{_fmt(eff):>16}  {ci:>24}  {_fmt(p,4):>7}  {verdict}"
        )
    return "\n".join(lines)


def render_report(agg, infer) -> str:
    blocks = [
        "=" * 86,
        "VELYNX Sprint R2A.1 - Policy Comparison on HeldOutPredictiveRMSE",
        "(primary metric; lower is better; held-out, seed-disjoint probe stream)",
        "=" * 86,
        "",
        _stat_table("[POOLED across both environments | 10 runs/policy = 2 envs x 5 seeds]",
                    agg["overall"]),
        "",
    ]
    for env in ENVIRONMENTS:
        blocks.append(_stat_table(
            f"[ENVIRONMENT = {env} (noise_sigma={ENVIRONMENTS[env]}) | 5 seeds/policy]",
            agg["by_environment"][env]))
        blocks.append("")
    blocks.append(_inference_table(
        "[INFERENCE | bootstrap mean-difference, 10k resamples | POOLED]",
        infer["overall"]))
    blocks.append("")
    for env in ENVIRONMENTS:
        blocks.append(_inference_table(
            f"[INFERENCE | bootstrap mean-difference | ENVIRONMENT = {env}]",
            infer["by_environment"][env]))
        blocks.append("")
    return "\n".join(blocks)


def main() -> int:
    start = time.perf_counter()
    records = run_matrix(verbose=True)
    agg = aggregate(records)
    infer = inference(records)
    report = render_report(agg, infer)

    print("\n" + report)
    total_dt = time.perf_counter() - start
    print(f"[r2a.1] completed {len(records)} runs in {total_dt:.1f}s")

    # -- artifacts (additive; under research_artifacts/) -------------------
    group = time.strftime("r2a1_policy_benchmark_%Y%m%dT%H%M%S")
    out_dir = os.path.join("research_artifacts", group)
    os.makedirs(out_dir, exist_ok=True)

    payload = {
        "sprint": "R2A.1",
        "question": "Does FreeEnergyPolicy provide measurable predictive benefit "
                    "over simpler heuristics (HeldOutPredictiveRMSE)?",
        "metric": METRIC_NAME,
        "metric_direction": "lower_is_better",
        "fixed_hyperparameters": {
            "replay_horizon": REPLAY_HORIZON,
            "proximity_threshold": PROXIMITY_THRESHOLD,
            "max_clusters": MAX_CLUSTERS,
            "num_ticks": NUM_TICKS,
            "merge_budget_per_cycle": 3,
            "probe_ticks": PROBE_TICKS,
            "dataset": DATASET,
            "scheduler": "MemoryScheduler default (fixed in runner)",
        },
        "matrix": {"policies": POLICIES, "environments": ENVIRONMENTS, "seeds": SEEDS},
        "raw_runs": records,
        "summary_statistics": agg,
        "inference_bootstrap_mean_difference": infer,
    }
    with open(os.path.join(out_dir, "r2a1_analysis.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(out_dir, "r2a1_report.txt"), "w", encoding="utf-8") as fh:
        fh.write(report + "\n")

    print(f"[r2a.1] artifacts: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
