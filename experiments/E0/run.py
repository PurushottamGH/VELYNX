"""E0: Emergence-vs-Injection Discrimination — Canonical Implementation.

Central experiment that decides H* — emergence vs injection
on a nonlinear-latent stream.

Conditions:
    T  (Treatment):            Error-gated growth ON (MDL trigger)
    C1 (Fixed-capacity):       No growth, fixed predictor capacity
    C2 (Error-decoupled):      Capacity-matched growth at random times
    C3 (Shuffled-input):       Temporal order destroyed, marginals preserved

Measurements:
    DV-a: Held-out predictive log-likelihood
    DV-b: Emergence statistic M = NMI(learned, true) - NMI(learned, shuffled)

Reference: PROGRAM_D_CANONICAL.md §7 (E0)
           SCIENTIFIC_EXECUTION_SPEC.md §E0
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Ensure project root is on path
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from core.predictors.dirichlet_markov import DirichletMarkovPredictor
from core.mdl.mdl_growth import should_grow
from experiments.E0.dataset import NonlinearLatentEnvironment
from experiments.E0.analysis import (  # noqa: E402
    analyze_conditions,
)
from experiments.E0.decision import E0Decider, M_STATISTIC_MARGIN


# --- Default configuration ---

DEFAULT_CONFIG: Dict[str, Any] = {
    "experiment_id": "E0",
    "seed": 42,
    "env_seed": 101,  # Separate seed for environment generation
    "num_train_steps": 10000,
    "num_test_steps": 2000,
    "environment": {
        "num_latent_states": 10,
        "observation_dim": 16,
        "transition_alpha": 1.0,
        "noise_sigma": 0.05,
    },
    "predictor": {
        "initial_capacity": 2,
        "alpha": 1.0,  # Dirichlet concentration
    },
    "growth": {
        "b": 1.0,  # Bits per parameter (scientific constant)
        "evaluate_every": 500,  # Steps between growth evaluations
        "warmup_steps": 1000,   # Minimum steps before first growth
    },
    "conditions": ["T", "C1", "C2", "C3"],
    "num_seeds": 5,
    "results_dir": None,  # Auto-generated
}

_CONFIG_SCHEMA_VERSION = "1.0.0"


# --- Seed manager ---


class SeedRegistry:
    """Central PRNG registry with separate env/agent seeds.

    Ensures the agent cannot predict the environment by sharing a PRNG.
    """

    def __init__(
        self,
        master_seed: int,
        env_seed_offset: int = 1000,
    ):
        self.master_seed = master_seed
        self._env_seed = master_seed + env_seed_offset
        self._used_seeds: Dict[str, int] = {}

    def env_seed(self) -> int:
        return self._env_seed

    def agent_seed(self, condition: str, seed_idx: int) -> int:
        seed_bytes = f"agent::{condition}::{seed_idx}".encode()
        digest = hashlib.sha256(seed_bytes).hexdigest()
        return self.master_seed + int(digest[:8], 16) % (2**31)




# --- Held-out evaluation ---


def _evaluate_held_out(
    predictor: DirichletMarkovPredictor,
    env: NonlinearLatentEnvironment,
    test_steps: int,
) -> Dict[str, Any]:
    """Evaluate the trained predictor on a genuinely independent held-out sequence.

    The test sequence is generated from a fresh environment instance
    (different initial state, same transition matrix and base vectors)
    so it is independent of the training trajectory.

    The predictor is NOT updated during test evaluation — only
    log-predictive probabilities are computed using the trained
    transition counts.

    Returns
    -------
    dict with keys:
        test_log_likelihoods: List[float] — per-step log-likelihoods
        test_latent_states: List[np.ndarray] — latents from env
    """
    test_log_likelihoods: List[float] = []
    context: List[float] = []
    test_latent_states: List[int] = []

    env.reset()
    for step in range(test_steps):
        latent, obs = env.step()
        obs_list = obs.tolist()
        test_latent_states.append(latent)

        if len(context) > 0:
            ll = predictor.log_predictive_probability(obs_list, context)
            test_log_likelihoods.append(ll)

        # Update context WITHOUT updating predictor state
        context = obs_list

    return {
        "test_log_likelihoods": test_log_likelihoods,
        "test_latent_states": test_latent_states,
    }


# --- Condition runners ---


def run_treatment(
    env: NonlinearLatentEnvironment,
    predictor: DirichletMarkovPredictor,
    train_steps: int,
    evaluate_every: int,
    warmup_steps: int,
    b: float = 1.0,
    test_steps: int = 0,
) -> Dict[str, Any]:
    """Condition T (Treatment): Error-gated growth ON.

    The predictor grows capacity when the MDL gain G > 0, meaning
    the description length strictly decreases. Growth is evaluated
    hypothetically BEFORE committing — the predictor's internal state
    is never modified by speculative growth.

    Canonical rule: predictor.grow() is called ONLY after G > λ_model.
    """
    growth_events: List[int] = []  # ticks when growth occurred
    per_step_log: List[Dict] = []
    capacities: List[int] = []
    log_losses: List[float] = []
    log_likelihoods: List[float] = []

    context: List[float] = []
    inferred_latent_states: List[int] = []
    true_latent_states: List[int] = []

    env.reset()
    predictor.reset()

    for step in range(train_steps):
        # Get observation
        latent, obs = env.step()
        obs_list = obs.tolist()
        true_latent_states.append(latent)
        capacities.append(predictor.capacity)

        # Predict before update
        if len(context) > 0:
            ll = predictor.log_predictive_probability(obs_list, context)
            log_likelihoods.append(ll)
            log_losses.append(-ll)

        # Update predictor with observation
        predictor.update(obs_list)

        # Log the predictor's inferred latent state (after update)
        inferred = predictor.current_state if predictor.current_state is not None else 0
        inferred_latent_states.append(inferred)

        # Evaluate growth periodically:
        #   Compute hypothetical entropy after growth WITHOUT calling grow()
        #   Only commit growth AFTER G > λ_model is verified
        if (
            step >= warmup_steps
            and step % evaluate_every == 0
        ):
            k = predictor.capacity
            n = k  # parameter dimension = current capacity
            N = predictor.n_observations

            # Entropy before (current model)
            entropy_before = predictor.entropy()

            # Hypothetical entropy after growth (no state mutation)
            entropy_after = predictor.hypothetical_entropy_after_growth()

            # Evaluate MDL gain — strictly on hypothetical values
            decision, gain, lam = should_grow(
                entropy_before=entropy_before,
                entropy_after=entropy_after,
                k=k,
                n=n,
                N=N,
                b=b,
            )

            # Committed growth ONLY after positive MDL gain
            if decision:
                predictor.grow()
                growth_events.append(step)

            per_step_log.append({
                "step": step,
                "capacity_before": k,
                "capacity_after": predictor.capacity,
                "entropy_before": entropy_before,
                "entropy_after": entropy_after,
                "lambda_model": lam,
                "gain": gain,
                "grew": decision,
            })

        context = obs_list

    # Held-out evaluation on independent test sequence
    test_result: Dict[str, Any] = {}
    if test_steps > 0:
        test_env = NonlinearLatentEnvironment(
            num_latent_states=env.K,
            observation_dim=env.D,
            transition_alpha=env._transition_alpha,
            noise_sigma=env.noise_sigma,
            seed=env.get_state_info()["env_seed"] + 9999,
        )
        test_result = _evaluate_held_out(predictor, test_env, test_steps)

    return {
        "condition": "T",
        "test_log_likelihoods": test_result.get("test_log_likelihoods", []),
        "growth_events": growth_events,
        "final_capacity": predictor.capacity,
        "capacities": capacities,
        "log_losses": log_losses,
        "log_likelihoods": log_likelihoods,
        "latent_states": inferred_latent_states,
        "true_latent_states": true_latent_states,
        "per_step_log": per_step_log,
        "final_predictor_state": predictor.state_dict(),
    }


def run_fixed_capacity(
    env: NonlinearLatentEnvironment,
    predictor: DirichletMarkovPredictor,
    train_steps: int,
    evaluate_every: int,
    test_steps: int = 0,
) -> Dict[str, Any]:
    """Condition C1 (Fixed-capacity): No growth.

    The predictor keeps its initial capacity and never grows.
    This is a null baseline to compare error-gated growth against.
    """
    log_losses: List[float] = []
    log_likelihoods: List[float] = []
    capacities: List[int] = []
    inferred_latent_states: List[int] = []
    true_latent_states: List[int] = []

    context: List[float] = []
    env.reset()
    predictor.reset()

    for step in range(train_steps):
        latent, obs = env.step()
        obs_list = obs.tolist()
        true_latent_states.append(latent)
        capacities.append(predictor.capacity)

        if len(context) > 0:
            ll = predictor.log_predictive_probability(obs_list, context)
            log_likelihoods.append(ll)
            log_losses.append(-ll)

        predictor.update(obs_list)
        inferred = predictor.current_state if predictor.current_state is not None else 0
        inferred_latent_states.append(inferred)
        context = obs_list

    # Held-out evaluation on independent test sequence
    # (only runs when test_steps > 0, passed from run_single_seed)
    test_result: Dict[str, Any] = {}
    if test_steps > 0:
        test_env = NonlinearLatentEnvironment(
            num_latent_states=env.K,
            observation_dim=env.D,
            transition_alpha=env._transition_alpha,
            noise_sigma=env.noise_sigma,
            seed=env.get_state_info()["env_seed"] + 9999,
        )
        test_result = _evaluate_held_out(predictor, test_env, test_steps)

    return {
        "condition": "C1",
        "test_log_likelihoods": test_result.get("test_log_likelihoods", []),
        "growth_events": [],
        "final_capacity": predictor.capacity,
        "capacities": capacities,
        "log_losses": log_losses,
        "log_likelihoods": log_likelihoods,
        "latent_states": inferred_latent_states,
        "true_latent_states": true_latent_states,
        "final_predictor_state": predictor.state_dict(),
    }


def apply_growth_at_random_times(
    predictor: DirichletMarkovPredictor,
    env: NonlinearLatentEnvironment,
    train_steps: int,
    growth_count: int,
    rng: np.random.RandomState,
    test_steps: int = 0,
) -> Dict[str, Any]:
    """Apply a specific number of growth events at random times.

    This is the capacity-matched control: same number of growth events
    as the treatment condition, but at random positions uncorrelated
    with prediction error.
    """
    if growth_count <= 0:
        result = run_fixed_capacity(env, predictor, train_steps, evaluate_every=0, test_steps=test_steps)
        result["condition"] = "C2"
        return result

    log_losses: List[float] = []
    log_likelihoods: List[float] = []
    capacities: List[int] = []
    inferred_latent_states: List[int] = []
    true_latent_states: List[int] = []
    growth_events: List[int] = []
    context: List[float] = []

    env.reset()
    predictor.reset()

    # Pick random positions for the growth events (uniformly distributed)
    min_step = max(train_steps // 10, 10)  # Don't grow in first 10%
    if train_steps - min_step < growth_count:
        growth_positions = list(range(min_step, train_steps))
    else:
        growth_positions = sorted(
            rng.choice(range(min_step, train_steps), size=growth_count, replace=False)
        )

    growth_idx = 0
    for step in range(train_steps):
        latent, obs = env.step()
        obs_list = obs.tolist()
        true_latent_states.append(latent)
        capacities.append(predictor.capacity)

        if len(context) > 0:
            ll = predictor.log_predictive_probability(obs_list, context)
            log_likelihoods.append(ll)
            log_losses.append(-ll)

        predictor.update(obs_list)
        inferred = predictor.current_state if predictor.current_state is not None else 0
        inferred_latent_states.append(inferred)

        # Grow at predetermined random positions (decoupled from error)
        if growth_idx < len(growth_positions) and step == growth_positions[growth_idx]:
            predictor.grow()
            growth_events.append(step)
            growth_idx += 1

        context = obs_list

    # Held-out evaluation on independent test sequence
    test_result: Dict[str, Any] = {}
    if test_steps > 0:
        test_env = NonlinearLatentEnvironment(
            num_latent_states=env.K,
            observation_dim=env.D,
            transition_alpha=env._transition_alpha,
            noise_sigma=env.noise_sigma,
            seed=env.get_state_info()["env_seed"] + 9999,
        )
        test_result = _evaluate_held_out(predictor, test_env, test_steps)

    return {
        "condition": "C2",
        "test_log_likelihoods": test_result.get("test_log_likelihoods", []),
        "growth_events": growth_events,
        "final_capacity": predictor.capacity,
        "capacities": capacities,
        "log_losses": log_losses,
        "log_likelihoods": log_likelihoods,
        "latent_states": inferred_latent_states,
        "true_latent_states": true_latent_states,
        "final_predictor_state": predictor.state_dict(),
    }


def run_shuffled_input(
    env: NonlinearLatentEnvironment,
    predictor: DirichletMarkovPredictor,
    train_steps: int,
    evaluate_every: int,
    warmup_steps: int,
    b: float = 1.0,
    test_steps: int = 0,
) -> Dict[str, Any]:
    """Condition C3 (Shuffled-input): Temporal order destroyed.

    The observation marginal distribution is preserved, but temporal order
    is destroyed. This tests whether temporal dependencies are necessary
    for structure acquisition.
    """
    log_losses: List[float] = []
    log_likelihoods: List[float] = []
    capacities: List[int] = []
    inferred_latent_states: List[int] = []
    true_latent_states: List[int] = []
    growth_events: List[int] = []
    context: List[float] = []

    env.reset()
    predictor.reset()

    # Generate full sequence first, then shuffle
    full_obs: List[np.ndarray] = []
    full_latents: List[int] = []
    for step in range(train_steps):
        latent, obs = env.step()
        full_obs.append(obs)
        full_latents.append(latent)

    # Shuffle observations (preserve marginals, destroy temporal order)
    shuffled_indices = list(range(len(full_obs)))
    shuffle_rng = np.random.RandomState(env.get_state_info()["env_seed"] + 999)
    shuffle_rng.shuffle(shuffled_indices)

    # Run through shuffled sequence
    for step, idx in enumerate(shuffled_indices):
        obs = full_obs[idx]
        latent = full_latents[idx]
        obs_list = obs.tolist()
        true_latent_states.append(latent)
        capacities.append(predictor.capacity)

        if len(context) > 0:
            ll = predictor.log_predictive_probability(obs_list, context)
            log_likelihoods.append(ll)
            log_losses.append(-ll)

        predictor.update(obs_list)
        inferred = predictor.current_state if predictor.current_state is not None else 0
        inferred_latent_states.append(inferred)

        # Same growth trigger as treatment (but on shuffled data)
        # Uses hypothetical entropy computation — no speculative growth
        if step >= warmup_steps and step % evaluate_every == 0:
            k = predictor.capacity
            n = k
            N = predictor.n_observations
            entropy_before = predictor.entropy()
            entropy_after = predictor.hypothetical_entropy_after_growth()
            decision, gain, lam = should_grow(
                entropy_before=entropy_before,
                entropy_after=entropy_after,
                k=k, n=n, N=N, b=b,
            )
            if decision:
                predictor.grow()
                growth_events.append(step)

        context = obs_list

    # Held-out evaluation on independent test sequence
    test_result: Dict[str, Any] = {}
    if test_steps > 0:
        test_env = NonlinearLatentEnvironment(
            num_latent_states=env.K,
            observation_dim=env.D,
            transition_alpha=env._transition_alpha,
            noise_sigma=env.noise_sigma,
            seed=env.get_state_info()["env_seed"] + 9999,
        )
        test_result = _evaluate_held_out(predictor, test_env, test_steps)

    return {
        "condition": "C3",
        "test_log_likelihoods": test_result.get("test_log_likelihoods", []),
        "growth_events": growth_events,
        "final_capacity": predictor.capacity,
        "capacities": capacities,
        "log_losses": log_losses,
        "log_likelihoods": log_likelihoods,
        "latent_states": inferred_latent_states,
        "true_latent_states": true_latent_states,
        "final_predictor_state": predictor.state_dict(),
    }


# --- Main experiment runner ---


def run_single_seed(
    seed: int,
    env_seed: int,
    config: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Run E0 for a single seed across all conditions.

    Parameters
    ----------
    seed : int
        Master random seed for this run.
    env_seed : int
        Separate seed for environment generation.
    config : dict
        Experiment configuration.
    output_dir : str
        Path to output directory for artifacts.

    Returns
    -------
    dict with results for all conditions
    """
    seed_registry = SeedRegistry(master_seed=seed, env_seed_offset=env_seed - seed)
    env_cfg = config["environment"]
    pred_cfg = config["predictor"]
    growth_cfg = config["growth"]
    num_train = config["num_train_steps"]
    conditions_to_run = config.get("conditions", ["T", "C1", "C2", "C3"])

    results: Dict[str, Any] = {
        "config": config,
        "seed": seed,
        "env_seed": env_seed,
        "conditions": {},
        "analysis": {},
        "decision": None,
    }

    # Run T first to get growth count, then use it for C2 (capacity-matched)
    t_growth_count = 0
    for condition in conditions_to_run:
        env = NonlinearLatentEnvironment(
            num_latent_states=env_cfg["num_latent_states"],
            observation_dim=env_cfg["observation_dim"],
            transition_alpha=env_cfg.get("transition_alpha", 1.0),
            noise_sigma=env_cfg.get("noise_sigma", 0.05),
            seed=env_seed,
        )

        predictor = DirichletMarkovPredictor(
            initial_capacity=pred_cfg["initial_capacity"],
            alpha=pred_cfg.get("alpha", 1.0),
            rng_seed=seed_registry.agent_seed(condition, 0),
        )

        condition_seed_bytes = condition.encode()
        condition_digest = hashlib.sha256(condition_seed_bytes).hexdigest()
        condition_rng = np.random.RandomState(seed + 1000 + int(condition_digest[:8], 16) % 10000)
        kwargs = {
            "env": env,
            "predictor": predictor,
            "train_steps": num_train,
            "evaluate_every": growth_cfg["evaluate_every"],
            "test_steps": config.get("num_test_steps", 2000),
        }

        if condition == "T":
            kwargs["warmup_steps"] = growth_cfg["warmup_steps"]
            kwargs["b"] = growth_cfg["b"]
            condition_result = run_treatment(**kwargs)
            t_growth_count = len(condition_result.get("growth_events", []))
        elif condition == "C1":
            condition_result = run_fixed_capacity(**kwargs)
        elif condition == "C2":
            # Capacity-matched: same number of growth events as T, at random times
            condition_result = apply_growth_at_random_times(
                predictor=predictor,
                env=env,
                train_steps=num_train,
                growth_count=t_growth_count,
                rng=condition_rng,
                test_steps=config.get("num_test_steps", 2000),
            )
        elif condition == "C3":
            kwargs["warmup_steps"] = growth_cfg["warmup_steps"]
            kwargs["b"] = growth_cfg["b"]
            condition_result = run_shuffled_input(**kwargs)
        else:
            raise ValueError(f"Unknown condition: {condition}")

        results["conditions"][condition] = condition_result

    # Run analysis on all conditions
    analysis_results = analyze_conditions(results["conditions"])
    results["analysis"] = analysis_results

    # Compute pass/kill decision
    decider = E0Decider(p_threshold=0.01, min_seeds=3)
    decision = decider.evaluate(results)
    results["decision"] = decision

    return results


def run_multi_seed(
    num_seeds: int,
    base_seed: int,
    config: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Run E0 across multiple seeds and aggregate results.

    Each seed gets its own unique master seed = base_seed + seed_idx.
    Results are aggregated across seeds for the final pass/kill decision.

    Parameters
    ----------
    num_seeds : int
        Number of seeds to run (>=5 per canonical requirement).
    base_seed : int
        Base master seed. Each run uses base_seed + i.
    config : dict
        Experiment configuration.
    output_dir : str
        Path to output directory for artifacts.

    Returns
    -------
    dict with per-seed results and aggregated decision
    """
    per_seed_results: List[Dict[str, Any]] = []
    total_start = time.time()

    print(f"[E0] Multi-seed run: {num_seeds} seeds starting at base_seed={base_seed}")
    print(f"[E0] Output: {output_dir}")

    for i in range(num_seeds):
        seed = base_seed + i
        env_seed = seed + 1000  # Distinct env seed per seed

        seed_start = time.time()
        result = run_single_seed(
            seed=seed,
            env_seed=env_seed,
            config=config,
            output_dir=output_dir,
        )
        seed_elapsed = time.time() - seed_start

        per_seed_results.append(result)

        decision = result.get("decision", {})
        print(f"[E0]   seed {seed}: {decision.get('verdict', '?')} "
              f"({seed_elapsed:.1f}s)")

    total_elapsed = time.time() - total_start

    # Aggregate across seeds
    decider = E0Decider(
        p_threshold=0.01,
        min_seeds=config.get("min_seeds", 5),
        m_margin=M_STATISTIC_MARGIN,
    )
    aggregated_decision = decider.evaluate_multi_seed(per_seed_results)

    # Build aggregated results
    aggregated: Dict[str, Any] = {
        "experiment_id": "E0",
        "config": config,
        "num_seeds": num_seeds,
        "base_seed": base_seed,
        "per_seed_results": per_seed_results,
        "decision": aggregated_decision,
        "elapsed_seconds": total_elapsed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Save aggregated results
    output_path = Path(output_dir)
    results_path = output_path / "aggregated_results.json"
    with open(results_path, "w") as f:
        json.dump(aggregated, f, indent=2, default=_json_serialize)

    print(f"\n[E0] Multi-seed run completed in {total_elapsed:.1f}s")
    print(f"[E0] Aggregated decision: {aggregated_decision['verdict']}")
    print(f"[E0] Seeds: {aggregated_decision.get('n_seeds', '?')} / "
          f"{aggregated_decision.get('min_seeds', '?')} required")

    return aggregated


def main(
    output_dir: Optional[str] = None,
    config: Optional[str] = None,
    seed: int = 42,
    num_seeds: Optional[int] = None,
) -> Dict[str, Any]:
    """Main entry point for the E0 experiment.

    Parameters
    ----------
    output_dir : str or None
        Directory for experiment artifacts. Auto-generated if None.
    config : str or None
        Path to JSON config file. Uses defaults if None.
    seed : int
        Base master random seed.
    num_seeds : int or None
        Number of seeds to run. Defaults to config value.

    Returns
    -------
    dict with full experiment results
    """
    # Load configuration
    cfg = dict(DEFAULT_CONFIG)
    if config:
        with open(config) as f:
            user_cfg = json.load(f)
            cfg.update(user_cfg)

    cfg["seed"] = seed

    # Determine number of seeds
    n_seeds = num_seeds if num_seeds is not None else cfg.get("num_seeds", 5)

    # Set up output directory
    if output_dir is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_dir = str(
            _project_root / "artifacts" / "experiments" / "E0" / f"run_{timestamp}_s{seed}_n{n_seeds}"
        )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save configuration
    with open(output_path / "config.json", "w") as f:
        json.dump(cfg, f, indent=2, default=str)

    # Run multi-seed experiment
    print(f"[E0] Starting multi-seed experiment: {n_seeds} seeds")
    print(f"[E0] Output: {output_dir}")
    print(f"[E0] Config: env_states={cfg['environment']['num_latent_states']}, "
          f"obs_dim={cfg['environment']['observation_dim']}, "
          f"train_steps={cfg['num_train_steps']}")

    all_results = run_multi_seed(
        num_seeds=n_seeds,
        base_seed=seed,
        config=cfg,
        output_dir=output_dir,
    )

    return all_results


def _json_serialize(obj: Any) -> Any:
    """JSON serializer for numpy types and other non-serializable objects."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (datetime,)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="E0: Emergence-vs-Injection Discrimination")
    parser.add_argument("--output-dir", help="Output directory for results")
    parser.add_argument("--config", help="Path to experiment config JSON")
    parser.add_argument("--seed", type=int, default=42, help="Base master random seed")
    parser.add_argument("--num-seeds", type=int, default=None,
                        help="Number of seeds to run (default: config value, min 5)")
    args = parser.parse_args()

    main(
        output_dir=args.output_dir,
        config=args.config,
        seed=args.seed,
        num_seeds=args.num_seeds,
    )
