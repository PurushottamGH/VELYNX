"""Configuration system: versioning, validation, identity, overrides.

The properties tested here are what make stored results interpretable: a config
that silently accepted a typo, or a hash that changed when a run was renamed, would
make cross-run comparison unreliable.
"""

from __future__ import annotations

import pytest

from experiments.engine.config import (
    CONFIG_VERSION,
    ConfigError,
    RunConfig,
    apply_overrides,
    flatten_axes,
)
from tests.m1.conftest import CONFIG_DIR, smoke_dict


class TestValidation:
    def test_version_is_mandatory(self):
        raw = smoke_dict()
        del raw["config_version"]
        with pytest.raises(ConfigError, match="config_version"):
            RunConfig.from_dict(raw)

    def test_future_version_is_refused_not_reinterpreted(self):
        with pytest.raises(ConfigError, match="not supported"):
            RunConfig.from_dict(smoke_dict(config_version=CONFIG_VERSION + 1))

    def test_unknown_top_level_key_is_an_error(self):
        with pytest.raises(ConfigError, match="unexpected top-level keys"):
            RunConfig.from_dict(smoke_dict(mdoel={"name": "count_model"}))

    def test_missing_section_is_named(self):
        raw = smoke_dict()
        del raw["gate"]
        with pytest.raises(ConfigError, match="'gate'"):
            RunConfig.from_dict(raw)

    def test_duplicate_metric_is_rejected(self):
        raw = smoke_dict(metrics=[{"name": "compute"}, {"name": "compute"}])
        with pytest.raises(ConfigError, match="more than once"):
            RunConfig.from_dict(raw)

    def test_invalid_seed_mode_is_rejected(self):
        raw = smoke_dict(seeds={"master": 0, "mode": "sloppy"})
        with pytest.raises(ConfigError, match="seeds.mode"):
            RunConfig.from_dict(raw)

    def test_negative_compute_limit_is_rejected(self):
        raw = smoke_dict(compute={"max_steps": 0})
        with pytest.raises(ConfigError, match="positive"):
            RunConfig.from_dict(raw)

    def test_unknown_logging_key_is_rejected(self):
        raw = smoke_dict(logging={"level": "info", "verbose": True})
        with pytest.raises(ConfigError, match="logging"):
            RunConfig.from_dict(raw)


class TestIdentity:
    def test_hash_ignores_cosmetic_fields(self):
        """Renaming a run or enabling plots must not invalidate its results."""
        a = RunConfig.from_dict(smoke_dict())
        b = RunConfig.from_dict(
            smoke_dict(
                name="different",
                description="also different",
                logging={"level": "debug", "console": True, "step_format": "jsonl", "plots": True},
            )
        )
        assert a.config_hash == b.config_hash

    def test_hash_tracks_every_scientific_field(self):
        base = RunConfig.from_dict(smoke_dict())
        for path, value in [
            ("model.params.decay", 0.5),
            ("gate.params.k", 3),
            ("gate.name", "never"),
            ("replay.name", "current_sample"),
            ("memory.params.capacity", 10),
            ("environment.params.n_tasks", 3),
            ("benchmark.params", {"probe_pairs": 7}),
            ("seeds.master", 4),
            ("seeds.mode", "legacy_v0"),
            ("compute.max_steps", 5),
        ]:
            assert base.with_overrides({path: value}).config_hash != base.config_hash, path

    def test_metrics_affect_identity(self):
        base = RunConfig.from_dict(smoke_dict())
        fewer = RunConfig.from_dict(smoke_dict(metrics=[{"name": "compute"}]))
        assert base.config_hash != fewer.config_hash

    def test_run_id_is_readable_and_seed_tagged(self):
        config = RunConfig.from_dict(smoke_dict()).with_seed(12)
        assert config.run_id.startswith("unit__seed12__")
        assert len(config.run_id.split("__")[-1]) == 12

    def test_yaml_snapshot_reloads_identically(self):
        import yaml

        original = RunConfig.from_dict(smoke_dict())
        restored = RunConfig.from_dict(yaml.safe_load(original.to_yaml()))
        assert restored.config_hash == original.config_hash


class TestOverrides:
    def test_sets_nested_value(self):
        out = apply_overrides({"a": {"b": {"c": 1}}}, {"a.b.c": 2})
        assert out["a"]["b"]["c"] == 2

    def test_does_not_mutate_input(self):
        source = {"a": {"b": 1}}
        apply_overrides(source, {"a.b": 2})
        assert source["a"]["b"] == 1

    def test_missing_parent_is_an_error(self):
        """A misspelled sweep axis must fail rather than add a key nobody reads."""
        with pytest.raises(ConfigError, match="does not exist"):
            apply_overrides({"a": {"b": 1}}, {"z.b": 2})

    def test_new_leaf_key_is_allowed(self):
        out = apply_overrides({"a": {"params": {}}}, {"a.params.new": 5})
        assert out["a"]["params"]["new"] == 5


class TestGrid:
    def test_cartesian_product_size_and_order(self):
        points = list(flatten_axes({"x": [1, 2], "y": ["a", "b", "c"]}))
        assert len(points) == 6
        assert points[0] == {"x": 1, "y": "a"}

    def test_empty_grid_yields_one_point(self):
        assert list(flatten_axes({})) == [{}]


class TestShippedConfigs:
    """Every config in the repository must load. A broken example is worse than
    no example."""

    @pytest.mark.parametrize(
        "filename",
        ["smoke.yaml", "baseline.yaml", "m0_replication.yaml"],
    )
    def test_run_configs_load(self, filename):
        config = RunConfig.load(CONFIG_DIR / filename)
        assert config.config_version == CONFIG_VERSION
        assert config.name

    def test_m0_replication_uses_legacy_seeds(self):
        """Its whole purpose is bit-equivalence with the frozen rig."""
        config = RunConfig.load(CONFIG_DIR / "m0_replication.yaml")
        assert config.seeds.mode == "legacy_v0"
        assert config.environment.name == "markov_blocks_v0"

    def test_baseline_uses_split_seeds(self):
        config = RunConfig.load(CONFIG_DIR / "baseline.yaml")
        assert config.seeds.mode == "independent"
        assert config.environment.name == "markov_blocks_split"
        names = [m.name for m in config.metrics]
        assert "excess_loss" in names and "plasticity" in names
