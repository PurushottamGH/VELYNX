"""Benchmark runner.

Consolidated from validation/runner.py and research/runner.py.
Provides a uniform interface for running all benchmark types.
"""
import sys
import time
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments.artifacts import ArtifactStore
from experiments.metrics import MetricsCollector


@dataclass
class BenchmarkResult:
    name: str
    passed: bool
    metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0


class BenchmarkRunner:
    """Generic benchmark runner with artifact tracking."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path("artifacts/benchmarks")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.store = ArtifactStore(base_path=self.output_dir.parent)
        self.results: List[BenchmarkResult] = []

    def register(self, name: str, fn: Callable[[], BenchmarkResult]) -> None:
        """Register a benchmark function."""
        setattr(self, f"_benchmark_{name}", fn)
        # Store in a registry dict too
        if not hasattr(self, "_benchmark_registry"):
            self._benchmark_registry = {}
        self._benchmark_registry[name] = fn

    def run(self, name: str) -> BenchmarkResult:
        fn = self._benchmark_registry.get(name)
        if not fn:
            raise ValueError(f"Unknown benchmark: {name}")

        start = time.time()
        try:
            result = fn()
        except Exception as e:
            result = BenchmarkResult(
                name=name,
                passed=False,
                errors=[str(e)],
            )
        result.duration_seconds = time.time() - start
        self.results.append(result)

        self.store.store_benchmark_result(name, asdict(result))
        return result

    def run_all(self) -> List[BenchmarkResult]:
        for name in sorted(self._benchmark_registry.keys()):
            self.run(name)
        return self.results

    def summary(self) -> Dict:
        passed = sum(1 for r in self.results if r.passed)
        return {
            "total": len(self.results),
            "passed": passed,
            "failed": len(self.results) - passed,
            "results": [asdict(r) for r in self.results],
        }

    def save_summary(self, path: Optional[Path] = None):
        output = path or (self.output_dir / "summary.json")
        with open(output, "w") as f:
            json.dump(self.summary(), f, indent=2)
