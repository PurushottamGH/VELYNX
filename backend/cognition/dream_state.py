"""
VELYNX Dream State — subconscious synthesis loop
================================================

Background process that "sleeps" over the active memory graph and surfaces
latent metaphorical connections between concepts that are currently charged
but not yet directly linked.

Pipeline
--------
1. Pull the active concept pool from ``data/concepts.json`` /
   ``data/soul_concepts.json`` and from ``MemoryCore`` (filtering out any
   whose ``current_intensity`` has decayed below ``INTENSITY_FLOOR``).
2. Encode each concept name + definition into a vector with a single,
   module-level ``SentenceTransformer`` instance (so the model stays
   resident in VRAM — re-instantiating costs ~22 s per call).
3. Use a FAISS inner-product index to compute pairwise cosine similarity
   in O(N log N) instead of the O(N^2) Python double-loop.
4. For every pair with ``cosine_sim > SIMILARITY_THRESHOLD`` that is NOT
   already connected by a graph edge, emit a metaphorical link proposal
   to ``data/proposed_nodes.json`` with ``origin: "dream_state"`` so the
   review gateway can sit it next to Auto-Learner patches.

The script is idempotent: existing proposals (matched by the
``(source, target, "metaphorically_links")`` triple) are not duplicated.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch

try:
    import faiss  # type: ignore
    _FAISS_AVAILABLE = True
except Exception:  # pragma: no cover - import-time guard
    faiss = None  # type: ignore
    _FAISS_AVAILABLE = False

from sentence_transformers import SentenceTransformer

# Reuse the production memory store so we honour temporal decay thresholds
# computed in memory_graph.calculate_decay.
from backend.memory.memory_graph import MemoryCore

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
CONCEPTS_PATH = DATA_DIR / "concepts.json"
SOUL_CONCEPTS_PATH = DATA_DIR / "soul_concepts.json"
PROPOSED_NODES_PATH = DATA_DIR / "proposed_nodes.json"

MODEL_NAME = "all-MiniLM-L6-v2"
INTENSITY_FLOOR = 0.40
SIMILARITY_THRESHOLD = 0.65
TOP_K_NEIGHBOURS = 10  # candidates per query vector; capped by N-1
LOG_PREFIX = "[dream_state]"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("velynx.dream_state")

# ── Global, persistent model instance ────────────────────────────────────
# Loaded once at import. Mirrors the VRAM strategy in embed_index.py:
# never instantiate SentenceTransformer inside a function scope.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info("%s Loading SentenceTransformer %s on %s", LOG_PREFIX, MODEL_NAME, DEVICE)
_MODEL_INSTANCE = SentenceTransformer(MODEL_NAME, device=DEVICE)


class Consolidator:
    """Surface latent metaphorical edges between active memory nodes."""

    def __init__(
        self,
        intensity_floor: float = INTENSITY_FLOOR,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        concepts_path: Path = CONCEPTS_PATH,
        soul_concepts_path: Path = SOUL_CONCEPTS_PATH,
        proposed_nodes_path: Path = PROPOSED_NODES_PATH,
    ) -> None:
        self.intensity_floor = intensity_floor
        self.similarity_threshold = similarity_threshold
        self.concepts_path = concepts_path
        self.soul_concepts_path = soul_concepts_path
        self.proposed_nodes_path = proposed_nodes_path
        self.memory = MemoryCore()
        self.active_concepts: list[str] = []
        self.existing_edges: set[tuple[str, str, str]] = set()
        self.proposals: list[dict[str, Any]] = []

    # ── Active-pool assembly ───────────────────────────────────────────

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("%s Could not read %s: %s", LOG_PREFIX, path, exc)
            return {}

    def _load_concept_pool(self) -> dict[str, dict[str, Any]]:
        """Merge nodes from concepts.json + soul_concepts.json.

        Soul entries win on collision because they carry richer metadata
        (taught_by, intensity, related_concepts).
        """

        merged: dict[str, dict[str, Any]] = {}

        knowledge = self._read_json(self.concepts_path)
        for name, entry in (knowledge.get("nodes") or {}).items():
            merged[name.lower()] = {
                "name": name.lower(),
                "definition": (entry or {}).get("definition", ""),
                "source_file": "concepts.json",
            }

        soul = self._read_json(self.soul_concepts_path)
        for name, entry in (soul.get("concepts") or {}).items():
            merged[name.lower()] = {
                "name": name.lower(),
                "definition": (entry or {}).get("core", ""),
                "intensity": (entry or {}).get("intensity"),
                "emotional_valence": (entry or {}).get("emotional_valence"),
                "source_file": "soul_concepts.json",
            }
        return merged

    def _load_existing_edges(self) -> set[tuple[str, str, str]]:
        edges: set[tuple[str, str, str]] = set()
        for path in (self.concepts_path, self.soul_concepts_path):
            data = self._read_json(path)
            raw_edges = data.get("edges") or []
            for edge in raw_edges:
                if not isinstance(edge, dict):
                    continue
                src = str(edge.get("source", "")).lower()
                tgt = str(edge.get("target", "")).lower()
                rel = str(edge.get("relationship_type", "")).lower()
                if src and tgt and rel:
                    edges.add((src, tgt, rel))
                    edges.add((tgt, src, rel))  # treat edges as undirected
        return edges

    def fetch_active_memories(self) -> list[str]:
        """Return the names of all currently active concepts.

        A concept is "active" if:

        * it appears in the merged concept pool (concepts.json or
          soul_concepts.json), AND
        * it has a SQLite experience row whose ``current_intensity`` is at
          least ``intensity_floor`` (so decayed / healed nodes are ignored),
          OR it has no SQLite footprint yet (brand-new soul concept — we
          let it dream).
        """

        pool = self._load_concept_pool()
        if not pool:
            logger.info("%s No concepts found in pool.", LOG_PREFIX)
            return []

        try:
            live_rows = self.memory.retrieve_recent_state(limit=10_000)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("%s MemoryCore read failed: %s", LOG_PREFIX, exc)
            live_rows = []

        # Map concept_name -> max current_intensity observed
        live_intensity: dict[str, float] = {}
        for row in live_rows:
            for key in ("primary_soul_concept", "primary_domain_concept"):
                name = (row.get(key) or "").lower()
                if not name:
                    continue
                intensity = float(row.get("current_intensity", 0.0) or 0.0)
                prev = live_intensity.get(name, 0.0)
                if intensity > prev:
                    live_intensity[name] = intensity

        active: list[str] = []
        for name, meta in pool.items():
            if name in live_intensity:
                if live_intensity[name] >= self.intensity_floor:
                    active.append(name)
            else:
                # New concept with no memory footprint yet — keep it so the
                # dream state can connect it to established nodes.
                if meta.get("definition"):
                    active.append(name)

        active.sort()
        self.active_concepts = active
        logger.info(
            "%s Active concept pool: %d / %d (floor=%.2f)",
            LOG_PREFIX, len(active), len(pool), self.intensity_floor,
        )
        return active

    # ── Embedding + FAISS pair search ──────────────────────────────────

    def _ensure_model(self) -> SentenceTransformer:
        return _MODEL_INSTANCE

    def _encode(self, concepts: list[str]) -> np.ndarray:
        model = self._ensure_model()
        pool = self._load_concept_pool()
        texts = [
            f"{name}: {pool.get(name, {}).get('definition', '')}".strip(": ")
            or name
            for name in concepts
        ]
        logger.info("%s Encoding %d concept vectors on %s", LOG_PREFIX, len(texts), model.device)
        matrix = model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        )
        return matrix.astype("float32")

    def _pairwise_similarities(
        self, matrix: np.ndarray
    ) -> list[tuple[int, int, float]]:
        """Return (i, j, score) for every pair above the threshold.

        Uses FAISS when available for the O(N log N) k-NN pass; otherwise
        falls back to a single matrix multiplication (still vectorised
        but O(N^2) memory).
        """

        n = matrix.shape[0]
        if n < 2:
            return []

        pairs: list[tuple[int, int, float]] = []
        if _FAISS_AVAILABLE:
            index = faiss.IndexFlatIP(matrix.shape[1])
            index.add(matrix)
            k = min(TOP_K_NEIGHBOURS, n)
            scores, neighbours = index.search(matrix, k)
            for i in range(n):
                for j_idx, score in zip(neighbours[i], scores[i]):
                    if j_idx <= i or j_idx < 0:
                        continue
                    if score >= self.similarity_threshold:
                        pairs.append((i, int(j_idx), float(score)))
        else:
            sims = matrix @ matrix.T
            iu = np.triu_indices(n, k=1)
            for i, j in zip(iu[0], iu[1]):
                score = float(sims[i, j])
                if score >= self.similarity_threshold:
                    pairs.append((int(i), int(j), score))
        return pairs

    # ── Synthesis ──────────────────────────────────────────────────────

    def run_synthesis(self) -> list[dict[str, Any]]:
        """Discover latent metaphorical edges and return new proposals.

        Algorithm::

            active = fetch_active_memories()
            matrix = encode(active)
            pairs  = pairwise_similarities(matrix)        # sim >= threshold
            edges  = _load_existing_edges()
            for i, j, score in pairs:
                a, b = active[i], active[j]
                if (a, b, *) in edges: skip
                emit proposal: a -> metaphorically_links -> b

        Existing ``proposed_nodes.json`` entries are also consulted so we
        never re-emit the same proposal twice.
        """

        active = self.fetch_active_memories()
        if len(active) < 2:
            logger.info("%s Pool too small to dream (%d).", LOG_PREFIX, len(active))
            self.proposals = []
            return self.proposals

        self.existing_edges = self._load_existing_edges()
        existing_proposals = self._load_existing_proposals()
        logger.info(
            "%s Pre-existing edges considered: %d | pending proposals: %d",
            LOG_PREFIX, len(self.existing_edges), len(existing_proposals),
        )

        matrix = self._encode(active)
        pairs = self._pairwise_similarities(matrix)
        logger.info(
            "%s Found %d candidate pair(s) above similarity %.2f",
            LOG_PREFIX, len(pairs), self.similarity_threshold,
        )

        proposals: list[dict[str, Any]] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for i, j, score in pairs:
            a, b = active[i], active[j]
            rel = "metaphorically_links"

            # Skip if a directed edge of any type already connects them.
            if (a, b, rel) in self.existing_edges:
                continue

            # Skip if we already proposed this exact metaphorical link.
            proposal_key = (a, b, rel)
            if proposal_key in existing_proposals:
                continue

            proposals.append(
                {
                    "concept": a,
                    "definition": "",
                    "synonyms": [],
                    "matched_existing_concepts": [b],
                    "proposed_edges": [
                        {
                            "source": a,
                            "relationship": rel,
                            "target": b,
                        }
                    ],
                    "origin": "dream_state",
                    "source": f"sentence_transformers::{MODEL_NAME}",
                    "status": "pending_review",
                    "metadata": {
                        "cosine_similarity": round(score, 4),
                        "neighbour": b,
                        "discovered_at": now_iso,
                        "intensity_floor": self.intensity_floor,
                        "similarity_threshold": self.similarity_threshold,
                    },
                }
            )

        self.proposals = proposals
        logger.info("%s Generated %d new metaphorical edge proposal(s).", LOG_PREFIX, len(proposals))
        return proposals

    def _load_existing_proposals(self) -> set[tuple[str, str, str]]:
        if not self.proposed_nodes_path.exists():
            return set()
        try:
            with self.proposed_nodes_path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return set()

        keys: set[tuple[str, str, str]] = set()
        for proposal in payload.get("proposals", []):
            for edge in proposal.get("proposed_edges", []) or []:
                src = str(edge.get("source", "")).lower()
                tgt = str(edge.get("target", "")).lower()
                rel = str(edge.get("relationship", "")).lower()
                if src and tgt and rel:
                    keys.add((src, tgt, rel))
                    keys.add((tgt, src, rel))
        return keys

    # ── Output ─────────────────────────────────────────────────────────

    def write_proposals(self, merge: bool = True) -> Path:
        """Append the dream_state proposals to ``proposed_nodes.json``.

        With ``merge=True`` (default) we keep any Auto-Learner entries that
        are already on disk, so the review gateway can process both
        pipelines in a single sweep.
        """

        self.proposed_nodes_path.parent.mkdir(parents=True, exist_ok=True)

        existing_payload: dict[str, Any] = {}
        if merge and self.proposed_nodes_path.exists():
            try:
                with self.proposed_nodes_path.open("r", encoding="utf-8") as fh:
                    existing_payload = json.load(fh)
            except (json.JSONDecodeError, OSError):
                existing_payload = {}

        existing_proposals = existing_payload.get("proposals", []) if isinstance(existing_payload, dict) else []
        existing_keys = self._load_existing_proposals()

        merged: list[dict[str, Any]] = list(existing_proposals) if isinstance(existing_proposals, list) else []
        for proposal in self.proposals:
            edge = (proposal.get("proposed_edges") or [{}])[0]
            key = (
                str(edge.get("source", "")).lower(),
                str(edge.get("target", "")).lower(),
                str(edge.get("relationship", "")).lower(),
            )
            if key in existing_keys:
                continue
            merged.append(proposal)
            existing_keys.add(key)

        payload = {
            "generated_by": "backend.cognition.dream_state.Consolidator",
            "version": existing_payload.get("version", 1) if isinstance(existing_payload, dict) else 1,
            "existing_concept_count": len(self.active_concepts),
            "proposals": merged,
        }
        with self.proposed_nodes_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

        logger.info(
            "%s Wrote %d proposal(s) to %s (merged total: %d)",
            LOG_PREFIX, len(self.proposals), self.proposed_nodes_path, len(merged),
        )
        return self.proposed_nodes_path


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    intensity_floor = INTENSITY_FLOOR
    similarity_threshold = SIMILARITY_THRESHOLD
    if len(argv) >= 1:
        try:
            intensity_floor = float(argv[0])
        except ValueError:
            pass
    if len(argv) >= 2:
        try:
            similarity_threshold = float(argv[1])
        except ValueError:
            pass

    consolidator = Consolidator(
        intensity_floor=intensity_floor,
        similarity_threshold=similarity_threshold,
    )
    proposals = consolidator.run_synthesis()
    output_path = consolidator.write_proposals(merge=True)

    print(f"{LOG_PREFIX} Wrote {len(proposals)} dream_state proposal(s) to {output_path}")
    for proposal in proposals:
        edge = (proposal.get("proposed_edges") or [{}])[0]
        score = proposal.get("metadata", {}).get("cosine_similarity", 0.0)
        print(
            f"  - {edge.get('source')} -> {edge.get('relationship')} -> "
            f"{edge.get('target')}  (cos={score:.3f})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
