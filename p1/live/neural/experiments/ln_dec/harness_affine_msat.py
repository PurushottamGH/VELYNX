"""Executable Capacity-Scaling & C2/C3 Evaluation Harness for AFFINE-MSAT(ℤ₁₇).

Implements real empirical NN-0 experiments for:
  1. Task A — C2 3-Arm Exposure-Matched Control Experiment (Arm A: Frozen Baseline,
     Arm B: Matched-Distractor Online SGD, Arm C: Live Online SGD).
  2. Task B — C3 Memory-Zero Intervention (do(M = ∅)) vs Full-Memory empirical evaluation across d_hidden ∈ {8, 16, 32, 64, 128}.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

import torch

from p1.live.neural.experiments.ln_dec.affine_msat import (
    HEADER_VOCAB_SIZE,
    MODULUS,
    AffineMSATCorpus,
    AffineMSATInstance,
    build_affine_msat_corpus,
    compute_task_state_bits,
    compute_task_state_nats,
)
from p1.live.neural.nn0.nucleus import NN0Config, NN0Trainer


@dataclass
class CapacityScalingPoint:
    d_hidden: int
    num_keys: int
    parameter_count: int
    task_bits: float
    task_nats: float
    recurrent_float_bits: int
    capacity_ratio: float
    capacity_cliff_active: bool
    # Empirical Memory-Zero Intervention Results
    memory_zero_nll: float
    memory_zero_acc: float
    memory_zero_state_size: int
    # Empirical Full-Memory Results
    full_memory_nll: float
    full_memory_acc: float
    full_memory_state_size: int
    # Isolation verification
    no_hidden_carryover: bool
    # Legacy theoretical attributes for backward compatibility
    memory_zero_theoretical_ceiling_nats: float = 0.0
    memory_zero_theoretical_acc: float = 0.0


@dataclass
class C2ExposureControlSummary:
    # Arm NLL and Accuracy
    arm_a_frozen_nll: float
    arm_a_frozen_acc: float
    arm_b_distractor_nll: float
    arm_b_distractor_acc: float
    arm_c_live_nll: float
    arm_c_live_acc: float
    # Tracked exposure quantities
    arm_a_tokens_seen: int
    arm_b_tokens_seen: int
    arm_c_tokens_seen: int
    arm_a_sequence_count: int
    arm_b_sequence_count: int
    arm_c_sequence_count: int
    arm_b_gradient_opportunities: int
    arm_c_gradient_opportunities: int
    arm_b_optimizer_steps: int
    arm_c_optimizer_steps: int
    arm_b_replay_exposure: int
    arm_c_replay_exposure: int
    arm_b_distractor_exposure: int
    arm_c_distractor_exposure: int
    # Provenance & state witnesses
    arm_a_param_hash: str
    arm_b_param_hash: str
    arm_c_param_hash: str
    optimizer_state_empty_arm_a: bool
    # Invariant assertion flags
    tokens_equalized: bool
    sequence_count_equalized: bool
    gradient_steps_equalized: bool
    optimizer_steps_equalized: bool
    replay_exposure_equalized: bool
    initialization_equalized: bool
    c2_identifiable: bool


def _evaluate_instance_on_trainer(
    trainer: NN0Trainer,
    instance: AffineMSATInstance,
    use_external_memory: bool = True,
) -> Tuple[float, bool]:
    """Evaluate one instance on NN0Trainer without mutating model parameters."""
    live_tokens = instance.render_tokens(instance.num_keys)
    probe = instance.probes[0]
    query_tokens = [probe.query_context[0], probe.query_context[1]]
    context = live_tokens + query_tokens

    probs = trainer.predict_context(context, use_external_memory=use_external_memory)

    # Output probabilities for field targets 0..16 are at indices 0..16
    target = probe.target
    field_probs = probs[:MODULUS]
    p_sum = field_probs.sum().item()

    if p_sum > 0:
        target_pmf = field_probs / p_sum
    else:
        target_pmf = torch.full((MODULUS,), 1.0 / MODULUS)

    p_target = float(target_pmf[target].item())
    nll = -math.log(max(p_target, 1e-15))

    pred_target = int(target_pmf.argmax().item())
    is_correct = (pred_target == target)

    return nll, is_correct


def run_c2_exposure_experiment(
    corpus: AffineMSATCorpus,
    config: Optional[NN0Config] = None,
    eval_corpus: Optional[AffineMSATCorpus] = None,
    online_steps: int = 1,
) -> C2ExposureControlSummary:
    """Execute real 3-arm C2 exposure-matched control experiment using NN0Trainer.

    Arms:
      Arm A: Frozen Baseline (no SGD updates, parameter hash theta_0)
      Arm B: Matched-Distractor Online SGD (updates theta_0 on distractor stream)
      Arm C: Live Online SGD (updates theta_0 on live stream)
    """
    if config is None:
        config = NN0Config(
            vocab_size=corpus.vocab_size,
            d_embed=32,
            d_hidden=128,
            seed=corpus.seed,
            training_mode="sequence",
            bptt_window=16,
        )

    if eval_corpus is None:
        eval_corpus = corpus

    # --- Arm A: Frozen Baseline ---
    trainer_a = NN0Trainer(config)
    arm_a_param_hash = trainer_a.parameter_hash()
    trainer_a.freeze_parameters()
    optimizer_state_empty_arm_a = trainer_a.optimizer_state_is_empty()

    arm_a_nlls = []
    arm_a_corrects = []
    for inst in eval_corpus.instances:
        nll, is_corr = _evaluate_instance_on_trainer(trainer_a, inst, use_external_memory=True)
        arm_a_nlls.append(nll)
        arm_a_corrects.append(is_corr)

    arm_a_frozen_nll = sum(arm_a_nlls) / len(arm_a_nlls)
    arm_a_frozen_acc = sum(arm_a_corrects) / len(arm_a_corrects)

    # --- Arm B: Matched-Distractor Online SGD ---
    trainer_b = NN0Trainer(config)
    arm_b_param_hash = trainer_b.parameter_hash()
    assert arm_b_param_hash == arm_a_param_hash, "Arm B initialization hash mismatch!"

    arm_b_tokens_seen = 0
    arm_b_sequence_count = 0
    arm_b_gradient_opportunities = 0
    arm_b_optimizer_steps = 0
    arm_b_replay_exposure = 0
    arm_b_distractor_exposure = 0

    key_offset = HEADER_VOCAB_SIZE
    op_offset = HEADER_VOCAB_SIZE + corpus.num_keys

    for _ in range(online_steps):
        for inst in corpus.instances:
            distractor_tokens = []
            for ep in inst.distractor_episodes:
                distractor_tokens.extend(ep.to_tokens(key_offset, op_offset))

            probe = inst.probes[0]
            query_tokens = [probe.query_context[0], probe.query_context[1]]
            distractor_seq = distractor_tokens + query_tokens + [probe.target]

            res = trainer_b.step_sequence(distractor_seq, source_id="distractor_stream")

            arm_b_tokens_seen += len(distractor_seq)
            arm_b_sequence_count += 1
            chunks = int(res["chunks"])
            arm_b_gradient_opportunities += chunks
            arm_b_optimizer_steps += chunks
            arm_b_replay_exposure += len(trainer_b.replay)
            arm_b_distractor_exposure += len(distractor_tokens)

    trainer_b.freeze_parameters()

    arm_b_nlls = []
    arm_b_corrects = []
    for inst in eval_corpus.instances:
        nll, is_corr = _evaluate_instance_on_trainer(trainer_b, inst, use_external_memory=True)
        arm_b_nlls.append(nll)
        arm_b_corrects.append(is_corr)

    arm_b_distractor_nll = sum(arm_b_nlls) / len(arm_b_nlls)
    arm_b_distractor_acc = sum(arm_b_corrects) / len(arm_b_corrects)

    # --- Arm C: Live Online SGD ---
    trainer_c = NN0Trainer(config)
    arm_c_param_hash = trainer_c.parameter_hash()
    assert arm_c_param_hash == arm_a_param_hash, "Arm C initialization hash mismatch!"

    arm_c_tokens_seen = 0
    arm_c_sequence_count = 0
    arm_c_gradient_opportunities = 0
    arm_c_optimizer_steps = 0
    arm_c_replay_exposure = 0
    arm_c_distractor_exposure = 0

    for _ in range(online_steps):
        for inst in corpus.instances:
            live_tokens = inst.render_tokens(inst.num_keys)
            probe = inst.probes[0]
            query_tokens = [probe.query_context[0], probe.query_context[1]]
            live_seq = live_tokens + query_tokens + [probe.target]

            res = trainer_c.step_sequence(live_seq, source_id="live_stream")

            arm_c_tokens_seen += len(live_seq)
            arm_c_sequence_count += 1
            chunks = int(res["chunks"])
            arm_c_gradient_opportunities += chunks
            arm_c_optimizer_steps += chunks
            arm_c_replay_exposure += len(trainer_c.replay)
            arm_c_distractor_exposure += 0

    trainer_c.freeze_parameters()

    arm_c_nlls = []
    arm_c_corrects = []
    for inst in eval_corpus.instances:
        nll, is_corr = _evaluate_instance_on_trainer(trainer_c, inst, use_external_memory=True)
        arm_c_nlls.append(nll)
        arm_c_corrects.append(is_corr)

    arm_c_live_nll = sum(arm_c_nlls) / len(arm_c_nlls)
    arm_c_live_acc = sum(arm_c_corrects) / len(arm_c_corrects)

    # --- Equalization Invariant Verification ---
    tokens_equalized = (arm_b_tokens_seen == arm_c_tokens_seen)
    sequence_count_equalized = (arm_b_sequence_count == arm_c_sequence_count)
    gradient_steps_equalized = (arm_b_gradient_opportunities == arm_c_gradient_opportunities)
    optimizer_steps_equalized = (arm_b_optimizer_steps == arm_c_optimizer_steps)
    replay_exposure_equalized = (arm_b_replay_exposure == arm_c_replay_exposure)
    initialization_equalized = (arm_a_param_hash == arm_b_param_hash == arm_c_param_hash)

    c2_identifiable = (
        tokens_equalized
        and sequence_count_equalized
        and gradient_steps_equalized
        and optimizer_steps_equalized
        and replay_exposure_equalized
        and initialization_equalized
    )

    return C2ExposureControlSummary(
        arm_a_frozen_nll=arm_a_frozen_nll,
        arm_a_frozen_acc=arm_a_frozen_acc,
        arm_b_distractor_nll=arm_b_distractor_nll,
        arm_b_distractor_acc=arm_b_distractor_acc,
        arm_c_live_nll=arm_c_live_nll,
        arm_c_live_acc=arm_c_live_acc,
        arm_a_tokens_seen=0,
        arm_b_tokens_seen=arm_b_tokens_seen,
        arm_c_tokens_seen=arm_c_tokens_seen,
        arm_a_sequence_count=0,
        arm_b_sequence_count=arm_b_sequence_count,
        arm_c_sequence_count=arm_c_sequence_count,
        arm_b_gradient_opportunities=arm_b_gradient_opportunities,
        arm_c_gradient_opportunities=arm_c_gradient_opportunities,
        arm_b_optimizer_steps=arm_b_optimizer_steps,
        arm_c_optimizer_steps=arm_c_optimizer_steps,
        arm_b_replay_exposure=arm_b_replay_exposure,
        arm_c_replay_exposure=arm_c_replay_exposure,
        arm_b_distractor_exposure=arm_b_distractor_exposure,
        arm_c_distractor_exposure=arm_c_distractor_exposure,
        arm_a_param_hash=arm_a_param_hash,
        arm_b_param_hash=arm_b_param_hash,
        arm_c_param_hash=arm_c_param_hash,
        optimizer_state_empty_arm_a=optimizer_state_empty_arm_a,
        tokens_equalized=tokens_equalized,
        sequence_count_equalized=sequence_count_equalized,
        gradient_steps_equalized=gradient_steps_equalized,
        optimizer_steps_equalized=optimizer_steps_equalized,
        replay_exposure_equalized=replay_exposure_equalized,
        initialization_equalized=initialization_equalized,
        c2_identifiable=c2_identifiable,
    )


def evaluate_c2_exposure_arms(corpus: AffineMSATCorpus) -> C2ExposureControlSummary:
    """Evaluate preregistered 3-arm C2 exposure control invariants via NN0Trainer."""
    return run_c2_exposure_experiment(corpus)


def run_c3_memory_zero_intervention(
    corpus: AffineMSATCorpus,
    d_hidden: int,
    seed: int = 42,
    eval_corpus: Optional[AffineMSATCorpus] = None,
) -> CapacityScalingPoint:
    """Execute real C3 Memory-Zero intervention (do(M = ∅)) vs Full-Memory on NN0Trainer."""
    if eval_corpus is None:
        eval_corpus = corpus

    cfg = NN0Config(
        vocab_size=corpus.vocab_size,
        d_embed=32,
        d_hidden=d_hidden,
        seed=seed,
        training_mode="sequence",
        bptt_window=16,
    )

    trainer = NN0Trainer(cfg)
    param_count = trainer.parameter_count()

    # Train / populate memory on training corpus
    for inst in corpus.instances:
        live_tokens = inst.render_tokens(inst.num_keys)
        probe = inst.probes[0]
        query_tokens = [probe.query_context[0], probe.query_context[1]]
        seq = live_tokens + query_tokens + [probe.target]
        trainer.step_sequence(seq, source_id="c3_train")

    trainer.freeze_parameters()

    # --- Condition 1: Full-Memory Evaluation ---
    full_nlls = []
    full_corrects = []
    for inst in eval_corpus.instances:
        nll, is_corr = _evaluate_instance_on_trainer(trainer, inst, use_external_memory=True)
        full_nlls.append(nll)
        full_corrects.append(is_corr)

    full_memory_nll = sum(full_nlls) / len(full_nlls)
    full_memory_acc = sum(full_corrects) / len(full_corrects)
    full_memory_state_size = len(trainer.memory)

    # --- Condition 2: Memory-Zero Intervention (do(M = ∅)) ---
    # Apply causal intervention to wipe external memory, replay, and recurrent hidden state
    trainer.clear_external_memory()
    trainer.clear_replay()
    trainer.reset_state()

    assert len(trainer.memory) == 0, "External memory not cleared!"
    assert len(trainer.replay) == 0, "Replay not cleared!"
    assert trainer.last_h is None, "Recurrent hidden state not cleared!"

    mz_nlls = []
    mz_corrects = []
    for inst in eval_corpus.instances:
        # Guarantee no state carryover survives between evaluation episodes
        trainer.clear_external_memory()
        trainer.clear_replay()
        trainer.reset_state()

        nll, is_corr = _evaluate_instance_on_trainer(trainer, inst, use_external_memory=False)
        mz_nlls.append(nll)
        mz_corrects.append(is_corr)

    memory_zero_nll = sum(mz_nlls) / len(mz_nlls)
    memory_zero_acc = sum(mz_corrects) / len(mz_corrects)
    memory_zero_state_size = 0

    no_hidden_carryover = (len(trainer.memory) == 0 and len(trainer.replay) == 0 and trainer.last_h is None)

    task_bits = compute_task_state_bits(corpus.num_keys)
    task_nats = compute_task_state_nats(corpus.num_keys)
    recurrent_float_bits = d_hidden * 32
    capacity_ratio = recurrent_float_bits / task_bits
    capacity_cliff_active = (task_bits > recurrent_float_bits)

    theoretical_ceiling_nats = math.log(MODULUS) if capacity_cliff_active else 0.0
    theoretical_acc = (1.0 / MODULUS) if capacity_cliff_active else 1.0

    return CapacityScalingPoint(
        d_hidden=d_hidden,
        num_keys=corpus.num_keys,
        parameter_count=param_count,
        task_bits=task_bits,
        task_nats=task_nats,
        recurrent_float_bits=recurrent_float_bits,
        capacity_ratio=capacity_ratio,
        capacity_cliff_active=capacity_cliff_active,
        memory_zero_nll=memory_zero_nll,
        memory_zero_acc=memory_zero_acc,
        memory_zero_state_size=memory_zero_state_size,
        full_memory_nll=full_memory_nll,
        full_memory_acc=full_memory_acc,
        full_memory_state_size=full_memory_state_size,
        no_hidden_carryover=no_hidden_carryover,
        memory_zero_theoretical_ceiling_nats=theoretical_ceiling_nats,
        memory_zero_theoretical_acc=theoretical_acc,
    )


def evaluate_capacity_matrix(
    d_hidden_list: Tuple[int, ...] = (8, 16, 32, 64, 128),
    num_keys_list: Tuple[int, ...] = (8, 128),
    seed: int = 42,
    num_instances: int = 20,
) -> List[CapacityScalingPoint]:
    """Compute empirical capacity-scaling matrix for all d_hidden and N_K settings via C3 interventions."""
    scaling_points: List[CapacityScalingPoint] = []

    for num_keys in num_keys_list:
        corpus = build_affine_msat_corpus(seed=seed, num_instances=num_instances, num_keys=num_keys)
        for d_hidden in d_hidden_list:
            pt = run_c3_memory_zero_intervention(corpus, d_hidden=d_hidden, seed=seed)
            scaling_points.append(pt)

    return scaling_points
