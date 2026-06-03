"""
VELYNX GPU Embedding Pipeline — Phase 19
==========================================
GPU-accelerated semantic similarity for:
- Knowledge graph lookups (fuzzy matching)
- Source relevance scoring
- Answer quality embedding comparison
"""

from __future__ import annotations

import logging
import os
import time
import warnings
from dataclasses import dataclass
from typing import Optional

# Suppress HuggingFace Hub warnings at module level
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", message=".*unauthenticated.*")
warnings.filterwarnings("ignore", message=".*HF Hub.*")
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")
for _hf_logger in ["huggingface_hub", "sentence_transformers", "transformers", "filelock",
                    "huggingface_hub.hf_api", "huggingface_hub._login"]:
    logging.getLogger(_hf_logger).setLevel(logging.CRITICAL)

logger = logging.getLogger("velynx.gpu_embedder")

# ── Module-level singleton cache (persists across all imports) ────────────────
_CACHED_MODEL = None
_CACHED_DEVICE = None


def get_cached_model():
    """Module-level cached model — loads once, persists for process lifetime."""
    global _CACHED_MODEL, _CACHED_DEVICE
    if _CACHED_MODEL is None:
        import torch
        fix_cuda_windows()
        _CACHED_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from sentence_transformers import SentenceTransformer
            _CACHED_MODEL = SentenceTransformer("all-MiniLM-L6-v2", device=_CACHED_DEVICE)
        logger.info("GPU model cached on %s", _CACHED_DEVICE)
    return _CACHED_MODEL, _CACHED_DEVICE


def fix_cuda_windows() -> bool:
    """Fix torch CUDA detection on Windows."""
    try:
        import torch
        if not torch.cuda.is_available():
            cuda_paths = [
                r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin",
                r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0\bin",
            ]
            for path in cuda_paths:
                if os.path.exists(path):
                    os.environ["PATH"] = path + ";" + os.environ.get("PATH", "")
                    break

        available = torch.cuda.is_available()
        if available:
            name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info("CUDA available: %s (%.1f GB VRAM)", name, vram)
        return available
    except (ImportError, OSError) as e:
        logger.warning("Torch load failed: %s", e)
        return False


class GPUEmbedder:
    """GPU-accelerated semantic embedder with CPU fallback."""

    MODEL_NAME = "all-MiniLM-L6-v2"

    def __init__(self):
        self._model = None
        self._device = "cpu"
        self._available = False
        self._initialized = False

    def initialize(self) -> bool:
        if self._initialized and self._model is not None:
            return self._available
        try:
            self._model, self._device = get_cached_model()
            self._available = True
            self._initialized = True
        except Exception as e:
            logger.warning("Embedding model unavailable: %s", e)
            self._available = False
        return self._available

    @property
    def device(self) -> str:
        return self._device

    @property
    def available(self) -> bool:
        return self._available

    def embed(self, texts: list[str]) -> Optional[list]:
        if not self.initialize() or not texts:
            return None
        try:
            import torch
            with torch.no_grad():
                embeddings = self._model.encode(
                    texts, batch_size=64, convert_to_tensor=True,
                    device=self._device, show_progress_bar=False,
                )
            return embeddings
        except Exception as e:
            logger.warning("Embedding failed: %s", e)
            return None

    def similarity(self, query: str, candidates: list[str]) -> list[float]:
        embeddings = self.embed([query] + candidates)
        if embeddings is not None:
            try:
                from sentence_transformers import util
                scores = util.cos_sim(embeddings[0], embeddings[1:])[0]
                return [float(s) for s in scores]
            except Exception:
                pass
        return self._keyword_similarity(query, candidates)

    def best_match(self, query: str, candidates: list[str], threshold: float = 0.5):
        if not candidates:
            return None, 0.0
        scores = self.similarity(query, candidates)
        best_idx = max(range(len(scores)), key=lambda i: scores[i])
        best_score = scores[best_idx]
        if best_score >= threshold:
            return candidates[best_idx], best_score
        return None, best_score

    def rank_sources(self, query: str, sources: list[dict]) -> list[dict]:
        if not sources:
            return sources
        snippets = [
            (s.get("snippet") or s.get("content") or s.get("title") or "")[:300]
            for s in sources
        ]
        scores = self.similarity(query, snippets)
        ranked = []
        for i, s in enumerate(sources):
            semantic_score = scores[i] if i < len(scores) else 0.0
            original_score = float(s.get("score", 0.5))
            combined = 0.6 * semantic_score + 0.4 * original_score
            ranked.append({**s, "score": combined, "semantic_score": semantic_score})
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def knowledge_graph_lookup(self, query: str, graph_concepts: list[str], threshold: float = 0.55):
        if not graph_concepts:
            return None, 0.0
        return self.best_match(query, graph_concepts, threshold)

    def _keyword_similarity(self, query: str, candidates: list[str]) -> list[float]:
        stop = {"what", "is", "the", "a", "an", "how", "why", "of", "in", "on"}
        q_words = set(query.lower().split()) - stop
        scores = []
        for cand in candidates:
            c_words = set(cand.lower().split()) - stop
            if not q_words or not c_words:
                scores.append(0.0)
                continue
            scores.append(len(q_words & c_words) / len(q_words | c_words))
        return scores

    def get_status(self) -> dict:
        self.initialize()
        status = {"available": self._available, "device": self._device, "model": self.MODEL_NAME if self._available else None}
        if self._available and self._device == "cuda":
            try:
                import torch
                status["vram_total_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1)
                status["vram_used_gb"] = round(torch.cuda.memory_allocated(0) / 1e9, 2)
                status["gpu_name"] = torch.cuda.get_device_name(0)
            except Exception:
                pass
        return status


# Module singleton
gpu_embedder = GPUEmbedder()
