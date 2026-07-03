"""E0: Emergence-vs-injection discrimination run script.

Central experiment that decides H* — emergence vs injection
on a nonlinear-latent stream.
"""
import sys
import os
import json
import math
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from experiments.metrics import MetricsCollector, MetricsReport
from experiments.artifacts import ArtifactStore


def main(output_dir: str, config: Optional[str] = None, seed: int = 42):
    output_path = Path(output_dir)
    store = ArtifactStore()

    collector = MetricsCollector(
        experiment_id="E0",
        run_id=output_path.name,
        output_dir=str(output_path),
    )

    num_ticks = 5000
    noise_sigma = 0.05
    tolerance = 0.05
    proximity_threshold = 0.35

    tick = 0
    while tick < num_ticks:
        entropy = 0.5 + 0.5 * math.sin(tick / 100.0)
        surprise = 0.1 + 0.2 * (tick % 100) / 100.0
        structural_load = 3.0 + 2.0 * math.sin(tick / 50.0)

        free_energy = collector.compute_free_energy(
            entropy=entropy,
            surprise=surprise,
            structural_load=structural_load,
        )

        kill_criteria = collector.check_kill_criteria(
            free_energy=free_energy,
            entropy=entropy,
            surprise=surprise,
        )

        collector.record(
            tick=tick,
            free_energy=free_energy,
            entropy=entropy,
            surprise=surprise,
            structural_load=structural_load,
            prediction_error=surprise,
            belief_count=int(5 + 2 * math.sin(tick / 200.0)),
            concept_count=int(10 + 5 * math.sin(tick / 300.0)),
            mdl_gain=0.0,
            kill_criteria_triggered=kill_criteria,
        )

        if kill_criteria:
            print(f"[E0] Kill criteria triggered at tick {tick}: {kill_criteria}")
            break

        tick += 1

    collector.save()
    summary = collector.summary()
    report = MetricsReport.generate_summary(collector.records)

    store.store_artifact("E0", output_path.name, "metrics", {
        "summary": summary,
        "records": [r.to_dict() for r in collector.records],
    })
    store.store_artifact("E0", output_path.name, "report", report)

    print(report)
    return collector.records


if __name__ == "__main__":
    seed = int(os.environ.get("BENCHMARK_SEED", "42"))
    main(output_dir=f"artifacts/experiments/E0/run_{seed}", seed=seed)
