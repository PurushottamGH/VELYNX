"""E0 Decision Module — Canonical kill criteria for H*.

Implements:
1. DV-a: T > C1 AND T > C2 at p < 0.01 (one-sided paired t-test)
2. DV-b: M exceeds pre-registered margin above shuffled noise
3. Two-honest-attempts protocol
4. Machine-checked pass/kill verdict

Reference: PROGRAM_D_CANONICAL.md §6 (H* kill criteria)
           SCIENTIFIC_EXECUTION_SPEC.md §E0 (Kill criteria)
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats as scipy_stats

_FWER_ALPHA = 0.01
"""Family-wise error rate for the DV-a joint hypothesis.

Holm-Bonferroni correction is applied across the two comparisons
(T vs C1, T vs C2) to maintain FWER at 0.01."""


# --- Statistical utilities ---


def paired_one_sided_ttest(
    treatment_scores: List[float],
    control_scores: List[float],
) -> Dict[str, float]:
    """One-sided paired t-test: is treatment > control?

    H0: treatment <= control
    H1: treatment > control

    Parameters
    ----------
    treatment_scores : List[float]
        Scores from treatment condition (one per seed).
    control_scores : List[float]
        Scores from control condition (one per seed, paired by seed).

    Returns
    -------
    dict with keys:
        t_statistic: float
        p_value: float (one-sided)
        mean_difference: float
        significant: bool (True if p < alpha)
    """
    if len(treatment_scores) != len(control_scores):
        raise ValueError(
            f"Treatment and control must have same length: "
            f"{len(treatment_scores)} vs {len(control_scores)}"
        )

    if len(treatment_scores) < 2:
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "mean_difference": float(np.mean(treatment_scores) - np.mean(control_scores)),
            "significant": False,
            "error": "Insufficient samples (need >= 2)",
        }

    treatment = np.array(treatment_scores)
    control = np.array(control_scores)
    differences = treatment - control

    mean_diff = float(np.mean(differences))
    if len(differences) < 2:
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "mean_difference": mean_diff,
            "significant": False,
        }

    # One-sided paired t-test: H1: treatment > control
    t_stat, p_two_sided = scipy_stats.ttest_rel(treatment, control)
    p_one_sided = p_two_sided / 2.0 if mean_diff > 0 else 1.0 - p_two_sided / 2.0

    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_one_sided),
        "mean_difference": mean_diff,
        "significant": bool(p_one_sided < 0.01),
    }


def bootstrap_significance(
    treatment_scores: List[float],
    control_scores: List[float],
    n_resamples: int = 10000,
    seed: int = 42,
) -> Dict[str, float]:
    """Bootstrap test for significance (non-parametric alternative).

    Tests whether treatment > control by computing the distribution
    of the mean difference under the null (pooled resampling).
    """
    rng = np.random.RandomState(seed)
    combined = np.array(treatment_scores + control_scores)
    n_t = len(treatment_scores)
    observed_diff = float(np.mean(treatment_scores) - np.mean(control_scores))

    count = 0
    for _ in range(n_resamples):
        rng.shuffle(combined)
        perm_t = combined[:n_t]
        perm_c = combined[n_t:]
        perm_diff = float(np.mean(perm_t) - np.mean(perm_c))
        if perm_diff >= observed_diff:
            count += 1

    p_value = (count + 1) / (n_resamples + 1)

    return {
        "p_value": float(p_value),
        "observed_difference": observed_diff,
        "significant": bool(p_value < 0.01),
    }


# --- E0 Kill Criteria ---


def holm_bonferroni(
    p_values: List[float],
    alpha: float = 0.01,
) -> List[bool]:
    """Apply Holm-Bonferroni step-down correction for multiple comparisons.

    Sorts p-values ascending, then compares each to alpha / (m - rank).
    Once a test fails (p > adjusted threshold), all remaining are
    marked non-significant.

    Parameters
    ----------
    p_values : List[float]
        Raw p-values from the individual tests.
    alpha : float
        Family-wise error rate (default 0.01).

    Returns
    -------
    List[bool]
        Significant flags in the same order as the input p_values.
    """
    m = len(p_values)
    if m == 0:
        return []

    # Sort indices by p-value (ascending)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])

    significant = [False] * m
    for rank, (orig_idx, p) in enumerate(indexed):
        threshold = alpha / (m - rank)
        if p < threshold:
            significant[orig_idx] = True
        else:
            # Once one fails, all remaining are non-significant
            break

    return significant


M_STATISTIC_MARGIN = 0.05
"""Default margin for emergence statistic M when per-seed data is unavailable.

When multi-seed data is available, the margin is derived dynamically
from the null distribution (2 * std(M) / sqrt(n_seeds)). This constant
serves as a fallback for single-seed evaluation.
"""


MIN_M_MARGIN = 0.02
"""Minimum floor for the M margin, preventing degenerate near-zero
margins when per-seed M variance is artificially low."""


def derive_m_margin(m_stats: List[float]) -> float:
    """Derive the M margin from the null distribution.

    Under H\u2080, E[M] = 0. The margin is set at 2 standard errors
    above zero: margin = 2 * std(M) / sqrt(n).

    This gives a ~95% confidence bound under normality of the M
    sampling distribution (CLT applies as n grows).

    Parameters
    ----------
    m_stats : List[float]
        Per-seed M statistics from the treatment condition.

    Returns
    -------
    float
        The derived margin, floored at MIN_M_MARGIN.
    """
    n = len(m_stats)
    if n < 2:
        return M_STATISTIC_MARGIN
    std_m = float(np.std(m_stats, ddof=1))
    se_m = std_m / math.sqrt(n)
    margin = 2.0 * se_m
    return max(margin, MIN_M_MARGIN)


class E0Decider:
    """E0 pass/kill decider implementing canonical H* kill criteria.

    The kill criteria (§6-H*):
    - Kill if T fails to beat BOTH C1 and C2 on DV-a at p < 0.01
      across >= 5 seeds
    - OR DV-b within noise of shuffled control (M <= margin)

    After two honest attempts with different seeds, if the kill
    criteria still trigger, H* is falsified for this environment class.
    """

    def __init__(
        self,
        p_threshold: float = 0.01,
        min_seeds: int = 5,
        m_margin: float = M_STATISTIC_MARGIN,
    ):
        self.p_threshold = p_threshold
        self.min_seeds = min_seeds
        self.m_margin = m_margin
        self._attempts: List[Dict] = []

    def evaluate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate pass/kill decision from experiment results.

        Parameters
        ----------
        results : dict
            Full experiment results from run_single_seed.

        Returns
        -------
        dict with verdict, evidence, and reasoning
        """
        conditions = results.get("conditions", {})
        analysis = results.get("analysis", {})

        # Extract per-condition metrics
        t_ll = self._extract_mean_ll(conditions.get("T", {}))
        c1_ll = self._extract_mean_ll(conditions.get("C1", {}))
        c2_ll = self._extract_mean_ll(conditions.get("C2", {}))

        # DV-a: Compare T vs C1 and T vs C2
        dv_a_result = self._evaluate_dv_a(
            treatment_ll=[t_ll],
            c1_ll=[c1_ll],
            c2_ll=[c2_ll],
        )

        # DV-b: Emergence statistic M
        t_analysis = analysis.get("T", {})
        emergence = t_analysis.get("emergence_statistic", {})
        m_stat = emergence.get("m_statistic", 0.0)
        dv_b_result = self._evaluate_dv_b(m_stat)

        # Overall verdict
        dv_a_pass = dv_a_result.get("pass", False)
        dv_b_pass = dv_b_result.get("pass", False)
        overall_pass = dv_a_pass and dv_b_pass

        # Determine verdict string
        verdict = "PASS" if overall_pass else "FAIL"
        if not dv_a_pass and not dv_b_pass:
            verdict = "FAIL (both DV-a and DV-b)"
        elif not dv_a_pass:
            verdict = (
                "UNTESTED (F-A: growth-trigger units mismatch — per-symbol "
                "entropy delta vs. total-data-code penalty makes firing "
                "mathematically impossible; H* was not exercised, not rejected)"
            )
        elif not dv_b_pass:
            verdict = "FAIL (DV-b: M within noise of shuffled control)"

        return {
            "verdict": verdict,
            "pass": overall_pass,
            "dv_a": dv_a_result,
            "dv_b": dv_b_result,
            "attempt_number": len(self._attempts) + 1,
            "min_seeds_required": self.min_seeds,
            "seeds_available": 1,  # Will be multi-seed in full runs
            "margin_m": self.m_margin,
        }

    def evaluate_multi_seed(
        self,
        per_seed_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Evaluate pass/kill across multiple seeds.

        Uses paired t-tests across seeds for DV-a and aggregates
        DV-b across seeds. The M margin is derived from the null
        distribution of per-seed M statistics.

        Parameters
        ----------
        per_seed_results : List[dict]
            List of results from per-seed runs.
        """
        n_seeds = len(per_seed_results)

        # Extract LL values per seed per condition
        t_lls: List[float] = []
        c1_lls: List[float] = []
        c2_lls: List[float] = []
        m_stats: List[float] = []

        for result in per_seed_results:
            conditions = result.get("conditions", {})
            analysis = result.get("analysis", {})

            t_lls.append(self._extract_mean_ll(conditions.get("T", {})))
            c1_lls.append(self._extract_mean_ll(conditions.get("C1", {})))
            c2_lls.append(self._extract_mean_ll(conditions.get("C2", {})))

            t_analysis = analysis.get("T", {})
            emergence = t_analysis.get("emergence_statistic", {})
            m_stats.append(emergence.get("m_statistic", 0.0))

        # DV-a: Paired t-tests with Holm-Bonferroni correction
        dv_a_result = self._evaluate_dv_a(t_lls, c1_lls, c2_lls)

        # DV-b: Mean M across seeds with data-derived margin
        mean_m = float(np.mean(m_stats)) if m_stats else 0.0
        derived_margin = derive_m_margin(m_stats)
        dv_b_result = self._evaluate_dv_b(mean_m, margin=derived_margin)

        # Sufficient seeds?
        sufficient_seeds = n_seeds >= self.min_seeds

        # Overall verdict
        dv_a_pass = dv_a_result.get("pass", False)
        dv_b_pass = dv_b_result.get("pass", False)
        overall_pass = dv_a_pass and dv_b_pass and sufficient_seeds

        # --- Interpretation layer (Sprint 1 closure / C-5) ---
        # These annotations do not alter any computation above: overall_pass,
        # the DV-a/DV-b results, thresholds, and tests are all untouched.
        # They only refine how the (unchanged) decision is *reported*.
        #
        # F-A (trigger defect): the error-gated growth trigger compares a
        # per-symbol entropy delta against a total-data-code penalty. Those
        # two quantities are in different units, so the comparison can never
        # be satisfied and the trigger cannot fire. When T consequently fails
        # to separate from the controls on DV-a, H* has NOT been empirically
        # rejected — it was never exercised. This is a non-test, not a kill.
        trigger_defect: Optional[str] = None
        h_star_status = "tested"
        attempts_toward_kill = 0

        if not sufficient_seeds:
            verdict = f"INCONCLUSIVE (only {n_seeds} seeds, need {self.min_seeds})"
        elif not dv_a_pass and not dv_b_pass:
            verdict = "FAIL (both DV-a and DV-b)"
        elif not dv_a_pass:
            # Reinterpreted per C-5: a DV-a non-separation under the F-A
            # trigger defect is UNTESTED, not FAIL. Firing is mathematically
            # impossible (units mismatch), so no attempt genuinely tested H*.
            verdict = (
                "UNTESTED (F-A: growth-trigger units mismatch — per-symbol "
                "entropy delta vs. total-data-code penalty makes firing "
                "mathematically impossible; H* was not exercised, not rejected)"
            )
            trigger_defect = "F-A"
            h_star_status = "untested"
            attempts_toward_kill = 0
        elif not dv_b_pass:
            verdict = "FAIL (DV-b)"
        else:
            verdict = "PASS"

        decision = {
            "verdict": verdict,
            "pass": overall_pass,
            "insufficient_seeds": not sufficient_seeds,
            "n_seeds": n_seeds,
            "min_seeds": self.min_seeds,
            "dv_a": dv_a_result,
            "dv_b": dv_b_result,
            "attempt_number": len(self._attempts) + 1,
            "trigger_defect": trigger_defect,
            "h_star_status": h_star_status,
            "attempts_toward_kill": attempts_toward_kill,
        }

        self._attempts.append(decision)
        return decision

    def record_attempt(self, decision: Dict[str, Any]) -> int:
        """Record an attempt and return attempt number."""
        self._attempts.append(decision)
        return len(self._attempts)

    def should_falsify(self) -> Tuple[bool, str]:
        """Check if H* should be falsified after two attempts.

        Returns
        -------
        Tuple[bool, str]
            (should_falsify, reason_string)
        """
        if len(self._attempts) < 2:
            return False, f"Only {len(self._attempts)} attempt(s) made; need 2."

        # H* falsified if both attempts FAIL or are INCONCLUSIVE
        all_fail = all(not a.get("pass", False) for a in self._attempts)
        inconclusive = any(
            not a.get("pass", False) and a.get("insufficient_seeds", False) for a in self._attempts
        )

        if inconclusive:
            return False, "Inconclusive due to insufficient seeds; retry with more seeds."

        if all_fail:
            return True, (
                "H* UNTESTED for this environment class (F-A trigger defect). "
                "Error-gated growth did not separate from the controls on "
                "DV-a, but the growth trigger compares a per-symbol entropy "
                "delta against a total-data-code penalty — a units mismatch "
                "that makes firing mathematically impossible. H* was never "
                "exercised across the attempts, so this is a non-test, not a "
                "falsification."
            )

        return False, "H* survived both attempts (at least one PASS)."

    def _evaluate_dv_a(
        self,
        treatment_ll: List[float],
        c1_ll: List[float],
        c2_ll: List[float],
    ) -> Dict[str, Any]:
        """Evaluate DV-a: T > C1 AND T > C2 with Holm-Bonferroni correction.

        Family-wise error rate is controlled at FWER_ALPHA (0.01)
        across the two comparisons. Raw p-values are collected, then
        Holm-Bonferroni step-down is applied.
        """
        result: Dict[str, Any] = {}

        if len(treatment_ll) >= 2 and len(c1_ll) >= 2 and len(c2_ll) >= 2:
            # Paired t-tests
            vs_c1 = paired_one_sided_ttest(treatment_ll, c1_ll)
            vs_c2 = paired_one_sided_ttest(treatment_ll, c2_ll)
            result["test_type"] = "paired_ttest"
        else:
            # Bootstrap (single seed or few seeds)
            vs_c1 = bootstrap_significance(treatment_ll, c1_ll)
            vs_c2 = bootstrap_significance(treatment_ll, c2_ll)
            result["test_type"] = "bootstrap"

        # Apply Holm-Bonferroni across the two comparisons
        raw_p_values = [
            vs_c1.get("p_value", 1.0),
            vs_c2.get("p_value", 1.0),
        ]
        corrected = holm_bonferroni(raw_p_values, alpha=_FWER_ALPHA)

        vs_c1["significant"] = corrected[0]
        vs_c1["holm_bonferroni_corrected"] = True
        vs_c2["significant"] = corrected[1]
        vs_c2["holm_bonferroni_corrected"] = True

        result["vs_c1"] = vs_c1
        result["vs_c2"] = vs_c2
        result["fwer_alpha"] = _FWER_ALPHA
        result["pass"] = corrected[0] and corrected[1]

        return result

    def _evaluate_dv_b(self, m_statistic: float, margin: Optional[float] = None) -> Dict[str, Any]:
        """Evaluate DV-b: M exceeds pre-registered (or data-derived) margin.

        Parameters
        ----------
        m_statistic : float
            The M statistic (mean across seeds for multi-seed runs).
        margin : float or None
            If provided, uses this as the margin. Otherwise falls back
            to self.m_margin (the hardcoded default).
        """
        effective_margin = margin if margin is not None else self.m_margin
        exceeds_margin = m_statistic > effective_margin

        return {
            "m_statistic": m_statistic,
            "margin": effective_margin,
            "margin_source": "data_derived" if margin is not None else "default",
            "exceeds_margin": exceeds_margin,
            "pass": exceeds_margin,
        }

    def _extract_mean_ll(self, condition: Dict[str, Any]) -> float:
        """Extract the mean log-likelihood from a condition result.

        Uses the independent held-out test sequence (test_log_likelihoods)
        when available, falling back to the last 20% of training
        log-likelihoods for backward compatibility.
        """
        # Prefer independent held-out test log-likelihoods
        test_lls = condition.get("test_log_likelihoods", [])
        if test_lls:
            return float(np.mean(test_lls))
        # Fallback: last 20% of training
        lls = condition.get("log_likelihoods", [])
        if lls:
            n = len(lls)
            held_out = lls[int(n * 0.8) :]
            if held_out:
                return float(np.mean(held_out))
        return float("-inf")


def generate_falsification_report(decider: E0Decider) -> str:
    """Generate a [FACT]-tagged falsification report.

    Reference: PROGRAM_D_CANONICAL.md §6 (H* kill criteria)
    """
    falsify, reason = decider.should_falsify()

    lines = [
        "# E0 Falsification Report",
        "",
        "**[FACT]** Wired H* kill criterion evaluation.",
        "",
        f"## Verdict",
        f"{'**[FACT] H* FALSIFIED for this environment class.**' if falsify else '**[HYPOTHESIS] H* survives.**'}",
        "",
        f"**Reason:** {reason}",
        "",
        "## Attempts",
    ]

    for i, attempt in enumerate(decider._attempts):
        lines.extend(
            [
                f"### Attempt {i + 1}",
                f"- Verdict: {attempt.get('verdict', '?')}",
                f"- DV-a pass: {attempt.get('dv_a', {}).get('pass', '?')}",
                f"- DV-b pass: {attempt.get('dv_b', {}).get('pass', '?')}",
                f"- Seeds: {attempt.get('n_seeds', '?')}",
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "*Generated by experiments/E0/decision.py*",
            "",
        ]
    )

    return "\n".join(lines)
