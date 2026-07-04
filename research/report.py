"""
research/report.py
==================

Cross-experiment analysis and the ``ablation_report.md`` renderer
(Sprint R1, Task 6).

Two responsibilities:

* :func:`build_analysis` — pool the per-run measurement records into per-policy
  distribution summaries and run the (pluggable) hypothesis test of the
  FreeEnergy policy against every other policy on the headline metrics.
* :func:`render_report` — turn that analysis into an honest Markdown report with
  the mandated structure (Research Question, Experimental Design, Independent
  Variables, Dependent Variables, Results, Statistical Summary, Limitations,
  Threats to Validity, Future Work).

Honesty is enforced structurally: the verdict is computed mechanically from the
means and the test p-values, so the report states whatever the data say — if
FreeEnergy loses or ties, it says so. There is no path by which the renderer can
flatter the FreeEnergy policy.

Standard library only.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

from research import metrics as research_metrics
from research.metrics import HIGHER_IS_BETTER, LOWER_IS_BETTER, METRICS_BY_NAME
from research.stats import SummaryStatistics, build_test

#: The dependent variables the headline verdict is computed on. Both are
#: lower-is-better and genuinely measurable in R1.
HEADLINE_METRICS = ["PredictionRMSE", "FinalEnergy"]

#: The principled policy under test.
TREATMENT_POLICY = "free_energy"


def build_analysis(
    records: Sequence[Mapping[str, Any]],
    *,
    treatment: str = TREATMENT_POLICY,
    test_name: str = "bootstrap_mean_difference",
    test_seed: int = 0,
) -> Dict[str, Any]:
    """Aggregate runs into per-policy summaries and FreeEnergy-vs-baseline tests.

    Parameters
    ----------
    records :
        One entry per run, each a mapping with ``policy`` and ``measurements``
        (the flat measurement record). Other keys (seed, horizon, noise) are
        carried through for context but not required here.
    treatment :
        The policy whose advantage we are testing (default ``"free_energy"``).
    test_name, test_seed :
        Which registered :class:`~research.stats.HypothesisTest` to use and its
        seed, kept configurable so a future t-test/permutation test drops in.
    """
    policies = _ordered_policies(records)

    # Pool measurement records by policy (across horizon, noise, and seed).
    by_policy: Dict[str, List[Mapping[str, Any]]] = {p: [] for p in policies}
    for rec in records:
        by_policy[rec["policy"]].append(rec["measurements"])

    per_policy: Dict[str, Dict[str, SummaryStatistics]] = {
        p: research_metrics.aggregate(recs) for p, recs in by_policy.items()
    }

    # Raw per-run scalar samples per (policy, metric) for the hypothesis tests.
    samples: Dict[str, Dict[str, List[float]]] = {}
    for p, recs in by_policy.items():
        samples[p] = {}
        for spec in research_metrics.METRIC_REGISTRY:
            vals = [spec.extract(r) for r in recs]
            samples[p][spec.name] = [v for v in vals if v is not None]

    test = build_test(test_name, seed=test_seed)
    tests: Dict[str, Dict[str, Any]] = {}
    if treatment in samples:
        for metric in HEADLINE_METRICS:
            tests[metric] = {}
            treat_vals = samples[treatment].get(metric, [])
            for p in policies:
                if p == treatment:
                    continue
                base_vals = samples[p].get(metric, [])
                result = test.compare(base_vals, treat_vals)
                tests[metric][p] = {
                    "effect_treatment_minus_baseline": result.effect,
                    "p_value": result.p_value,
                    "n_baseline": result.n_baseline,
                    "n_treatment": result.n_treatment,
                    "details": result.details,
                }

    verdict = _verdict(per_policy, tests, treatment)

    return {
        "policies": policies,
        "treatment": treatment,
        "test_name": test_name,
        "n_experiments": len(records),
        "per_policy": per_policy,
        "tests": tests,
        "verdict": verdict,
    }


def _ordered_policies(records: Sequence[Mapping[str, Any]]) -> List[str]:
    """Preserve the canonical ablation order for whatever policies are present."""
    from research.policies import DEFAULT_POLICY_ORDER

    present = {r["policy"] for r in records}
    ordered = [p for p in DEFAULT_POLICY_ORDER if p in present]
    # Append any non-standard policies (e.g. oracle) deterministically.
    ordered += sorted(p for p in present if p not in DEFAULT_POLICY_ORDER)
    return ordered


def _verdict(
    per_policy: Mapping[str, Mapping[str, SummaryStatistics]],
    tests: Mapping[str, Mapping[str, Any]],
    treatment: str,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """Mechanically decide, per headline metric, whether the treatment wins.

    A win requires BOTH (a) the treatment's mean is better (lower, since the
    headline metrics are lower-is-better) than the *best* baseline's mean, and
    (b) the treatment-vs-that-baseline test is significant at ``alpha`` in the
    treatment's favour. Anything else is reported as a tie or a loss — honestly.
    """
    out: Dict[str, Any] = {}
    for metric in HEADLINE_METRICS:
        spec = METRICS_BY_NAME[metric]
        treat_summary = per_policy.get(treatment, {}).get(metric)
        treat_mean = treat_summary.mean if treat_summary else None

        # Best baseline by mean (excluding the treatment).
        best_baseline = None
        best_mean = None
        for p, summaries in per_policy.items():
            if p == treatment:
                continue
            s = summaries.get(metric)
            if s is None or s.mean is None:
                continue
            if best_mean is None or _is_better(s.mean, best_mean, spec.direction):
                best_mean = s.mean
                best_baseline = p

        decision = "indeterminate"
        if treat_mean is not None and best_mean is not None:
            mean_better = _is_better(treat_mean, best_mean, spec.direction)
            test_entry = tests.get(metric, {}).get(best_baseline, {})
            p_value = test_entry.get("p_value")
            significant = (p_value is not None) and (p_value < alpha)
            if mean_better and significant:
                decision = "treatment_wins"
            elif (not mean_better) and significant:
                decision = "treatment_loses"
            else:
                decision = "tie"

        out[metric] = {
            "treatment_mean": treat_mean,
            "best_baseline": best_baseline,
            "best_baseline_mean": best_mean,
            "decision": decision,
        }
    return out


def _is_better(a: float, b: float, direction: str) -> bool:
    """Is ``a`` better than ``b`` under the metric's directionality?"""
    if direction == HIGHER_IS_BETTER:
        return a > b
    if direction == LOWER_IS_BETTER:
        return a < b
    return False  # NEUTRAL metrics have no "better"


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _fmt(x: Optional[float], places: int = 4) -> str:
    if x is None:
        return "n/a"
    return f"{x:.{places}f}"


def _summary_cell(s: Optional[SummaryStatistics]) -> str:
    if s is None or s.n == 0 or s.mean is None:
        return "n/a"
    return f"{_fmt(s.mean)} ± {_fmt((s.ci95_high - s.mean) if s.ci95_high is not None else None)}"


def render_report(analysis: Mapping[str, Any], matrix: Mapping[str, Any]) -> str:
    """Render the full ``ablation_report.md`` from an analysis + sweep matrix."""
    L: List[str] = []
    A = L.append

    A("# VELYNX Research Sprint R1 — Consolidation Policy Ablation\n")
    A(
        "> Auto-generated by `research/report.py`. Every number below is computed "
        "mechanically from immutable per-experiment artifacts; the verdict logic "
        "cannot favour any policy.\n"
    )

    # -- Research Question -------------------------------------------------
    A("## Research Question\n")
    A(
        "Does the existing **FreeEnergyPolicy** (VELYNX C8 Free-Energy "
        "Minimization) deliver a *measurable* benefit over reasonable, simpler "
        "consolidation heuristics — or is memory consolidation in VELYNX no "
        "better than naive baselines? A null or negative result is an equally "
        "valid scientific outcome.\n"
    )

    # -- Experimental Design ----------------------------------------------
    A("## Experimental Design\n")
    A(
        "Each experiment drives a freshly-seeded C7 Sensorium dataset through "
        "an unmodified `VectorPredictionCore` for a fixed number of ticks. When "
        "the (frozen) `MemoryScheduler` triggers a sleep cycle, the consolidation "
        "policy under test selects which clusters to merge and whether to commit; "
        "**every** proposal is measured identically by a read-only `ReplayEngine` "
        "rehearsal so policies are comparable. Only the policy varies between "
        "arms; the dataset, core, scheduler, replay engine, and measurement are "
        "held constant.\n"
    )
    A(f"- **Total experiments:** {analysis['n_experiments']}")
    A(f"- **Policies compared:** {', '.join(analysis['policies'])}")
    A(f"- **Replay horizons:** {matrix.get('replay_horizons')}")
    A(f"- **Noise levels (sensor σ):** {matrix.get('noise_levels')}")
    A(f"- **Seeds:** {matrix.get('seeds')}")
    A(f"- **Ticks per run:** {matrix.get('num_ticks')}")
    A(f"- **Dataset:** {matrix.get('dataset_name')}\n")

    # -- Independent Variables --------------------------------------------
    A("## Independent Variables\n")
    A("| Variable | Levels |")
    A("|---|---|")
    A(f"| Consolidation policy | {', '.join(analysis['policies'])} |")
    A(f"| Replay horizon | {matrix.get('replay_horizons')} |")
    A(f"| Sensor noise σ | {matrix.get('noise_levels')} |")
    A(f"| Random seed | {matrix.get('seeds')} |\n")

    # -- Dependent Variables ----------------------------------------------
    A("## Dependent Variables\n")
    A("Metrics are grouped into primary, secondary, and engineering tiers. "
      "Each is aggregated across seeds as mean, standard deviation, 95% "
      "confidence interval, and sample count.\n")
    A("| Metric | Tier | Direction | Units | Available | Note |")
    A("|---|---|---|---|---|---|")
    for m in research_metrics.METRIC_REGISTRY:
        avail = "yes" if m.available else "**NO**"
        A(f"| {m.name} | {m.category} | {m.direction} | {m.units} | {avail} | {m.note} |")
    A("")

    # -- Results -----------------------------------------------------------
    A("## Results\n")
    A("Per-policy summary (mean ± half-95%-CI), pooled over all horizons, noise "
      "levels, and seeds. `n/a` means the metric was not measurable.\n")
    _render_results_tables(A, analysis)

    # -- Statistical Summary ----------------------------------------------
    A("## Statistical Summary\n")
    A(
        f"Hypothesis test: **{analysis['test_name']}** comparing "
        f"`{analysis['treatment']}` (treatment) against each baseline on the "
        "headline metrics. Effect = treatment mean − baseline mean (negative "
        "favours the treatment, since both headline metrics are lower-is-better). "
        "Two-sided p-values.\n"
    )
    for metric in HEADLINE_METRICS:
        A(f"### {metric}\n")
        A("| Baseline | Effect (treat − base) | p-value | 95% CI of difference |")
        A("|---|---|---|---|")
        for base, entry in analysis["tests"].get(metric, {}).items():
            d = entry.get("details", {})
            ci = (
                f"[{_fmt(d.get('diff_ci95_low'))}, {_fmt(d.get('diff_ci95_high'))}]"
                if d else "n/a"
            )
            A(
                f"| {base} | {_fmt(entry.get('effect_treatment_minus_baseline'))} "
                f"| {_fmt(entry.get('p_value'), 4)} | {ci} |"
            )
        A("")

    # -- Verdict (mechanical) ---------------------------------------------
    A("### Verdict\n")
    for metric, v in analysis["verdict"].items():
        decision = v["decision"]
        phrase = {
            "treatment_wins": "FreeEnergy **wins** (better mean and significant)",
            "treatment_loses": "FreeEnergy **loses** (worse mean and significant)",
            "tie": "**tie / inconclusive** (no significant difference vs best baseline)",
            "indeterminate": "indeterminate (insufficient data)",
        }[decision]
        A(
            f"- **{metric}:** {phrase}. "
            f"FreeEnergy mean = {_fmt(v['treatment_mean'])}; "
            f"best baseline = `{v['best_baseline']}` "
            f"({_fmt(v['best_baseline_mean'])})."
        )
    A("")

    # -- Limitations -------------------------------------------------------
    A("## Limitations\n")
    A(_LIMITATIONS)

    # -- Threats to Validity ----------------------------------------------
    A("## Threats to Validity\n")
    A(_THREATS)

    # -- Future Work -------------------------------------------------------
    A("## Future Work\n")
    A(_FUTURE_WORK)

    return "\n".join(L) + "\n"


def _render_results_tables(A, analysis: Mapping[str, Any]) -> None:
    """Render one results table per metric tier."""
    policies = analysis["policies"]
    per_policy = analysis["per_policy"]
    for tier in (research_metrics.PRIMARY, research_metrics.SECONDARY,
                 research_metrics.ENGINEERING):
        specs = research_metrics.metrics_for(tier)
        A(f"### {tier.capitalize()} metrics\n")
        header = "| Metric | " + " | ".join(policies) + " |"
        sep = "|---|" + "|".join(["---"] * len(policies)) + "|"
        A(header)
        A(sep)
        for spec in specs:
            cells = []
            for p in policies:
                s = per_policy.get(p, {}).get(spec.name)
                cells.append(_summary_cell(s))
            A(f"| {spec.name} | " + " | ".join(cells) + " |")
        A("")


_LIMITATIONS = """\
- **Only one primary metric is measurable.** Of the six primary metrics the
  sprint specifies, only `PredictionRMSE` is computable from the current
  substrate. `HeldOutPredictiveLogLikelihood`, `RareEventRecall`,
  `KnowledgeRetentionScore`, `GeneralizationScore`, and `TransferScore` require
  machinery VELYNX does not yet have (a held-out split, exposed ground-truth
  labels, and multi-task/multi-phase protocols). They are reported as
  unavailable rather than fabricated.
- **Single dataset family.** All runs use the C7 Sensorium (`environment`).
  Conclusions may not transfer to other dynamics.
- **Small seed count.** Each cell is averaged over only a handful of seeds, so
  confidence intervals are correspondingly wide and modest effects cannot be
  resolved.
- **Replay horizon as IV proxy.** "Replay horizon" is operationalised as the
  recent-vector window length fed to the replay engine, the closest existing
  knob to the sprint's intent.
"""

_THREATS = """\
- **Construct validity / circularity on FinalEnergy.** `FreeEnergyPolicy`
  selects merges to minimise cognitive free energy, and `FinalEnergy` measures
  exactly that quantity. A FreeEnergy advantage on `FinalEnergy` is therefore
  partly *definitional*, not evidence of general superiority. `PredictionRMSE`
  is the more independent test of real predictive benefit and should be weighted
  accordingly.
- **CI distributional assumption.** The 95% CI on the mean uses a Student-t
  approximation that assumes approximate normality of the sampling distribution.
  With n=5 this is not guaranteed; the bootstrap hypothesis test is reported
  alongside precisely because it makes no such assumption.
- **Multiple comparisons.** FreeEnergy is tested against several baselines on
  several metrics; p-values are not corrected for multiplicity, so isolated
  significant results should be treated cautiously.
- **Unconditional-commit baselines.** Null never merges; Random/FIFO/Similarity/
  Utility commit every proposal. Differences may reflect *how often* a policy
  merges as much as *which* clusters it picks; the decision audit retains the
  per-merge energy deltas needed to disentangle these post hoc.
- **Shared measurement path.** All policies are scored by the same free-energy
  replay measurement; any bias in that measurement is shared across arms (which
  preserves *relative* comparison but could bias absolute values).
"""

_FUTURE_WORK = """\
- Implement the five unavailable primary metrics behind a held-out evaluation
  split and an offline ground-truth channel (the `Dataset` already hides regime
  labels that could feed `RareEventRecall`).
- Add a `t-test` and a `permutation` test as sibling `HypothesisTest` subclasses
  (the registry already supports this) and report agreement across tests.
- Implement the reserved `PlaceholderOraclePolicy` as a ground-truth upper bound
  to contextualise the gap between heuristics and the achievable optimum.
- Broaden the dataset family and increase seed counts to tighten the intervals.
- Disentangle *selection* from *commit frequency* by adding accept-gated variants
  of the heuristic policies (e.g. Similarity + free-energy gate).
"""


__all__ = [
    "HEADLINE_METRICS",
    "TREATMENT_POLICY",
    "build_analysis",
    "render_report",
]
