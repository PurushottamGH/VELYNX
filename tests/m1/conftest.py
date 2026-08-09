"""Shared fixtures.

Every test writes artifacts under a pytest `tmp_path`, never under the repository's
artifact root: a test run must not be able to overwrite a real result, and must not
depend on one existing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest

from experiments.engine.config import RunConfig
from experiments.engine.plugins import load_plugins

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "configs" / "v0"


@pytest.fixture(scope="session", autouse=True)
def _plugins() -> None:
    """Registries must be populated before any test touches them."""
    load_plugins()


@pytest.fixture
def artifact_root(tmp_path: Path) -> Path:
    return tmp_path / "runs"


def smoke_dict(**overrides: Any) -> Dict[str, Any]:
    """A minimal, fast, fully deterministic run config as a plain dict.

    Uses the `deterministic` benchmark so engine tests do not depend on any
    scientific component: a failure is then unambiguously an engine fault.
    """
    config: Dict[str, Any] = {
        "config_version": 1,
        "name": "unit",
        "benchmark": {"name": "deterministic", "params": {}},
        "environment": {
            "name": "cyclic",
            "params": {"n_tasks": 2, "alphabet": 4, "steps_per_task": 20, "cycles": 2},
        },
        "model": {"name": "count_model", "params": {"alpha": 0.5, "decay": 0.9}},
        "memory": {"name": "reservoir", "params": {"capacity": 25}},
        "gate": {"name": "always", "params": {"k": 2}},
        "replay": {"name": "buffer_sample", "params": {"weight": 1.0}},
        "metrics": [
            {"name": "online_loss", "params": {"tail": 10}},
            {"name": "excess_loss"},
            {"name": "compute"},
            {"name": "gate_activity", "params": {"boundary_window": 5}},
        ],
        "seeds": {"master": 0, "mode": "independent", "overrides": {}},
        "compute": {},
        "logging": {"level": "info", "console": False, "step_format": "csv", "plots": False},
    }
    config.update(overrides)
    return config


@pytest.fixture
def smoke_config() -> RunConfig:
    return RunConfig.from_dict(smoke_dict())


def markov_dict(**params: Any) -> Dict[str, Any]:
    """A small but genuinely stochastic Markov-retention config."""
    env_params = {
        "n_tasks": 3,
        "alphabet": 6,
        "steps_per_task": 200,
        "cycles": 1,
        "fanout": 2,
    }
    env_params.update(params)
    return {
        "config_version": 1,
        "name": "unit_markov",
        "benchmark": {"name": "markov_retention", "params": {"probe_pairs": 100}},
        "environment": {"name": "markov_blocks_v0", "params": env_params},
        "model": {"name": "count_model", "params": {"alpha": 0.5, "decay": 0.9}},
        "memory": {"name": "reservoir", "params": {"capacity": 200}},
        "gate": {"name": "surprise", "params": {"threshold": 1.5, "k": 4}},
        "replay": {"name": "buffer_sample", "params": {"weight": 1.0}},
        "metrics": [
            {"name": "online_loss", "params": {"tail": 50}},
            {"name": "retention"},
            {"name": "excess_loss"},
            {"name": "plasticity", "params": {"window": 50}},
            {"name": "compute"},
            {"name": "gate_activity", "params": {"boundary_window": 20}},
        ],
        "seeds": {"master": 0, "mode": "legacy_v0", "overrides": {}},
        "compute": {},
        "logging": {"level": "info", "console": False, "step_format": "csv", "plots": False},
    }
