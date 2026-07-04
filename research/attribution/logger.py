"""
research/attribution/logger.py
===============================

The :class:`AttributionLogger` — structured logging for the R3 counterfactual
evaluation experiment.

Writes two kinds of output into a timestamp-stamped results directory:

1. **Window-level JSONL** (``evaluation_log.jsonl``) — one line per
   consolidation window, each a JSON object with:

   * ``window_index``, ``tick``
   * ``pool_diversity`` (strategy entropy, average pair overlap, consensus)
   * ``evaluator_result`` (winner, rankings with energy/rank/margin)
   * ``counterfactual_result`` (counterfactual_best, pareto_frontier,
     no_merge_energy, replay_error per proposal)
   * ``is_top_k_correct`` (boolean: did the policy's winner land in the top 3
     of counterfactual_best ranking?)
   * ``winner_is_pareto_optimal``

2. **Experiment manifest** (``experiment_manifest.json``) — the full
   reproducibility bundle:

   * Config (seeds, hyperparameters, policy settings)
   * Environment hashes (config hash, code hash)
   * Git commit hash, Python version, platform info
   * Source panel description
   * Aggregated attribution summary statistics

Standard library + optional ``subprocess`` for Git hash (falls back gracefully).
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from research.attribution.counterfactual import CounterfactualResult
from research.attribution.evaluator import EvaluatorResult
from research.attribution.metrics import aggregate_attribution, AttributionSummary
from research.proposals.base import ProposalSource


@dataclass
class WindowRecord:
    """One row of the evaluation log — a single consolidation window."""

    window_index: int
    tick: int
    evaluator: EvaluatorResult
    counterfactual: CounterfactualResult
    is_top_k_correct: Optional[bool] = None
    winner_is_pareto_optimal: Optional[bool] = None

    def to_jsonl(self) -> Dict[str, Any]:
        """Produce a JSON-safe dict for serialisation."""
        winner = self.evaluator.winner

        # Build counterfactual ranking of proposal_ids (best-first by
        # actual_energy_held_out or energy_after).
        ranked_ids: List[str] = []
        scored = list(self.evaluator.rankings)
        # Sort by counterfactual energy when available, else by energy_after.
        def _cf_key(p):
            ct = p.counterfactual_block or {}
            return ct.get("actual_energy_held_out") or ct.get("energy_merge") or float("inf")
        cf_ranked = sorted(scored, key=_cf_key)
        ranked_ids = [p.proposal_id for p in cf_ranked]

        # Per-proposal replay errors.
        replay_errors: Dict[str, Optional[float]] = {}
        for p in self.evaluator.rankings:
            ct = p.counterfactual_block or {}
            err = ct.get("replay_error")
            replay_errors[p.proposal_id] = float(err) if err is not None else None

        return {
            "window_index": self.window_index,
            "tick": self.tick,
            "pool_diversity": self.evaluator.pool_diversity,
            "evaluator_result": self.evaluator.as_dict(),
            "counterfactual_result": self.counterfactual.as_dict(),
            "counterfactual_ranking_ids": ranked_ids,
            "counterfactual_best_id": self.counterfactual.best_id(),
            "replay_errors_per_proposal": replay_errors,
            "is_top_k_correct": self.is_top_k_correct,
            "winner_is_pareto_optimal": self.winner_is_pareto_optimal,
        }


class AttributionLogger:
    """Structured logging and manifest generation for the R3 experiment.

    Parameters
    ----------
    output_dir :
        Root directory for results. A timestamped subdirectory is created
        within it: ``<output_dir>/attribution_YYYYMMDDTHHMMSS/``.
    config :
        The experiment configuration dict (seeds, hyperparameters, etc.).
    sources :
        The proposal source panel (used for the manifest's source
        descriptions).
    """

    def __init__(
        self,
        output_dir: str,
        config: Dict[str, Any],
        sources: Optional[List[ProposalSource]] = None,
    ):
        self.output_dir = output_dir
        self.config = dict(config)
        self.sources = sources or []
        self.windows: List[WindowRecord] = []

        # Timestamped subdirectory.
        self.timestamp = time.strftime("%Y%m%dT%H%M%S")
        self.run_dir = os.path.join(output_dir, f"attribution_{self.timestamp}")
        os.makedirs(self.run_dir, exist_ok=True)

        # Paths.
        self.jsonl_path = os.path.join(self.run_dir, "evaluation_log.jsonl")
        self.manifest_path = os.path.join(self.run_dir, "experiment_manifest.json")

        # Open JSONL for append-only writing.
        self._jsonl_file: Optional[Any] = None

    # -- window logging ----------------------------------------------------

    def log_window(self, record: WindowRecord) -> None:
        """Write one evaluation-window record to the JSONL stream."""
        self.windows.append(record)
        if self._jsonl_file is None:
            self._jsonl_file = open(self.jsonl_path, "w", encoding="utf-8")
        payload = record.to_jsonl()
        self._jsonl_file.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")
        self._jsonl_file.flush()

    # -- manifest generation -----------------------------------------------

    def write_manifest(self) -> str:
        """Generate and write the experiment manifest.

        Returns the path to the written manifest file.
        """
        manifest = self._build_manifest()
        with open(self.manifest_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        return self.manifest_path

    def close(self) -> None:
        """Flush and close the JSONL file."""
        if self._jsonl_file is not None:
            self._jsonl_file.close()
            self._jsonl_file = None

    def _build_manifest(self) -> Dict[str, Any]:
        """Assemble the full reproducibility manifest."""
        summary = self._compute_summary()

        # Collect per-window aggregate data for the summary.
        window_records: List[Dict[str, Any]] = []
        for w in self.windows:
            wr = {
                "winner_id": w.evaluator.winner_id(),
                "counterfactual_best_id": w.counterfactual.best_id(),
                "counterfactual_ranking": [],
                "winner_is_pareto_optimal": w.winner_is_pareto_optimal,
            }
            # Build counterfactual ranking for top-K from the counterfactual result.
            cf = w.counterfactual
            wr["counterfactual_ranking"] = cf.pareto_frontier or []
            # Also compute avg replay error for this window.
            errs = [
                v for v in w.to_jsonl().get("replay_errors_per_proposal", {}).values()
                if v is not None
            ]
            wr["avg_replay_error"] = sum(errs) / len(errs) if errs else None
            window_records.append(wr)

        attr_summary = aggregate_attribution(window_records)
        config_hash = self._config_hash()
        code_hash = self._code_hash()

        return {
            "sprint": "R3",
            "experiment": "counterfactual_merge_evaluation",
            "schema_version": "r3.0",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            # --- Reproducibility ------------------------------------------
            "reproducibility": {
                "git_commit": _git_commit_hash(),
                "python_version": sys.version,
                "platform": platform.platform(),
                "platform_arch": platform.machine(),
                "system": platform.system(),
                "node": platform.node(),
                "config_hash": config_hash,
                "code_hash": code_hash,
            },
            # --- Configuration --------------------------------------------
            "configuration": self.config,
            "source_panel": [s.describe() for s in self.sources],
            # --- Summary statistics ---------------------------------------
            "summary": attr_summary.as_dict(),
            "num_windows": len(self.windows),
            # --- Output files ---------------------------------------------
            "artifacts": {
                "evaluation_log": "evaluation_log.jsonl",
                "experiment_manifest": "experiment_manifest.json",
            },
        }

    def _compute_summary(self) -> AttributionSummary:
        """Aggregate all logged windows into summary statistics."""
        records: List[Dict[str, Any]] = []
        for w in self.windows:
            wr = {
                "winner_id": w.evaluator.winner_id(),
                "counterfactual_best_id": w.counterfactual.best_id(),
                "counterfactual_ranking": [],
                "winner_is_pareto_optimal": w.winner_is_pareto_optimal,
            }
            # Ranking from the counterfactual result.
            ranked_ids: List[str] = []
            scored = list(w.evaluator.rankings)
            def _cf_key(p):
                ct = p.counterfactual_block or {}
                return ct.get("actual_energy_held_out") or ct.get("energy_merge") or float("inf")
            cf_ranked = sorted(scored, key=_cf_key)
            ranked_ids = [p.proposal_id for p in cf_ranked]
            wr["counterfactual_ranking"] = ranked_ids

            # Avg replay error per window.
            j = w.to_jsonl()
            errs = [v for v in j.get("replay_errors_per_proposal", {}).values() if v is not None]
            wr["avg_replay_error"] = sum(errs) / len(errs) if errs else None
            records.append(wr)
        return aggregate_attribution(records)

    def _config_hash(self) -> str:
        """Stable SHA-256 hash of the configuration payload."""
        canonical = json.dumps(self.config, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]

    def _code_hash(self) -> str:
        """SHA-256 of the attribution package source files' concatenation.

        Produces a stable fingerprint of the evaluation code itself. Falls
        back to the git commit if files can't be read.
        """
        try:
            pkg_dir = os.path.dirname(os.path.abspath(__file__))
            files = sorted(
                f for f in os.listdir(pkg_dir)
                if f.endswith(".py") and f != "__pycache__"
            )
            hasher = hashlib.sha256()
            for fn in files:
                with open(os.path.join(pkg_dir, fn), "rb") as fh:
                    hasher.update(fh.read())
            return hasher.hexdigest()[:12]
        except Exception:
            return "unavailable"

    def __enter__(self) -> "AttributionLogger":
        return self

    def __exit__(self, *args: Any) -> None:
        self.write_manifest()
        self.close()


def _git_commit_hash() -> str:
    """Return the current Git commit hash, or ``"unavailable"``."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unavailable"


__all__ = [
    "AttributionLogger",
    "WindowRecord",
]
