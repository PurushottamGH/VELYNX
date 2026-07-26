"""VELYNX Metrics Subsystem.

Single source of truth for all experiment and benchmark metrics.
Consolidates from validation/metrics.py, research/metrics.py, and research/stats.py.
"""

import math
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict

# --- Free Energy Coefficients (Single Source of Truth) ---
LAMBDA = 1.0  # weight on transition uncertainty (Entropy H)
MU = 2.0  # weight on spatial prediction error (Surprise S)
NU = 0.5  # weight on structural load (Active clusters + anomaly volume)

# --- Thresholds ---
ENTROPY_HIGH = 2.0  # bits
SURPRISE_HIGH = 0.5  # Euclidean distance
SURPRISE_MILD = 0.2  # Euclidean distance
PRESSURE_HIGH = 1.0  # anomalies/cluster
PRESSURE_MILD = 0.25  # anomalies/cluster
ENERGY_EXHAUSTION = 18.0  # free energy


@dataclass
class MetricsRecord:
    experiment_id: str
    run_id: str
    tick: int
    free_energy: float = 0.0
    entropy: float = 0.0
    surprise: float = 0.0
    structural_load: float = 0.0
    prediction_error: float = 0.0
    belief_count: int = 0
    concept_count: int = 0
    mdl_gain: float = 0.0
    kill_criteria_triggered: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class MetricsCollector:
    def __init__(self, experiment_id: str, run_id: str, output_dir: Optional[str] = None):
        self.experiment_id = experiment_id
        self.run_id = run_id
        self.records: List[MetricsRecord] = []
        self.output_dir = Path(output_dir) if output_dir else None

    def record(self, tick: int, **kwargs) -> MetricsRecord:
        rec = MetricsRecord(
            experiment_id=self.experiment_id, run_id=self.run_id, tick=tick, **kwargs
        )
        self.records.append(rec)
        return rec

    def compute_free_energy(self, entropy: float, surprise: float, structural_load: float) -> float:
        return LAMBDA * entropy + MU * surprise + NU * structural_load

    def check_kill_criteria(self, free_energy: float, entropy: float, surprise: float) -> List[str]:
        triggered = []
        if free_energy > ENERGY_EXHAUSTION:
            triggered.append("energy_exhaustion")
        if entropy > ENTROPY_HIGH:
            triggered.append("entropy_high")
        if surprise > SURPRISE_HIGH:
            triggered.append("surprise_high")
        return triggered

    def save(self, path: Optional[Path] = None):
        output = path or (self.output_dir / "metrics.jsonl" if self.output_dir else None)
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            with open(output, "w") as f:
                for rec in self.records:
                    f.write(json.dumps(rec.to_dict()) + "\n")

    def load(self, path: Path) -> List[MetricsRecord]:
        self.records = []
        with open(path) as f:
            for line in f:
                if line.strip():
                    self.records.append(MetricsRecord.from_dict(json.loads(line)))
        return self.records

    def summary(self) -> Dict:
        if not self.records:
            return {}
        energies = [r.free_energy for r in self.records]
        surprises = [r.surprise for r in self.records]
        entropies = [r.entropy for r in self.records]
        return {
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "num_ticks": len(self.records),
            "mean_free_energy": float(np.mean(energies)),
            "max_free_energy": float(np.max(energies)),
            "mean_surprise": float(np.mean(surprises)),
            "mean_entropy": float(np.mean(entropies)),
            "kill_criteria_triggered": any(r.kill_criteria_triggered for r in self.records),
        }


# --- Statistical Analysis ---


def bootstrap_ci(
    data: np.ndarray, statistic=np.mean, n_resamples: int = 10000, ci: float = 0.95
) -> Tuple[float, float]:
    """Bootstrap confidence interval for a statistic."""
    n = len(data)
    bootstraps = np.array(
        [statistic(np.random.choice(data, size=n, replace=True)) for _ in range(n_resamples)]
    )
    alpha = (1.0 - ci) / 2.0
    lower = np.percentile(bootstraps, alpha * 100)
    upper = np.percentile(bootstraps, (1.0 - alpha) * 100)
    return float(lower), float(upper)


def effect_size_cohens_d(control: np.ndarray, treatment: np.ndarray) -> float:
    """Cohen's d effect size."""
    n1, n2 = len(control), len(treatment)
    s1, s2 = np.var(control, ddof=1), np.var(treatment, ddof=1)
    pooled = math.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if pooled == 0:
        return 0.0
    return float((np.mean(treatment) - np.mean(control)) / pooled)


def permutation_test(
    control: np.ndarray, treatment: np.ndarray, n_permutations: int = 10000
) -> float:
    """Two-sided permutation test p-value."""
    observed = abs(np.mean(treatment) - np.mean(control))
    combined = np.concatenate([control, treatment])
    n = len(control)
    count = 0
    for _ in range(n_permutations):
        np.random.shuffle(combined)
        perm_control = combined[:n]
        perm_treatment = combined[n:]
        perm_diff = abs(np.mean(perm_treatment) - np.mean(perm_control))
        if perm_diff >= observed:
            count += 1
    return (count + 1) / (n_permutations + 1)


def compute_nmi(labels_true: np.ndarray, labels_pred: np.ndarray) -> float:
    """Normalized Mutual Information."""
    from sklearn.metrics.cluster import normalized_mutual_info_score

    return float(normalized_mutual_info_score(labels_true, labels_pred))


class MetricsReport:
    """Generate human-readable and publication-ready metrics reports."""

    @staticmethod
    def generate_summary(records: List[MetricsRecord], output_path: Optional[Path] = None) -> str:
        collector = MetricsCollector("", "")
        collector.records = records
        summary = collector.summary()
        lines = [
            "=" * 60,
            f"Experiment: {summary.get('experiment_id', '?')}",
            f"Run: {summary.get('run_id', '?')}",
            f"Ticks: {summary.get('num_ticks', 0)}",
            "-" * 60,
            f"Mean free energy:  {summary.get('mean_free_energy', 0):.4f}",
            f"Max free energy:   {summary.get('max_free_energy', 0):.4f}",
            f"Mean surprise:     {summary.get('mean_surprise', 0):.4f}",
            f"Mean entropy:      {summary.get('mean_entropy', 0):.4f}",
            f"Kill criteria hit: {summary.get('kill_criteria_triggered', False)}",
            "=" * 60,
        ]
        report = "\n".join(lines)
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
        return report
