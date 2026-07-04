"""
validation/artifact.py
======================

Artifact persistence for the VELYNX Cognitive Lab.

``ResultSerializer`` writes structured experiment outputs to a versioned
directory tree so that results are never silently overwritten and can be
reloaded later for cross-version statistical comparison.

Folder layout::

    artifacts/
    ├── exp_001/
    │   ├── data.csv         # tick-by-tick log
    │   ├── metadata.json    # RegressionResult + experiment config
    │   └── version.json     # timestamp + git commit hash
    ├── exp_002/
    ...
"""

from __future__ import annotations

import csv
import json
import logging
import os
import re
import subprocess
import threading
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from validation.regression import RegressionResult

logger = logging.getLogger("velynx.validation")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ARTIFACTS_ROOT = "artifacts"
"""Name of the root directory for all experiment artifacts (relative to cwd)."""

_EXPERIMENT_PREFIX = "exp_"
"""Prefix for auto-incrementing experiment folders (e.g. ``exp_001``)."""

_EXPERIMENT_DIR_PATTERN = re.compile(r"^exp_(\d{3,})$")
"""Matches ``exp_001``, ``exp_099`` — extracts the numeric suffix."""

_METADATA_FILE = "metadata.json"
_DATA_FILE = "data.csv"
_VERSION_FILE = "version.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_git_commit(root_dir: Optional[Path] = None) -> str:
    """Return the short (7-char) HEAD commit hash, or ``"unknown"``.

    Runs ``git rev-parse --short HEAD`` from ``root_dir`` (defaults to
    current working directory). Silently returns ``"unknown"`` on any
    failure — git not installed, not a repo, or the command times out.
    """
    cwd = str(root_dir) if root_dir else None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return "unknown"


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string with ``Z`` suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _next_experiment_dir(artifacts_path: Path) -> Path:
    """Scan *artifacts_path* and return a ``Path`` for the next numbered folder.

    Finds the highest existing ``exp_XXX`` number and increments by one,
    zero-padded to three digits.  If the artifacts folder does not exist yet,
    returns ``exp_001``.
    """
    artifacts_path.mkdir(parents=True, exist_ok=True)

    max_num = 0
    for entry in artifacts_path.iterdir():
        if entry.is_dir():
            match = _EXPERIMENT_DIR_PATTERN.match(entry.name)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num

    next_num = max_num + 1
    folder_name = f"{_EXPERIMENT_PREFIX}{next_num:03d}"
    return artifacts_path / folder_name


def _json_default(obj: Any) -> Any:
    """Convert non-serializable objects for ``json.dumps``.

    Handles tuples, sets, and other common types so serialization never
    crashes silently on benign data shapes.
    """
    if isinstance(obj, (set, tuple)):
        return list(obj)
    if isinstance(obj, RegressionResult):
        return asdict(obj)
    # Let the caller know what we couldn't handle.
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON-serializable")


def _flatten_logs_to_rows(logs: List[Dict[str, Any]]) -> tuple[List[Dict[str, str]], List[str]]:
    """Convert a list-of-dicts log into CSV-safe rows with sorted field names.

    Non-scalar values (lists, tuples, dicts) are JSON-stringified so they
    survive the CSV round-trip.
    """
    # Collect all unique keys across every log entry.
    all_keys: set = set()
    for entry in logs:
        all_keys.update(entry.keys())

    sorted_keys = sorted(all_keys)

    rows: list[dict[str, str]] = []
    for entry in logs:
        row: dict[str, str] = {}
        for key in sorted_keys:
            value = entry.get(key)
            if value is None or isinstance(value, (str, int, float, bool)):
                row[key] = "" if value is None else str(value)
            else:
                row[key] = json.dumps(value, default=_json_default, ensure_ascii=False)
        rows.append(row)

    return rows, sorted_keys


def _unflatten_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Reverse ``_flatten_logs_to_rows`` — parse CSV strings back to typed values.

    Attempts JSON parsing for non-trivial strings; falls back to numeric or
    literal string types.
    """
    result: Dict[str, Any] = {}
    for key, raw in row.items():
        if not raw:
            result[key] = None
            continue

        # Try JSON first — catches complex values and quoted strings.
        if raw.startswith(("{", "[", '"')):
            try:
                result[key] = json.loads(raw)
                continue
            except (json.JSONDecodeError, ValueError):
                pass

        # Try numeric.
        try:
            if "." in raw:
                result[key] = float(raw)
            else:
                result[key] = int(raw)
        except (ValueError, TypeError):
            result[key] = raw

    return result


# ---------------------------------------------------------------------------
# Serializer
# ---------------------------------------------------------------------------


class ResultSerializer:
    """Persist, load, and compare experiment artifacts.

    Thread-safe for concurrent ``save_experiment`` calls.  Each saved
    experiment gets an auto-incrementing folder (``exp_001``, ``exp_002``,
    ...) under the *root_dir* / ``artifacts``.

    Parameters
    ----------
    root_dir : str or Path, optional
        Base directory for the ``artifacts`` folder.  Defaults to the
        current working directory.
    """

    def __init__(self, root_dir: Optional[os.PathLike] = None) -> None:
        self._root: Path = Path(root_dir).resolve() if root_dir else Path.cwd()
        self._artifacts: Path = self._root / _ARTIFACTS_ROOT
        self._lock = threading.Lock()

    # -- public API --------------------------------------------------------

    def save_experiment(
        self,
        experiment_name: str,
        logs: List[Dict[str, Any]],
        result: RegressionResult,
        config: Dict[str, Any],
    ) -> Path:
        """Persist a single experiment run to a versioned artifact folder.

        Creates three files under a new ``exp_NNN`` directory:

        * ``data.csv`` — the tick-by-tick log (all keys, non-scalar cells
          JSON-encoded so the round-trip is lossless).
        * ``metadata.json`` — the :class:`RegressionResult` and the
          experiment ``config`` dict, under a top-level ``"experiment_name"``
          key.
        * ``version.json`` — a lightweight provenance record.

        Parameters
        ----------
        experiment_name : str
            A human-readable label for the experiment (stored in
            ``metadata.json``).
        logs : list of dict
            The tick-by-tick log, typically
            :attr:`~validation.runner.BenchmarkRunner.output_log`.
        result : RegressionResult
            The itemised verdict from a
            :meth:`~validation.regression.RegressionGate.evaluate` call.
        config : dict
            The configuration dict that produced this run (will be round-
            tripped through JSON, so prefer JSON-safe types).

        Returns
        -------
        Path
            The absolute path of the created artifact directory.

        Raises
        ------
        IOError
            If the artifact directory cannot be created (e.g. permissions)
            even after a retry.
        """
        with self._lock:
            exp_dir = _next_experiment_dir(self._artifacts)
            try:
                exp_dir.mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                # Race condition or folder picked up by another thread.
                # Increment once more.  This is safe under the lock because
                # only one thread runs _next_experiment_dir + mkdir at a time.
                exp_dir = _next_experiment_dir(self._artifacts)
                exp_dir.mkdir(parents=True, exist_ok=False)

            logger.info("Saving experiment to %s", exp_dir)

        # -- data.csv ------------------------------------------------------
        self._write_csv(exp_dir / _DATA_FILE, logs)

        # -- metadata.json -------------------------------------------------
        metadata = {
            "experiment_name": experiment_name,
            "config": config,
            "result": asdict(result),
        }
        self._write_json(exp_dir / _METADATA_FILE, metadata)

        # -- version.json --------------------------------------------------
        version = {
            "timestamp": _now_iso(),
            "commit_hash": _get_git_commit(self._root),
        }
        self._write_json(exp_dir / _VERSION_FILE, version)

        return exp_dir.resolve()

    def load_experiment(self, path: os.PathLike) -> dict:
        """Load a previously saved experiment artifact into memory.

        Parameters
        ----------
        path : str or Path
            Path to an ``exp_NNN`` directory (either absolute or relative to
            the current working directory).

        Returns
        -------
        dict
            A dict with keys:

            * ``"experiment_name"`` — str
            * ``"config"`` — the original config dict
            * ``"result"`` — a :class:`RegressionResult` reconstructed from
              the saved metadata
            * ``"logs"`` — the tick-by-tick log as a ``list[dict]``
            * ``"version"`` — the provenance dict (timestamp + commit_hash)
        """
        exp_dir = Path(path).resolve()
        metadata = self._read_json(exp_dir / _METADATA_FILE)
        version_data = self._read_json(exp_dir / _VERSION_FILE)
        logs = self._read_csv(exp_dir / _DATA_FILE)

        return {
            "experiment_name": metadata.get("experiment_name", "unknown"),
            "config": metadata.get("config", {}),
            "result": RegressionResult(**metadata.get("result", {})),
            "logs": logs,
            "version": version_data,
        }

    def list_artifacts(self) -> List[Tuple[int, Path]]:
        """Enumerate every saved experiment artifact in order.

        Returns
        -------
        list of (int, Path)
            Each tuple is ``(experiment_number, absolute_path)`` sorted
            ascending by number (``exp_001`` → ``exp_002`` → …).
        """
        if not self._artifacts.is_dir():
            return []

        entries: list[tuple[int, Path]] = []
        for entry in self._artifacts.iterdir():
            if not entry.is_dir():
                continue
            match = _EXPERIMENT_DIR_PATTERN.match(entry.name)
            if match:
                entries.append((int(match.group(1)), entry.resolve()))

        entries.sort(key=lambda t: t[0])
        return entries

    def compare_experiments(
        self,
        path_a: os.PathLike,
        path_b: os.PathLike,
    ) -> dict:
        """Compare two experiment artifacts side-by-side.

        Useful for tracking how the brain's regression profile changes across
        versions.

        Parameters
        ----------
        path_a, path_b : str or Path
            Paths to the two ``exp_NNN`` directories to compare.

        Returns
        -------
        dict
            A dict with keys ``"a"``, ``"b"`` (the respective
            ``RegressionResult`` + version info), and ``"delta_is_improvement"``
            which is ``True`` if the later experiment passed while the earlier
            one failed (or both passed but the second has fewer regressions).
        """
        # Resolve paths early so error messages are clear.
        data_a = self.load_experiment(path_a)
        data_b = self.load_experiment(path_b)

        result_a: RegressionResult = data_a["result"]
        result_b: RegressionResult = data_b["result"]

        delta_improvement = False
        if result_b.passed and not result_a.passed:
            delta_improvement = True
        elif result_b.passed and result_a.passed:
            # Both passed — the direction of change in the *number* of
            # regressing metrics tells us if we're trending better or worse.
            delta_improvement = len(result_b.regressions) <= len(result_a.regressions)

        return {
            "a": {
                "path": str(Path(path_a).resolve()),
                "result": result_a,
                "version": data_a["version"],
            },
            "b": {
                "path": str(Path(path_b).resolve()),
                "result": result_b,
                "version": data_b["version"],
            },
            "delta_is_improvement": delta_improvement,
        }

    # -- IO internals ------------------------------------------------------

    @staticmethod
    def _write_csv(path: Path, logs: List[Dict[str, Any]]) -> None:
        """Write *logs* as a CSV file at *path*.

        Every unique key across all entries becomes a column.  Non-scalar
        values are JSON-encoded so the round-trip is information-preserving.
        On failure, the error is logged and the (partial) file is cleaned up.
        """
        try:
            rows, fieldnames = _flatten_logs_to_rows(logs)
            with open(path, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        except (OSError, csv.Error) as exc:
            logger.error("Failed to write %s: %s", path, exc)
            # Clean up partial file so we never leave a corrupt artifact.
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
            raise IOError(f"Cannot write CSV artifact at {path}") from exc

    @staticmethod
    def _write_json(path: Path, data: Any) -> None:
        """Write *data* as a pretty-printed JSON file at *path*.

        On failure the error is logged and the partial file is cleaned up.
        """
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, default=_json_default, ensure_ascii=False)
                fh.write("\n")
        except (OSError, TypeError, ValueError) as exc:
            logger.error("Failed to write %s: %s", path, exc)
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
            raise IOError(f"Cannot write JSON artifact at {path}") from exc

    @staticmethod
    def _read_json(path: Path) -> Any:
        """Load and return the contents of a JSON file at *path*.

        Raises ``FileNotFoundError`` with a descriptive message if the file
        does not exist, and logs + re-raises on parse errors so callers never
        silently get an empty dict for a malformed artifact.
        """
        if not path.is_file():
            raise FileNotFoundError(f"Artifact file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to read %s: %s", path, exc)
            raise

    @staticmethod
    def _read_csv(path: Path) -> List[Dict[str, Any]]:
        """Load and return the CSV artifact at *path* as a list of dicts.

        Each cell is parsed back through ``_unflatten_row`` to reconstruct
        JSON-encoded values, numerics, and nulls.
        """
        if not path.is_file():
            raise FileNotFoundError(f"Artifact file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                return [_unflatten_row(row) for row in reader]
        except (csv.Error, OSError) as exc:
            logger.error("Failed to read %s: %s", path, exc)
            raise


__all__ = [
    "ResultSerializer",
]
