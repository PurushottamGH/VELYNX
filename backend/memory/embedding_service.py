"""Embedding service — sentence-transformers with LRU cache."""
from __future__ import annotations

import asyncio
import hashlib
import logging
from collections import OrderedDict
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger("uvicorn")

_CACHE_SIZE = 2048
_MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingService:
    """Lazy-loaded sentence-transformers embedding with in-memory LRU cache."""

    def __init__(self, model_name: str = _MODEL_NAME) -> None:
        self._model_name = model_name
        self._model = None
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._loading = False

    @property
    def available(self) -> bool:
        import os
        if os.getenv("VELYNX_SKIP_EMBEDDING"):
            return False
        try:
            import sentence_transformers  # noqa: F401
            return True
        except (ImportError, OSError):
            return False

    def _get_device(self) -> str:
        """Auto-detect GPU for embeddings."""
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
        except (ImportError, OSError):
            pass
        return "cpu"

    def _get_model(self):
        import os
        if os.getenv("VELYNX_SKIP_EMBEDDING"):
            raise RuntimeError("Embedding disabled by VELYNX_SKIP_EMBEDDING")
        if self._model is None:
            # Reuse the shared singleton from gpu_embedder to avoid loading the model twice
            from backend.memory.gpu_embedder import get_cached_model
            model, _device = get_cached_model()
            self._model = model
        return self._model

    def _cache_key(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def _get_cached(self, key: str):
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def _put_cached(self, key: str, value) -> None:
        self._cache[key] = value
        if len(self._cache) > _CACHE_SIZE:
            self._cache.popitem(last=False)

    async def embed(self, text: str):
        """Embed a single text string. Returns numpy array (384-dim)."""
        return await asyncio.to_thread(self._embed_sync, text)

    async def embed_batch(self, texts: list[str]):
        """Embed multiple texts. Returns list of numpy arrays."""
        return await asyncio.to_thread(self._embed_batch_sync, texts)

    def _embed_sync(self, text: str):
        import numpy as np

        key = self._cache_key(text)
        cached = self._get_cached(key)
        if cached is not None:
            return cached

        model = self._get_model()
        embedding = model.encode(text, normalize_embeddings=True)
        self._put_cached(key, embedding)
        return embedding

    def _embed_batch_sync(self, texts: list[str]):
        import numpy as np

        results = [None] * len(texts)
        to_embed_idx = []
        to_embed_text = []

        for i, text in enumerate(texts):
            key = self._cache_key(text)
            cached = self._get_cached(key)
            if cached is not None:
                results[i] = cached
            else:
                to_embed_idx.append(i)
                to_embed_text.append(text)

        if to_embed_text:
            model = self._get_model()
            embeddings = model.encode(to_embed_text, normalize_embeddings=True, batch_size=64)
            for idx, embedding in zip(to_embed_idx, embeddings):
                key = self._cache_key(texts[idx])
                self._put_cached(key, embedding)
                results[idx] = embedding

        return results


# Module-level singleton
embedding_service = EmbeddingService()
