"""CLI contract: exit codes and the checks each command performs.

Exit codes are tested because CI depends on them: a sweep that returned 0 with
failed runs inside would make a green build meaningless.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from experiments.engine.cli import EXIT_BAD_REQUEST, EXIT_FAILED_RUNS, EXIT_OK, main
from tests.m1.conftest import CONFIG_DIR, smoke_dict


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    path = tmp_path / "run.yaml"
    path.write_text(yaml.safe_dump(smoke_dict()), encoding="utf-8")
    return path


class TestRun:
    def test_completes(self, config_file, artifact_root):
        assert main(["run", str(config_file), "--root", str(artifact_root), "--quiet"]) == EXIT_OK

    def test_override_is_applied(self, config_file, artifact_root, capsys):
        code = main(
            [
                "run",
                str(config_file),
                "--root",
                str(artifact_root),
                "--quiet",
                "--set",
                "model.params.decay=1.0",
            ]
        )
        assert code == EXIT_OK
        run_dir = Path(capsys.readouterr().out.split("artifacts:")[1].split("\n")[0].strip())
        snapshot = yaml.safe_load((run_dir / "config.yaml").read_text(encoding="utf-8"))
        assert snapshot["model"]["params"]["decay"] == 1.0

    def test_override_value_uses_yaml_scalar_rules(self, config_file, artifact_root, capsys):
        """`1.0` must arrive as a float, not the string '1.0'."""
        main(
            [
                "run",
                str(config_file),
                "--root",
                str(artifact_root),
                "--quiet",
                "--set",
                "logging.plots=false",
            ]
        )
        run_dir = Path(capsys.readouterr().out.split("artifacts:")[1].split("\n")[0].strip())
        snapshot = yaml.safe_load((run_dir / "config.yaml").read_text(encoding="utf-8"))
        assert snapshot["logging"]["plots"] is False

    def test_malformed_override_is_a_bad_request(self, config_file, artifact_root):
        code = main(
            ["run", str(config_file), "--root", str(artifact_root), "--set", "no_equals_sign"]
        )
        assert code == EXIT_BAD_REQUEST

    def test_missing_file_is_a_bad_request(self, artifact_root):
        assert main(["run", "nope.yaml", "--root", str(artifact_root)]) == EXIT_BAD_REQUEST

    def test_unknown_component_is_a_bad_request(self, tmp_path, artifact_root):
        raw = smoke_dict()
        raw["gate"] = {"name": "suprise"}
        path = tmp_path / "bad.yaml"
        path.write_text(yaml.safe_dump(raw), encoding="utf-8")
        assert main(["run", str(path), "--root", str(artifact_root)]) == EXIT_BAD_REQUEST


class TestSweep:
    @pytest.fixture
    def sweep_file(self, tmp_path: Path) -> Path:
        (tmp_path / "base.yaml").write_text(yaml.safe_dump(smoke_dict()), encoding="utf-8")
        path = tmp_path / "sweep.yaml"
        path.write_text(
            yaml.safe_dump(
                {"config_version": 1, "name": "cli_sweep", "base": "base.yaml", "seeds": [0, 1]}
            ),
            encoding="utf-8",
        )
        return path

    def test_dry_run_executes_nothing(self, sweep_file, artifact_root, capsys):
        assert (
            main(["sweep", str(sweep_file), "--root", str(artifact_root), "--dry-run"]) == EXIT_OK
        )
        assert "runs expanded : 2" in capsys.readouterr().out
        assert not artifact_root.exists() or not any(artifact_root.rglob("metrics.json"))

    def test_dry_run_validates(self, tmp_path, artifact_root):
        """A dry run that skipped validation would give false confidence."""
        (tmp_path / "base.yaml").write_text(yaml.safe_dump(smoke_dict()), encoding="utf-8")
        path = tmp_path / "bad.yaml"
        path.write_text(
            yaml.safe_dump(
                {
                    "config_version": 1,
                    "name": "bad",
                    "base": "base.yaml",
                    "grid": {"model.params.decy": [0.5]},
                }
            ),
            encoding="utf-8",
        )
        assert (
            main(["sweep", str(path), "--root", str(artifact_root), "--dry-run"])
            == EXIT_BAD_REQUEST
        )

    def test_executes_and_resumes(self, sweep_file, artifact_root):
        assert main(["sweep", str(sweep_file), "--root", str(artifact_root)]) == EXIT_OK
        assert len(list(artifact_root.rglob("metrics.json"))) == 2
        # Second invocation must be a no-op, not a re-run.
        stamps = {p: p.stat().st_mtime_ns for p in artifact_root.rglob("metrics.json")}
        assert main(["sweep", str(sweep_file), "--root", str(artifact_root)]) == EXIT_OK
        assert {p: p.stat().st_mtime_ns for p in artifact_root.rglob("metrics.json")} == stamps

    def test_parallel_workers(self, sweep_file, artifact_root):
        code = main(["sweep", str(sweep_file), "--root", str(artifact_root), "--workers", "2"])
        assert code == EXIT_OK


class TestInspection:
    def test_list_shows_every_registry(self, capsys):
        assert main(["list"]) == EXIT_OK
        out = capsys.readouterr().out
        for kind in (
            "benchmark",
            "environment",
            "gate",
            "logger",
            "memory",
            "metric",
            "model",
            "replay",
        ):
            assert f"{kind}:" in out
        assert "surprise" in out and "excess_loss" in out and "matched_random" in out

    def test_status_on_empty_root(self, tmp_path, capsys):
        assert main(["status", "--root", str(tmp_path / "nothing")]) == EXIT_OK
        assert "no artifact root" in capsys.readouterr().out

    def test_status_counts_runs(self, config_file, artifact_root, capsys):
        main(["run", str(config_file), "--root", str(artifact_root), "--quiet"])
        capsys.readouterr()
        assert main(["status", "--root", str(artifact_root)]) == EXIT_OK
        assert "completed  1" in capsys.readouterr().out


class TestVerify:
    def _run_dir(self, config_file, artifact_root, capsys) -> Path:
        main(["run", str(config_file), "--root", str(artifact_root), "--quiet"])
        return Path(capsys.readouterr().out.split("artifacts:")[1].split("\n")[0].strip())

    def test_intact_run_verifies(self, config_file, artifact_root, capsys):
        run_dir = self._run_dir(config_file, artifact_root, capsys)
        assert main(["verify", str(run_dir)]) == EXIT_OK
        assert "verified" in capsys.readouterr().out

    def test_tampering_is_detected(self, config_file, artifact_root, capsys):
        """The point of the inventory: a silently edited result is detectable."""
        run_dir = self._run_dir(config_file, artifact_root, capsys)
        metrics = run_dir / "metrics.json"
        payload = json.loads(metrics.read_text(encoding="utf-8"))
        payload["online_loss"]["online_loss_mean"] = 0.0
        metrics.write_text(json.dumps(payload), encoding="utf-8")
        assert main(["verify", str(run_dir)]) == EXIT_FAILED_RUNS

    def test_deletion_is_detected(self, config_file, artifact_root, capsys):
        run_dir = self._run_dir(config_file, artifact_root, capsys)
        (run_dir / "steps.csv").unlink()
        assert main(["verify", str(run_dir)]) == EXIT_FAILED_RUNS

    def test_missing_inventory_is_a_bad_request(self, tmp_path):
        assert main(["verify", str(tmp_path)]) == EXIT_BAD_REQUEST


class TestShippedSmokeConfig:
    def test_smoke_config_runs_through_the_cli(self, artifact_root):
        code = main(
            ["run", str(CONFIG_DIR / "smoke.yaml"), "--root", str(artifact_root), "--quiet"]
        )
        assert code == EXIT_OK
