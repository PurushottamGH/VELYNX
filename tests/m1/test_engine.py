"""Engine behaviour: determinism, artifacts, resume, limits, isolation.

Every test here uses the deterministic test-double benchmark, so a failure points
at the engine and not at a mechanism.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from core.types import RunStatus
from experiments.engine.artifacts import is_complete, read_status
from experiments.engine.config import ConfigError, RunConfig
from experiments.engine.engine import build_components, run, run_dir_for
from core.seeds import SeedSet
from tests.m1.conftest import smoke_dict


def _run(root: Path, **overrides) -> object:
    return run(RunConfig.from_dict(smoke_dict(**overrides)), root=root, quiet=True)


class TestDeterminism:
    def test_same_config_gives_identical_metrics(self, artifact_root):
        a = _run(artifact_root / "a")
        b = _run(artifact_root / "b")
        assert a.config_hash == b.config_hash
        assert a.metrics == b.metrics

    def test_adding_a_metric_does_not_change_the_trajectory(self, artifact_root):
        """Metrics are observers. If this fails, a metric is mutating state."""
        few = _run(artifact_root / "few", metrics=[{"name": "online_loss", "params": {"tail": 10}}])
        many = _run(
            artifact_root / "many",
            metrics=[
                {"name": "online_loss", "params": {"tail": 10}},
                {"name": "excess_loss"},
                {"name": "plasticity", "params": {"window": 5}},
                {"name": "compute"},
                {"name": "gate_activity"},
                {"name": "retention"},
            ],
        )
        assert few.metrics["online_loss"] == many.metrics["online_loss"]

    def test_disabling_step_records_does_not_change_results(self, artifact_root):
        """Artifact settings must not be able to move a number."""
        with_steps = _run(artifact_root / "with")
        logging = dict(smoke_dict()["logging"])
        logging["step_format"] = "none"
        without = _run(artifact_root / "without", logging=logging)
        assert with_steps.metrics["online_loss"] == without.metrics["online_loss"]

    def test_seed_only_matters_where_randomness_exists(self, artifact_root):
        """With no replay and a deterministic benchmark, nothing in the run consumes
        randomness, so the seed must not change any number. This confirms the engine
        itself draws no random numbers.

        With replay enabled the seed *must* matter, because the reservoir and the
        replay sampler are seeded — asserting otherwise would hide a broken sampler.
        """
        no_randomness = dict(gate={"name": "never", "params": {}}, replay={"name": "none"})
        a = _run(
            artifact_root / "d0",
            seeds={"master": 0, "mode": "independent", "overrides": {}},
            **no_randomness,
        )
        b = _run(
            artifact_root / "d9",
            seeds={"master": 9, "mode": "independent", "overrides": {}},
            **no_randomness,
        )
        assert a.metrics["online_loss"] == b.metrics["online_loss"]

        c = _run(artifact_root / "r0", seeds={"master": 0, "mode": "independent", "overrides": {}})
        d = _run(artifact_root / "r9", seeds={"master": 9, "mode": "independent", "overrides": {}})
        assert c.metrics["online_loss"] != d.metrics["online_loss"]


class TestArtifacts:
    @pytest.fixture
    def completed(self, artifact_root):
        config = RunConfig.from_dict(smoke_dict())
        result = run(config, root=artifact_root, quiet=True)
        return config, result, Path(result.run_dir)

    def test_every_expected_file_is_written(self, completed):
        _, _, run_dir = completed
        for name in (
            "config.yaml",
            "manifest.json",
            "metrics.json",
            "steps.csv",
            "probes.csv",
            "status.json",
            "inventory.json",
            "run.log",
        ):
            assert (run_dir / name).is_file(), name

    def test_config_snapshot_reloads_to_the_same_identity(self, completed):
        config, _, run_dir = completed
        assert RunConfig.load(run_dir / "config.yaml").config_hash == config.config_hash

    def test_manifest_records_provenance(self, completed):
        _, _, run_dir = completed
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["status"] == "completed"
        assert manifest["timing"]["duration_seconds"] >= 0
        assert manifest["runtime"]["python"]
        assert manifest["code"]["code_state"] in ("clean", "dirty", "untracked")
        assert manifest["compute"]["steps"] == 80  # 2 tasks x 20 steps x 2 cycles
        assert manifest["seeds"]["mode"] == "independent"
        assert manifest["benchmark"]["name"] == "deterministic"

    def test_step_csv_has_one_row_per_step(self, completed):
        _, _, run_dir = completed
        with (run_dir / "steps.csv").open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 80
        assert int(rows[0]["updates"]) == 3  # 1 online + k=2 replay

    def test_probe_csv_is_long_form(self, completed):
        _, _, run_dir = completed
        with (run_dir / "probes.csv").open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 4 * 2  # 4 checkpoints x 2 tasks
        assert rows[0]["excess"] != ""

    def test_inventory_hashes_match_the_files(self, completed):
        import hashlib

        _, _, run_dir = completed
        inventory = json.loads((run_dir / "inventory.json").read_text(encoding="utf-8"))["files"]
        assert inventory
        for relative, entry in inventory.items():
            digest = hashlib.sha256((run_dir / relative).read_bytes()).hexdigest()
            assert digest == entry["sha256"], relative

    def test_plots_are_written_when_enabled(self, artifact_root):
        logging = dict(smoke_dict()["logging"])
        logging["plots"] = True
        result = _run(artifact_root, logging=logging)
        plots = Path(result.run_dir) / "plots"
        assert (plots / "online_loss.png").is_file()
        assert (plots / "retention.png").is_file()


class TestResume:
    def test_completed_run_is_skipped(self, artifact_root):
        config = RunConfig.from_dict(smoke_dict())
        first = run(config, root=artifact_root, quiet=True)
        marker = Path(first.run_dir) / "metrics.json"
        stamp = marker.stat().st_mtime_ns

        second = run(config, root=artifact_root, quiet=True)
        assert second.status is RunStatus.COMPLETED
        assert marker.stat().st_mtime_ns == stamp, "resume re-executed a completed run"
        assert second.metrics["online_loss"] == first.metrics["online_loss"]

    def test_no_resume_forces_re_execution(self, artifact_root):
        config = RunConfig.from_dict(smoke_dict())
        first = run(config, root=artifact_root, quiet=True)
        stamp = (Path(first.run_dir) / "metrics.json").stat().st_mtime_ns
        run(config, root=artifact_root, resume=False, quiet=True)
        assert (Path(first.run_dir) / "metrics.json").stat().st_mtime_ns != stamp

    def test_changed_config_is_not_treated_as_complete(self, artifact_root):
        """Same directory, different config hash: skipping would report stale numbers."""
        config = RunConfig.from_dict(smoke_dict())
        run(config, root=artifact_root, quiet=True)
        changed = config.with_overrides({"model.params.decay": 0.5})
        assert not is_complete(run_dir_for(config, artifact_root), changed.config_hash)

    def test_interrupted_run_is_not_complete(self, artifact_root):
        config = RunConfig.from_dict(smoke_dict())
        result = run(config, root=artifact_root, quiet=True)
        status_path = Path(result.run_dir) / "status.json"
        payload = json.loads(status_path.read_text(encoding="utf-8"))
        payload["status"] = "running"
        status_path.write_text(json.dumps(payload), encoding="utf-8")
        assert not is_complete(Path(result.run_dir), config.config_hash)


class TestLimits:
    def test_step_ceiling_truncates_without_failing(self, artifact_root):
        result = _run(artifact_root, compute={"max_steps": 30})
        assert result.ok
        assert result.compute["steps"] == 30
        assert result.compute["truncated_by"] == "max_steps"
        assert result.metrics["online_loss"]["steps"] == 30

    def test_update_ceiling_truncates(self, artifact_root):
        result = _run(artifact_root, compute={"max_updates": 30})
        assert result.ok
        assert result.compute["truncated_by"] == "max_updates"
        assert result.compute["updates_total"] <= 33


class TestFailureHandling:
    def test_metric_requiring_an_oracle_is_rejected_at_build_time(self):
        """Config errors must surface immediately, not as a silently wrong number."""

        class NoOracle:
            name = "no_oracle"
            has_oracle = False

            def build_environment(self):
                raise AssertionError("should not be reached")

        from science.registries import BENCHMARKS

        BENCHMARKS.register("_no_oracle_test")(lambda **kw: NoOracle())
        config = RunConfig.from_dict(
            smoke_dict(benchmark={"name": "_no_oracle_test"}, metrics=[{"name": "excess_loss"}])
        )
        with pytest.raises(ConfigError, match="oracle"):
            build_components(config, SeedSet.build(0, "independent"))

    def test_component_failure_is_recorded_not_raised(self, artifact_root, monkeypatch):
        """One broken condition must not abort a 200-run batch."""
        import science.mechanisms.v0 as v0

        def explode(self, context):
            raise RuntimeError("synthetic model failure")

        monkeypatch.setattr(v0.CountModelPlugin, "predict", explode)
        result = run(RunConfig.from_dict(smoke_dict()), root=artifact_root, quiet=True)
        assert result.status is RunStatus.FAILED
        assert "synthetic model failure" in result.error
        status = read_status(result.run_dir)
        assert status["status"] == "failed"
        manifest = json.loads((Path(result.run_dir) / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["status"] == "failed"


class TestBudgetAccounting:
    def test_updates_equal_online_plus_replay(self, artifact_root):
        result = _run(artifact_root)
        compute = result.metrics["compute"]
        assert compute["online_updates"] == compute["steps"]
        assert compute["updates_total"] == compute["online_updates"] + compute["replay_updates"]
        assert result.compute["updates_total"] == compute["updates_total"]

    def test_replay_shortfall_is_reported(self, artifact_root):
        """historical_only cannot spend its budget during the first block; that gap
        must be visible, or the control looks matched when it is not."""
        result = _run(artifact_root, replay={"name": "historical_only", "params": {"weight": 1.0}})
        assert result.compute["replay_shortfall"] > 0
