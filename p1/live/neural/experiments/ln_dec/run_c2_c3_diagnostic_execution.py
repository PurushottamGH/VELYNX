from __future__ import annotations

import copy
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F

from p1.live.neural.nn0.nucleus import NN0Config, NN0Trainer, set_global_seed
from p1.live.neural.experiments.ln_dec.affine_msat import (
    MODULUS,
    HEADER_VOCAB_SIZE,
    AffineMSATCorpus,
    AffineMSATInstance,
    build_affine_msat_corpus,
    compute_task_state_bits,
)


@dataclass
class C2ArmResult:
    arm_name: str
    nll: float
    accuracy: float
    parameter_hash_before: str
    parameter_hash_after: str
    parameter_delta: float
    tokens_seen: int
    optimizer_steps: int
    frozen: bool


@dataclass
class C2ExperimentResult:
    arm_a: C2ArmResult
    arm_b: C2ArmResult
    arm_c: C2ArmResult
    seed: int
    num_keys: int
    vocab_size: int


@dataclass
class C3ConditionResult:
    d_hidden: int
    num_keys: int
    memory_condition: str
    nll: float
    accuracy: float
    parameter_hash: str
    memory_size: int
    replay_size: int
    hidden_state_is_zero: bool


@dataclass
class C3ExperimentResult:
    conditions: List[C3ConditionResult]
    seed: int


def _build_trainer(
    seed: int,
    vocab_size: int,
    d_hidden: int,
    device: str = "cpu",
) -> NN0Trainer:
    cfg = NN0Config(
        vocab_size=vocab_size,
        d_embed=32,
        d_hidden=d_hidden,
        d_read=32,
        kv_capacity=4096,
        kv_top_k=4,
        replay_capacity=4096,
        replay_alpha=0.6,
        replay_batch_size=8,
        replay_every=1,
        lr=1e-3,
        weight_decay=5e-4,
        store_threshold=0.0,
        training_mode="transition",
        bptt_window=1,
        seed=seed,
        device=device,
        experiment_id="c2c3-diagnostic",
        run_id=0,
    )
    return NN0Trainer(cfg)


def _clone_trainer(source: NN0Trainer, new_seed: Optional[int] = None) -> NN0Trainer:
    snap = source.snapshot()
    seed = new_seed if new_seed is not None else source.cfg.seed
    clone = _build_trainer(seed, source.cfg.vocab_size, source.cfg.d_hidden, str(source.device))
    clone.restore(snap)
    return clone


def _parameter_checksum(trainer: NN0Trainer) -> str:
    return trainer.parameter_hash()


def _parameter_delta(trainer_a: NN0Trainer, trainer_b: NN0Trainer) -> float:
    sa = trainer_a.model.state_dict()
    sb = trainer_b.model.state_dict()
    total = 0.0
    for k in sa:
        diff = (sa[k].float() - sb[k].float()).abs().sum().item()
        total += diff
    return total


def _train_on_tokens(
    trainer: NN0Trainer,
    tokens: List[int],
    source_id: str,
) -> int:
    steps = 0
    for i in range(len(tokens) - 1):
        x_val = tokens[i]
        y_val = tokens[i + 1]
        trainer.step(x_val, y_val, source_id=source_id)
        steps += 1
    return steps


def _evaluate_probe_nll(
    trainer: NN0Trainer,
    instances: List[AffineMSATInstance],
    num_keys: int,
) -> Tuple[float, float]:
    trainer.model.eval()
    total_nll = 0.0
    correct = 0
    count = 0
    key_offset = HEADER_VOCAB_SIZE
    with torch.no_grad():
        for inst in instances:
            probe = inst.probes[0]
            context_tokens = inst.render_tokens(num_keys)
            query_tokens = list(probe.query_context)
            full_context = context_tokens + query_tokens
            x = torch.tensor([full_context], dtype=torch.long, device=trainer.device)
            h = trainer._zero_h(1)
            logits, _ = trainer.model(x, h, None)
            last_logits = logits[0, -1, :]
            probs = F.softmax(last_logits, dim=-1)
            target = probe.target
            nll = -math.log(max(probs[target].item(), 1e-15))
            total_nll += nll
            pred = int(last_logits.argmax().item())
            if pred == target:
                correct += 1
            count += 1
    trainer.model.train()
    if count == 0:
        return 0.0, 0.0
    return total_nll / count, correct / count


def run_c2_exposure_experiment(
    corpus: AffineMSATCorpus,
    eval_instances: List[AffineMSATInstance],
    seed: int = 300,
    d_hidden: int = 32,
    device: str = "cpu",
) -> C2ExperimentResult:
    set_global_seed(seed)
    vocab_size = corpus.vocab_size
    base = _build_trainer(seed, vocab_size, d_hidden, device)
    base_hash = _parameter_checksum(base)

    trainer_a = _clone_trainer(base, new_seed=seed)
    trainer_a.freeze_parameters()
    hash_a_before = _parameter_checksum(trainer_a)

    trainer_b = _clone_trainer(base, new_seed=seed)
    hash_b_before = _parameter_checksum(trainer_b)

    trainer_c = _clone_trainer(base, new_seed=seed)
    hash_c_before = _parameter_checksum(trainer_c)

    assert hash_a_before == hash_b_before == hash_c_before == base_hash

    train_inst = corpus.instances[0]
    live_tokens = train_inst.render_tokens(corpus.num_keys)
    key_offset = HEADER_VOCAB_SIZE
    op_offset = HEADER_VOCAB_SIZE + corpus.num_keys
    distractor_tokens: List[int] = []
    for ep in train_inst.distractor_episodes:
        distractor_tokens.extend(ep.to_tokens(key_offset, op_offset))

    assert len(live_tokens) == len(distractor_tokens)

    steps_a = 0
    steps_b = _train_on_tokens(trainer_b, distractor_tokens, source_id="arm_b_distractor")
    steps_c = _train_on_tokens(trainer_c, live_tokens, source_id="arm_c_live")

    assert steps_b == steps_c
    assert steps_b == len(live_tokens) - 1

    hash_a_after = _parameter_checksum(trainer_a)
    hash_b_after = _parameter_checksum(trainer_b)
    hash_c_after = _parameter_checksum(trainer_c)

    delta_a = _parameter_delta(base, trainer_a)
    delta_b = _parameter_delta(base, trainer_b)
    delta_c = _parameter_delta(base, trainer_c)

    nll_a, acc_a = _evaluate_probe_nll(trainer_a, eval_instances, corpus.num_keys)
    nll_b, acc_b = _evaluate_probe_nll(trainer_b, eval_instances, corpus.num_keys)
    nll_c, acc_c = _evaluate_probe_nll(trainer_c, eval_instances, corpus.num_keys)

    return C2ExperimentResult(
        arm_a=C2ArmResult(
            arm_name="A_frozen",
            nll=nll_a,
            accuracy=acc_a,
            parameter_hash_before=hash_a_before,
            parameter_hash_after=hash_a_after,
            parameter_delta=delta_a,
            tokens_seen=len(live_tokens),
            optimizer_steps=steps_a,
            frozen=True,
        ),
        arm_b=C2ArmResult(
            arm_name="B_distractor",
            nll=nll_b,
            accuracy=acc_b,
            parameter_hash_before=hash_b_before,
            parameter_hash_after=hash_b_after,
            parameter_delta=delta_b,
            tokens_seen=len(distractor_tokens),
            optimizer_steps=steps_b,
            frozen=False,
        ),
        arm_c=C2ArmResult(
            arm_name="C_live",
            nll=nll_c,
            accuracy=acc_c,
            parameter_hash_before=hash_c_before,
            parameter_hash_after=hash_c_after,
            parameter_delta=delta_c,
            tokens_seen=len(live_tokens),
            optimizer_steps=steps_c,
            frozen=False,
        ),
        seed=seed,
        num_keys=corpus.num_keys,
        vocab_size=vocab_size,
    )


def run_c3_memory_zero_intervention(
    corpus: AffineMSATCorpus,
    eval_instances: List[AffineMSATInstance],
    d_hidden_list: Tuple[int, ...] = (8, 16, 32, 64, 128),
    seed: int = 301,
    device: str = "cpu",
) -> C3ExperimentResult:
    conditions: List[C3ConditionResult] = []
    vocab_size = corpus.vocab_size
    train_inst = corpus.instances[0]
    train_tokens = train_inst.render_tokens(corpus.num_keys)

    for d_hidden in d_hidden_list:
        set_global_seed(seed)
        trainer = _build_trainer(seed, vocab_size, d_hidden, device)
        _train_on_tokens(trainer, train_tokens, source_id="c3_train")
        param_hash = _parameter_checksum(trainer)

        trainer_full = _clone_trainer(trainer, new_seed=seed)
        nll_full, acc_full = _evaluate_probe_nll(trainer_full, eval_instances, corpus.num_keys)
        conditions.append(C3ConditionResult(
            d_hidden=d_hidden,
            num_keys=corpus.num_keys,
            memory_condition="FULL_MEMORY",
            nll=nll_full,
            accuracy=acc_full,
            parameter_hash=param_hash,
            memory_size=len(trainer_full.memory),
            replay_size=len(trainer_full.replay),
            hidden_state_is_zero=False,
        ))

        trainer_zero = _clone_trainer(trainer, new_seed=seed)
        trainer_zero.clear_external_memory()
        trainer_zero.clear_replay()
        trainer_zero.reset_state()

        assert len(trainer_zero.memory) == 0
        assert len(trainer_zero.replay) == 0
        assert trainer_zero.last_h is None

        nll_zero, acc_zero = _evaluate_probe_nll(trainer_zero, eval_instances, corpus.num_keys)
        conditions.append(C3ConditionResult(
            d_hidden=d_hidden,
            num_keys=corpus.num_keys,
            memory_condition="MEMORY_ZERO",
            nll=nll_zero,
            accuracy=acc_zero,
            parameter_hash=param_hash,
            memory_size=len(trainer_zero.memory),
            replay_size=len(trainer_zero.replay),
            hidden_state_is_zero=True,
        ))

    return C3ExperimentResult(conditions=conditions, seed=seed)

</content>