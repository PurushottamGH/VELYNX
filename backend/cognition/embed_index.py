"""
VELYNX Embedding Index — GPU-accelerated soul concept lookup.
Layer 1: Encodes soul concepts into a FAISS-ready embedding matrix.
No external APIs. Runs on GTX 1070.

The SentenceTransformer model is loaded exactly ONCE at module import time and
kept resident in VRAM for the lifetime of the process. Never instantiate it
inside a function scope — that costs ~22s per call.
"""

import json
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

SOUL_PATH = Path(__file__).parent.parent / "soul" / "concepts.json"
INDEX_PATH = Path(__file__).parent.parent.parent / "backend" / "velynx_data" / "embed_index.npy"
KEYS_PATH = Path(__file__).parent.parent.parent / "backend" / "velynx_data" / "embed_keys.json"
MODEL_NAME = "all-MiniLM-L6-v2"  # 80MB, fits easily in 8GB VRAM

# ── Global, persistent model instance ────────────────────────────────────
# Loaded once at import. Stays in VRAM. No per-call instantiation.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_MODEL_INSTANCE = SentenceTransformer(MODEL_NAME, device=DEVICE)

_matrix = None  # (N, 384) float32
_keys = None  # list of concept names


def _load_index():
    global _matrix, _keys
    if _matrix is None and INDEX_PATH.exists():
        _matrix = np.load(str(INDEX_PATH))
        with open(KEYS_PATH, "r") as f:
            _keys = json.load(f)
    return _matrix, _keys


def build_index():
    """Encode all soul concepts into a FAISS-ready embedding matrix."""
    soul = _read_soul()
    if not soul:
        print("  No soul concepts found. Run teach.py first.")
        return

    keys, texts = [], []
    for name, entry in soul.items():
        keys.append(name)
        if isinstance(entry, dict):
            definition = entry.get("definition", entry.get("core", ""))
            situations = entry.get("real_situations", [])
            if isinstance(situations, list):
                real = " ".join(
                    s.get("situation", str(s)) if isinstance(s, dict) else str(s)
                    for s in situations[:2]
                )
            else:
                real = ""
            text = f"{name}: {definition} {real}".strip()
        else:
            text = f"{name}: {entry}"
        texts.append(text)

    print(f"  Encoding {len(texts)} concepts on {_MODEL_INSTANCE.device}...")
    matrix = _MODEL_INSTANCE.encode(
        texts, convert_to_numpy=True, normalize_embeddings=True
    )

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(INDEX_PATH), matrix)
    with open(KEYS_PATH, "w") as f:
        json.dump(keys, f)

    global _matrix, _keys
    _matrix, _keys = matrix, keys
    print(f"  Embedding index built: {len(keys)} concepts, shape {matrix.shape}")


def semantic_lookup(query: str, top_k: int = 3, threshold: float = 0.35) -> list[dict]:
    """
    Find soul concepts semantically similar to the query.
    Returns list of {concept, score} sorted by score descending.
    Falls back to empty list if index not built.
    """
    matrix, keys = _load_index()
    if matrix is None:
        return []

    vec = _MODEL_INSTANCE.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True
    )[0]
    scores = matrix @ vec  # cosine similarity (normalized)

    results = []
    for i, score in enumerate(scores):
        if score >= threshold:
            results.append({"concept": keys[i], "score": float(score)})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def concept_similarity(a: str, b: str) -> float:
    """Cosine similarity between two concept embeddings."""
    matrix, keys = _load_index()
    if matrix is None or a not in keys or b not in keys:
        return 0.0
    ia, ib = keys.index(a), keys.index(b)
    return float(matrix[ia] @ matrix[ib])


def classify_edge_type(a: str, b: str, score: float) -> str:
    """Classify edge relationship type from embedding similarity score. Pure local heuristic."""
    soul = _read_soul()
    def_a = _get_def(soul, a).lower()
    def_b = _get_def(soul, b).lower()

    negative_words = {"loss", "pain", "destroy", "absence", "fail", "end", "empty", "broken"}
    positive_words = {"grow", "build", "hope", "heal", "trust", "love", "rise", "forward"}

    neg_a = any(w in def_a for w in negative_words)
    pos_b = any(w in def_b for w in positive_words)
    neg_b = any(w in def_b for w in negative_words)
    pos_a = any(w in def_a for w in positive_words)

    if score > 0.75:
        return "deepens"
    elif score > 0.60:
        if neg_a and pos_b:
            return "catalyzes"
        elif pos_a and neg_b:
            return "corrupts"
        return "amplifies"
    elif score > 0.45:
        if neg_a and neg_b:
            return "compounds"
        elif pos_a and pos_b:
            return "sustains"
        return "informs"
    elif score > 0.35:
        return "contrasts"
    else:
        return "distant"


def _read_soul() -> dict:
    if not SOUL_PATH.exists():
        return {}
    with open(SOUL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_def(soul: dict, concept: str) -> str:
    entry = soul.get(concept, {})
    if isinstance(entry, dict):
        return entry.get("definition", entry.get("core", ""))
    return str(entry)
