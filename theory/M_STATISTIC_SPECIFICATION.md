# M-Statistic Specification (Sprint 1.3 companion)

**Status:** Proposed (companion to Sprint 1.3 forced-growth preregistration)
**Author scope:** Resolves three previously unaddressed problems with `M = NMI(learned, true) - NMI(learned, C3-shuffled)`:
  (1) cluster-labeling identifiability, (2) C3 reference conflates temporal and static
  structure, (3) orphaning of M from the primary outcome DV-a.

---

## 1. Definitions and notation

Let:
- `z_t \in {1,...,K}` for `t = 1,...,T` be the true latent state sequence (K = ground-truth number of latent states, preregistered per environment).
- `\hat{z}_t \in {1,...,K'}` be the inferred sequence produced by the predictor after training, where `K'` is the learned model order. **K and K' may differ.**
- `\tilde{z}_t` be the reference null sequence from the C3 control (shuffled inputs, §3.2).
- `H(P)` = Shannon entropy in nats, `I(P;Q)` = mutual information, `NMI = 2 I / (H(P) + H(Q))` (arithmetic-mean normalization, the only form that is symmetric and bounded in [0,1] for differing support sizes — geometric-mean NMI is undefined when either marginal entropy is zero).

All information quantities are estimated using the **plug-in estimator with Miller-Madow bias correction** at order 1/K_eff, where K_eff = min(K, K', \tilde{K}) is the effective alphabet size. Bias-corrected estimates are reported with bootstrap 95% CIs (B=2000, block size = sqrt(T) to preserve short-range temporal dependence).

## 2. Cluster alignment (resolves failure mode 1)

NMI is invariant to permutation of cluster labels, but the **learned→true correspondence** is not, because K' may differ from K. We preregister the following protocol:

**Primary alignment: optimal permutation via Hungarian algorithm.**
1. Compute the K' x K contingency table `N_{ij} = |{t : \hat{z}_t = i, z_t = j}|`.
2. If `K' = K`: solve the assignment problem maximizing `sum_{i} N_{i, pi(i)}` over permutations pi. This is the standard label-matching step. Report NMI on the aligned label sequences.
3. If `K' != K`: pad the smaller side to `max(K, K')` with all-zero rows/columns, solve the same assignment, and use only the matched `min(K, K')` diagonal entries in subsequent computation. Report both the raw NMI and the truncated NMI as supplementary.

**Fallback metric: Adjusted Rand Index (ARI).** ARI is invariant to K != K' *without* requiring an alignment step, because it operates on pairwise co-assignment rather than label identity. ARI is preregistered as the **primary metric** if and only if K' != K occurs in > 25% of seeds; otherwise Hungarian-aligned NMI is primary.

**Both metrics are reported in every seed regardless**; the primary/secondary designation is preregistered, not post-hoc.

## 3. Null reference: replacing the raw C3 sequence (resolves failure mode 2)

The original `NMI(learned, C3-shuffled)` is a poor reference because C3 destroys only *temporal* structure; if the true generator has a heavy marginal, learned and shuffled look artificially similar in the per-position marginal sense, and their NMI can be small for reasons unrelated to temporal learning.

**Preregistered null construction:** A *temporal* null, not a *marginal* null. Concretely:

> The null sequence `\tilde{z}` is the predictor's own inferred sequence `\hat{z}`, but with **temporal order destroyed within blocks of length L**, where L is chosen to be the median run-length of `\hat{z}` (estimated from the same seed). Block-shuffling within L-preserving runs preserves marginal and short-range statistics while destroying the long-range temporal structure that the emergence claim is about.

This gives a sharper test: `M` measures how much of the *learned* temporal structure is shared with the *true* temporal structure, above what the predictor can explain by its own marginals and short-range runs.

Equivalently, we can state `M` as:

  `M = I(\hat{z}; z) - I(\hat{z}; \tilde{z})`

where `\tilde{z}` is the block-shuffled null above. This is a *self-normalized* emergence statistic: it asks whether the learned sequence shares more information with truth than with a temporally-scrambled version of itself.

## 4. Pre-registered relationship to DV-a (resolves failure mode 3)

The primary outcome is held-out log-likelihood (DV-a). M is a secondary outcome. The two are not redundant, but they must be connected by a preregistered relationship, or M is a free-floating number.

**Preregistered joint hypothesis (H2):**

> If internal growth improves predictive learning, then seeds with higher M (better latent recovery) will also have higher held-out log-likelihood (DV-a), conditional on environment class. Specifically, the partial Spearman correlation between M and DV-a across the n=22 seeds, controlling for environment K and noise sigma, satisfies `rho(M, DV-a | K, sigma) > 0`, tested one-sided at alpha = 0.025.

**Preregistered null (H2_0):** `rho <= 0`.

**Rationale:** This is the minimum claim that makes M scientifically load-bearing. Without this preregistration, a positive M with zero DV-a effect (the current state, per `LIMITATIONS.md` and `FINAL_PUBLICATION_CLAIM.md`) is unfalsifiable. With it, M is either predictive of generalization or it isn't, and the preregistration commits us to that test.

**Secondary preregistered analysis:** Decompose M into
  - M_within = NMI between learned and true, *within matched label clusters* (using the Hungarian alignment from §2), and
  - M_across = NMI attributable to cluster-cardinality match (K' vs K).
Report both. A growth effect that operates only through M_across (more clusters) without improving M_within is consistent with the DV-a null.

## 5. Reporting requirements

Per `NX\publication_infrastructure\checklists\master_publication_checklist.md` and the figure specs in `figure_table_specifications.md`, every M-related figure or table must include:

1. **Per-seed Hungarian alignment matrix** (K' x K, with matched entries highlighted). This is what makes the alignment auditable.
2. **NMI with and without alignment**, and ARI, in the same table. A reviewer should be able to verify the alignment by reading off the contingency table.
3. **Block-shuffled null** (from §3) and the raw C3 null (preserved for backwards compatibility) in adjacent columns.
4. **The M vs DV-a scatter with the preregistered Spearman test** (from §4), not just the marginal M.
5. **Bootstrap CIs** on every M estimate, not standard errors from a single seed.

## 6. What this specification does NOT change

- The MDL trigger logic itself. That is governed by `core/mdl/mdl_growth.py` and is unchanged here.
- The environment generator (`NonlinearLatentEnvironment`).
- The primary outcome DV-a (held-out log-likelihood) or its preregistered test (Holm-Bonferroni across 5 hypotheses in Sprint 1.3).
- The capacity k-grid (1, 2, 4, 8) for C2f.

## 7. Preregistration addendum text (drop-in)

> **H2 (secondary, pre-registered).** Internal growth that recovers latent structure will also improve held-out predictive performance. Operationalization: across the n=22 seeds of Sprint 1.3, partial Spearman correlation between the emergence statistic M (defined in §1-3 above) and held-out log-likelihood (DV-a), conditional on environment K and noise sigma, is positive (one-sided alpha = 0.025). M is computed with Hungarian alignment (primary) and Adjusted Rand Index (secondary), against a block-shuffled temporal null. Failure to reject H2_0 is treated as a negative result for the emergence claim, not a deferred sensitivity.

---

*End of specification.*
