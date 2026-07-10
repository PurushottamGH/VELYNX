# Predictive Processing

This document covers the canonical predictive-processing machinery in `core/`.
It is the scientific center of VELYNX. The substrate is exactly five
primitives (PROGRAM_D_CANONICAL.md Section 5): `x_t`, `P_theta`, `L`, `G`,
`M` - and nothing else. Adding a sixth primitive is forbidden (see
`coding.md`).

## 1. The five primitives and where they live

| Primitive | Meaning                                             | Implementation                                   |
|-----------|-----------------------------------------------------|--------------------------------------------------|
| `x_t`     | Observation stream `x_t in X`                        | provided by experiment datasets (e.g. `experiments/E0/dataset.py`) |
| `P_theta` | Growable predictor `{ P_theta(x_{t+1} | x_<=t) }`    | `core/predictors/base.py`, `core/predictors/dirichlet_markov.py` |
| `L`       | Proper scoring loss `L = -log P_theta(x_{t+1} | x_<=t)` | `core/measurement/proper_scoring.py`             |
| `G`       | MDL growth operator                                 | `core/mdl/mdl_growth.py`                          |
| `M`       | Emergence statistic (null-referenced)               | `core/emergence/emergence_statistic.py` (+ `experiments/E0/analysis.py`) |

`core/__init__.py` is the documented "Single source of truth for all
reusable scientific machinery". The subpackages are `predictors`,
`emergence`, `mdl`, `measurement`, `controls`.

## 2. Responsibilities

- Provide the growable predictor class and its interface.
- Provide the unique proper scoring rule (`L`) that replaces the rejected
  `E = lambda*H + mu*S + nu*A`.
- Provide the MDL growth trigger `G` as a derivation, not a threshold.
- Provide the null-referenced emergence statistic `M` with `E[M | H0] = 0`.
- Provide the experimental controls (C1 fixed-capacity, C2 random-growth,
  C3 shuffled-input) that make H* falsifiable.

## 3. Interfaces

### Predictor ABC (`core/predictors/base.py`)

Every predictor implements this ABC:

- `predict(context) -> List[float]` - forecast the next observation.
- `update(observation) -> None` - absorb an observation.
- `entropy() -> float` - current predictive uncertainty in bits.
- `reset() -> None` - return to initial state.
- `state_dict() -> dict` - serializable state for reproducibility.
- `load_state_dict(state) -> None` - restore state.

### DirichletMarkovPredictor (`core/predictors/dirichlet_markov.py`)

The canonical predictor `P_theta`. A conjugate Dirichlet-Markov predictor
with growable capacity `k`. The label "belief model" is deliberately absent
- it is a mechanical predictor, not a cognitive agent (canon Section 5.2).

Construction: `DirichletMarkovPredictor(initial_capacity=2, alpha=1.0,
rng_seed=None)`. Validates `initial_capacity >= 1` and `alpha > 0`.

Canonical API beyond the ABC:

- `capacity`, `n_observations`, `current_state` (read-only properties).
- `grow() -> int` - add one state with a flat Dirichlet prior, preserving
  all existing transition counts.
- `log_predictive_probability(observation, context) -> float` -
  `log P_theta(observation | context)`.
- `log_loss(observation, context) -> float` - the canonical `L`.
- `posterior_transition_matrix() -> List[List[float]]`.
- `hypothetical_entropy_after_growth() -> float` - evaluate the MDL gain
  **without** mutating state (no speculative growth before the decision).
- `description_length() -> float` - two-part MDL description length.

Factory: `create_predictor(initial_capacity, alpha, seed)`.

### Proper scoring (`core/measurement/proper_scoring.py`)

- `predictive_log_likelihood(predicted_probs, actual_index, eps=1e-15)` -
  `log P_theta(x_{t+1} | x_<=t)`. "The unique local strictly-proper scoring
  rule (Bernardo 1979) - a derivation, not a choice. Permanently replaces
  `E = lambda*H + mu*S + nu*A`." (canon Section 5.3)
- `scoring_loss(predicted_probs, actual_index, eps=1e-15)` - `L`, the
  canonical loss used in E0's DV-a. Lower is better; perfect = 0.0.
- `expected_calibration_error(probabilities, outcomes, n_bins=10)` - ECE,
  used by EXP-1 (see `experiments.md`).
- `log_loss`, `brier_score`, `r2_score` - supporting scorers.

### MDL growth (`core/mdl/mdl_growth.py`)

- `BITS_PER_PARAMETER = 1.0` - a scientific constant, not a hyperparameter.
- `compute_lambda_model_corrected(N, b=BITS_PER_PARAMETER) -> float` -
  the F-A corrected marginal cost `lambda = b + log2(N)` (total bits).
- `should_grow(entropy_before, entropy_after, k, n, N, b=...) ->
  (decision, gain, lambda_model)` - the corrected trigger.
- `mdl_gain(entropy_before, entropy_after, lambda_model) -> float` - legacy
  gain (kept for backward compatibility).
- `two_part_description_length(model_params, log_likelihood,
  n_observations) -> float`.

### Emergence statistic (`core/emergence/emergence_statistic.py`)

- `compute_nmi(labels_true, labels_pred) -> float` - Normalized Mutual
  Information, `2 * I(X;Y) / (H(X) + H(Y))`.
- `compute_held_out_log_likelihood(train, test, alpha=1.0) -> float` -
  held-out LL under a Dirichlet-Markov model (E0's DV-a).

The statistic `M` itself is assembled in `experiments/E0/analysis.py`:
`M = NMI(learned, true) - NMI(learned, shuffled)` (canon Section 5.5,
`parameter_registry.yaml`).

### Controls (`core/controls/`)

- `FixedCapacityControl` (C1) - bounded FIFO memory that cannot discover
  structure beyond its slot count.
- `RandomGrowthControl` (C2) - capacity-matched growth with random
  centroids; error-decoupled.
- `ShuffledInputControl` (C3) - buffers a stream and replays it with
  temporal order destroyed, preserving the marginal distribution.

## 4. Constraints (binding)

1. **Five primitives only.** No sixth. `P_theta` is the only predictor
   family in `core/`.
2. **`L` is derived, not chosen.** The log score is the unique local
   strictly-proper scoring rule. Do not reintroduce
   `E = lambda*H + mu*S + nu*A` or the `lambda/mu/nu` coefficients into
   `core/`. (They remain in `backend/` as the C8 operational policy - see
   `replay.md` Section 6 - but are `[REJECTED]` as science.)
3. **`b = 1.0` is a scientific constant.** It is not tunable. `lambda_model`
   is derived (`k*b + n*log2(N)`; marginal cost `b + log2(N)`), not
   configurable.
4. **The growth trigger must not be hand-set.** A hand-set threshold
   violates assumption I2 by construction (failure mode F2). The trigger is
   the derived inequality, hardcoded.
5. **`G` is dimensionally consistent (total bits).** The F-A corrected
   trigger is `G = N * (H_before - H_after) - (b + log2(N)) > 0`
   (`F_A_TRIGGER_FIX_PREREGISTRATION.md`). The Sprint-1 buggy formula
   `G = H_before - H_after - lambda_model` mixed bits/symbol with total bits
   - a unit-incommensurate comparison that made growth mathematically
   impossible. Unit-incommensurate mathematics are prohibited (canon
   Section 1).
6. **`M` is null-referenced.** `E[M | H0] = 0` by construction. The
   "graph-isomorphism / topological-alignment" formulation of `M` is
   `[REJECTED]` (researcher degrees of freedom, failure mode F3; undefined
   for a probabilistic predictor).
7. **No speculative growth.** `hypothetical_entropy_after_growth` evaluates
   the gain without mutating state; the decision precedes the mutation.
8. **Determinism.** Every predictor takes an `rng_seed` / `seed` and uses
   `numpy.random.RandomState`. `state_dict`/`load_state_dict` make runs
   reproducible.

## 5. Validation expectations

Predictive processing is validated through E0 (H*, see `experiments.md`):

- **DV-a:** held-out predictive log-likelihood
  (`compute_held_out_log_likelihood`). Treatment T must beat **both**
  controls C1 (fixed-capacity) and C2 (error-decoupled, capacity-matched)
  at `p < 0.01` across `>= 5` seeds.
- **DV-b:** the emergence statistic `M`. T must exceed the shuffled-input
  null (C3) by the pre-registered margin `0.05`
  (`parameter_registry.yaml`).
- **Kill:** T fails to beat both C1 and C2 on DV-a, **or** DV-b is within
  noise of the shuffled control, after two honest attempts -> H* is
  falsified for this environment class.

Failure modes to guard against (HYPOTHESIS_REGISTER.md):

- F1 - environment too easy.
- F2 - growth uncoupled from error in practice.
- F3 - emergence statistic has researcher degrees of freedom.
- F4 - observability gap (metrics unmeasurable).

Unit tests in `tests/unit/test_core_canonical.py`, `test_e0_components.py`,
and `test_fa_trigger_fix.py` guard the primitive contracts and the F-A
correction (see `testing.md`).

## 6. What is not present

- There is no hierarchical/multi-level predictor in `core/`. The canon
  notes the single-level predictor is "weakly instantiated" (assumption
  I1); a hierarchy is not built.
- There is no "belief model", "curiosity", or anthropomorphic predictor.
  Such names are prohibited (canon Section 1).
- `core/` contains no persistence, no telemetry, and no replay. Those live
  in `backend/` (see `sqlite.md`, `telemetry.md`, `replay.md`).