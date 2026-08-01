"""Paired inference at the environment-seed level.

Responsibility: turn per-seed run outcomes into an effect estimate with
uncertainty, and apply the decision rule that was declared before the data were
seen.

The M0 review rejected the originally proposed acceptance rule outright: overlap
of two separate 95% CIs is not a paired test, rank stability is not an effect
size, and bootstrap validity depends on resampling the correct independent unit.
Steps and probe transitions are autocorrelated and are *not* independent units;
the environment seed is. This module therefore:

  * pairs conditions by shared environment realisation and resamples seeds;
  * reports an effect size with a CI, never a rank;
  * evaluates against a preregistered SESOI, so "statistically detectable" and
    "scientifically relevant" stay separate;
  * offers an equivalence test, because V0-1's no-decay control must be shown
    *similar to zero*, which a failed difference test does not establish;
  * offers Holm correction, because several contrasts are inspected per experiment.

It is analysis code: nothing in the engine imports it, and it never touches disk.
"""

from __future__ import annotations

from typing import Dict, Mapping, Sequence

import numpy as np

#: Resample count. High enough that CI endpoints are stable to ~3 decimals.
DEFAULT_BOOTSTRAP = 10_000


def paired_differences(a: Mapping[int, float], b: Mapping[int, float]) -> Dict[int, float]:
    """`a - b` for seeds present in both, with a usable value in both.

    Silently substituting a mean for a missing seed would fabricate pairing, which
    is the failure mode this function exists to prevent. Missing values arrive as
    `None` from sanitised artifacts (see `artifacts.sanitise`) or as NaN in memory;
    both are dropped, and the returned pair count tells the caller how many
    survived.
    """
    shared = sorted(set(a) & set(b))
    out: Dict[int, float] = {}
    for seed in shared:
        left, right = a[seed], b[seed]
        if left is None or right is None:
            continue
        left, right = float(left), float(right)
        if left != left or right != right:
            continue
        out[seed] = left - right
    return out


def paired_bootstrap(
    diffs: Sequence[float],
    n_boot: int = DEFAULT_BOOTSTRAP,
    alpha: float = 0.05,
    seed: int = 0,
) -> Dict[str, object]:
    """Bootstrap the mean paired difference by resampling seeds with replacement."""
    values = np.asarray(
        [float(d) for d in diffs if d is not None and float(d) == float(d)], dtype=float
    )
    n = int(values.size)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "ci_lo": float("nan"), "ci_hi": float("nan")}
    if n < 3:
        # A CI from one or two units is not meaningful; report the point estimate
        # and say so rather than emitting a misleadingly narrow interval.
        return {
            "n": n,
            "mean": float(values.mean()),
            "ci_lo": float("nan"),
            "ci_hi": float("nan"),
            "note": "n < 3: interval not estimated",
        }

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = values[idx].mean(axis=1)
    lo, hi = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return {
        "n": n,
        "mean": float(values.mean()),
        "sd": float(values.std(ddof=1)),
        "ci_lo": float(lo),
        "ci_hi": float(hi),
        "alpha": alpha,
        "n_boot": n_boot,
        "fraction_negative": float((values < 0).mean()),
        "fraction_positive": float((values > 0).mean()),
    }


def decide_superiority(
    boot: Mapping[str, object],
    sesoi: float,
    direction: str = "lower_is_better",
) -> str:
    """Apply a preregistered SESOI to a bootstrapped paired difference.

    Returns "supported", "not_supported" or "inconclusive". Inconclusive is a real
    outcome and must not be collapsed into either of the others: a CI that spans
    the SESOI means the study lacked precision, not that the effect is absent.
    """
    if sesoi <= 0:
        raise ValueError("sesoi must be a positive magnitude")
    if direction not in ("lower_is_better", "higher_is_better"):
        raise ValueError("direction must be 'lower_is_better' or 'higher_is_better'")
    lo, hi = boot.get("ci_lo"), boot.get("ci_hi")
    if lo is None or hi is None or lo != lo or hi != hi:
        return "inconclusive"
    lo, hi = float(lo), float(hi)
    if direction == "lower_is_better":
        if hi < -sesoi:
            return "supported"
        if lo > -sesoi:
            return "not_supported"
    else:
        if lo > sesoi:
            return "supported"
        if hi < sesoi:
            return "not_supported"
    return "inconclusive"


def decide_equivalence(boot: Mapping[str, object], margin: float) -> str:
    """Is the paired difference inside `[-margin, +margin]`?

    Required by V0-1: the no-decay control must be shown equivalent to zero, and
    failing to detect a difference is not evidence of equivalence.
    """
    if margin <= 0:
        raise ValueError("margin must be a positive magnitude")
    lo, hi = boot.get("ci_lo"), boot.get("ci_hi")
    if lo is None or hi is None or lo != lo or hi != hi:
        return "inconclusive"
    if -margin <= float(lo) and float(hi) <= margin:
        return "equivalent"
    if float(lo) > margin or float(hi) < -margin:
        return "different"
    return "inconclusive"


def holm(pvalues: Mapping[str, float]) -> Dict[str, float]:
    """Holm-Bonferroni adjusted p-values. Controls familywise error without
    assuming independence, which the correlated contrasts here do not have."""
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted: Dict[str, float] = {}
    running = 0.0
    for i, (key, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * float(p)))
        adjusted[key] = running
    return adjusted
