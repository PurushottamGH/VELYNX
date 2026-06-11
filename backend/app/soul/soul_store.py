"""Relational Soul — directed worldview graph store.

Atomic, thread-safe JSON persistence for VELYNX concept nodes
and semantic edges.  Replaces the legacy flat-dictionary format.
"""
from __future__ import annotations

import json
import os
import threading
from copy import deepcopy
from typing import Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
JSON_PATH = os.path.join(DATA_DIR, "concepts.json")
LOCK = threading.Lock()


class SoulStore:
    """Thread-safe graph store backed by a single JSON file."""

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    def load_soul(self) -> dict[str, Any]:
        """Read the worldview graph, migrating legacy flat formats on first load."""
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(JSON_PATH):
            seed = {"nodes": {}, "edges": []}
            self._atomic_write(seed)
            return seed

        raw = self._read_json()
        if "nodes" not in raw or "edges" not in raw:
            raw = self._migrate_flat(raw)
            self._atomic_write(raw)
        return raw

    def add_concept(
        self,
        name: str,
        definition: str,
        origin: str = "taught",
        confidence: float = 1.0,
    ) -> None:
        """Create or overwrite a concept node."""
        with LOCK:
            soul = self._read_json()
            soul["nodes"][name] = {
                "definition": definition,
                "origin": origin,
                "confidence": float(confidence),
            }
            self._atomic_write(soul)

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str,
        weight: float,
        tension: bool,
        context: str,
    ) -> None:
        """Add a directed edge.  Both source and target nodes must exist."""
        with LOCK:
            soul = self._read_json()
            nodes = soul.setdefault("nodes", {})
            if source not in nodes:
                raise KeyError(f"Source node '{source}' does not exist")
            if target not in nodes:
                raise KeyError(f"Target node '{target}' does not exist")

            edge = {
                "source": source,
                "target": target,
                "relationship_type": relationship_type,
                "weight": float(weight),
                "tension": bool(tension),
                "context": context,
            }

            # replace an existing identical directed edge
            edges: list[dict[str, Any]] = soul.setdefault("edges", [])
            updated = False
            for i, existing in enumerate(edges):
                if existing["source"] == source and existing["target"] == target:
                    edges[i] = edge
                    updated = True
                    break
            if not updated:
                edges.append(edge)

            self._atomic_write(soul)

    def get_concept_network(self, name: str) -> dict[str, Any]:
        """Return a node's metadata plus its outgoing & incoming edges."""
        soul = self._read_json()
        nodes: dict[str, dict[str, Any]] = soul.get("nodes", {})
        if name not in nodes:
            raise KeyError(f"Concept '{name}' not found")

        edges: list[dict[str, Any]] = soul.get("edges", [])
        outgoing = [e for e in edges if e["source"] == name]
        incoming = [e for e in edges if e["target"] == name]

        return {
            "node": nodes[name],
            "outgoing_edges": outgoing,
            "incoming_edges": incoming,
        }

    def get_tensions(self) -> list[dict[str, Any]]:
        """Return every edge flagged with tension == true."""
        soul = self._read_json()
        return [e for e in soul.get("edges", []) if e.get("tension")]

    # ------------------------------------------------------------------
    #  Internal helpers
    # ------------------------------------------------------------------

    def _read_json(self) -> dict[str, Any]:
        """Read the JSON file with safety guarantees."""
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"nodes": {}, "edges": []}

    def _atomic_write(self, data: dict[str, Any]) -> None:
        """Write to .tmp then os.replace to avoid WinError 1225 / corruption."""
        tmp = JSON_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, JSON_PATH)

    @staticmethod
    def _migrate_flat(legacy: dict[str, Any]) -> dict[str, Any]:
        """Convert a flat {concept_name: {…}} dict into the graph schema."""
        migrated: dict[str, Any] = {"nodes": {}, "edges": []}
        for name, meta in legacy.items():
            if isinstance(meta, dict):
                core = meta.get("core", json.dumps(meta, ensure_ascii=False))
                migrated["nodes"][name] = {
                    "definition": core,
                    "origin": "taught",
                    "confidence": float(meta.get("confidence_score", 0.5)),
                }
        return migrated
