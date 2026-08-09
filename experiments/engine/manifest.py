"""Run provenance.

Responsibility: record everything needed to explain, trust and repeat a run,
without needing the person who launched it.

The M0 review ranked "no immutable evidence identity" as risk 7: the reviewed rig
was uncommitted, and a stored artifact did not match the reported run length. The
manifest is the fix. It captures the git commit *and* whether the tree was dirty,
because a commit id alone is a false guarantee when uncommitted edits are present.

`code_state` is therefore a first-class field with three values:
    "clean"     committed, no local modifications — reproducible from git alone
    "dirty"     committed, with local modifications — NOT reproducible from git
    "untracked" no git information available at all

A run whose `code_state` is not "clean" must not be used as confirmatory evidence.
The engine records the fact rather than refusing to run, because exploratory work
on a dirty tree is legitimate; what is illegitimate is forgetting.
"""

from __future__ import annotations

import getpass
import platform
import socket
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

#: Recorded because a change in any of these can move a number.
_TRACKED_PACKAGES: Sequence[str] = ("numpy", "scipy", "matplotlib", "pyyaml")

_GIT_TIMEOUT = 10


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _git(args: Sequence[str], repo: Path) -> str:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def git_info(repo: str | Path = ".") -> Dict[str, Any]:
    """Commit, branch, dirty flag and whether the rig itself is tracked."""
    repo_path = Path(repo).resolve()
    commit = _git(["rev-parse", "HEAD"], repo_path)
    if not commit:
        return {
            "commit": "",
            "branch": "",
            "dirty": None,
            "code_state": "untracked",
            "untracked_rig": None,
        }
    status = _git(["status", "--porcelain"], repo_path)
    dirty = bool(status)
    # Specifically flag the frozen rig and the platform being untracked: that is
    # the exact failure the M0 review recorded as risk 7.
    untracked_rig = any(
        line.startswith("??") and any(part in line for part in ("p1v0/", "core/", "science/"))
        for line in status.splitlines()
    )
    return {
        "commit": commit,
        "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path),
        "dirty": dirty,
        "code_state": "dirty" if dirty else "clean",
        "untracked_rig": untracked_rig,
        "dirty_file_count": len(status.splitlines()) if status else 0,
    }


def runtime_info() -> Dict[str, Any]:
    """Interpreter, OS and dependency versions."""
    packages: Dict[str, str] = {}
    for name in _TRACKED_PACKAGES:
        try:
            packages[name] = importlib_metadata.version(name)
        except importlib_metadata.PackageNotFoundError:
            packages[name] = "absent"
    try:
        user = getpass.getuser()
    except Exception:  # noqa: BLE001 — unavailable in some sandboxes
        user = ""
    return {
        "python": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": socket.gethostname(),
        "user": user,
        "packages": packages,
    }


def build_manifest(
    *,
    run_id: str,
    config: Mapping[str, Any],
    config_hash: str,
    seeds: Mapping[str, Any],
    benchmark: Mapping[str, Any],
    components: Mapping[str, Any],
    metrics_requested: Sequence[str],
    started_at: str,
    finished_at: str,
    duration_seconds: float,
    compute: Mapping[str, Any],
    status: str,
    error: str = "",
    repo: str | Path = ".",
    p1v0_version: str = "",
) -> Dict[str, Any]:
    """Assemble the manifest written as `manifest.json`.

    Everything here is derived, never configured: a manifest a user could edit
    would not be provenance.
    """
    return {
        "manifest_version": 1,
        "run_id": run_id,
        "status": status,
        "error": error,
        "config_hash": config_hash,
        "config": dict(config),
        "seeds": dict(seeds),
        "benchmark": dict(benchmark),
        "components": dict(components),
        "metrics_requested": list(metrics_requested),
        "timing": {
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_seconds": round(duration_seconds, 6),
        },
        "compute": dict(compute),
        "code": {**git_info(repo), "frozen_rig_version": p1v0_version},
        "runtime": runtime_info(),
    }
