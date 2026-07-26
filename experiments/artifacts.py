"""VELYNX Artifact Storage System.

Manages experiment artifacts: versioning, storage, retrieval, and integrity.
"""

import json
import hashlib
import shutil
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timezone

ARTIFACTS_BASE = Path(__file__).resolve().parent.parent / "artifacts"


class ArtifactStore:
    """Versioned artifact storage with integrity verification."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base = Path(base_path) if base_path else ARTIFACTS_BASE

    def _ensure_dir(self, path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _compute_hash(self, data: Any) -> str:
        if isinstance(data, (dict, list)):
            content = json.dumps(data, sort_keys=True).encode()
        elif isinstance(data, str):
            content = data.encode()
        elif isinstance(data, bytes):
            content = data
        else:
            content = str(data).encode()
        return hashlib.sha256(content).hexdigest()

    def store_artifact(
        self,
        experiment_id: str,
        run_id: str,
        name: str,
        data: Any,
        metadata: Optional[Dict] = None,
    ) -> Path:
        dir_path = self._ensure_dir(self.base / "experiments" / experiment_id / run_id)
        artifact_hash = self._compute_hash(data)

        artifact = {
            "name": name,
            "hash": artifact_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
        version_path = dir_path / "version.json"
        if version_path.exists():
            with open(version_path) as f:
                version_data = json.load(f)
        else:
            version_data = {"artifacts": []}
        version_data["artifacts"].append(artifact)

        if isinstance(data, (dict, list)):
            file_path = dir_path / f"{name}.json"
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        elif isinstance(data, str):
            file_path = dir_path / f"{name}.txt"
            file_path.write_text(data)
        elif isinstance(data, bytes):
            file_path = dir_path / f"{name}.bin"
            file_path.write_bytes(data)
        else:
            file_path = dir_path / f"{name}.json"
            with open(file_path, "w") as f:
                json.dump({"value": data}, f, indent=2)

        with open(version_path, "w") as f:
            json.dump(version_data, f, indent=2)
        return file_path

    def retrieve_artifact(self, experiment_id: str, run_id: str, name: str) -> Optional[Any]:
        dir_path = self.base / "experiments" / experiment_id / run_id
        for ext in [".json", ".txt", ".bin", ".csv"]:
            file_path = dir_path / f"{name}{ext}"
            if file_path.exists():
                if ext == ".json":
                    with open(file_path) as f:
                        return json.load(f)
                elif ext == ".txt":
                    return file_path.read_text()
                elif ext == ".bin":
                    return file_path.read_bytes()
                elif ext == ".csv":
                    return file_path.read_text()
        return None

    def verify_integrity(self, experiment_id: str, run_id: str) -> bool:
        dir_path = self.base / "experiments" / experiment_id / run_id
        version_path = dir_path / "version.json"
        if not version_path.exists():
            return False
        with open(version_path) as f:
            version_data = json.load(f)
        for artifact in version_data.get("artifacts", []):
            name = artifact["name"]
            expected_hash = artifact["hash"]
            data = self.retrieve_artifact(experiment_id, run_id, name)
            if data is None:
                return False
            actual_hash = self._compute_hash(data)
            if actual_hash != expected_hash:
                return False
        return True

    def list_runs(self, experiment_id: str) -> list:
        dir_path = self.base / "experiments" / experiment_id
        if not dir_path.exists():
            return []
        return sorted([d.name for d in dir_path.iterdir() if d.is_dir()], reverse=True)

    def list_artifacts(self, experiment_id: str, run_id: str) -> list:
        dir_path = self.base / "experiments" / experiment_id / run_id
        version_path = dir_path / "version.json"
        if not version_path.exists():
            return []
        with open(version_path) as f:
            version_data = json.load(f)
        return version_data.get("artifacts", [])

    def store_benchmark_result(
        self,
        benchmark_name: str,
        result: Dict,
        metadata: Optional[Dict] = None,
    ) -> Path:
        dir_path = self._ensure_dir(self.base / "benchmarks" / benchmark_name)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        file_path = dir_path / f"result_{timestamp}.json"
        payload = {
            "benchmark": benchmark_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result,
            "metadata": metadata or {},
            "hash": self._compute_hash(result),
        }
        with open(file_path, "w") as f:
            json.dump(payload, f, indent=2)
        return file_path

    def export_for_publication(self, experiment_id: str, run_id: str, output_dir: Path) -> Path:
        pub_dir = self._ensure_dir(output_dir / "publication" / experiment_id)
        src_dir = self.base / "experiments" / experiment_id / run_id
        if src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, pub_dir / item.name)
        manifest_path = pub_dir / "publication_manifest.json"
        manifest = {
            "experiment_id": experiment_id,
            "run_id": run_id,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "files": [f.name for f in pub_dir.iterdir() if f.is_file()],
        }
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        return pub_dir
