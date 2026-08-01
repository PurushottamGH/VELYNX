"""Run configuration, variant registry, and artifact writing.

Responsibility: the only module that touches disk or the command line.

Variants are mechanism sets. Comparing them is how v0 answers "which
mechanisms are necessary":
    online           -- online learning only (no memory, no replay)
    replay_always    -- memory + unconditional replay
    replay_surprise  -- memory + replay gated on prediction loss
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from p1v0 import gate as gates
from p1v0 import metrics
from p1v0.loop import run
from p1v0.memory import NullBuffer, ReplayBuffer
from p1v0.model import CountModel
from p1v0.probe import ProbeSuite
from p1v0.stream import TaskStream

VARIANTS = ("online", "replay_always", "replay_surprise")


@dataclass
class Config:
    variant: str = "replay_surprise"
    seed: int = 0
    n_tasks: int = 4
    alphabet: int = 8
    steps_per_task: int = 2000
    cycles: int = 1
    fanout: int = 2
    alpha: float = 0.5
    decay: float = 0.99
    capacity: int = 1000
    replay_k: int = 4
    replay_weight: float = 1.0
    surprise_threshold: float = 1.5
    probe_pairs: int = 500


def build(cfg: Config):
    """Instantiate the mechanism set for cfg.variant."""
    if cfg.variant not in VARIANTS:
        raise ValueError(f"unknown variant {cfg.variant!r}; expected one of {VARIANTS}")

    stream = TaskStream(
        n_tasks=cfg.n_tasks,
        alphabet=cfg.alphabet,
        steps_per_task=cfg.steps_per_task,
        seed=cfg.seed,
        cycles=cfg.cycles,
        fanout=cfg.fanout,
    )
    model = CountModel(alphabet=cfg.alphabet, alpha=cfg.alpha, decay=cfg.decay)

    if cfg.variant == "online":
        memory = NullBuffer(seed=cfg.seed)
        gate = gates.NeverGate()
    elif cfg.variant == "replay_always":
        memory = ReplayBuffer(capacity=cfg.capacity, seed=cfg.seed)
        gate = gates.AlwaysGate(k=cfg.replay_k)
    else:
        memory = ReplayBuffer(capacity=cfg.capacity, seed=cfg.seed)
        gate = gates.SurpriseGate(threshold=cfg.surprise_threshold, k=cfg.replay_k)

    return stream, model, memory, gate


def execute(cfg: Config) -> Tuple[Dict, List[Dict]]:
    """Run one configuration. Returns (summary, step_records)."""
    stream, model, memory, gate = build(cfg)
    probes = ProbeSuite(stream, n_pairs=cfg.probe_pairs)
    checkpoints = {end: task for task, end in stream.blocks()}

    losses: List[float] = []
    records: List[Dict] = []
    probe_matrix: List[List[float]] = []
    block_tasks: List[int] = []

    for rec in run(stream, model, memory, gate, replay_weight=cfg.replay_weight):
        losses.append(rec.loss)
        records.append(asdict(rec))
        if rec.t in checkpoints:
            probe_matrix.append(probes.evaluate(model))
            block_tasks.append(checkpoints[rec.t])

    summary = {
        "config": asdict(cfg),
        "uniform_baseline": metrics.uniform_baseline(cfg.alphabet),
        "online": metrics.summarise_online(losses),
        "probe_matrix": probe_matrix,
        "block_tasks": block_tasks,
        "gate_fired_steps": gate.n_fired,
        "gate_total_replays": gate.n_replays,
        "buffer_size": len(memory),
        **metrics.forgetting(probe_matrix, block_tasks),
    }
    return summary, records


def write_artifacts(summary: Dict, records: List[Dict], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (out_dir / "steps.jsonl").open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")
    return out_dir


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a P1 v0 continual-learning trial.")
    parser.add_argument("--variant", default="replay_surprise", choices=list(VARIANTS) + ["all"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--n-tasks", type=int, default=4)
    parser.add_argument("--alphabet", type=int, default=8)
    parser.add_argument("--steps-per-task", type=int, default=2000)
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--decay", type=float, default=0.99)
    parser.add_argument("--replay-k", type=int, default=4)
    parser.add_argument("--out", default="p1v0_runs")
    parser.add_argument("--no-artifacts", action="store_true")
    args = parser.parse_args(argv)

    variants = list(VARIANTS) if args.variant == "all" else [args.variant]
    for variant in variants:
        cfg = Config(
            variant=variant,
            seed=args.seed,
            n_tasks=args.n_tasks,
            alphabet=args.alphabet,
            steps_per_task=args.steps_per_task,
            cycles=args.cycles,
            decay=args.decay,
            replay_k=args.replay_k,
        )
        summary, records = execute(cfg)
        if not args.no_artifacts:
            write_artifacts(summary, records, Path(args.out) / f"{variant}_seed{args.seed}")
        print(
            f"{variant:16s} "
            f"online_tail={summary['online']['online_loss_tail']:.4f} "
            f"retention={summary['retention']:+.4f} "
            f"replays={summary['gate_total_replays']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
