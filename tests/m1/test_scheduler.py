"""Scheduler: expansion, deduplication, resume, and parallel equivalence.

The load-bearing test here is `test_parallel_matches_sequential`. If worker count
could change a number, every sweep result would be unreproducible, and no amount of
seeding elsewhere would fix it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from experiments.engine.config import ConfigError, RunConfig
from experiments.engine.engine import run_dir_for
from experiments.engine.scheduler import (
    Sweep,
    _parse_seeds,
    batch_summary,
    interrupted_runs,
    pending_runs,
    run_batch,
    validate_batch,
)
from tests.m1.conftest import smoke_dict


@pytest.fixture
def sweep_files(tmp_path: Path):
    """Write a base config and a sweep that references it, as on disk."""
    base = tmp_path / "base.yaml"
    base.write_text(yaml.safe_dump(smoke_dict()), encoding="utf-8")

    def write(name: str, payload: dict) -> Path:
        payload = {"config_version": 1, "base": "base.yaml", **payload}
        path = tmp_path / name
        path.write_text(yaml.safe_dump(payload), encoding="utf-8")
        return path

    return write


class TestExpansion:
    def test_multi_seed_only(self, sweep_files):
        sweep = Sweep.load(sweep_files("s.yaml", {"name": "seeds_only", "seeds": [0, 1, 2]}))
        configs = sweep.expand()
        assert [c.seeds.master for c in configs] == [0, 1, 2]
        assert len({c.config_hash for c in configs}) == 3

    def test_grid_times_seeds(self, sweep_files):
        sweep = Sweep.load(
            sweep_files(
                "s.yaml",
                {
                    "name": "grid",
                    "seeds": {"start": 0, "count": 2},
                    "grid": {"model.params.decay": [0.9, 1.0], "gate.params.k": [1, 2]},
                },
            )
        )
        assert len(sweep.expand()) == 2 * 2 * 2

    def test_conditions_swap_whole_components(self, sweep_files):
        """A gate swap implies matching params; a grid would combine them wrongly."""
        sweep = Sweep.load(
            sweep_files(
                "s.yaml",
                {
                    "name": "conditions",
                    "seeds": [0],
                    "conditions": [
                        {"gate.name": "surprise", "gate.params": {"threshold": 1.5, "k": 4}},
                        {"gate.name": "never", "gate.params": {}},
                    ],
                },
            )
        )
        configs = sweep.expand()
        assert [c.gate.name for c in configs] == ["surprise", "never"]
        assert configs[0].gate.params == {"threshold": 1.5, "k": 4}
        assert configs[1].gate.params == {}

    def test_conditions_crossed_with_grid(self, sweep_files):
        sweep = Sweep.load(
            sweep_files(
                "s.yaml",
                {
                    "name": "both",
                    "seeds": [0, 1],
                    "grid": {"model.params.decay": [0.9, 1.0]},
                    "conditions": [{"gate.name": "never"}, {"gate.name": "always"}],
                },
            )
        )
        assert len(sweep.expand()) == 2 * 2 * 2

    def test_duplicate_points_are_dropped(self, sweep_files):
        sweep = Sweep.load(
            sweep_files(
                "s.yaml",
                {
                    "name": "dupes",
                    "seeds": [0],
                    "conditions": [{"gate.name": "never"}, {"gate.name": "never"}],
                },
            )
        )
        assert len(sweep.expand()) == 1

    def test_expansion_is_pure(self, sweep_files):
        """No disk writes, no registry access — so `--dry-run` is always safe."""
        sweep = Sweep.load(sweep_files("s.yaml", {"name": "pure", "seeds": [0, 1]}))
        first = [c.config_hash for c in sweep.expand()]
        assert first == [c.config_hash for c in sweep.expand()]

    def test_misspelled_parent_path_is_rejected_at_expansion(self, sweep_files):
        """A path whose parent does not exist cannot be a real axis."""
        sweep = Sweep.load(
            sweep_files("s.yaml", {"name": "typo", "grid": {"modl.params.decay": [0.9]}})
        )
        with pytest.raises(ConfigError, match="does not exist"):
            sweep.expand()

    def test_misspelled_parameter_is_caught_before_any_run_executes(
        self, sweep_files, artifact_root
    ):
        """`model.params` is a free-form mapping, so the schema cannot reject `decy`.
        Component construction can, and validation runs it before execution."""
        sweep = Sweep.load(
            sweep_files(
                "s.yaml", {"name": "typo", "seeds": [0, 1], "grid": {"model.params.decy": [0.9]}}
            )
        )
        configs = sweep.expand()  # expansion stays pure
        with pytest.raises(ConfigError, match="unexpected keyword argument 'decy'"):
            validate_batch(configs)
        with pytest.raises(ConfigError, match="misconfigured"):
            run_batch(configs, root=artifact_root, workers=1)
        assert not any(artifact_root.rglob("metrics.json")), "a run executed despite a bad config"

    def test_validation_reports_every_bad_arm_at_once(self, sweep_files):
        sweep = Sweep.load(
            sweep_files(
                "s.yaml",
                {"name": "typos", "seeds": [0, 1, 2], "grid": {"model.params.decy": [0.9]}},
            )
        )
        with pytest.raises(ConfigError) as exc:
            validate_batch(sweep.expand())
        assert "3 of 3 runs are misconfigured" in str(exc.value)

    def test_unknown_sweep_key_is_rejected(self, sweep_files):
        with pytest.raises(ConfigError, match="unexpected keys"):
            Sweep.load(sweep_files("s.yaml", {"name": "x", "gird": {}}))

    def test_empty_grid_axis_is_rejected(self, sweep_files):
        with pytest.raises(ConfigError, match="non-empty"):
            Sweep.load(sweep_files("s.yaml", {"name": "x", "grid": {"model.params.decay": []}}))


class TestSeedParsing:
    def test_list_form(self):
        assert _parse_seeds([3, 4]) == [3, 4]

    def test_count_form(self):
        assert _parse_seeds({"start": 5, "count": 3}) == [5, 6, 7]

    def test_stop_form(self):
        assert _parse_seeds({"start": 0, "stop": 4}) == [0, 1, 2, 3]

    def test_step_form(self):
        assert _parse_seeds({"start": 0, "count": 3, "step": 10}) == [0, 10, 20]

    def test_default_is_one_seed(self):
        assert _parse_seeds(None) == [0]

    def test_rejects_empty_and_malformed(self):
        with pytest.raises(ConfigError):
            _parse_seeds([])
        with pytest.raises(ConfigError):
            _parse_seeds({"start": 0})
        with pytest.raises(ConfigError):
            _parse_seeds("all of them")


class TestBatchExecution:
    def _configs(self, n: int = 4):
        base = RunConfig.from_dict(smoke_dict())
        return [base.with_seed(seed) for seed in range(n)]

    def test_sequential_batch_completes_every_run(self, artifact_root):
        results = run_batch(self._configs(), root=artifact_root, workers=1)
        assert len(results) == 4
        assert all(r.ok for r in results)
        summary = batch_summary(results)
        assert summary["completed"] == 4 and summary["failed"] == 0

    @pytest.mark.parametrize("workers", [2, 3])
    def test_parallel_matches_sequential(self, tmp_path, workers):
        """Worker count must not be able to change a result."""
        configs = self._configs(4)
        serial = run_batch(configs, root=tmp_path / "serial", workers=1)
        parallel = run_batch(configs, root=tmp_path / f"par{workers}", workers=workers)
        assert [r.run_id for r in serial] == [r.run_id for r in parallel]
        for a, b in zip(serial, parallel):
            assert a.metrics == b.metrics

    def test_results_keep_input_order_not_completion_order(self, tmp_path):
        configs = self._configs(5)
        results = run_batch(configs, root=tmp_path / "ordered", workers=3)
        assert [r.run_id for r in results] == [c.run_id for c in configs]

    def test_rejects_zero_workers(self, artifact_root):
        with pytest.raises(ValueError, match="workers"):
            run_batch(self._configs(1), root=artifact_root, workers=0)


class TestResume:
    def test_pending_split_reflects_what_is_done(self, artifact_root):
        configs = [RunConfig.from_dict(smoke_dict()).with_seed(s) for s in range(3)]
        run_batch(configs[:2], root=artifact_root, workers=1)
        todo, done = pending_runs(configs, artifact_root)
        assert len(done) == 2 and len(todo) == 1
        assert todo[0].seeds.master == 2

    def test_second_pass_does_not_rewrite_completed_runs(self, artifact_root):
        configs = [RunConfig.from_dict(smoke_dict()).with_seed(s) for s in range(3)]
        run_batch(configs, root=artifact_root, workers=1)
        stamps = {
            c.run_id: (Path(run_dir_for(c, artifact_root)) / "metrics.json").stat().st_mtime_ns
            for c in configs
        }
        run_batch(configs, root=artifact_root, workers=1)
        for config in configs:
            path = Path(run_dir_for(config, artifact_root)) / "metrics.json"
            assert path.stat().st_mtime_ns == stamps[config.run_id]

    def test_interrupted_runs_are_listed_and_re_executed(self, artifact_root):
        configs = [RunConfig.from_dict(smoke_dict()).with_seed(s) for s in range(2)]
        run_batch(configs, root=artifact_root, workers=1)

        victim = Path(run_dir_for(configs[0], artifact_root)) / "status.json"
        payload = json.loads(victim.read_text(encoding="utf-8"))
        payload["status"] = "running"
        victim.write_text(json.dumps(payload), encoding="utf-8")

        assert str(victim.parent) in interrupted_runs(artifact_root)
        todo, done = pending_runs(configs, artifact_root)
        assert len(todo) == 1 and len(done) == 1

        results = run_batch(configs, root=artifact_root, workers=1)
        assert all(r.ok for r in results)
        assert json.loads(victim.read_text(encoding="utf-8"))["status"] == "completed"


class TestShippedSweeps:
    """Every shipped sweep must expand. A broken protocol scaffold is a trap."""

    @pytest.mark.parametrize(
        "filename",
        [
            "v0_1_assay_validity.yaml",
            "v0_2_matched_updates.yaml",
            "v0_3_surprise_ablation.yaml",
            "v0_4_variance.yaml",
        ],
    )
    def test_expands(self, filename):
        from tests.m1.conftest import CONFIG_DIR

        sweep = Sweep.load(CONFIG_DIR / filename)
        configs = sweep.expand()
        assert configs
        assert len({c.config_hash for c in configs}) == len(configs)

    def test_v0_2_holds_gate_and_updates_constant_across_arms(self):
        """The whole design depends on only replay *content* varying."""
        from tests.m1.conftest import CONFIG_DIR

        configs = Sweep.load(CONFIG_DIR / "v0_2_matched_updates.yaml").expand()
        assert {c.gate.name for c in configs} == {"always"}
        assert {c.gate.params["k"] for c in configs} == {4}
        assert {c.replay.name for c in configs} == {
            "buffer_sample",
            "historical_only",
            "current_sample",
            "task_balanced",
            "none",
        }

    def test_v0_1_varies_only_decay(self):
        from tests.m1.conftest import CONFIG_DIR

        configs = Sweep.load(CONFIG_DIR / "v0_1_assay_validity.yaml").expand()
        assert {c.model.params["decay"] for c in configs} == {0.99, 1.0}
        assert {c.gate.name for c in configs} == {"never"}
