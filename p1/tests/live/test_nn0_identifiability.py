"""NN-0 identifiability acceptance suite (T1-T14).

Covers the architectural repairs required to make the future capacity-scaling
experiment (``d_hidden`` swept, ``M`` manipulated) scientifically identifiable:
configurable hidden dimension, non-degenerate memory addressing under
``do(h=0)``, optimizer reset, parameter freeze, and deep state snapshots.

Nothing here trains a decisive arm, seals a protocol, or consumes seeds 200-209.
"""

import copy
from pathlib import Path

import pytest
import torch

from p1.live.neural.nn0.nucleus import NN0Config, NN0Trainer, _hash_state

D_HIDDENS = (8, 16, 32, 64, 128)


def cfg(d_hidden: int = 32, seed: int = 0, device: str = "cpu") -> NN0Config:
    return NN0Config(
        vocab_size=32,
        d_embed=16,
        d_hidden=d_hidden,
        d_read=16,
        kv_capacity=256,
        kv_top_k=4,
        replay_capacity=256,
        replay_batch_size=8,
        seed=seed,
        device=device,
    )


def expected_params(c: NN0Config) -> int:
    """Closed-form parameter count, derived independently of the model."""
    emb = c.vocab_size * c.d_embed
    key = c.d_hidden * c.d_read + c.d_read
    gin = c.d_embed + c.d_read
    gru = 3 * c.d_hidden * gin + 3 * c.d_hidden * c.d_hidden + 2 * 3 * c.d_hidden
    out = c.d_hidden * c.vocab_size + c.vocab_size
    return emb + key + gru + out


def train_a_little(t: NN0Trainer, n: int = 12, seed: int = 0) -> None:
    for i in range(n):
        t.step((i * 7 + seed) % t.cfg.vocab_size, (i * 5 + 3) % t.cfg.vocab_size)


# --- T1: every required d_hidden constructs with a deterministic param count --


@pytest.mark.parametrize("d_hidden", D_HIDDENS)
def test_t1_configurable_hidden_dimension(d_hidden: int) -> None:
    t = NN0Trainer(cfg(d_hidden=d_hidden))
    assert t.cfg.d_hidden == d_hidden  # not clamped or reinterpreted
    assert t.model.d_hidden == d_hidden
    assert t.parameter_count() == expected_params(t.cfg)
    assert t._zero_h(1).shape == (1, 1, d_hidden)
    train_a_little(t, 3)


def test_t1b_parameter_count_is_strictly_monotone_in_capacity() -> None:
    counts = [NN0Trainer(cfg(d_hidden=d)).parameter_count() for d in D_HIDDENS]
    assert counts == sorted(counts) and len(set(counts)) == len(counts)


# --- T2: deterministic initialization at every d_hidden -----------------------


@pytest.mark.parametrize("d_hidden", D_HIDDENS)
def test_t2_deterministic_initialization(d_hidden: int) -> None:
    a = NN0Trainer(cfg(d_hidden=d_hidden, seed=21))
    b = NN0Trainer(cfg(d_hidden=d_hidden, seed=21))
    c = NN0Trainer(cfg(d_hidden=d_hidden, seed=22))
    assert a.parameter_hash() == b.parameter_hash()
    assert a.parameter_hash() != c.parameter_hash()
    # the frozen address projection is seeded too, and differs across seeds
    assert torch.equal(a.model.key_token_proj, b.model.key_token_proj)
    assert not torch.equal(a.model.key_token_proj, c.model.key_token_proj)


# --- T3: checkpoint / reload equivalence at every d_hidden --------------------


@pytest.mark.parametrize("d_hidden", D_HIDDENS)
def test_t3_checkpoint_reload_equivalence(tmp_path: Path, d_hidden: int) -> None:
    t = NN0Trainer(cfg(d_hidden=d_hidden, seed=5))
    train_a_little(t)
    ck = t.save_checkpoint(tmp_path / f"ck{d_hidden}")

    import json

    meta = json.loads((ck / "meta.json").read_text())
    assert meta["d_hidden"] == d_hidden  # capacity is recorded, not inferred
    assert meta["cfg"]["d_hidden"] == d_hidden
    assert meta["parameter_count"] == expected_params(t.cfg)

    r = NN0Trainer.from_checkpoint(ck)
    assert r.cfg.d_hidden == d_hidden
    assert r.parameter_hash() == t.parameter_hash()
    assert r.parameter_count() == t.parameter_count()
    assert len(r.memory) == len(t.memory) and len(r.replay) == len(t.replay)
    assert torch.equal(r.model.key_token_proj, t.model.key_token_proj)


def test_t3b_checkpoint_refuses_a_mismatched_capacity(tmp_path: Path) -> None:
    import json

    t = NN0Trainer(cfg(d_hidden=32, seed=1))
    ck = t.save_checkpoint(tmp_path / "ck")
    meta = json.loads((ck / "meta.json").read_text())
    meta["d_hidden"] = 64  # a capacity claim the weights do not support
    (ck / "meta.json").write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="d_hidden"):
        NN0Trainer.from_checkpoint(ck)


# --- T4: CPU/CUDA parity ------------------------------------------------------


@pytest.mark.parametrize("d_hidden", D_HIDDENS)
def test_t4_cpu_cuda_parity(d_hidden: int) -> None:
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    c = NN0Trainer(cfg(d_hidden=d_hidden, seed=2, device="cpu"))
    g = NN0Trainer(cfg(d_hidden=d_hidden, seed=2, device="cuda"))
    assert c.parameter_hash() == g.parameter_hash()
    assert c.parameter_count() == g.parameter_count()

    c.model.eval()
    g.model.eval()
    xs = torch.tensor([[1, 4, 9, 2]])
    with torch.no_grad():
        lc, _ = c.model(xs, c._zero_h(1), None)
        lg, _ = g.model(xs.cuda(), g._zero_h(1), None)
    assert (lc - lg.cpu()).abs().max().item() < 1e-4

    kc = c.model.project_key_token(torch.tensor([3, 7]))
    kg = g.model.project_key_token(torch.tensor([3, 7], device="cuda"))
    assert (kc - kg.cpu()).abs().max().item() < 1e-5


# --- T5: optimizer reset actually clears AdamW state --------------------------


def test_t5_reset_optimizer_clears_adamw_state() -> None:
    t = NN0Trainer(cfg(seed=3))
    train_a_little(t)
    assert not t.optimizer_state_is_empty()
    state = t.optim.state_dict()["state"]
    assert any("exp_avg" in s for s in state.values())

    theta_before = t.parameter_hash()
    t.reset_optimizer()

    assert t.optimizer_state_is_empty()
    assert t.optim.state_dict()["state"] == {}
    assert all(p.grad is None for p in t.model.parameters())
    # an optimizer reset is not a parameter reset
    assert t.parameter_hash() == theta_before


def test_t5b_reset_optimizer_gives_a_deterministic_identical_update() -> None:
    """train -> snapshot -> reset optimizer -> identical update, twice, exactly.

    The update is restored from a full snapshot rather than θ alone: ``step``
    also draws a replay sample and appends to KV, so restoring only θ would let
    replay RNG and memory drift confound the optimizer contrast.
    """
    t = NN0Trainer(cfg(seed=4))
    train_a_little(t, 20)
    snap = t.snapshot()
    theta = t.parameter_hash()

    hashes = []
    for _ in range(2):
        t.restore(snap)
        assert t.parameter_hash() == theta  # restore is exact
        t.reset_optimizer()
        assert t.optimizer_state_is_empty()  # and the reset really cleared it
        t.step(5, 9)
        hashes.append(t.parameter_hash())
    assert hashes[0] == hashes[1]

    # the optimizer state was causally active: the same update from the same θ
    # lands elsewhere when AdamW moments and step counters are left in place
    t.restore(snap)
    t.step(5, 9)
    assert t.parameter_hash() != hashes[0]


# --- T6 / T12: freeze prevents mutation, survives prediction ------------------


def test_t6_freeze_parameters_prevents_mutation() -> None:
    t = NN0Trainer(cfg(seed=6))
    train_a_little(t)
    t.freeze_parameters()

    assert t.parameters_frozen
    assert all(not p.requires_grad for p in t.model.parameters())
    assert all(p.grad is None for p in t.model.parameters())

    before = t.parameter_hash()
    with pytest.raises(AssertionError, match="frozen"):
        t.step(1, 2)
    with pytest.raises(AssertionError, match="frozen"):
        t.step_sequence([1, 2, 3])
    assert t.parameter_hash() == before

    # a stale optimizer step cannot move frozen weights either
    t.optim.step()
    assert t.parameter_hash() == before

    t.unfreeze_parameters()
    assert not t.parameters_frozen
    assert all(p.requires_grad for p in t.model.parameters())
    t.step(1, 2)
    assert t.parameter_hash() != before  # trainability really came back


def test_t12_parameter_checksum_unchanged_across_frozen_prediction() -> None:
    t = NN0Trainer(cfg(seed=7))
    train_a_little(t)
    t.freeze_parameters()
    before = t.parameter_hash()

    p1 = t.predict_context([1, 2, 3])
    t.probe([1, 2, 3], [2, 3, 4])
    p2 = t.predict_context([1, 2, 3])

    assert t.parameter_hash() == before
    assert torch.equal(p1, p2)  # frozen prediction is also repeatable
    assert t.parameters_frozen  # the freeze survived the evaluation calls


# --- T7 / T8: exact hidden and memory resets ----------------------------------


def test_t7_hidden_reset_is_exactly_zero() -> None:
    t = NN0Trainer(cfg(seed=8))
    train_a_little(t)
    assert t.last_h is not None and t.last_h.abs().sum() > 0

    t.reset_state()
    assert t.last_h is None
    h = t._zero_h(1)
    assert torch.count_nonzero(h) == 0 and h.shape == (1, 1, t.cfg.d_hidden)

    t.reset_episode()
    assert t.last_h is None


def test_t8_memory_reset_is_exactly_empty() -> None:
    t = NN0Trainer(cfg(seed=9))
    train_a_little(t)
    assert len(t.memory) > 0

    theta = t.parameter_hash()
    replay_n = len(t.replay)
    t.clear_external_memory()

    assert len(t.memory) == 0
    assert t.memory.keys == [] and t.memory.values == []
    assert t.memory.outcomes == [] and t.memory.errors == []
    assert t.memory.source_ids == [] and t.memory.dropped == 0
    assert t.memory.read(torch.zeros(1, t.cfg.d_read), 4) is None
    # clearing M touches nothing else
    assert t.parameter_hash() == theta and len(t.replay) == replay_n


# --- T9: the address stays query-dependent under do(h=0) ----------------------


def test_t9_key_addressing_is_query_dependent_at_h_zero() -> None:
    t = NN0Trainer(cfg(seed=10))
    h0 = t._zero_h(1)

    # the documented defect, retained as the contrast
    assert torch.count_nonzero(t.model.project_key(h0)) == 0

    tokens = torch.tensor([1, 2, 3, 4, 5])
    keys = t.model.project_key_token(tokens)
    assert keys.shape == (5, t.cfg.d_read)
    assert torch.count_nonzero(keys) > 0
    # distinct key tokens must address distinct slots
    for i in range(5):
        for j in range(i + 1, 5):
            assert not torch.allclose(keys[i], keys[j], atol=1e-6)
    # and the same token always addresses the same slot
    assert torch.equal(keys[0], t.model.project_key_token(torch.tensor([1]))[0])


def test_t9b_memory_read_at_h_zero_differs_by_key_token() -> None:
    """The real failure the h=0 intervention had to survive: a key-blind read."""
    t = NN0Trainer(cfg(seed=11))
    for token, value in ((3, 10), (4, 20), (5, 30)):
        t.memory.write(
            t.model.project_key_token(torch.tensor([token])),
            t.model.embedding(torch.tensor([value])),
            value,
            0.5,
        )

    reads = [t.memory.read(t.model.project_key_token(torch.tensor([tok])), 1) for tok in (3, 4, 5)]
    assert not torch.allclose(reads[0], reads[1], atol=1e-6)
    assert not torch.allclose(reads[1], reads[2], atol=1e-6)

    # the h-conditioned address, by contrast, is one constant for every query
    blind = [t.memory.read(t.model.project_key(t._zero_h(1)), 1) for _ in range(3)]
    assert torch.allclose(blind[0], blind[1], atol=1e-9)


# --- T10: two states differing only in M are identical outside M --------------


def test_t10_states_differing_only_in_memory() -> None:
    a = NN0Trainer(cfg(seed=12))
    train_a_little(a, 15)

    b = NN0Trainer(cfg(seed=12))
    b.restore(a.snapshot())
    b.clear_external_memory()  # the sole manipulated variable

    assert len(a.memory) > 0 and len(b.memory) == 0
    assert a.parameter_hash() == b.parameter_hash()
    assert a.step_count == b.step_count
    assert torch.equal(a.last_h, b.last_h)
    assert a.replay.digest_rows() == b.replay.digest_rows()
    assert a.cfg.d_hidden == b.cfg.d_hidden
    assert a.history == b.history

    # M is the only channel that can move the prediction
    ctx = [1, 2, 3]
    assert torch.equal(
        a.predict_context(ctx, use_external_memory=False),
        b.predict_context(ctx, use_external_memory=False),
    )


# --- T11: snapshot / restore round-trip --------------------------------------


def test_t11_snapshot_restore_round_trip() -> None:
    t = NN0Trainer(cfg(seed=13))
    train_a_little(t, 15)
    snap = t.snapshot()
    baseline = [t.step(i % 32, (i + 1) % 32)["err"] for i in range(6)]
    after = t.parameter_hash()

    t.restore(snap)
    replayed = [t.step(i % 32, (i + 1) % 32)["err"] for i in range(6)]

    assert replayed == pytest.approx(baseline, abs=1e-9)
    assert t.parameter_hash() == after  # deterministic to the bit


def test_t11b_snapshot_is_deep_not_aliased() -> None:
    """A snapshot must not mutate when the live trainer moves on."""
    t = NN0Trainer(cfg(seed=14))
    train_a_little(t, 10)
    snap = t.snapshot()
    frozen = copy.deepcopy(snap)

    train_a_little(t, 10, seed=5)
    t.clear_external_memory()

    assert len(snap["memory"]["keys"]) == len(frozen["memory"]["keys"]) > 0
    assert all(torch.equal(a, b) for a, b in zip(snap["memory"]["keys"], frozen["memory"]["keys"]))
    assert snap["memory"]["errors"] == frozen["memory"]["errors"]
    assert snap["replay"]["items"] == frozen["replay"]["items"]
    assert snap["step_count"] == frozen["step_count"] != t.step_count


def test_t11c_restore_refuses_a_foreign_capacity() -> None:
    small = NN0Trainer(cfg(d_hidden=16, seed=15))
    big = NN0Trainer(cfg(d_hidden=64, seed=15))
    with pytest.raises(ValueError, match="d_hidden"):
        big.restore(small.snapshot())


def test_t11d_snapshot_carries_freeze_and_optimizer_state() -> None:
    t = NN0Trainer(cfg(seed=16))
    train_a_little(t)
    t.freeze_parameters()
    snap = t.snapshot()

    t.unfreeze_parameters()
    t.reset_optimizer()
    assert t.optimizer_state_is_empty() and not t.parameters_frozen

    t.restore(snap)
    assert t.parameters_frozen
    assert not t.optimizer_state_is_empty()  # AdamW moments came back


# --- T13: no stale cache survives a memory mutation ---------------------------


def test_t13_no_stale_cache_survives_memory_mutation() -> None:
    t = NN0Trainer(cfg(seed=17))
    q = t.model.project_key_token(torch.tensor([3]))

    t.memory.write(q, t.model.embedding(torch.tensor([10])), 10, 0.5)
    first = t.memory.read(q, 1).clone()
    assert t.memory._stack_cache is not None  # the cache is populated

    # a write must invalidate it
    t.memory.write(
        t.model.project_key_token(torch.tensor([4])),
        t.model.embedding(torch.tensor([20])),
        20,
        0.5,
    )
    assert t.memory._stack_cache is None
    assert not torch.allclose(t.memory.read(q, 2), first, atol=1e-6)

    # so must a clear
    t.memory.read(q, 1)
    t.clear_external_memory()
    assert t.memory._stack_cache is None
    assert t.memory.read(q, 1) is None

    # and so must a load
    t.memory.write(q, t.model.embedding(torch.tensor([10])), 10, 0.5)
    t.memory.read(q, 1)
    t.memory.load_state_dict(t.memory.state_dict())
    assert t.memory._stack_cache is None


def test_t13b_restore_leaves_no_stale_memory_cache() -> None:
    t = NN0Trainer(cfg(seed=18))
    train_a_little(t)
    snap = t.snapshot()
    q = t.model.project_key_token(torch.tensor([3]))
    t.memory.read(q, 4)

    t.restore(snap)
    assert t.memory._stack_cache is None
