"""Core contracts: registry, seeds, budget, records.

These test the properties the rest of the platform relies on. If the registry
silently accepted a duplicate name, or seed derivation varied between processes,
every downstream guarantee would be void.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from core.budget import Budget, BudgetExceeded, Limits
from core.protocols import Benchmark, Environment, Gate, Memory, Metric, Model, Replay
from core.registry import Registry, Spec
from core.seeds import MODES, STREAMS, SeedSet, derive_seed
from core.types import Observation, ProbeRecord, RunStatus, StepRecord


class TestSpec:
    def test_parses_all_three_forms(self):
        assert Spec.parse("never") == Spec(name="never", params={})
        assert Spec.parse({"name": "surprise"}) == Spec(name="surprise", params={})
        assert Spec.parse({"name": "surprise", "params": {"k": 4}}).params == {"k": 4}

    def test_rejects_missing_name(self):
        with pytest.raises(ValueError, match="missing 'name'"):
            Spec.parse({"params": {"k": 1}})

    def test_rejects_stray_keys_instead_of_ignoring_them(self):
        """A parameter placed outside `params` must fail, not vanish."""
        with pytest.raises(ValueError, match="unexpected keys"):
            Spec.parse({"name": "surprise", "threshold": 1.5})


class TestRegistry:
    def test_register_and_create(self):
        reg: Registry[dict] = Registry("thing")
        reg.register("a")(lambda **kw: {"made": "a", **kw})
        assert reg.available() == ["a"]
        assert reg.create("a") == {"made": "a"}

    def test_duplicate_registration_is_an_error(self):
        reg: Registry[dict] = Registry("thing")
        reg.register("a")(lambda: {})
        with pytest.raises(ValueError, match="already registered"):
            reg.register("a")(lambda: {})

    def test_unknown_name_lists_alternatives(self):
        reg: Registry[dict] = Registry("thing")
        reg.register("alpha")(lambda: {})
        with pytest.raises(KeyError) as exc:
            reg.create("alfa")
        assert "alpha" in str(exc.value)

    def test_config_cannot_override_engine_injected_argument(self):
        """The guard that stops a config from setting `alphabet` behind the
        environment's back."""
        reg: Registry[dict] = Registry("model")
        reg.register("m")(lambda alphabet: {"alphabet": alphabet})
        with pytest.raises(ValueError, match="supplied by the engine"):
            reg.create({"name": "m", "params": {"alphabet": 3}}, alphabet=8)


class TestSeeds:
    def test_legacy_mode_reproduces_a_single_composite_seed(self):
        seeds = SeedSet.build(7, "legacy_v0")
        assert all(seeds[s] == 7 for s in STREAMS)

    def test_independent_mode_separates_every_stream(self):
        seeds = SeedSet.build(7, "independent")
        values = [seeds[s] for s in STREAMS]
        assert len(set(values)) == len(STREAMS)
        assert 7 not in values

    def test_derivation_is_stable_across_processes(self):
        """Salted `hash()` would break this; SHA-256 does not."""
        code = "from core.seeds import derive_seed; print(derive_seed(3, 'probe'))"
        out = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=True
        )
        assert int(out.stdout.strip()) == derive_seed(3, "probe")

    def test_overrides_are_recorded_as_explicit(self):
        seeds = SeedSet.build(0, "independent", {"probe": 123})
        assert seeds["probe"] == 123
        assert seeds.explicit == ("probe",)

    def test_rejects_unknown_mode_and_stream(self):
        with pytest.raises(ValueError, match="unknown seed mode"):
            SeedSet.build(0, "whatever")
        with pytest.raises(ValueError, match="unknown seed stream"):
            SeedSet.build(0, "independent", {"nonsense": 1})

    def test_modes_are_closed(self):
        assert MODES == ("legacy_v0", "independent")


class TestBudget:
    def test_counts_and_totals(self):
        budget = Budget()
        budget.online_updates = 10
        budget.replay_updates = 40
        assert budget.updates_total == 50
        assert budget.as_dict()["updates_total"] == 50

    def test_step_limit_trips(self):
        budget = Budget(limits=Limits(max_steps=3))
        budget.start()
        for _ in range(3):
            budget.check()
            budget.steps += 1
        with pytest.raises(BudgetExceeded):
            budget.check()
        assert budget.truncated_by == "max_steps"

    def test_update_limit_trips(self):
        budget = Budget(limits=Limits(max_updates=5))
        budget.start()
        budget.check()
        budget.online_updates = 5
        with pytest.raises(BudgetExceeded):
            budget.check()
        assert budget.truncated_by == "max_updates"


class TestRecords:
    def test_records_are_frozen(self):
        rec = StepRecord(
            t=0, task=0, loss=1.0, replays=0, gate_fired=False, buffer_size=0, updates=1
        )
        with pytest.raises(Exception):
            rec.loss = 2.0  # type: ignore[misc]

    def test_excess_is_derived_not_stored(self):
        rec = ProbeRecord(t=0, block=0, trained_task=0, losses=(1.5, 2.0), oracle=(1.0, 1.0))
        assert rec.excess == pytest.approx((0.5, 1.0))

    def test_excess_is_empty_without_an_oracle(self):
        """Absent ground truth must not silently become zero."""
        rec = ProbeRecord(t=0, block=0, trained_task=0, losses=(1.5,))
        assert rec.excess == ()

    def test_status_terminality(self):
        assert RunStatus.COMPLETED.is_terminal
        assert not RunStatus.RUNNING.is_terminal

    def test_observation_roundtrips(self):
        obs = Observation(t=1, task=2, context=3, target=4)
        assert obs.as_dict() == {"t": 1, "task": 2, "context": 3, "target": 4}


class TestProtocolConformance:
    """Registered components must satisfy the contracts the engine calls."""

    def test_registered_components_conform(self):
        from core.seeds import SeedSet as SS
        from science.registries import BENCHMARKS, GATES, MEMORIES, METRICS, MODELS, REPLAYS

        seeds = SS.build(0, "independent")
        env_spec = {"name": "cyclic", "params": {"n_tasks": 2, "alphabet": 4, "steps_per_task": 5}}

        benchmark = BENCHMARKS.create("deterministic", seeds=seeds, environment=env_spec)
        assert isinstance(benchmark, Benchmark)
        env = benchmark.build_environment()
        assert isinstance(env, Environment)
        hints = dict(env.hints)
        hints["total_steps"] = env.total_steps

        assert isinstance(MODELS.create("count_model", **hints), Model)
        assert isinstance(MEMORIES.create("reservoir", seed=0, **hints), Memory)
        assert isinstance(MEMORIES.create("null", seed=0, **hints), Memory)
        for gate in ("never", "always", "surprise"):
            assert isinstance(GATES.create(gate, seed=0, **hints), Gate)
        # `boundary` needs a window no larger than the block length; the block
        # length is injected, so an oversized window is a config error by design.
        assert isinstance(
            GATES.create({"name": "boundary", "params": {"window": 2}}, seed=0, **hints), Gate
        )
        assert isinstance(
            GATES.create({"name": "matched_random", "params": {"rate": 0.1}}, seed=0, **hints), Gate
        )
        for replay in (
            "none",
            "buffer_sample",
            "current_sample",
            "historical_only",
            "task_balanced",
        ):
            assert isinstance(REPLAYS.create(replay, seed=0, **hints), Replay)
        for metric in METRICS.available():
            assert isinstance(METRICS.create(metric), Metric)
