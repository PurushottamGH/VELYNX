"""Versioned run configuration.

Responsibility: define what a run *is*, validate it before anything executes, and
give it a stable identity.

Design rules, each with a reason:

  * **Versioned.** `config_version` is mandatory. A config whose meaning changed
    must fail loudly rather than run with the new interpretation, because stored
    results are only comparable if their configs mean the same thing.
  * **Closed.** Unknown keys are errors. A typo in `sourprise_threshold` that was
    silently ignored would produce a run that looks like the intended one and is
    not.
  * **Frozen.** Configs are immutable; sweeps produce new configs via
    `with_overrides` rather than mutating a shared object, so a parallel worker
    cannot observe a half-modified config.
  * **Identity excludes cosmetics.** The config hash covers everything that can
    change a number, and excludes `name`, `description` and `logging`. Renaming a
    run or turning on plots must not invalidate its results.

Sections map one-to-one onto component registries, so adding a component kind is
a config-schema change and is therefore versioned.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

import yaml

from core.budget import Limits
from core.registry import Spec
from core.seeds import MODES as SEED_MODES
from core.seeds import STREAMS as SEED_STREAMS

#: Current schema version. Bump when a section's meaning changes, and record the
#: change in docs/engineering/Configuration.md.
CONFIG_VERSION = 1

#: Versions this code can still read. Add a migration before extending.
SUPPORTED_VERSIONS: Tuple[int, ...] = (1,)

_COMPONENT_SECTIONS: Tuple[str, ...] = (
    "benchmark",
    "environment",
    "model",
    "memory",
    "gate",
    "replay",
)

_TOP_LEVEL_KEYS = frozenset(
    {
        "config_version",
        "name",
        "description",
        "metrics",
        "seeds",
        "compute",
        "logging",
        *_COMPONENT_SECTIONS,
    }
)

LOG_LEVELS: Tuple[str, ...] = ("debug", "info", "warning", "error")
STEP_FORMATS: Tuple[str, ...] = ("csv", "jsonl", "none")


class ConfigError(ValueError):
    """Raised for any invalid configuration. Always names the offending key."""


@dataclass(frozen=True)
class SeedConfig:
    """Random identity. `overrides` pins individual substreams by hand."""

    master: int = 0
    mode: str = "independent"
    overrides: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> "SeedConfig":
        raw = dict(raw or {})
        unknown = set(raw) - {"master", "mode", "overrides"}
        if unknown:
            raise ConfigError(f"seeds: unexpected keys {sorted(unknown)}")
        mode = str(raw.get("mode", "independent"))
        if mode not in SEED_MODES:
            raise ConfigError(f"seeds.mode: {mode!r} not in {SEED_MODES}")
        overrides = dict(raw.get("overrides") or {})
        bad = set(overrides) - set(SEED_STREAMS)
        if bad:
            raise ConfigError(f"seeds.overrides: unknown stream(s) {sorted(bad)}")
        try:
            master = int(raw.get("master", 0))
            overrides = {k: int(v) for k, v in overrides.items()}
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"seeds: values must be integers ({exc})") from exc
        return cls(master=master, mode=mode, overrides=overrides)

    def as_dict(self) -> Dict[str, Any]:
        return {"master": self.master, "mode": self.mode, "overrides": dict(self.overrides)}


@dataclass(frozen=True)
class LoggingConfig:
    """Output verbosity and which artifacts to emit. Never affects results."""

    level: str = "info"
    console: bool = True
    step_format: str = "csv"
    plots: bool = True

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> "LoggingConfig":
        raw = dict(raw or {})
        unknown = set(raw) - {"level", "console", "step_format", "plots"}
        if unknown:
            raise ConfigError(f"logging: unexpected keys {sorted(unknown)}")
        level = str(raw.get("level", "info")).lower()
        if level not in LOG_LEVELS:
            raise ConfigError(f"logging.level: {level!r} not in {LOG_LEVELS}")
        step_format = str(raw.get("step_format", "csv")).lower()
        if step_format not in STEP_FORMATS:
            raise ConfigError(f"logging.step_format: {step_format!r} not in {STEP_FORMATS}")
        return cls(
            level=level,
            console=bool(raw.get("console", True)),
            step_format=step_format,
            plots=bool(raw.get("plots", True)),
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "console": self.console,
            "step_format": self.step_format,
            "plots": self.plots,
        }


def _limits_from_dict(raw: Mapping[str, Any] | None) -> Limits:
    raw = dict(raw or {})
    unknown = set(raw) - {"max_steps", "max_updates", "max_wall_seconds"}
    if unknown:
        raise ConfigError(f"compute: unexpected keys {sorted(unknown)}")

    def _opt(key: str, cast: Any) -> Any:
        value = raw.get(key)
        if value is None:
            return None
        try:
            cast_value = cast(value)
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"compute.{key}: not a number ({exc})") from exc
        if cast_value <= 0:
            raise ConfigError(f"compute.{key}: must be positive or null")
        return cast_value

    return Limits(
        max_steps=_opt("max_steps", int),
        max_updates=_opt("max_updates", int),
        max_wall_seconds=_opt("max_wall_seconds", float),
    )


@dataclass(frozen=True)
class RunConfig:
    """One fully specified, reproducible run."""

    name: str
    benchmark: Spec
    environment: Spec
    model: Spec
    memory: Spec
    gate: Spec
    replay: Spec
    metrics: Tuple[Spec, ...]
    seeds: SeedConfig = field(default_factory=SeedConfig)
    compute: Limits = field(default_factory=Limits)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    description: str = ""
    config_version: int = CONFIG_VERSION

    # ---------------------------------------------------------------- loading
    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RunConfig":
        if not isinstance(raw, Mapping):
            raise ConfigError(f"config must be a mapping, got {type(raw).__name__}")
        unknown = set(raw) - _TOP_LEVEL_KEYS
        if unknown:
            raise ConfigError(
                f"unexpected top-level keys {sorted(unknown)}; allowed: {sorted(_TOP_LEVEL_KEYS)}"
            )
        if "config_version" not in raw:
            raise ConfigError("missing 'config_version'; every config must declare its schema")
        version = raw["config_version"]
        if version not in SUPPORTED_VERSIONS:
            raise ConfigError(
                f"config_version {version!r} is not supported by this code "
                f"(supported: {list(SUPPORTED_VERSIONS)}); migrate the file rather than "
                "reinterpreting it"
            )
        for section in _COMPONENT_SECTIONS:
            if section not in raw:
                raise ConfigError(f"missing required section {section!r}")
        if "name" not in raw:
            raise ConfigError("missing 'name'; runs must be identifiable in artifacts")

        metrics_raw = raw.get("metrics") or []
        if isinstance(metrics_raw, Mapping) or isinstance(metrics_raw, str):
            raise ConfigError("metrics must be a list of component specs")
        try:
            metrics = tuple(Spec.parse(m) for m in metrics_raw)
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"metrics: {exc}") from exc
        names = [m.name for m in metrics]
        duplicates = sorted({n for n in names if names.count(n) > 1})
        if duplicates:
            raise ConfigError(f"metrics: {duplicates} listed more than once")

        def _spec(section: str) -> Spec:
            try:
                return Spec.parse(raw[section])
            except (TypeError, ValueError) as exc:
                raise ConfigError(f"{section}: {exc}") from exc

        return cls(
            name=str(raw["name"]),
            description=str(raw.get("description", "")),
            benchmark=_spec("benchmark"),
            environment=_spec("environment"),
            model=_spec("model"),
            memory=_spec("memory"),
            gate=_spec("gate"),
            replay=_spec("replay"),
            metrics=metrics,
            seeds=SeedConfig.from_dict(raw.get("seeds")),
            compute=_limits_from_dict(raw.get("compute")),
            logging=LoggingConfig.from_dict(raw.get("logging")),
            config_version=int(version),
        )

    @classmethod
    def load(cls, path: str | Path) -> "RunConfig":
        return cls.from_dict(read_mapping(path))

    # ------------------------------------------------------------ serialising
    def as_dict(self) -> Dict[str, Any]:
        return {
            "config_version": self.config_version,
            "name": self.name,
            "description": self.description,
            "benchmark": self.benchmark.as_dict(),
            "environment": self.environment.as_dict(),
            "model": self.model.as_dict(),
            "memory": self.memory.as_dict(),
            "gate": self.gate.as_dict(),
            "replay": self.replay.as_dict(),
            "metrics": [m.as_dict() for m in self.metrics],
            "seeds": self.seeds.as_dict(),
            "compute": self.compute.as_dict(),
            "logging": self.logging.as_dict(),
        }

    def identity_dict(self) -> Dict[str, Any]:
        """Everything that can change a reported number, and nothing else."""
        out = self.as_dict()
        for cosmetic in ("name", "description", "logging"):
            out.pop(cosmetic, None)
        return out

    @property
    def config_hash(self) -> str:
        payload = json.dumps(self.identity_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @property
    def run_id(self) -> str:
        """Readable and unique: name, seed, and the first 12 hash characters."""
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in self.name)
        return f"{safe}__seed{self.seeds.master}__{self.config_hash[:12]}"

    def with_overrides(self, overrides: Mapping[str, Any]) -> "RunConfig":
        """Return a new config with dotted-path values replaced.

        Used by the scheduler to expand sweeps. Paths must already exist, so a
        misspelled sweep axis cannot silently add a key nobody reads.
        """
        raw = apply_overrides(self.as_dict(), overrides)
        return RunConfig.from_dict(raw)

    def with_seed(self, master: int) -> "RunConfig":
        return replace(self, seeds=replace(self.seeds, master=int(master)))

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.as_dict(), sort_keys=False, default_flow_style=False)


# --------------------------------------------------------------------------- #
# Helpers shared with the scheduler
# --------------------------------------------------------------------------- #


def read_mapping(path: str | Path) -> Dict[str, Any]:
    """Load a YAML or JSON mapping. Extension decides the parser."""
    p = Path(path)
    if not p.is_file():
        raise ConfigError(f"config file not found: {p}")
    text = p.read_text(encoding="utf-8")
    try:
        data = json.loads(text) if p.suffix.lower() == ".json" else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ConfigError(f"{p}: cannot parse ({exc})") from exc
    if not isinstance(data, Mapping):
        raise ConfigError(f"{p}: top level must be a mapping, got {type(data).__name__}")
    return dict(data)


def apply_overrides(raw: Mapping[str, Any], overrides: Mapping[str, Any]) -> Dict[str, Any]:
    """Set dotted paths in a nested mapping. Returns a deep copy.

    `model.params.decay` addresses `raw["model"]["params"]["decay"]`. The final key
    may be new (so a component can gain a parameter it does not currently set), but
    every parent must exist and be a mapping: `modl.params.decay` is an error, not
    a new top-level section.
    """
    out = copy.deepcopy(dict(raw))
    for path, value in overrides.items():
        parts = str(path).split(".")
        if not parts or any(not p for p in parts):
            raise ConfigError(f"override path {path!r} is malformed")
        node: Any = out
        for i, part in enumerate(parts[:-1]):
            if not isinstance(node, dict) or part not in node:
                trail = ".".join(parts[: i + 1])
                raise ConfigError(f"override path {path!r}: {trail!r} does not exist in config")
            node = node[part]
            if node is None and i < len(parts) - 2:
                raise ConfigError(f"override path {path!r}: {part!r} is null")
        if not isinstance(node, dict):
            raise ConfigError(f"override path {path!r}: parent is not a mapping")
        node[parts[-1]] = value
    return out


def flatten_axes(grid: Mapping[str, Sequence[Any]]) -> Iterable[Dict[str, Any]]:
    """Cartesian product of a `{dotted_path: [values]}` grid, in declared order."""
    import itertools

    if not grid:
        yield {}
        return
    keys = list(grid)
    for combo in itertools.product(*(list(grid[k]) for k in keys)):
        yield dict(zip(keys, combo))
