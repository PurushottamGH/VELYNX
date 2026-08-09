"""P1 experiment engine — configuration-driven execution.

Responsibility: run configurations. It knows nothing about what a mechanism means
or what a metric computes; every such choice arrives through a registry.

    config.py     versioned run configuration and dotted-path overrides
    plugins.py    the single import list that defines what exists
    engine.py     the fixed experiment loop, one run at a time
    scheduler.py  sweeps, grids, multi-seed batches, parallelism, resume
    artifacts.py  the on-disk layout and every file written
    manifest.py   provenance: git state, runtime, timing, compute
    logs.py       event sinks
    cli.py        argument parsing and exit codes

Import direction: this package imports `benchmarks`, `science` and `core`; none of
them import it.
"""

from __future__ import annotations

from experiments.engine.config import CONFIG_VERSION, ConfigError, RunConfig
from experiments.engine.engine import DEFAULT_ROOT, build_components, run, run_dir_for
from experiments.engine.scheduler import Sweep, batch_summary, pending_runs, run_batch

__all__ = [
    "CONFIG_VERSION",
    "ConfigError",
    "DEFAULT_ROOT",
    "RunConfig",
    "Sweep",
    "batch_summary",
    "build_components",
    "pending_runs",
    "run",
    "run_batch",
    "run_dir_for",
]
