"""The experiment loop. Written once; not edited to add components.

Responsibility: drive observations through the configured components in a fixed
order, hand records to metrics, and hand files to the artifact writer.

The step order is fixed and identical for every configuration, because losses from
different orders are not comparable:

    1. predict         model has not seen this target yet -> prequential loss
    2. score
    3. learn           online update
    4. store
    5. gate            how many replay updates to spend now
    6. select          which items to replay
    7. learn each

Nothing in this module knows what a mechanism *means*, which benchmark is running,
or what any metric computes. Every such decision arrives through a registry, so
this file has no reason to change when the science does. That property is what the
plugin protocols exist to buy.

Determinism: all randomness comes from `SeedSet`-derived seeds passed to component
factories. The engine itself draws no random numbers, so a run's result depends
only on its configuration — not on wall-clock time, process identity, worker count,
or which metrics were enabled.
"""

from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from core.budget import Budget, BudgetExceeded
from core.seeds import SeedSet
from core.types import RunResult, RunStatus, StepRecord
from experiments.engine.artifacts import ArtifactWriter, is_complete, read_status, sanitise
from experiments.engine.config import ConfigError, RunConfig
from experiments.engine.logs import ConsoleLogger, JsonlLogger, MultiLogger, NullLogger
from experiments.engine.manifest import build_manifest, utc_now
from experiments.engine.plugins import load_plugins

#: Default artifact root. Overridable per call; the CLI exposes `--root`.
DEFAULT_ROOT = Path("artifacts") / "runs"


class Components:
    """The instantiated component set for one run. Built once, then read-only."""

    __slots__ = ("benchmark", "environment", "model", "memory", "gate", "replay", "metrics")

    def __init__(
        self,
        benchmark: Any,
        environment: Any,
        model: Any,
        memory: Any,
        gate: Any,
        replay: Any,
        metrics: Sequence[Any],
    ) -> None:
        self.benchmark = benchmark
        self.environment = environment
        self.model = model
        self.memory = memory
        self.gate = gate
        self.replay = replay
        self.metrics = list(metrics)

    def describe(self) -> Dict[str, Any]:
        return {
            "benchmark": type(self.benchmark).__name__,
            "environment": type(self.environment).__name__,
            "model": type(self.model).__name__,
            "memory": type(self.memory).__name__,
            "gate": type(self.gate).__name__,
            "replay": type(self.replay).__name__,
            "metrics": [m.name for m in self.metrics],
        }


def build_components(config: RunConfig, seeds: SeedSet) -> Components:
    """Resolve every config section into a live object.

    Injection rules, enforced by `Registry.create` refusing overlaps:

      * the benchmark receives the environment spec and the seed set, and owns
        environment construction — so probes and oracle cannot drift from the
        stream they are supposed to measure;
      * every mechanism receives the environment's `hints` (alphabet, horizon,
        block length). A config cannot set them, which removes a whole class of
        silent mismatch: a `boundary` gate whose period disagrees with the actual
        block length would produce plausible nonsense;
      * memory, gate and replay share the `replay` seed substream, covering both
        replay timing and replay content randomness.
    """
    load_plugins()
    from science.registries import BENCHMARKS, GATES, MEMORIES, METRICS, MODELS, REPLAYS

    benchmark = BENCHMARKS.create(config.benchmark, seeds=seeds, environment=config.environment)

    # Validate before doing any work: an invalid metric/benchmark pairing must be
    # reported before an environment is generated, not after.
    metrics = [METRICS.create(spec) for spec in config.metrics]
    needs_oracle = [m.name for m in metrics if getattr(m, "requires_oracle", False)]
    if needs_oracle and not getattr(benchmark, "has_oracle", False):
        raise ConfigError(
            f"metrics {needs_oracle} require a ground-truth oracle, but benchmark "
            f"{config.benchmark.name!r} does not provide one; remove the metric or "
            "choose a benchmark with an oracle"
        )

    environment = benchmark.build_environment()
    hints: Dict[str, Any] = dict(getattr(environment, "hints", {}))
    hints.setdefault("total_steps", environment.total_steps)
    hints.setdefault("n_tasks", getattr(environment, "n_tasks", 1))
    replay_seed = seeds["replay"]

    return Components(
        benchmark=benchmark,
        environment=environment,
        model=MODELS.create(config.model, **hints),
        memory=MEMORIES.create(config.memory, seed=replay_seed, **hints),
        gate=GATES.create(config.gate, seed=replay_seed, **hints),
        replay=REPLAYS.create(config.replay, seed=replay_seed, **hints),
        metrics=metrics,
    )


def run_dir_for(config: RunConfig, root: str | Path = DEFAULT_ROOT) -> Path:
    """`<root>/<experiment name>/<run id>`. Stable across processes and machines."""
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in config.name)
    return Path(root) / safe / config.run_id


def run(
    config: RunConfig,
    root: str | Path = DEFAULT_ROOT,
    resume: bool = True,
    quiet: bool = False,
) -> RunResult:
    """Execute one configuration and write its artifacts.

    Never raises for an experiment-level failure: a batch of 200 runs must not lose
    199 results because one condition was misconfigured. The failure is recorded in
    `status.json` and `manifest.json`, and returned as a non-ok `RunResult`.
    `ConfigError` is the exception — it means the request itself was invalid, and
    silently returning "failed" would hide a typo in a sweep definition.
    """
    run_dir = run_dir_for(config, root)
    if resume and is_complete(run_dir, config.config_hash):
        return _result_from_disk(config, run_dir)

    seeds = SeedSet.build(config.seeds.master, config.seeds.mode, config.seeds.overrides)
    components = build_components(config, seeds)  # ConfigError propagates: see docstring

    writer = ArtifactWriter(run_dir, step_format=config.logging.step_format)
    logger = _build_logger(config, run_dir, quiet)
    budget = Budget(limits=config.compute)

    writer.write_config(config.to_yaml())
    writer.write_status(RunStatus.RUNNING, config.config_hash, config.run_id)

    env = components.environment
    checkpoints: Dict[int, Tuple[int, int]] = {
        step: (block, task) for block, (task, step) in enumerate(env.checkpoints())
    }
    started_at = utc_now()
    logger.event(
        "run_start",
        {
            "run_id": config.run_id,
            "config_hash": config.config_hash,
            "total_steps": env.total_steps,
            "seed_mode": seeds.mode,
            "master_seed": seeds.master,
            **components.describe(),
        },
    )

    status = RunStatus.COMPLETED
    error = ""
    budget.start()
    try:
        _execute(components, budget, writer, logger, checkpoints)
    except BudgetExceeded as exc:
        # A declared ceiling is an expected outcome, not a failure. The manifest
        # records `compute.truncated_by` so a truncated run is never mistaken for
        # a complete one.
        logger.event("truncated", {"reason": str(exc), "steps": budget.steps})
    except ConfigError:
        budget.stop()
        writer.finish_steps()
        writer.write_status(RunStatus.FAILED, config.config_hash, config.run_id, "config error")
        logger.close()
        raise
    except Exception as exc:  # noqa: BLE001 — see docstring
        status = RunStatus.FAILED
        error = f"{type(exc).__name__}: {exc}"
        logger.event("error", {"error": error, "traceback": traceback.format_exc()})
    finally:
        budget.stop()
        writer.finish_steps()

    results: Dict[str, Any] = {}
    if status is RunStatus.COMPLETED:
        for metric in components.metrics:
            try:
                results[metric.name] = metric.result()
            except Exception as exc:  # noqa: BLE001 — one bad metric must not void the run
                results[metric.name] = {"error": f"{type(exc).__name__}: {exc}"}

    writer.write_json("metrics.json", results)
    writer.write_probes_csv()
    plots = writer.write_plots() if config.logging.plots else []

    manifest = build_manifest(
        run_id=config.run_id,
        config=config.as_dict(),
        config_hash=config.config_hash,
        seeds=seeds.as_dict(),
        benchmark=_safe_describe(components.benchmark),
        components=components.describe(),
        metrics_requested=[m.name for m in config.metrics],
        started_at=started_at,
        finished_at=utc_now(),
        duration_seconds=budget.wall_seconds,
        compute=budget.as_dict(),
        status=status.value,
        error=error,
        p1v0_version=_frozen_rig_version(),
    )
    manifest["artifacts"] = {"plots": plots}
    writer.write_json("manifest.json", manifest)
    writer.write_status(
        status,
        config.config_hash,
        config.run_id,
        error=error,
        extra={"duration_seconds": round(budget.wall_seconds, 3), "steps": budget.steps},
    )
    logger.event(
        "run_end",
        {
            "run_id": config.run_id,
            "status": status.value,
            "steps": budget.steps,
            "updates_total": budget.updates_total,
            "seconds": round(budget.wall_seconds, 3),
            "error": error,
        },
    )
    logger.close()

    # Inventory last, and only after the log is closed: a hash taken before the
    # final write would never match, making `p1 verify` useless.
    writer.write_inventory()

    return RunResult(
        run_id=config.run_id,
        config_hash=config.config_hash,
        status=status,
        metrics=sanitise(results),
        compute=budget.as_dict(),
        run_dir=str(run_dir),
        error=error,
    )


def _execute(
    components: Components,
    budget: Budget,
    writer: ArtifactWriter,
    logger: Any,
    checkpoints: Mapping[int, Tuple[int, int]],
) -> None:
    """The loop. Deliberately flat: every branch here is a per-step cost."""
    model = components.model
    memory = components.memory
    gate = components.gate
    replay = components.replay
    metrics = components.metrics
    benchmark = components.benchmark
    probe_cost = int(getattr(benchmark, "predictions_per_probe", 0))

    writer.start(components.environment.total_steps)

    for obs in components.environment:
        budget.check()

        prediction = model.predict(obs.context)
        loss = model.score(prediction, obs.target)
        model.learn(obs.context, obs.target)
        memory.append(obs)

        k = gate.replay_count(loss, obs.t)
        replays = 0
        if k > 0:
            batch = replay.select(memory, k, obs)
            for context, target, weight in batch:
                model.learn(context, target, weight)
            replays = len(batch)
            budget.replay_batches += 1
            budget.replay_shortfall += k - replays

        budget.steps += 1
        budget.predictions += 1
        budget.online_updates += 1
        budget.replay_updates += replays

        rec = StepRecord(
            t=obs.t,
            task=obs.task,
            loss=loss,
            replays=replays,
            gate_fired=k > 0,
            buffer_size=len(memory),
            updates=1 + replays,
        )
        for metric in metrics:
            metric.on_step(rec)
        writer.write_step(rec)

        checkpoint = checkpoints.get(obs.t)
        if checkpoint is not None:
            block, trained_task = checkpoint
            probe = benchmark.evaluate(model, block, obs.t, trained_task)
            for metric in metrics:
                metric.on_probe(probe)
            writer.write_probe(probe)
            budget.probe_evaluations += 1
            budget.probe_predictions += probe_cost
            logger.event(
                "probe",
                {
                    "block": block,
                    "step": obs.t,
                    "trained_task": trained_task,
                    "losses": list(probe.losses),
                },
            )


def _build_logger(config: RunConfig, run_dir: Path, quiet: bool) -> Any:
    sinks: List[Any] = [JsonlLogger(run_dir / "run.log")]
    if config.logging.console and not quiet:
        sinks.append(ConsoleLogger(level=config.logging.level))
    return MultiLogger(sinks) if sinks else NullLogger()


def _result_from_disk(config: RunConfig, run_dir: Path) -> RunResult:
    """Reconstruct a `RunResult` for a run that was already completed."""
    import json

    metrics: Dict[str, Any] = {}
    compute: Dict[str, Any] = {}
    metrics_path = run_dir / "metrics.json"
    manifest_path = run_dir / "manifest.json"
    try:
        if metrics_path.is_file():
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        if manifest_path.is_file():
            compute = json.loads(manifest_path.read_text(encoding="utf-8")).get("compute", {})
    except (OSError, json.JSONDecodeError):
        pass
    status = read_status(run_dir) or {}
    return RunResult(
        run_id=str(status.get("run_id", config.run_id)),
        config_hash=config.config_hash,
        status=RunStatus.COMPLETED,
        metrics=metrics,
        compute=compute,
        run_dir=str(run_dir),
    )


def _safe_describe(obj: Any) -> Dict[str, Any]:
    describe = getattr(obj, "describe", None)
    if not callable(describe):
        return {"name": type(obj).__name__}
    try:
        described = describe()
    except Exception as exc:  # noqa: BLE001 — provenance must not break a run
        return {"name": type(obj).__name__, "describe_error": str(exc)}
    return dict(described) if isinstance(described, Mapping) else {"value": repr(described)}


def _frozen_rig_version() -> str:
    try:
        import p1v0

        return str(getattr(p1v0, "__version__", ""))
    except Exception:  # noqa: BLE001
        return ""
