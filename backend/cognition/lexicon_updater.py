"""
Phase 52.7 — Lexicon Auto-Healer

Reads Missed Concepts telemetry (gap_log.jsonl) and uses an LLM to
map unknown words into the governed CONCEPT_LEXICON, then safely
appends the new mappings to backend/data/lexicon.json.

Does NOT touch memory, thermodynamics, or logging subsystems.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from backend.models.llm_client import LLMMessage, llm_client

logger = logging.getLogger("uvicorn")

LEXICON_PATH = Path(__file__).parent.parent / "data" / "lexicon.json"
GAP_LOG_PATH = Path(__file__).parent.parent.parent / "data" / "gap_log.jsonl"

# Prompt template sent to the LLM for each unknown concept.
CLASSIFY_CONCEPT_PROMPT = (
    "You are a cognitive linguistics classifier for VELYNX, an AI with a governed emotional concept lexicon.\n\n"
    "Below is the current list of concept buckets and their trigger words:\n"
    "{existing_buckets}\n\n"
    "A word was heard that the system did not recognize: \"{unknown_term}\"\n\n"
    "Your task:\n"
    "1. Determine if \"{unknown_term}\" belongs to one of the EXISTING concept buckets above.\n"
    "   - If YES: return the EXACT bucket name and a confidence score (0.0-1.0).\n"
    "   - If NO: propose a NEW concept bucket name (lowercase, one word) and a short list of 4-6 synonym trigger words.\n"
    "2. Respond with ONLY a JSON object. No markdown, no explanation.\n\n"
    "JSON format:\n"
    '{{"action": "map", "bucket": "<existing_bucket_name>", "confidence": 0.85}}\n'
    "OR\n"
    '{{"action": "create", "bucket": "<new_bucket_name>", "triggers": ["syn1", "syn2", "syn3", "syn4", "syn5"], "confidence": 0.70}}\n'
)


class LexiconUpdater:
    """Standalone auto-healer that reads missed-concept telemetry, consults the LLM,
    and safely appends new mappings to the governed CONCEPT_LEXICON."""

    def __init__(self) -> None:
        self._lexicon_path = LEXICON_PATH
        self._gap_log_path = GAP_LOG_PATH

    # ── Public API ────────────────────────────────────────────────

    async def run(self) -> dict:
        """Main entry point: process all unresolved missed concepts and heal the lexicon.

        Returns a summary dict with counts of actions taken.
        """
        if not self._gap_log_path.exists():
            logger.info("LexiconUpdater: no gap log found — nothing to heal.")
            return {"processed": 0, "mapped": 0, "created": 0, "errors": 0}

        unprocessed = self._read_unresolved_gaps()
        if not unprocessed:
            logger.info("LexiconUpdater: no unresolved gaps found.")
            return {"processed": 0, "mapped": 0, "created": 0, "errors": 0}

        lexicon = self._load_lexicon()
        existing_buckets = self._format_buckets(lexicon)

        summary = {"processed": 0, "mapped": 0, "created": 0, "errors": 0}
        updated_gaps: list[dict] = []

        for gap in unprocessed:
            term = gap.get("term", "")
            if not term:
                continue

            result = await self._classify_term(term, existing_buckets)
            summary["processed"] += 1

            if result is None:
                summary["errors"] += 1
                continue

            if result["action"] == "map":
                success = self._apply_map(lexicon, term, result["bucket"])
                if success:
                    summary["mapped"] += 1
                    updated_gaps.append({**gap, "status": "resolved", "action": "map", "bucket": result["bucket"]})
                else:
                    summary["errors"] += 1
                    updated_gaps.append({**gap, "status": "error", "reason": "bucket_not_found"})

            elif result["action"] == "create":
                bucket = result["bucket"].lower().strip()
                triggers = result.get("triggers", [term])
                if bucket and bucket not in lexicon:
                    lexicon[bucket] = [term] + [t for t in triggers if t != term]
                    summary["created"] += 1
                    updated_gaps.append({**gap, "status": "resolved", "action": "create", "bucket": bucket})
                else:
                    summary["errors"] += 1
                    updated_gaps.append({**gap, "status": "error", "reason": "bucket_exists_or_invalid"})

        if summary["mapped"] > 0 or summary["created"] > 0:
            self._safe_write_lexicon(lexicon)
            logger.info(
                "LexiconUpdater: healed lexicon — %d mapped, %d new buckets created.",
                summary["mapped"], summary["created"],
            )

        self._update_gap_statuses(updated_gaps)

        return summary

    # ── LLM classification ────────────────────────────────────────

    async def _classify_term(self, term: str, existing_buckets: str) -> dict | None:
        """Ask the LLM to classify a single unknown term against existing concept buckets."""
        prompt = CLASSIFY_CONCEPT_PROMPT.format(
            existing_buckets=existing_buckets,
            unknown_term=term,
        )

        try:
            response = await llm_client.chat(
                [LLMMessage(role="user", content=prompt)],
                temperature=0.2,
            )
            parsed = llm_client.parse_json_content(response)
            if parsed and "action" in parsed:
                return parsed
            logger.warning("LexiconUpdater: LLM returned non-JSON for term '%s': %s", term, response.content[:200])
            return None
        except Exception as exc:
            logger.error("LexiconUpdater: LLM call failed for term '%s': %s", term, exc)
            return None

    # ── Lexicon I/O ───────────────────────────────────────────────

    def _load_lexicon(self) -> dict:
        """Load the full lexicon.json, returning just the 'lexicon' dict."""
        if not self._lexicon_path.exists():
            raise FileNotFoundError(f"Lexicon file missing: {self._lexicon_path}")
        data = json.loads(self._lexicon_path.read_text(encoding="utf-8"))
        return data.get("lexicon", {})

    def _format_buckets(self, lexicon: dict) -> str:
        """Format the current lexicon buckets for inclusion in the LLM prompt."""
        lines = []
        for bucket, triggers in sorted(lexicon.items()):
            lines.append(f"  - {bucket}: {', '.join(triggers)}")
        return "\n".join(lines)

    def _apply_map(self, lexicon: dict, term: str, bucket: str) -> bool:
        """Append a trigger word to an existing concept bucket in the lexicon dict.
        Returns True if the bucket existed and the word was added."""
        bucket = bucket.lower().strip()
        if bucket not in lexicon:
            return False
        if term not in lexicon[bucket]:
            lexicon[bucket].append(term)
        return True

    def _safe_write_lexicon(self, lexicon: dict) -> None:
        """Atomically write the lexicon dict back to lexicon.json using a temp-file + rename."""
        data = {
            "schema_version": 1,
            "description": "VELYNX Governed Concept Lexicon — maps cognitive concepts to trigger words for perception activation.",
            "lexicon": lexicon,
        }
        # Write to a temp file in the same directory, then atomically rename
        lexicon_dir = str(self._lexicon_path.parent)
        fd, tmp_path = tempfile.mkstemp(dir=lexicon_dir, prefix=".lexicon_", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            os.replace(tmp_path, str(self._lexicon_path))
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    # ── Gap log I/O ───────────────────────────────────────────────

    def _read_unresolved_gaps(self) -> list[dict]:
        """Read gap_log.jsonl and return entries with status='unresolved' and type='unknown_concept'."""
        entries: list[dict] = []
        if not self._gap_log_path.exists():
            return entries

        with open(self._gap_log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("status") == "unresolved" and entry.get("type") == "unknown_concept":
                    entries.append(entry)
        return entries

    def _update_gap_statuses(self, updated: list[dict]) -> None:
        """Rewrite gap_log.jsonl with updated statuses for processed entries.
        Matching is done by timestamp + term (natural composite key)."""
        if not updated or not self._gap_log_path.exists():
            return

        # Build lookup: (ts, term) → updated entry
        lookup: dict[tuple, dict] = {}
        for entry in updated:
            key = (entry.get("ts", ""), entry.get("term", ""))
            lookup[key] = entry

        lines: list[str] = []
        with open(self._gap_log_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    lines.append("\n")
                    continue
                try:
                    entry = json.loads(stripped)
                except json.JSONDecodeError:
                    lines.append(stripped + "\n")
                    continue

                key = (entry.get("ts", ""), entry.get("term", ""))
                if key in lookup:
                    updated_entry = lookup[key]
                    updated_entry["resolved_at"] = datetime.now(timezone.utc).isoformat()
                    lines.append(json.dumps(updated_entry, ensure_ascii=False) + "\n")
                else:
                    lines.append(stripped + "\n")

        with open(self._gap_log_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
