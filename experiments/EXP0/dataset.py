"""EXP-0 dataset loader.

Loads the frozen paired benchmark (paraphrases.json) and cross-validates it
against the live backend/soul/concepts.json on every import, so a silent
drift between the two (e.g. someone adds a 33rd concept, or edits a concept
name) is caught immediately and loudly rather than producing a quietly
wrong N.

This module does not import anything from backend.* or cognition.* -- it
only reads two JSON files. It is safe to import with no VELYNX dependencies
installed.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
_CONCEPTS_PATH = _REPO_ROOT / "backend" / "soul" / "concepts.json"
_PARAPHRASES_PATH = _HERE / "paraphrases.json"


class DatasetIntegrityError(RuntimeError):
    """Raised when paraphrases.json no longer matches concepts.json."""


@dataclass(frozen=True)
class BenchmarkItem:
    concept: str
    original_query: str
    paraphrase_query: str
    derivation: str  # "mechanical" | "mechanical-adjusted" | "hand-authored"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_items() -> list[BenchmarkItem]:
    """Load and validate the 32 paired items. Raises DatasetIntegrityError
    on any drift between paraphrases.json and the live concepts.json."""
    if not _CONCEPTS_PATH.exists():
        raise DatasetIntegrityError(f"concepts.json not found at {_CONCEPTS_PATH}")
    concepts = json.loads(_CONCEPTS_PATH.read_text(encoding="utf-8"))

    data = json.loads(_PARAPHRASES_PATH.read_text(encoding="utf-8"))
    recorded_hash = data.get("source_file_sha256")
    live_hash = _sha256_file(_CONCEPTS_PATH)
    if recorded_hash != live_hash:
        raise DatasetIntegrityError(
            "backend/soul/concepts.json has changed since paraphrases.json "
            f"was frozen (recorded sha256={recorded_hash}, live={live_hash}). "
            "EXP-0 requires the concept set to be frozen. Re-run "
            "leakage_check.py and re-freeze paraphrases.json (with a new "
            "schema_version) before proceeding, or restore the original "
            "concepts.json."
        )

    concept_names = set(concepts.keys())
    item_names = {item["concept"] for item in data["items"]}
    if concept_names != item_names:
        missing = concept_names - item_names
        extra = item_names - concept_names
        raise DatasetIntegrityError(
            f"Concept set mismatch. Missing from paraphrases.json: {sorted(missing)}. "
            f"Extra in paraphrases.json (not in concepts.json): {sorted(extra)}."
        )

    items = [
        BenchmarkItem(
            concept=item["concept"],
            original_query=item["original_query"],
            paraphrase_query=item["paraphrase_query"],
            derivation=item["derivation"],
        )
        for item in data["items"]
    ]
    # Deterministic order: sorted by concept name, independent of JSON key
    # order, so downstream seeded shuffles are reproducible regardless of
    # how paraphrases.json happens to be formatted.
    items.sort(key=lambda i: i.concept)
    return items


def dataset_manifest() -> dict:
    """Content-hash manifest for the artifact writer. Excludes nothing --
    every value here is fully reproducible from the two frozen input files."""
    return {
        "concepts_json_sha256": _sha256_file(_CONCEPTS_PATH),
        "paraphrases_json_sha256": _sha256_file(_PARAPHRASES_PATH),
        "item_count": len(load_items()),
    }


if __name__ == "__main__":
    items = load_items()
    print(f"Loaded {len(items)} items.")
    for item in items:
        print(f"  [{item.derivation:18s}] {item.concept}")
    print(dataset_manifest())
