"""
research/artifacts.py
=====================

Immutable, reproducible per-experiment artifacts (Sprint R1, Task 5).

For every run the writer emits the seven required JSON files into a fresh
``exp_NNNN`` directory:

* ``experiment.json``   — experiment identity, independent variables, schema
                          version, and a content-integrity hash.
* ``metrics.json``      — the run's raw measurement record, the per-metric
                          extracted scalars, and the metric-registry metadata.
* ``summary.json``      — the compact human-readable run summary.
* ``configuration.json``— the exact, fully-resolved run configuration.
* ``policy.json``       — the policy's self-description (incl. energy function).
* ``seed.json``         — every seed used, for bit-exact reproduction.
* ``decision_audit.json``— one record per evaluated merge proposal.

Immutability & reproducibility
------------------------------
* **Immutable.** The writer refuses to write into a directory that already
  exists (``FileExistsError``) unless ``allow_overwrite=True`` is explicitly
  passed. Artifacts are written once and never edited in place.
* **Reproducible.** Re-running the identical :class:`RunConfig` reproduces every
  *scientific* artifact byte-for-byte. The only non-reproducible field is the
  wall-clock ``created_utc`` in ``experiment.json``; the ``content_hash`` is
  computed over the reproducible payload only (it excludes the timestamp), so it
  is identical across reruns of the same config and serves as the integrity /
  reproducibility check.

Standard library only.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Optional

from research import metrics as research_metrics
from research.runner import NON_DETERMINISTIC_MEASUREMENTS, RunResult

#: Bumped whenever the artifact layout changes, so old artifacts stay readable.
ARTIFACT_SCHEMA_VERSION = "r1.0"

#: The seven required artifact filenames.
EXPERIMENT_FILE = "experiment.json"
METRICS_FILE = "metrics.json"
SUMMARY_FILE = "summary.json"
CONFIGURATION_FILE = "configuration.json"
POLICY_FILE = "policy.json"
SEED_FILE = "seed.json"
DECISION_AUDIT_FILE = "decision_audit.json"


def _dump(path: str, payload: Any) -> int:
    """Write ``payload`` as pretty, deterministic JSON; return bytes written.

    ``sort_keys=True`` makes the serialization order-independent, which is what
    lets two runs of the same config produce byte-identical files.
    """
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    text += "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return len(text.encode("utf-8"))


def _content_hash(payload: Any) -> str:
    """Stable SHA-256 over a JSON-canonicalised payload (excludes timestamps)."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _strip_nondeterministic(summary: Any) -> Any:
    """Defensively drop any non-deterministic keys from a summary before hashing.

    The current summary carries only deterministic fields, but this guards the
    integrity hash against future additions of timing/memory fields to it.
    """
    if isinstance(summary, dict):
        return {
            k: v
            for k, v in summary.items()
            if k not in NON_DETERMINISTIC_MEASUREMENTS
        }
    return summary


def allocate_experiment_dir(root: str, prefix: str = "exp_") -> str:
    """Create and return the next sequential ``exp_NNNN`` directory under ``root``.

    Sequential numbering keeps artifacts ordered and never reuses an id, which
    reinforces immutability (a new run always lands in a new directory).
    """
    os.makedirs(root, exist_ok=True)
    existing = [
        d for d in os.listdir(root)
        if d.startswith(prefix) and os.path.isdir(os.path.join(root, d))
    ]
    next_n = 1
    for d in existing:
        try:
            next_n = max(next_n, int(d[len(prefix):]) + 1)
        except ValueError:
            continue
    exp_dir = os.path.join(root, f"{prefix}{next_n:04d}")
    os.makedirs(exp_dir, exist_ok=False)  # immutable: must not already exist
    return exp_dir


class ArtifactWriter:
    """Writes the seven immutable artifacts for one :class:`RunResult`."""

    def write(
        self,
        result: RunResult,
        exp_dir: str,
        *,
        experiment_id: str,
        name: str = "velynx_research",
        group: Optional[str] = None,
        allow_overwrite: bool = False,
    ) -> Dict[str, str]:
        """Write all seven artifacts into ``exp_dir`` and return their paths."""
        if os.path.isdir(exp_dir) and os.listdir(exp_dir) and not allow_overwrite:
            raise FileExistsError(
                f"Refusing to overwrite non-empty artifact dir {exp_dir!r}; "
                f"artifacts are immutable (pass allow_overwrite=True to force)."
            )
        os.makedirs(exp_dir, exist_ok=True)

        cfg = result.config

        # --- the six reproducible payloads --------------------------------
        configuration = {
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            **cfg.as_dict(),
            "energy_weights": _resolve_weights(cfg),
        }
        policy_payload = result.policy_description
        seed_payload = result.seed_info
        audit_payload = result.decision_audit
        summary_payload = result.summary

        # metrics.json: raw record + extracted scalars + registry metadata.
        measurements = dict(result.measurements)
        metrics_payload = {
            "measurements": measurements,
            "extracted": research_metrics.extract_all(measurements),
            "registry": research_metrics.spec_metadata(),
        }

        # The reproducible content used for the integrity hash. Timings, peak
        # memory, and artifact size are inherently non-deterministic across
        # reruns of the same config, so they are excluded from the hash (but
        # still recorded in metrics.json for completeness).
        reproducible_measurements = {
            k: v
            for k, v in measurements.items()
            if k not in NON_DETERMINISTIC_MEASUREMENTS
        }
        reproducible = {
            "configuration": configuration,
            "policy": policy_payload,
            "seed": seed_payload,
            "summary": _strip_nondeterministic(summary_payload),
            "decision_audit": audit_payload,
            "metrics": reproducible_measurements,
        }
        content_hash = _content_hash(reproducible)

        # --- write the reproducible files first ---------------------------
        paths: Dict[str, str] = {}
        written_bytes = 0
        for filename, payload in (
            (CONFIGURATION_FILE, configuration),
            (POLICY_FILE, policy_payload),
            (SEED_FILE, seed_payload),
            (SUMMARY_FILE, summary_payload),
            (DECISION_AUDIT_FILE, audit_payload),
        ):
            p = os.path.join(exp_dir, filename)
            written_bytes += _dump(p, payload)
            paths[filename] = p

        # --- ArtifactSize: now that the bulk is on disk, record the size --
        # so the engineering ArtifactSize metric is populated rather than null.
        measurements["artifact_size_bytes"] = float(written_bytes)
        metrics_payload["measurements"] = measurements
        metrics_payload["extracted"] = research_metrics.extract_all(measurements)
        paths[METRICS_FILE] = os.path.join(exp_dir, METRICS_FILE)
        _dump(paths[METRICS_FILE], metrics_payload)

        # --- experiment.json (identity + IVs + integrity) ----------------
        experiment = {
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "experiment_id": experiment_id,
            "name": name,
            "group": group,
            "created_utc": _utc_now(),
            "independent_variables": {
                "policy": cfg.policy,
                "replay_horizon": cfg.replay_horizon,
                "noise_sigma": cfg.noise_sigma,
                "seed": cfg.seed,
            },
            "fixed_factors": {
                "dataset_name": cfg.dataset_name,
                "num_ticks": cfg.num_ticks,
                "proximity_threshold": cfg.proximity_threshold,
                "max_clusters": cfg.max_clusters,
            },
            "content_hash": content_hash,
            "artifacts": sorted(
                [
                    EXPERIMENT_FILE, METRICS_FILE, SUMMARY_FILE,
                    CONFIGURATION_FILE, POLICY_FILE, SEED_FILE,
                    DECISION_AUDIT_FILE,
                ]
            ),
        }
        paths[EXPERIMENT_FILE] = os.path.join(exp_dir, EXPERIMENT_FILE)
        _dump(paths[EXPERIMENT_FILE], experiment)

        return paths


def _resolve_weights(cfg) -> Dict[str, float]:
    """Resolve the energy coefficients for the configuration artifact.

    A tiny helper kept here (not imported from the runner) so the artifact
    module has no behavioural dependency on the runner beyond the result object.
    """
    from backend.cognition.decision_policy import resolve_coefficients

    return resolve_coefficients(cfg.decision_policy)


def _utc_now() -> str:
    """ISO-8601 UTC timestamp (the one intentionally non-reproducible field)."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def load_artifact(exp_dir: str, filename: str) -> Any:
    """Read one artifact file back as Python data (for verification/aggregation)."""
    with open(os.path.join(exp_dir, filename), "r", encoding="utf-8") as fh:
        return json.load(fh)


__all__ = [
    "ARTIFACT_SCHEMA_VERSION",
    "EXPERIMENT_FILE", "METRICS_FILE", "SUMMARY_FILE", "CONFIGURATION_FILE",
    "POLICY_FILE", "SEED_FILE", "DECISION_AUDIT_FILE",
    "ArtifactWriter",
    "allocate_experiment_dir",
    "load_artifact",
]
