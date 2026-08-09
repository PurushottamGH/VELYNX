"""Cross-run reporting: read artifacts, pair by seed, report effects.

Responsibility: read completed runs and summarise them. It never runs an
experiment and never writes into a run directory, so analysis can be re-done any
number of times without touching the evidence.

    python scripts/analyse.py artifacts/runs/v0_2_matched_updates
    python scripts/analyse.py <root> --metric excess_loss.final_prior_excess_mean \
                                     --reference "replay.name=none"

What it prints:
  * one row per condition: n seeds, mean of the chosen metric, and the realised
    compute — so a "resource-matched" design can be *checked*, not assumed;
  * paired contrasts against a reference condition, at the environment-seed level,
    with a bootstrap CI.

It deliberately does not apply a SESOI or declare a result. That requires a
preregistered threshold, and printing a verdict without one would invite exactly
the over-claiming the M0 review flagged. Feed the intervals to
`science.stats.decide_superiority` once the threshold is frozen.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from experiments.engine.artifacts import collect_metrics  # noqa: E402
from science.stats import paired_bootstrap, paired_differences  # noqa: E402

DEFAULT_METRIC = "excess_loss.final_prior_excess_mean"


def dig(payload: Dict[str, Any], dotted: str) -> Optional[float]:
    """Read `metric.field` out of a metrics dict, or None if absent."""
    node: Any = payload
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, (int, float)) else None


def condition_label(config: Dict[str, Any]) -> str:
    """Identify a condition by the component choices that define it.

    Seeds are excluded on purpose: runs differing only by seed are replicates of
    one condition, which is what makes the paired contrast possible.
    """
    parts = []
    for section in ("gate", "replay", "memory", "environment", "model"):
        spec = config.get(section) or {}
        name = spec.get("name", "?")
        params = spec.get("params") or {}
        interesting = {
            k: v
            for k, v in sorted(params.items())
            if k in ("k", "threshold", "decay", "rate", "n_fires", "order")
        }
        detail = ",".join(f"{k}={v}" for k, v in interesting.items())
        parts.append(f"{section}={name}" + (f"[{detail}]" if detail else ""))
    return " ".join(parts)


def group_runs(root: str | Path) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """`{condition label: {master seed: run record}}`."""
    grouped: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for record in collect_metrics(root):
        label = condition_label(record.get("config", {}))
        seed = int((record.get("seeds") or {}).get("master", -1))
        grouped.setdefault(label, {})[seed] = record
    return grouped


def summarise(grouped: Dict[str, Dict[int, Dict[str, Any]]], metric: str) -> List[Tuple[str, Any]]:
    rows = []
    for label, by_seed in sorted(grouped.items()):
        values = [dig(r["metrics"], metric) for r in by_seed.values()]
        finite = [v for v in values if v is not None]
        updates = {int(r["compute"].get("updates_total", 0)) for r in by_seed.values()}
        replays = {int(r["compute"].get("replay_updates", 0)) for r in by_seed.values()}
        shortfall = max(int(r["compute"].get("replay_shortfall", 0)) for r in by_seed.values())
        rows.append(
            (
                label,
                {
                    "n": len(by_seed),
                    "mean": sum(finite) / len(finite) if finite else None,
                    "updates_total": sorted(updates),
                    "replay_updates": sorted(replays),
                    "max_replay_shortfall": shortfall,
                },
            )
        )
    return rows


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Summarise completed P1 runs")
    parser.add_argument("root", help="artifact directory to read")
    parser.add_argument(
        "--metric", default=DEFAULT_METRIC, help=f"dotted metric path (default {DEFAULT_METRIC})"
    )
    parser.add_argument(
        "--reference", default="", help="substring identifying the reference condition"
    )
    parser.add_argument("--alpha", type=float, default=0.05)
    args = parser.parse_args(argv)

    grouped = group_runs(args.root)
    if not grouped:
        print(f"no completed runs under {args.root}", file=sys.stderr)
        return 1

    rows = summarise(grouped, args.metric)
    print(f"metric: {args.metric}\n")
    for label, stats in rows:
        mean = "n/a" if stats["mean"] is None else f"{stats['mean']:+.4f}"
        print(f"{label}")
        print(
            f"    n={stats['n']}  mean={mean}  updates={stats['updates_total']}  "
            f"replays={stats['replay_updates']}  shortfall<={stats['max_replay_shortfall']}"
        )

    # Compute matching is a precondition for interpreting any contrast, so it is
    # checked and reported rather than assumed.
    all_updates = {u for _, s in rows for u in s["updates_total"]}
    print(
        "\nupdate matching across conditions: "
        + ("MATCHED" if len(all_updates) == 1 else f"NOT MATCHED ({sorted(all_updates)})")
    )

    reference = next(
        (label for label, _ in rows if args.reference and args.reference in label), None
    )
    if args.reference and reference is None:
        print(f"\nreference {args.reference!r} matched no condition", file=sys.stderr)
        return 1
    if reference is None:
        return 0

    print(f"\npaired contrasts vs {reference}\n")
    ref_values = {seed: dig(r["metrics"], args.metric) for seed, r in grouped[reference].items()}
    for label, by_seed in sorted(grouped.items()):
        if label == reference:
            continue
        values = {seed: dig(r["metrics"], args.metric) for seed, r in by_seed.items()}
        diffs = paired_differences(values, ref_values)
        boot = paired_bootstrap(list(diffs.values()), alpha=args.alpha)
        lo, hi = boot.get("ci_lo"), boot.get("ci_hi")
        interval = "n/a" if lo is None or lo != lo else f"[{lo:+.4f}, {hi:+.4f}]"
        print(f"{label}")
        print(
            f"    n_pairs={boot['n']}  mean_diff={boot['mean']:+.4f}  {100*(1-args.alpha):.0f}% CI {interval}"
        )
    print(
        "\nNo verdict is printed: acceptance requires a preregistered SESOI. "
        "Pass these intervals to science.stats.decide_superiority once it is frozen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
