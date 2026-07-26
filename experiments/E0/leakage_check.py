"""Offline nonlinearity verification for E0 environment.

Verifies that a linear/fixed-capacity predictor cannot recover the latent
structure from the nonlinear environment. If linear probe recovery is at
or near chance level, the environment passes the nonlinearity check.

This addresses assumption I3: the environment must be rich enough to
require non-trivial structure yet learnable, and not linearly trivial.

Reference: PROGRAM_D_CANONICAL.md §7 (E0), F1
           SCIENTIFIC_EXECUTION_SPEC.md §E0 (Failure conditions)
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score


def check_linear_recovery(
    observations: np.ndarray,
    true_latents: np.ndarray,
    n_train: int = 2000,
    n_test: int = 1000,
) -> Dict[str, float]:
    """Test whether a linear classifier can recover latent states from observations.

    Fits a multinomial logistic regression (no hidden layers, no nonlinear
    features) to predict latent states from observation vectors. If the
    linear probe's accuracy is near chance (1/K), the nonlinearity is
    verified.

    Parameters
    ----------
    observations : np.ndarray
        Observation vectors, shape (N, D).
    true_latents : np.ndarray
        True latent state indices, shape (N,).
    n_train : int
        Number of samples to use for training.
    n_test : int
        Number of samples to use for testing.

    Returns
    -------
    dict with keys:
        accuracy: float — linear probe accuracy on test set
        chance: float — chance-level accuracy (1/K)
        nmi: float — normalized mutual info between pred and true
        adj_rand: float — adjusted rand index
        is_nonlinear: bool — True if accuracy < chance + 0.1
    """
    K = len(np.unique(true_latents))
    chance = 1.0 / K

    total = len(observations)
    if total < n_train + n_test:
        n_train = total // 2
        n_test = total - n_train

    X_train = observations[:n_train]
    y_train = true_latents[:n_train]
    X_test = observations[n_train : n_train + n_test]
    y_test = true_latents[n_train : n_train + n_test]

    # Fit logistic regression (linear classifier)
    # Use One-vs-Rest or multinomial based on sklearn version
    clf = LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
        random_state=42,
    )
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    accuracy = float(np.mean(y_pred == y_test))
    nmi = float(normalized_mutual_info_score(y_test, y_pred))
    ari = float(adjusted_rand_score(y_test, y_pred))

    # Environment passes nonlinearity check if accuracy is within 0.1 of chance
    # (or more conservatively, if the linear model fails to significantly
    #  outperform chance)
    margin = 0.10
    is_nonlinear = accuracy < (chance + margin)

    return {
        "accuracy": accuracy,
        "chance": chance,
        "nmi": nmi,
        "adj_rand": ari,
        "is_nonlinear": is_nonlinear,
        "n_train": n_train,
        "n_test": n_test,
        "margin": margin,
    }


def check_environment_nonlinearity(
    observations: np.ndarray,
    true_latents: np.ndarray,
) -> Dict[str, float]:
    """Comprehensive nonlinearity check with multiple metrics.

    Returns a dict with:
    - linear_probe: result of linear recovery check
    - unique_states: number of unique latent states detected
    - state_frequencies: histogram of latent state counts
    """
    result = check_linear_recovery(observations, true_latents)

    # Additional diagnostics
    unique, counts = np.unique(true_latents, return_counts=True)

    result["unique_states"] = len(unique)
    result["state_frequencies"] = {int(s): int(c) for s, c in zip(unique, counts)}

    return result


def generate_nonlinearity_certificate(
    observations: np.ndarray,
    true_latents: np.ndarray,
    env_params: Optional[Dict] = None,
) -> str:
    """Generate a human-readable nonlinearity certificate.

    Returns a [FACT]-tagged markdown report.
    """
    result = check_environment_nonlinearity(observations, true_latents)

    lines = [
        "# E0 Environment Nonlinearity Certificate",
        "",
        "**[FACT]** Offline verification that the environment is not linearly separable.",
        "",
        f"## Environment",
    ]

    if env_params:
        for k, v in env_params.items():
            lines.append(f"- **{k}**: {v}")

    lines.extend(
        [
            "",
            f"## Linear Probe Recovery",
            f"- **Accuracy**: {result['accuracy']:.4f}",
            f"- **Chance level**: {result['chance']:.4f} (1/K)",
            f"- **Margin**: ±{result['margin']}",
            f"- **NMI**: {result['nmi']:.4f}",
            f"- **Adjusted Rand Index**: {result['adj_rand']:.4f}",
            f"- **Training samples**: {result['n_train']}",
            f"- **Test samples**: {result['n_test']}",
            "",
        ]
    )

    if result["is_nonlinear"]:
        lines.append("**[FACT] Verdict: ENVIRONMENT IS NONLINEAR.**")
        lines.append(
            f"Linear probe accuracy ({result['accuracy']:.4f}) is within "
            f"{result['margin']} of chance ({result['chance']:.4f}). "
            "A linear/fixed-capacity predictor cannot recover the latent structure. "
            "Assumption I3 is satisfied for this environment."
        )
    else:
        lines.append("**[HYPOTHESIS] Verdict: ENVIRONMENT MAY BE LINEARLY RECOVERABLE.**")
        lines.append(
            f"Linear probe accuracy ({result['accuracy']:.4f}) exceeds "
            f"chance + margin ({result['chance'] + result['margin']:.4f}). "
            "The environment may not require nonlinear capacity growth. "
            "Either increase nonlinearity or reduce observation dimension."
        )

    lines.extend(
        [
            "",
            f"## State Distribution",
            f"- **Unique states**: {result['unique_states']}",
            f"- **State frequencies**: {result['state_frequencies']}",
            "",
            "---",
            "*Generated by experiments/E0/leakage_check.py*",
        ]
    )

    return "\n".join(lines)
