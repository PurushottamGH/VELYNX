"""NN-0 nucleus T0 test.

Transaction T0 of ``outputs/P1_LIVE_NN_NEURAL_ARCHITECTURE.md`` (Track C):

    * runs one stream of 1,024 tokens
    * asserts deterministic given seed
    * asserts learnable (held-out NLL < init chance)
    * asserts VRAM < 150 MB
    * records probe P1 (before experience) at init
"""

import json
import math
import random
from pathlib import Path

import pytest
import torch

from p1.live.neural.nn0.nucleus import (
    CHECKPOINT_VERSION,
    NN0_ARCH,
    NN0Config,
    NN0Trainer,
    ReplayReservoir,
    _hash_state,
)

STREAM_LEN = 1024
VAL_LEN = 64


def make_stream(n: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    period = rng.sample(range(1, 8), 5)
    return [period[i % len(period)] for i in range(n)]


def make_config(seed: int = 0, device: str = "cpu") -> NN0Config:
    return NN0Config(
        vocab_size=128,
        d_embed=32,
        d_hidden=128,
        kv_capacity=1024,
        kv_top_k=4,
        replay_capacity=1024,
        replay_batch_size=32,
        replay_every=1,
        lr=1e-3,
        weight_decay=5e-4,
        store_threshold=0.0,
        seed=seed,
        device=device,
    )


def train_on_stream(
    trainer: NN0Trainer, stream: list[int], n: int
) -> list[float]:
    errs = []
    for t in range(n - 1):
        info = trainer.step(stream[t], stream[t + 1])
        errs.append(info["err"])
    return errs


def probe_on_stream(trainer: NN0Trainer, stream: list[int], offset: int) -> float:
    xs = stream[offset:-1]
    ys = stream[offset + 1:]
    return trainer.probe(xs, ys)["nll_eval"]


def test_learnable_with_p1_before(tmp_path: Path) -> None:
    stream = make_stream(STREAM_LEN, seed=7)
    trainer = NN0Trainer(make_config(seed=0))

    nll_before = probe_on_stream(trainer, stream, STREAM_LEN - VAL_LEN)
    assert math.isfinite(nll_before)
    assert nll_before >= math.log(128) - 0.75  # at/near chance at init

    errs = train_on_stream(trainer, stream, STREAM_LEN - VAL_LEN)
    nll_after = probe_on_stream(trainer, stream, STREAM_LEN - VAL_LEN)

    assert len(errs) == STREAM_LEN - VAL_LEN - 1
    assert nll_after < nll_before
    assert nll_after < math.log(5)  # beats the marginal baseline

    assert len(trainer.memory) == STREAM_LEN - VAL_LEN - 1
    assert len(trainer.replay) == STREAM_LEN - VAL_LEN - 1
    assert trainer.step_count == STREAM_LEN - VAL_LEN - 1


def test_deterministic_given_seed() -> None:
    stream = make_stream(STREAM_LEN, seed=3)
    a = NN0Trainer(make_config(seed=42))
    b = NN0Trainer(make_config(seed=42))

    errs_a = train_on_stream(a, stream, STREAM_LEN - VAL_LEN)
    errs_b = train_on_stream(b, stream, STREAM_LEN - VAL_LEN)

    assert errs_a == pytest.approx(errs_b, abs=1e-6)
    assert _hash_state(a.model.state_dict()) == _hash_state(b.model.state_dict())
    assert a.parameter_count() == b.parameter_count()


def test_restart_equivalence(tmp_path: Path) -> None:
    stream = make_stream(STREAM_LEN, seed=11)
    trainer = NN0Trainer(make_config(seed=5))
    train_on_stream(trainer, stream, STREAM_LEN - VAL_LEN)
    ckpt = trainer.save_checkpoint(tmp_path / "ckpt")
    assert (ckpt / "meta.json").exists()

    restored = NN0Trainer.from_checkpoint(ckpt)
    assert restored.step_count == trainer.step_count
    assert _hash_state(restored.model.state_dict()) == _hash_state(
        trainer.model.state_dict()
    )
    assert len(restored.memory) == len(trainer.memory)
    assert len(restored.replay) == len(trainer.replay)

    n1 = probe_on_stream(trainer, stream, STREAM_LEN - VAL_LEN)
    n2 = probe_on_stream(restored, stream, STREAM_LEN - VAL_LEN)
    assert n1 == pytest.approx(n2, abs=1e-6)

    t = STREAM_LEN - VAL_LEN
    e1 = trainer.step(stream[t], stream[t + 1])["err"]
    e2 = restored.step(stream[t], stream[t + 1])["err"]
    assert e1 == pytest.approx(e2, abs=1e-6)


def test_parameter_budget() -> None:
    trainer = NN0Trainer(make_config())
    assert trainer.parameter_count() <= 110_000


def test_forward_pass() -> None:
    trainer = NN0Trainer(make_config())
    model = trainer.model
    x = torch.tensor([[0, 1, 2, 3], [4, 5, 6, 7]])
    h = torch.zeros(1, 2, trainer.cfg.d_hidden)
    read = torch.zeros(2, trainer.cfg.d_read)

    logits, h_out = model(x, h, read)
    assert logits.shape == (2, 4, trainer.cfg.vocab_size)
    assert h_out.shape == (2, 4, trainer.cfg.d_hidden)
    assert torch.allclose(logits, model.readout(h_out), atol=1e-6)
    probs = torch.softmax(logits, dim=-1)
    assert torch.allclose(probs.sum(dim=-1), torch.ones(2, 4), atol=1e-6)
    assert not torch.isnan(logits).any()

    logits_no_read, h_out_no_read = model(x, h, None)
    assert torch.isnan(logits_no_read).sum() == 0
    assert logits_no_read.shape == logits.shape

    key = model.project_key(h)
    assert key.shape == (2, trainer.cfg.d_read)

    # non-parametric memory invariant: the read path never carries a gradient
    trainer.memory.write(
        key, model.embedding(torch.tensor([3, 5])), 3, 0.5
    )
    mem_read = trainer.memory.read(model.project_key(h), trainer.cfg.kv_top_k)
    assert mem_read is not None
    assert mem_read.shape == (2, trainer.cfg.d_embed)
    assert not mem_read.requires_grad

    grad_params = [p for p in model.parameters() if p.requires_grad]
    assert len(grad_params) > 0
    assert sum(p.numel() for p in grad_params) == trainer.parameter_count()


def test_gradient_update() -> None:
    trainer = NN0Trainer(make_config(seed=3))
    before = _hash_state(trainer.model.state_dict())

    errs = []
    for _ in range(10):
        info = trainer.step(0, 5)
        errs.append(info["err"])

    after = _hash_state(trainer.model.state_dict())
    assert after != before  # a gradient update moved at least one parameter
    assert errs[-1] < errs[0]  # the fixed mapping x=0 -> y=5 became more likely
    assert any(p.grad is not None for p in trainer.model.parameters())


def test_deterministic_initialization() -> None:
    a = NN0Trainer(make_config(seed=21))
    b = NN0Trainer(make_config(seed=21))
    c = NN0Trainer(make_config(seed=22))

    assert _hash_state(a.model.state_dict()) == _hash_state(b.model.state_dict())
    assert _hash_state(a.model.state_dict()) != _hash_state(c.model.state_dict())

    h_a = torch.zeros(1, 1, a.cfg.d_hidden)
    x = torch.tensor([[7]])
    lg_a, _ = a.model(x, h_a, None)
    lg_b, _ = b.model(x, h_a, None)
    assert torch.equal(lg_a, lg_b)


def test_save_reload_equivalence(tmp_path: Path) -> None:
    stream = make_stream(512, seed=9)
    trainer = NN0Trainer(make_config(seed=9))
    train_on_stream(trainer, stream, 300)
    ckpt = trainer.save_checkpoint(tmp_path / "ckpt")

    files = sorted(p.name for p in ckpt.iterdir())
    assert files == [
        "episodic.pt",
        "lineage.json",
        "meta.json",
        "model.pt",
        "optim.pt",
        "replay.pt",
        "rng.pt",
    ]
    meta = json.loads((ckpt / "meta.json").read_text())
    assert meta["arch"] == NN0_ARCH
    assert meta["version"] == CHECKPOINT_VERSION
    assert meta["params_hash"] == _hash_state(trainer.model.state_dict())
    assert meta["step"] == trainer.step_count
    lineage = json.loads((ckpt / "lineage.json").read_text())
    assert lineage["last_step"] == trainer.step_count

    restored = NN0Trainer.from_checkpoint(ckpt)
    assert _hash_state(restored.model.state_dict()) == _hash_state(
        trainer.model.state_dict()
    )
    assert len(restored.memory) == len(trainer.memory)
    assert len(restored.replay) == len(trainer.replay)

    # frozen-θ probes are byte-identical before/after reload
    p1 = probe_on_stream(trainer, stream, 400)
    p2 = probe_on_stream(restored, stream, 400)
    assert p1 == pytest.approx(p2, abs=1e-6)

    # continuation from the same RNG state is identical
    e1 = [trainer.step(stream[t], stream[t + 1])["err"] for t in range(300, 310)]
    e2 = [restored.step(stream[t], stream[t + 1])["err"] for t in range(300, 310)]
    assert e1 == pytest.approx(e2, abs=1e-6)


def test_replay_reservoir() -> None:
    capacity = 64

    # reservoir eviction: bounded, never grows past capacity
    evict = ReplayReservoir(capacity=8, alpha=0.6, seed=5)
    for i in range(32):
        evict.push(i, i % 128, 0.0)
    assert len(evict) == 8

    # priority population: exactly `capacity` items, one with a huge error
    r = ReplayReservoir(capacity=capacity, alpha=20, seed=1)
    for i in range(capacity):
        r.push(0, i, 100.0 if i == 63 else 0.0)
    assert len(r) == capacity  # bounded by capacity

    for n in (0, 1, capacity // 2, 2 * capacity):
        sample = r.sample(n)
        expected = min(n, len(r))
        assert len(sample) == expected
        picked = [it[1] for it in sample]
        assert len(picked) == len(set(picked))  # no replacement

    assert r.sample(0) == []

    # error-ranked priority: the single high-error item dominates draws
    counts = {i: 0 for i in range(capacity)}
    for _ in range(400):
        picked = r.sample(1)[0][1]
        counts[picked] += 1
    assert counts[63] > 60  # deterministically seeded; ~107 on this host
    assert counts[63] > counts[0]  # strictly above a zero-error item

    # state round-trip reproduces the exact draw sequence
    r2 = ReplayReservoir(capacity=capacity, alpha=20, seed=0)
    r2.load_state_dict(r.state_dict())
    s1 = [r.sample(4) for _ in range(10)]
    s2 = [r2.sample(4) for _ in range(10)]
    assert s1 == s2


def test_cuda_cpu_execution() -> None:
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")

    cpu = NN0Trainer(make_config(seed=2, device="cpu"))
    gpu = NN0Trainer(make_config(seed=2, device="cuda"))

    # fresh-init forward parity: identical weights, near-identical math
    cpu.model.eval()
    gpu.model.eval()
    xs = random.Random(2).sample(range(128), 8)
    with torch.no_grad():
        lg_cpu, _ = cpu.model(
            torch.tensor([xs]), torch.zeros(1, 1, cpu.cfg.d_hidden)
        )
        lg_gpu, _ = gpu.model(
            torch.tensor([xs], device="cuda"),
            torch.zeros(1, 1, gpu.cfg.d_hidden, device="cuda"),
        )
    diff = (lg_cpu - lg_gpu.cpu()).abs().max().item()
    assert diff < 1e-4

    # online updates run on CUDA and learn
    stream = make_stream(256, seed=4)
    gpu = NN0Trainer(make_config(seed=1, device="auto"))
    assert next(iter(gpu.model.parameters())).device.type == "cuda"
    first = gpu.step(stream[0], stream[1])["err"]
    errs = [first]
    for t in range(1, 255):
        errs.append(gpu.step(stream[t], stream[t + 1])["err"])
    assert all(math.isfinite(e) for e in errs)
    assert errs[-1] < errs[0]
    assert any(p.grad is not None for p in gpu.model.parameters())
    assert len(gpu.replay) == len(gpu.memory) == 255


@pytest.mark.slow
def test_vram_budget_under_150mb() -> None:
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available")
    torch.cuda.reset_peak_memory_stats()
    stream = make_stream(256, seed=1)
    trainer = NN0Trainer(make_config(device="auto"))
    train_on_stream(trainer, stream, 256)
    peak = torch.cuda.max_memory_allocated() / (1024 * 1024)
    assert peak < 150.0
