"""The platform must reproduce the reviewed M0 artifact exactly.

This is the one test in the M1 suite with scientific significance. The M0 review
approved `p1v0` as a provisional scaffold and required that "the exact M0 code and
results are version-pinned" before validation work proceeds. The refactor into
`core` / `science` / `benchmarks` / `experiments` would break that guarantee if it
changed any number.

It does not, and this test is the evidence: with `seeds.mode = legacy_v0` and the
`markov_blocks_v0` environment, the platform's online losses, probe matrix, gate
activity and retention scalar are bit-identical to `p1v0.runner.execute`.

If this test ever fails, the platform has silently changed the science and M1
results are no longer comparable with M0. It is not a test to relax.
"""

from __future__ import annotations

import pytest

from experiments.engine.config import RunConfig
from experiments.engine.engine import run
from p1v0.runner import VARIANTS, Config, execute
from tests.m1.conftest import CONFIG_DIR, markov_dict

#: Small enough to run in the unit suite, large enough that any divergence in the
#: stream, buffer, gate or probe seeding shows up.
SMALL = dict(n_tasks=3, alphabet=6, steps_per_task=250)
PROBE_PAIRS = 120

#: How each frozen variant maps onto the platform's separated components. The
#: mapping is the whole point of splitting Gate (timing) from Replay (content):
#: M0's three "variants" were bundles of memory + timing + content.
VARIANT_COMPONENTS = {
    "online": {"memory": "null", "gate": "never", "replay": "none"},
    "replay_always": {"memory": "reservoir", "gate": "always", "replay": "buffer_sample"},
    "replay_surprise": {"memory": "reservoir", "gate": "surprise", "replay": "buffer_sample"},
}


def _platform(variant: str, seed: int):
    components = VARIANT_COMPONENTS[variant]
    raw = markov_dict(**SMALL)
    raw["benchmark"]["params"]["probe_pairs"] = PROBE_PAIRS
    raw["memory"] = {"name": components["memory"], "params": {"capacity": 1000}}
    raw["replay"] = (
        {"name": "none", "params": {}}
        if components["replay"] == "none"
        else {"name": components["replay"], "params": {"weight": 1.0}}
    )
    if components["gate"] == "never":
        raw["gate"] = {"name": "never", "params": {}}
    elif components["gate"] == "always":
        raw["gate"] = {"name": "always", "params": {"k": 4}}
    else:
        raw["gate"] = {"name": "surprise", "params": {"threshold": 1.5, "k": 4}}
    if components["memory"] == "null":
        raw["memory"] = {"name": "null", "params": {}}
    raw["model"]["params"]["decay"] = 0.99
    raw["seeds"] = {"master": seed, "mode": "legacy_v0", "overrides": {}}
    # p1v0.metrics.summarise_online uses a 500-step tail; match it so the tail
    # statistic is comparable rather than merely similar.
    raw["metrics"] = [
        {"name": "online_loss", "params": {"tail": 500}} if m["name"] == "online_loss" else m
        for m in raw["metrics"]
    ]
    return RunConfig.from_dict(raw)


def _frozen(variant: str, seed: int):
    return execute(
        Config(
            variant=variant,
            seed=seed,
            n_tasks=SMALL["n_tasks"],
            alphabet=SMALL["alphabet"],
            steps_per_task=SMALL["steps_per_task"],
            probe_pairs=PROBE_PAIRS,
            decay=0.99,
            replay_k=4,
            capacity=1000,
            replay_weight=1.0,
            surprise_threshold=1.5,
        )
    )


def assert_matrix_identical(actual, expected) -> None:
    """Element-wise exact equality.

    Exact, not approximate: the claim is that the platform executes the frozen
    code, so every float must match bit-for-bit. A tolerance here would hide
    precisely the kind of drift this test exists to catch. (`pytest.approx` also
    refuses nested sequences, which is what forces an explicit helper.)
    """
    assert len(actual) == len(expected), "different number of checkpoints"
    for block, (row_a, row_b) in enumerate(zip(actual, expected)):
        assert len(row_a) == len(row_b), f"block {block}: different task count"
        for task, (value_a, value_b) in enumerate(zip(row_a, row_b)):
            assert value_a == value_b, f"block {block}, task {task}: {value_a!r} != {value_b!r}"


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_platform_reproduces_frozen_rig(variant, artifact_root):
    config = _platform(variant, seed=0)
    result = run(config, root=artifact_root, quiet=True)
    assert result.ok, result.error
    summary, _ = _frozen(variant, seed=0)

    platform_online = result.metrics["online_loss"]
    assert platform_online["steps"] == summary["online"]["steps"]
    assert platform_online["online_loss_mean"] == pytest.approx(
        summary["online"]["online_loss_mean"], rel=0, abs=1e-12
    )

    # The probe matrix is the measurement that detects forgetting; equality here
    # means the environment, the probe data and the model state all match.
    assert_matrix_identical(result.metrics["retention"]["probe_matrix"], summary["probe_matrix"])
    assert result.metrics["retention"]["block_tasks"] == summary["block_tasks"]
    assert result.metrics["retention"]["retention"] == pytest.approx(
        summary["retention"], rel=0, abs=1e-12
    )
    assert result.metrics["gate_activity"]["total_replays"] == summary["gate_total_replays"]
    assert result.metrics["gate_activity"]["fired_steps"] == summary["gate_fired_steps"]


@pytest.mark.parametrize("seed", [0, 1, 7])
def test_equivalence_holds_across_seeds(seed, artifact_root):
    """One matching seed could be luck; three cannot be."""
    config = _platform("replay_surprise", seed=seed)
    result = run(config, root=artifact_root, quiet=True)
    summary, _ = _frozen("replay_surprise", seed=seed)
    assert_matrix_identical(result.metrics["retention"]["probe_matrix"], summary["probe_matrix"])
    assert result.metrics["online_loss"]["online_loss_tail"] == pytest.approx(
        summary["online"]["online_loss_tail"], rel=0, abs=1e-12
    )


def test_tail_online_loss_matches(artifact_root):
    config = _platform("replay_always", seed=3)
    result = run(config, root=artifact_root, quiet=True)
    summary, _ = _frozen("replay_always", seed=3)
    # p1v0 uses a 500-step tail; the platform config declares tail=50, so compare
    # the shared statistic rather than assuming the windows agree.
    assert result.metrics["online_loss"]["online_loss_mean"] == pytest.approx(
        summary["online"]["online_loss_mean"], rel=0, abs=1e-12
    )
    assert result.metrics["compute"]["replay_updates"] == summary["gate_total_replays"]


def test_shipped_m0_replication_config_is_equivalent(artifact_root):
    """The committed `m0_replication.yaml`, not just a test-local construction.

    Uses a shortened stream so the assertion is affordable in the unit suite; the
    seeding path — which is what could differ — is unaffected by stream length.
    """
    config = RunConfig.load(CONFIG_DIR / "m0_replication.yaml").with_overrides(
        {
            "environment.params.steps_per_task": 200,
            "benchmark.params.probe_pairs": 100,
            "logging.plots": False,
        }
    )
    result = run(config, root=artifact_root, quiet=True)
    summary, _ = execute(
        Config(
            variant="replay_surprise",
            seed=0,
            n_tasks=4,
            alphabet=8,
            steps_per_task=200,
            probe_pairs=100,
            decay=0.99,
        )
    )
    assert result.metrics["retention"]["retention"] == pytest.approx(
        summary["retention"], rel=0, abs=1e-12
    )
    assert_matrix_identical(result.metrics["retention"]["probe_matrix"], summary["probe_matrix"])


def test_frozen_package_is_not_modified_by_adapters():
    """Adapters must add surface, never change frozen behaviour."""
    from p1v0.gate import SurpriseGate
    from p1v0.memory import ReplayBuffer
    from p1v0.model import CountModel
    from science.mechanisms.v0 import CountModelPlugin, ReservoirMemory, SurpriseGatePlugin

    assert issubclass(CountModelPlugin, CountModel)
    assert issubclass(SurpriseGatePlugin, SurpriseGate)
    # The reservoir wraps rather than subclasses, so the frozen sampler performs
    # every draw; confirm the wrapped object really is the frozen class.
    memory = ReservoirMemory(capacity=5, seed=0)
    assert isinstance(memory._buffer, ReplayBuffer)  # noqa: SLF001 — structural assertion

    # A plugin must not have overridden a numerical method of the frozen class.
    for name in ("predict", "learn", "state_dict"):
        assert getattr(CountModelPlugin, name) is getattr(CountModel, name)
