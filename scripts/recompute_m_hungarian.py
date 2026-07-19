"""Recompute M (DV-b) with the stricter spec from M_STATISTIC_SPECIFICATION.md.

Applies the following to the n=20 evidence in
evidence/experiment_logs/run_20260704_n20/aggregated_results.json:

1. Hungarian-alignment NMI between T's latent_states and true_latent_states
   (and between T's latent_states and C3's latent_states for the legacy null).
2. ARI (Adjusted Rand Index) as K'!=K fallback metric.
3. Block-shuffled self-null: replaces C3 with a temporally-scrambled version
   of the predictor's own inferred sequence.
4. Reports the recomputed M and the recomputed data-derived margin.
5. Compares to the 0.044 margin reported in 06_statistical_results.md.

Reference: M_STATISTIC_SPECIFICATION.md (Sections 1-3).
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter
from typing import List, Tuple

import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.metrics import adjusted_rand_score


# -------- entropy / NMI primitives (same formulas as core.emergence.emergence_statistic) --------

def _entropy(counts: Counter) -> float:
    n = sum(counts.values())
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / n
            h -= p * math.log(p)
    return h


def _nmi_arithmetic(labels_a: List[int], labels_b: List[int]) -> float:
    """NMI with arithmetic-mean normalization, 2 I / (H(a) + H(b))."""
    n = len(labels_a)
    if n == 0:
        return 0.0
    contingency: dict = {}
    for a, b in zip(labels_a, labels_b):
        contingency[(a, b)] = contingency.get((a, b), 0) + 1
    n_a = Counter(labels_a)
    n_b = Counter(labels_b)
    mi = 0.0
    for (a, b), n_ab in contingency.items():
        if n_ab > 0:
            mi += n_ab / n * math.log(n * n_ab / (n_a[a] * n_b[b]) + 1e-15)
    h_a = _entropy(n_a)
    h_b = _entropy(n_b)
    denom = h_a + h_b
    if denom < 1e-12:
        return 0.0
    return 2.0 * mi / denom


# -------- Hungarian alignment (M_STATISTIC_SPECIFICATION.md §2) --------

def _contingency_table(z: List[int], z_hat: List[int]) -> Tuple[np.ndarray, int, int]:
    """Build K' x K contingency table from true vs learned sequences.

    Rows index learned clusters (0..K'-1), columns index true clusters (0..K-1).
    table[i, j] = number of timesteps where z_hat == i and z == j.
    """
    K = max(z) + 1 if z else 0
    Kp = max(z_hat) + 1 if z_hat else 0
    table = np.zeros((Kp, K), dtype=np.int64)
    for a, b in zip(z_hat, z):
        if 0 <= a < Kp and 0 <= b < K:
            table[a, b] += 1
    return table, Kp, K


def _hungarian_align(table: np.ndarray) -> Tuple[np.ndarray, float]:
    """Solve K'xK assignment maximizing diagonal mass.

    Pads the smaller side to max(K',K) and returns a permutation matrix pi
    such that learned[z_hat=i] is mapped to true[i] = pi[i] for the
    min(K',K) matched pairs. Returns (pi_matrix, matched_mass).
    """
    Kp, K = table.shape
    n = max(Kp, K)
    if n == 0:
        return np.eye(0, dtype=np.int64), 0.0

    cost = np.zeros((n, n), dtype=np.int64)
    cost[:Kp, :K] = -table  # negate for maximization via linear_sum_assignment
    row_ind, col_ind = linear_sum_assignment(cost)
    pi = np.zeros((n, n), dtype=np.int64)
    pi[row_ind, col_ind] = 1
    matched_mass = float(-cost[row_ind, col_ind].sum())
    return pi, matched_mass


def _apply_alignment(z_hat: List[int], z: List[int], pi: np.ndarray) -> List[int]:
    """Apply the learned->true mapping to z_hat, restricted to matched pairs."""
    Kp, K = pi.shape
    mapping = {}
    for i in range(Kp):
        for j in range(K):
            if pi[i, j] == 1:
                mapping[i] = j
    return [mapping.get(v, -1) for v in z_hat]


def _nmi_aligned(z: List[int], z_hat: List[int]) -> Tuple[float, float, int, int]:
    """Hungarian-aligned NMI (arithmetic-mean), padded for K'!=K.

    Returns (nmi, matched_mass, K_true, K_learned).
    """
    table, Kp, K = _contingency_table(z, z_hat)
    if Kp == 0 or K == 0:
        return 0.0, 0.0, K, Kp
    pi, matched_mass = _hungarian_align(table)
    aligned_hat = _apply_alignment(z_hat, z, pi)
    # Truncate to matched pairs only
    filtered = [(a, b) for a, b in zip(z, aligned_hat) if b != -1]
    if not filtered:
        return 0.0, matched_mass, K, Kp
    z_f = [a for a, _ in filtered]
    h_f = [b for _, b in filtered]
    return _nmi_arithmetic(z_f, h_f), matched_mass, K, Kp


# -------- Block-shuffled self-null (M_STATISTIC_SPECIFICATION.md §3) --------

def _block_shuffled(z_hat: List[int], rng: np.random.RandomState) -> List[int]:
    """Block-shuffle z_hat within the median run-length to destroy long-range
    temporal order while preserving marginals and short-range runs."""
    if not z_hat:
        return z_hat
    # Compute run-lengths
    runs = []
    i = 0
    n = len(z_hat)
    while i < n:
        j = i
        while j + 1 < n and z_hat[j + 1] == z_hat[i]:
            j += 1
        runs.append((i, j + 1))
        i = j + 1
    if not runs:
        return z_hat[:]
    run_lens = [b - a for a, b in runs]
    L = max(1, int(np.median(run_lens)))
    # Group consecutive runs into blocks of approximately L steps
    out: List[int] = []
    block: List[int] = []
    block_len = 0
    for a, b in runs:
        seg = z_hat[a:b]
        if block_len + (b - a) > L and block:
            rng.shuffle(block)
            out.extend(block)
            block = []
            block_len = 0
        block.extend(seg)
        block_len += b - a
    if block:
        rng.shuffle(block)
        out.extend(block)
    return out[:n]


# -------- Per-seed recomputation --------

def _per_seed_m(z_true: List[int], z_learned: List[int], z_c3: List[int],
                rng: np.random.RandomState) -> dict:
    """Compute all M variants for a single seed."""
    # Legacy M (unaligned, C3 reference) -- for direct comparison
    nmi_lt_legacy = _nmi_arithmetic(z_true, z_learned)
    nmi_lc3_legacy = _nmi_arithmetic(z_c3, z_learned) if z_c3 else 0.0
    m_legacy = nmi_lt_legacy - nmi_lc3_legacy

    # Hungarian-aligned NMI
    nmi_lt_aligned, _, K, Kp = _nmi_aligned(z_true, z_learned)
    nmi_lc3_aligned, _, _, _ = _nmi_aligned(z_c3, z_learned) if z_c3 else (0.0, 0.0, 0, 0)

    # Block-shuffled self-null
    z_null = _block_shuffled(z_learned, rng)
    nmi_lnull_aligned, _, _, _ = _nmi_aligned(z_null, z_learned)

    # ARI on raw (alignment-free) labels
    ari_lt = adjusted_rand_score(z_true, z_learned)
    ari_lc3 = adjusted_rand_score(z_c3, z_learned) if z_c3 else 0.0
    ari_lnull = adjusted_rand_score(z_null, z_learned)

    return {
        "K_true": int(K),
        "K_learned": int(Kp),
        "K_match": int(K == Kp),
        # Legacy (what 06_statistical_results.md reports)
        "nmi_lt_legacy": nmi_lt_legacy,
        "nmi_lc3_legacy": nmi_lc3_legacy,
        "m_legacy_C3": nmi_lt_legacy - nmi_lc3_legacy,
        # Hungarian-aligned, C3 reference
        "nmi_lt_aligned": nmi_lt_aligned,
        "nmi_lc3_aligned": nmi_lc3_aligned,
        "m_aligned_C3": nmi_lt_aligned - nmi_lc3_aligned,
        # Hungarian-aligned, block-shuffled self-null
        "m_aligned_selfnull": nmi_lt_aligned - nmi_lnull_aligned,
        # ARI variants
        "ari_lt": ari_lt,
        "ari_lc3": ari_lc3,
        "ari_lnull": ari_lnull,
        "ari_diff_C3": ari_lt - ari_lc3,
        "ari_diff_selfnull": ari_lt - ari_lnull,
    }


# -------- main --------

def main(path: str) -> None:
    with open(path, "r") as f:
        data = json.load(f)

    per_seed = data["per_seed_results"]
    print(f"Loaded n={len(per_seed)} seeds from {path}\n")

    rng = np.random.RandomState(20260107)  # preregistered seed

    rows = []
    for i, seed_result in enumerate(per_seed):
        seed = seed_result["seed"]
        conds = seed_result["conditions"]
        z_true = conds["T"]["true_latent_states"]
        z_learned = conds["T"]["latent_states"]
        z_c3 = conds["C3"]["latent_states"]
        row = {"seed": seed}
        row.update(_per_seed_m(z_true, z_learned, z_c3, rng))
        rows.append(row)

    # Aggregate
    legacy = np.array([r["m_legacy_C3"] for r in rows])
    aligned_c3 = np.array([r["m_aligned_C3"] for r in rows])
    aligned_selfnull = np.array([r["m_aligned_selfnull"] for r in rows])
    ari_c3 = np.array([r["ari_diff_C3"] for r in rows])
    ari_selfnull = np.array([r["ari_diff_selfnull"] for r in rows])

    def stats(name: str, arr: np.ndarray) -> Tuple[float, float, float, float]:
        n = len(arr)
        mean = float(np.mean(arr))
        std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
        se = std / math.sqrt(n) if n > 1 else 0.0
        margin = max(2 * se, 0.02)  # same floor as decision.py
        return mean, std, se, margin

    summary = {}
    for label, arr in [
        ("legacy (unaligned, C3 null)", legacy),
        ("hungarian-aligned, C3 null", aligned_c3),
        ("hungarian-aligned, block-shuffled self-null", aligned_selfnull),
        ("ARI, C3 null", ari_c3),
        ("ARI, block-shuffled self-null", ari_selfnull),
    ]:
        m, s, se, margin = stats(label, arr)
        summary[label] = {"mean": m, "std": s, "se": se, "margin": margin}

    # Print per-seed table (compact)
    kp_label = "K'"
    print(f"{'seed':>4} {'K':>3} {kp_label:>3}  {'legacy':>7} {'alg-C3':>7} {'alg-SN':>7} "
          f"{'ARI-C3':>7} {'ARI-SN':>7}")
    for r in rows:
        print(f"{r['seed']:>4} {r['K_true']:>3} {r['K_learned']:>3}  "
              f"{r['m_legacy_C3']:>7.4f} {r['m_aligned_C3']:>7.4f} "
              f"{r['m_aligned_selfnull']:>7.4f} "
              f"{r['ari_diff_C3']:>7.4f} {r['ari_diff_selfnull']:>7.4f}")

    print()
    print(f"{'method':<45} {'mean':>7} {'std':>7} {'SE':>7} {'margin':>7}  pass@{0.044}?")
    REPORTED_MARGIN = 0.0440
    for label, s in summary.items():
        passed = s["mean"] > REPORTED_MARGIN
        flag = "YES" if passed else "NO"
        print(f"{label:<45} {s['mean']:>7.4f} {s['std']:>7.4f} {s['se']:>7.4f} "
              f"{s['margin']:>7.4f}  {flag}")

    # Critical comparison: does the recomputed M (stricter) still exceed 0.044?
    print()
    print("=" * 72)
    print(f"Reported legacy M = 0.2949, margin = 0.0440, DV-b verdict: PASS")
    print("=" * 72)
    for label, s in summary.items():
        verdict = "PASS" if s["mean"] > s["margin"] else "FAIL"
        cross = "PASS" if s["mean"] > REPORTED_MARGIN else "FAIL"
        print(f"  {label:<45} -> DV-b: {verdict}  vs 0.044: {cross}")

    # K-match statistics
    K_match = sum(1 for r in rows if r["K_match"])
    print()
    print(f"K' = K in {K_match}/{len(rows)} seeds (K={rows[0]['K_true']} ground truth)")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else (
        r"C:\Users\Purushottam\Documents\VELYNX\evidence\experiment_logs"
        r"\run_20260704_n20\aggregated_results.json"
    )
    main(path)
