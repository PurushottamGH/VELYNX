"""E0 Analysis Module — Canonical metrics for emergence discrimination.

Computes:
    DV-a: Held-out predictive log-likelihood (proper scoring rule)
    DV-b: Emergence statistic M = NMI(learned, true) - NMI(learned, shuffled)

Reference: PROGRAM_D_CANONICAL.md §5.3, §5.5
           SCIENTIFIC_EXECUTION_SPEC.md §E0
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.metrics.cluster import normalized_mutual_info_score as sklearn_nmi

from core.emergence.emergence_statistic import compute_nmi


# --- DV-a: Held-out Predictive Log-Likelihood ---


def compute_held_out_log_likelihood(
    train_log_likelihoods: List[float],
    train_latent_states: List[int],
    test_log_likelihoods: Optional[List[float]] = None,
    test_latent_states: Optional[List[int]] = None,
) -> Dict[str, float]:
    """Compute held-out predictive log-likelihood (DV-a).

    The canonical proper scoring loss: L = -log P_θ(x_{t+1} | x_{≤t}).

    Uses the last 20% of the training sequence as a held-out set
    unless explicit test data is provided.

    Parameters
    ----------
    train_log_likelihoods : List[float]
        Per-step log-likelihoods from the training run.
    train_latent_states : List[int]
        True latent states for each step (for reference).
    test_log_likelihoods : List[float] or None
        Explicit held-out log-likelihoods (if provided).
    test_latent_states : List[int] or None
        Held-out latent states.

    Returns
    -------
    dict with keys:
        mean_log_likelihood: float — mean log P_θ (higher is better)
        mean_log_loss: float — mean -log P_θ (lower is better)
        held_out_fraction: float — fraction of data used as held-out
        n_held_out: int — number of held-out samples
    """
    if test_log_likelihoods is not None and len(test_log_likelihoods) > 0:
        held_out_ll = test_log_likelihoods
    else:
        # Use last 20% of training as held-out
        n_train = len(train_log_likelihoods)
        split = int(n_train * 0.8)
        held_out_ll = train_log_likelihoods[split:]

    if not held_out_ll:
        return {
            "mean_log_likelihood": float("-inf"),
            "mean_log_loss": float("inf"),
            "held_out_fraction": 0.0,
            "n_held_out": 0,
        }

    mean_ll = float(np.mean(held_out_ll))
    mean_loss = -mean_ll

    return {
        "mean_log_likelihood": mean_ll,
        "mean_log_loss": mean_loss,
        "held_out_fraction": len(held_out_ll) / max(len(train_log_likelihoods), 1),
        "n_held_out": len(held_out_ll),
    }


# --- DV-b: Emergence Statistic M ---


def compute_emergence_statistic(
    treatment_latent_states: List[int],
    true_latent_states: List[int],
    shuffled_latent_states: Optional[List[int]] = None,
) -> Dict[str, float]:
    """Compute the null-referenced emergence statistic M (DV-b).

    M = NMI(learned_partition, true_latent) - NMI(learned_partition, shuffled_input)

    Where E[M | H₀] = 0 by construction (the null-reference operationalizes I2).

    If shuffled_latent_states is not provided, computes the NMI against
    a random partition (theoretical null).

    Reference: PROGRAM_D_CANONICAL.md §5.5

    Parameters
    ----------
    treatment_latent_states : List[int]
        Latent states discovered by the treatment condition (T).
    true_latent_states : List[int]
        True latent states from the environment generator.
    shuffled_latent_states : List[int] or None
        Latent states discovered by the shuffled-input control (C3).
        If None, uses a random partition baseline.

    Returns
    -------
    dict with keys:
        m_statistic: float — M = NMI(learned, true) - NMI(learned, shuffled)
        nmi_learned_true: float
        nmi_learned_shuffled: float
        null_expected: float — should be ~0.0 for valid null
    """
    # Ensure same length
    min_len = min(
        len(treatment_latent_states),
        len(true_latent_states),
    )
    if shuffled_latent_states is not None:
        min_len = min(min_len, len(shuffled_latent_states))

    if min_len < 2:
        return {
            "m_statistic": 0.0,
            "nmi_learned_true": 0.0,
            "nmi_learned_shuffled": 0.0,
            "null_expected": 0.0,
            "error": "Insufficient data for NMI computation",
        }

    t_states = treatment_latent_states[:min_len]
    true_states = true_latent_states[:min_len]

    # NMI(learned, true)
    nmi_true = compute_nmi(true_states, t_states)
    if math.isnan(nmi_true) or math.isinf(nmi_true):
        nmi_true = 0.0

    # NMI(learned, shuffled)
    if shuffled_latent_states is not None:
        s_states = shuffled_latent_states[:min_len]
        nmi_shuffled = compute_nmi(s_states, t_states)
    else:
        # Generate random partition as null
        rng = np.random.RandomState(42)
        random_states = rng.randint(
            0, max(2, len(set(t_states))),
            size=min_len,
        ).tolist()
        nmi_shuffled = compute_nmi(random_states, t_states)

    if math.isnan(nmi_shuffled) or math.isinf(nmi_shuffled):
        nmi_shuffled = 0.0

    m_stat = nmi_true - nmi_shuffled

    return {
        "m_statistic": float(m_stat),
        "nmi_learned_true": float(nmi_true),
        "nmi_learned_shuffled": float(nmi_shuffled),
        "null_expected": 0.0,
    }


# --- Aggregate analysis across conditions ---


def analyze_conditions(
    conditions: Dict[str, Dict],
) -> Dict[str, Dict]:
    """Run DV-a and DV-b analysis across all conditions.

    Uses independently-generated held-out sequences (via
    test_log_likelihoods) when available, falling back to the
    last 20% of training for backward compatibility.

    Parameters
    ----------
    conditions : dict
        Dictionary of condition results from run_single_seed.
        Keys: "T", "C1", "C2", "C3"

    Returns
    -------
    dict with per-condition analysis results
    """
    analysis: Dict[str, Dict] = {}

    for cond_name, cond_result in conditions.items():
        lls = cond_result.get("log_likelihoods", [])
        latents = cond_result.get("latent_states", [])
        test_lls = cond_result.get("test_log_likelihoods", [])

        result: Dict = {}

        # DV-a: Held-out log-likelihood
        # Use independent held-out sequence if available
        if test_lls:
            held_out = compute_held_out_log_likelihood(
                train_log_likelihoods=lls,
                train_latent_states=latents,
                test_log_likelihoods=test_lls,
                test_latent_states=None,
            )
            result["held_out_ll"] = held_out
        elif lls:
            held_out = compute_held_out_log_likelihood(
                train_log_likelihoods=lls,
                train_latent_states=latents,
            )
            result["held_out_ll"] = held_out
        else:
            result["held_out_ll"] = {
                "mean_log_likelihood": 0.0,
                "mean_log_loss": 0.0,
                "n_held_out": 0,
            }

        # DV-b: Emergence statistic (only meaningful for T)
        if cond_name == "T":
            # TRUE LATENTS MUST COME FROM ENVIRONMENT GENERATOR ONLY.
            # This is verified by the condition runners which store
            # env.step() output in 'true_latent_states' and predictor
            # inferences in 'latent_states' as separate variables.
            # Never fall back to predictor-derived states.
            true_latents = cond_result.get("true_latent_states")
            if true_latents is None:
                raise KeyError(
                    "'true_latent_states' missing from condition T results. "
                    "The emergence statistic M requires ground truth from the "
                    "environment generator, not from the predictor."
                )

            # Get shuffled latent states from C3 if available
            shuffled_latents = None
            if "C3" in conditions:
                shuffled_latents = conditions["C3"].get("latent_states", [])

            emergence = compute_emergence_statistic(
                treatment_latent_states=latents,
                true_latent_states=true_latents,
                shuffled_latent_states=shuffled_latents,
            )
            result["emergence_statistic"] = emergence

        # Growth summary
        result["growth_events"] = len(cond_result.get("growth_events", []))
        result["final_capacity"] = cond_result.get("final_capacity", 0)
        if test_lls:
            result["held_out_type"] = "independent_sequence"
            result["n_test_steps"] = len(test_lls)
        elif lls:
            result["held_out_type"] = "last_20_percent"
        if lls:
            result["recent_mean_ll"] = float(np.mean(lls[-1000:])) if len(lls) >= 1000 else float(np.mean(lls))
            result["recent_mean_loss"] = -result["recent_mean_ll"]

        analysis[cond_name] = result

    return analysis


def compute_dv_a_summary(
    condition_analyses: Dict[str, Dict],
) -> Dict[str, float]:
    """Compute comparative summary of DV-a across conditions.

    Returns a dict with the mean held-out log-likelihood per condition
    and the deltas between treatment and controls.
    """
    summary: Dict[str, float] = {}

    for cond_name, analysis in condition_analyses.items():
        held_out = analysis.get("held_out_ll", {})
        summary[f"{cond_name}_mean_ll"] = held_out.get("mean_log_likelihood", 0.0)
        summary[f"{cond_name}_mean_loss"] = held_out.get("mean_log_loss", 0.0)

    # Deltas: T - C1, T - C2
    t_ll = summary.get("T_mean_ll", 0.0)
    c1_ll = summary.get("C1_mean_ll", 0.0)
    c2_ll = summary.get("C2_mean_ll", 0.0)
    summary["delta_T_minus_C1"] = t_ll - c1_ll
    summary["delta_T_minus_C2"] = t_ll - c2_ll

    return summary


def compute_dv_b_summary(
    condition_analyses: Dict[str, Dict],
) -> Dict[str, float]:
    """Compute comparative summary of DV-b across conditions.

    Returns the emergence statistic M for the treatment condition.
    """
    t_analysis = condition_analyses.get("T", {})
    emergence = t_analysis.get("emergence_statistic", {})
    m_stat = emergence.get("m_statistic", 0.0)

    return {
        "M_statistic": m_stat,
        "nmi_true": emergence.get("nmi_learned_true", 0.0),
        "nmi_shuffled": emergence.get("nmi_learned_shuffled", 0.0),
    }


def _safe_float(value, fmt: str = ".4f") -> str:
    """Format a value as float, returning '?' if not a number."""
    if isinstance(value, (int, float)):
        return f"{value:{fmt}}"
    return str(value)


def generate_e0_report(analysis: Dict[str, Dict]) -> str:
    """Generate a human-readable [FACT]-tagged E0 analysis report."""
    lines = [
        "# E0 Analysis Report",
        "",
        "**[FACT]** Canonical Emergence-vs-Injection Discrimination.",
        "",
        "## Results Summary",
        "",
    ]

    for cond_name in ["T", "C1", "C2", "C3"]:
        cond = analysis.get(cond_name, {})
        held_out = cond.get("held_out_ll", {})
        emergence = cond.get("emergence_statistic", {})

        lines.append(f"### Condition {cond_name}")
        lines.append(f"- Growth events: {cond.get('growth_events', '?')}")
        lines.append(f"- Final capacity: {cond.get('final_capacity', '?')}")
        lines.append(f"- Mean held-out LL: {_safe_float(held_out.get('mean_log_likelihood', '?'))}")
        lines.append(f"- Mean held-out loss: {_safe_float(held_out.get('mean_log_loss', '?'))}")
        if emergence:
            lines.append(f"- M statistic: {_safe_float(emergence.get('m_statistic', '?'))}")
            lines.append(f"- NMI(true): {_safe_float(emergence.get('nmi_learned_true', '?'))}")
            lines.append(f"- NMI(shuffled): {_safe_float(emergence.get('nmi_learned_shuffled', '?'))}")
        lines.append("")

    # Comparative
    dv_a = compute_dv_a_summary(analysis)
    dv_b = compute_dv_b_summary(analysis)

    lines.append("## Comparative Analysis")
    lines.append(f"- Δ(T - C1) LL: {dv_a.get('delta_T_minus_C1', 0):.4f}")
    lines.append(f"- Δ(T - C2) LL: {dv_a.get('delta_T_minus_C2', 0):.4f}")
    lines.append(f"- M statistic: {dv_b.get('M_statistic', 0):.4f}")
    lines.append(f"- NMI(true): {dv_b.get('nmi_true', 0):.4f}")
    lines.append(f"- NMI(shuffled): {dv_b.get('nmi_shuffled', 0):.4f}")
    lines.append("")

    return "\n".join(lines)
