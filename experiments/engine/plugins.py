"""Plugin bootstrap: the one place that decides what exists.

Responsibility: import every module that registers a component, exactly once.

There is no filesystem scan and no entry-point discovery. Both would make the set
of available mechanisms depend on the environment rather than on the source tree,
which is the wrong trade for a research platform: a run must be explainable from
the repository alone. The cost is one line per new module, in a file that is
trivial to review.

Import order does not matter, but the import *set* is the contract: a component
that is not reachable from here cannot be selected by any config.
"""

from __future__ import annotations

_loaded = False


def load_plugins() -> None:
    """Populate every registry. Idempotent, and safe to call in worker processes."""
    global _loaded
    if _loaded:
        return

    # Mechanisms and controls (models, memories, gates, replay policies, environments)
    import science.mechanisms  # noqa: F401

    # Measurement definitions
    import science.metrics  # noqa: F401

    # Benchmarks: scientific harnesses, then engine test doubles
    import benchmarks.retention  # noqa: F401
    import benchmarks.testing  # noqa: F401

    # Logger sinks
    import experiments.engine.logs  # noqa: F401

    _loaded = True


def registry_summary() -> dict[str, list[str]]:
    """`{kind: [available names]}`. Used by `p1 list` and by tests."""
    load_plugins()
    from experiments.engine.logs import LOGGERS
    from science.registries import ALL

    summary = {kind: reg.available() for kind, reg in ALL.items()}
    summary["logger"] = LOGGERS.available()
    return summary
