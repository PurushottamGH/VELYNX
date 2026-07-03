"""
VELYNX CORE v2 — learner.py
Continuous self-learning engine.
Crash-safe: uses atomic checkpointing — if it dies mid-learn, it resumes.
Pipeline: queue → fetch → extract → store → verify → queue next.
"""

import re
import time
import json
import logging
import hashlib
import threading
import traceback
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict
from urllib.parse import quote_plus
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from .memory import VelynxMemory, Concept, Relation

logger = logging.getLogger("velynx.learner")

# ── Learning item ────────────────────────────────────────────────────────────

@dataclass
class LearningItem:
    topic: str
    domain: str
    priority: float = 1.0
    attempts: int = 0
    last_attempted: float = 0.0
    status: str = "pending"   # pending | in_progress | done | failed
    item_id: str = ""

    def __post_init__(self):
        if not self.item_id:
            self.item_id = hashlib.sha256(
                f"{self.domain}::{self.topic}".encode()
            ).hexdigest()[:12]


# ── Checkpoint (crash-safe state) ────────────────────────────────────────────

class LearnerCheckpoint:
    """Atomic checkpoint: writes to .tmp then renames → no corrupt saves."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, queue: list[LearningItem], stats: dict):
        data = {
            "queue": [asdict(item) for item in queue],
            "stats": stats,
            "saved_at": time.time()
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2))
        tmp.rename(self.path)   # atomic on POSIX + Windows NTFS

    def load(self) -> tuple[list[LearningItem], dict]:
        if not self.path.exists():
            return [], {}
        try:
            data = json.loads(self.path.read_text())
            queue = [LearningItem(**item) for item in data.get("queue", [])]
            return queue, data.get("stats", {})
        except Exception as e:
            logger.warning(f"Checkpoint load failed ({e}), starting fresh")
            return [], {}


# ── Web fetchers ─────────────────────────────────────────────────────────────

def _http_get(url: str, timeout: int = 10) -> Optional[str]:
    try:
        req = Request(url, headers={
            "User-Agent": "VelynxLearner/2.0 (educational AI system)"
        })
        with urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except (URLError, HTTPError, Exception) as e:
        logger.debug(f"HTTP GET failed {url}: {e}")
        return None


def fetch_wikipedia(topic: str) -> Optional[dict]:
    """Fetch and parse a Wikipedia summary for a topic."""
    encoded = quote_plus(topic)
    url = (f"https://en.wikipedia.org/w/api.php"
           f"?action=query&prop=extracts&exintro&explaintext"
           f"&titles={encoded}&format=json&redirects=1")
    raw = _http_get(url)
    if not raw:
        return None
    try:
        data = json.loads(raw)
        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))
        if "missing" in page:
            return None
        extract = page.get("extract", "").strip()
        if len(extract) < 50:
            return None
        return {
            "title": page.get("title", topic),
            "text": extract,
            "url": f"https://en.wikipedia.org/wiki/{quote_plus(page.get('title', topic))}"
        }
    except Exception as e:
        logger.debug(f"Wikipedia parse failed: {e}")
        return None


def fetch_duckduckgo_instant(topic: str) -> Optional[dict]:
    """Use DDG instant answer API as a fallback."""
    encoded = quote_plus(topic)
    url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
    raw = _http_get(url)
    if not raw:
        return None
    try:
        data = json.loads(raw)
        abstract = data.get("AbstractText", "").strip()
        if len(abstract) < 40:
            return None
        return {
            "title": data.get("Heading", topic),
            "text": abstract,
            "url": data.get("AbstractURL", "")
        }
    except Exception:
        return None


# ── Concept extractor ────────────────────────────────────────────────────────

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

def _first_n_sentences(text: str, n: int) -> str:
    sentences = _SENT_SPLIT.split(text.strip())
    return " ".join(sentences[:n])

def _extract_how(text: str) -> str:
    """Look for 'works by', 'process', 'method', 'steps' in text."""
    patterns = [
        r"(?:works? by|operates? by|functions? by)\s+([^.]+\.)",
        r"(?:process|mechanism|method)\s+(?:is|involves?|includes?)\s+([^.]+\.)",
        r"(?:by|through|via)\s+([^,]+(?:,\s*[^,]+){1,3})\.",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    # fallback: sentences containing "by" or "through"
    for sent in _SENT_SPLIT.split(text):
        if re.search(r"\b(by|through|via|using|with)\b", sent, re.IGNORECASE):
            return sent.strip()
    return ""

def _extract_why(text: str) -> str:
    patterns = [
        r"(?:important|critical|essential|significant) because ([^.]+\.)",
        r"(?:enables?|allows?|permits?|facilitates?)\s+([^.]+\.)",
        r"(?:used to|designed to|meant to)\s+([^.]+\.)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""

def _extract_so_what(text: str) -> str:
    patterns = [
        r"(?:result(?:ing|s)?|therefore|thus|consequently|as a result)[,\s]+([^.]+\.)",
        r"(?:impact|effect|implication)[s]?\s+(?:is|are|include)\s+([^.]+\.)",
        r"(?:leads? to|causes?|produces?|results? in)\s+([^.]+\.)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""

def _estimate_confidence(source: dict, text_len: int) -> float:
    base = 0.6
    if "wikipedia" in source.get("url", ""):
        base = 0.75
    if text_len > 500:
        base += 0.05
    if text_len > 1000:
        base += 0.05
    return min(base, 0.95)

def extract_concept_from_source(topic: str, domain: str, source: dict) -> Optional[Concept]:
    """Parse raw text from a web source into a structured Concept."""
    text = source.get("text", "")
    if not text or len(text) < 40:
        return None

    what = _first_n_sentences(text, 2)
    how = _extract_how(text)
    why = _extract_why(text)
    so_what = _extract_so_what(text)

    # fallbacks
    if not how:
        how = _first_n_sentences(text, 4).split(". ")[-1] if ". " in text else ""
    if not why:
        why = f"Understanding {topic} is important in the field of {domain}."
    if not so_what:
        so_what = f"Knowledge of {topic} contributes to understanding {domain} systems."

    return Concept(
        id=Concept.make_id(topic, domain),
        name=topic,
        domain=domain,
        what=what[:400],
        why=why[:300],
        how=how[:300],
        so_what=so_what[:300],
        confidence=_estimate_confidence(source, len(text)),
        sources=[source.get("url", "unknown")]
    )


# ── Relation extractor ───────────────────────────────────────────────────────

RELATION_PATTERNS = [
    (r"(\w[\w\s]+)\s+causes?\s+([\w\s]+)",         "CAUSES"),
    (r"(\w[\w\s]+)\s+enables?\s+([\w\s]+)",         "ENABLES"),
    (r"(\w[\w\s]+)\s+requires?\s+([\w\s]+)",        "REQUIRES"),
    (r"(\w[\w\s]+)\s+is\s+part\s+of\s+([\w\s]+)",  "PART_OF"),
    (r"(\w[\w\s]+)\s+is\s+an?\s+example\s+of\s+([\w\s]+)", "EXAMPLE_OF"),
    (r"(\w[\w\s]+)\s+contradicts?\s+([\w\s]+)",     "CONTRADICTS"),
]

def extract_relations(text: str, concept_id: str,
                       known_ids: dict[str, str]) -> list[Relation]:
    """
    known_ids: {concept_name: concept_id}
    Returns list of Relation objects linking known concepts.
    """
    relations = []
    for pattern, rel_type in RELATION_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            a_name = m.group(1).strip().lower()
            b_name = m.group(2).strip().lower()
            if a_name in known_ids and b_name in known_ids:
                relations.append(Relation(
                    from_id=known_ids[a_name],
                    to_id=known_ids[b_name],
                    relation_type=rel_type,
                    weight=0.8,
                    evidence=m.group(0)[:120]
                ))
    return relations


# ── VelynxLearner ─────────────────────────────────────────────────────────────

class VelynxLearner:
    """
    Continuous crash-safe learning loop.
    - Maintains a priority queue of topics to learn.
    - Fetches → extracts → stores → checkspoints after each item.
    - Runs in background thread; can be stopped cleanly.
    """

    def __init__(self, memory: VelynxMemory,
                 checkpoint_path: str = "velynx_core/learner_state.json",
                 batch_size: int = 5,
                 sleep_between_items: float = 1.5,
                 max_retries: int = 3):
        self.memory = memory
        self.checkpoint = LearnerCheckpoint(checkpoint_path)
        self.batch_size = batch_size
        self.sleep_between = sleep_between_items
        self.max_retries = max_retries

        self._queue: list[LearningItem] = []
        self._stats: dict = {
            "total_learned": 0,
            "total_failed": 0,
            "total_fetches": 0,
            "start_time": time.time()
        }
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Load checkpoint
        saved_queue, saved_stats = self.checkpoint.load()
        self._queue = saved_queue
        if saved_stats:
            self._stats.update(saved_stats)

        # Reset any stuck "in_progress" items
        for item in self._queue:
            if item.status == "in_progress":
                item.status = "pending"

        logger.info(f"VelynxLearner init: {len(self._queue)} items in queue")

    # ── Queue management ─────────────────────────────────────────────────

    def enqueue(self, topic: str, domain: str = "general",
                priority: float = 1.0):
        """Add a topic to learn. No-op if already queued."""
        with self._lock:
            new_item = LearningItem(topic=topic, domain=domain, priority=priority)
            existing_ids = {i.item_id for i in self._queue}
            if new_item.item_id not in existing_ids:
                self._queue.append(new_item)
                self._queue.sort(key=lambda x: (-x.priority, x.attempts))
                logger.info(f"Queued: '{topic}' ({domain})")
                return True
        return False

    def enqueue_curriculum(self, items: list[dict]):
        """Bulk-enqueue from a curriculum list: [{topic, domain, priority}]"""
        added = 0
        for item in items:
            if self.enqueue(
                item["topic"],
                item.get("domain", "general"),
                item.get("priority", 1.0)
            ):
                added += 1
        logger.info(f"Curriculum: added {added} new topics to queue")
        return added

    def queue_size(self) -> int:
        with self._lock:
            return len([i for i in self._queue if i.status == "pending"])

    # ── Learning engine ──────────────────────────────────────────────────

    def _fetch_topic(self, item: LearningItem) -> Optional[dict]:
        """Try fetchers in order of quality."""
        self._stats["total_fetches"] += 1

        # Wikipedia first (highest quality)
        source = fetch_wikipedia(item.topic)
        if source:
            return source

        # DDG instant answer fallback
        source = fetch_duckduckgo_instant(item.topic)
        if source:
            return source

        return None

    def _learn_one(self, item: LearningItem) -> bool:
        """Learn a single topic. Returns True on success."""
        item.status = "in_progress"
        item.last_attempted = time.time()
        item.attempts += 1

        logger.info(f"Learning: '{item.topic}' ({item.domain}) [attempt {item.attempts}]")

        source = self._fetch_topic(item)
        if not source:
            logger.warning(f"No source found for '{item.topic}'")
            item.status = "failed" if item.attempts >= self.max_retries else "pending"
            self._stats["total_failed"] += 1
            return False

        concept = extract_concept_from_source(item.topic, item.domain, source)
        if not concept:
            logger.warning(f"Concept extraction failed for '{item.topic}'")
            item.status = "failed" if item.attempts >= self.max_retries else "pending"
            self._stats["total_failed"] += 1
            return False

        is_new = self.memory.store_concept(concept)
        item.status = "done"
        self._stats["total_learned"] += 1

        action = "Learned NEW" if is_new else "Updated"
        logger.info(
            f"{action}: '{concept.name}' | "
            f"confidence={concept.confidence:.2f} | "
            f"what={concept.what[:60]}..."
        )

        self.memory.log_event("learned", {
            "topic": item.topic, "domain": item.domain,
            "confidence": concept.confidence, "is_new": is_new
        })

        # Try to extract relations with already-known concepts
        try:
            all_concepts = self.memory.search_concepts("", top_k=100)
            known_ids = {c.name.lower(): c.id for c in all_concepts}
            relations = extract_relations(
                source.get("text", ""), concept.id, known_ids
            )
            for rel in relations:
                self.memory.add_relation(rel)
            if relations:
                logger.info(f"  → {len(relations)} relations added")
        except Exception as e:
            logger.debug(f"Relation extraction failed (non-fatal): {e}")

        return True

    # ── Main loop ────────────────────────────────────────────────────────

    def _run_loop(self):
        logger.info("Learning loop started")
        while self._running:
            try:
                batch = self._get_pending_batch()
                if not batch:
                    # Nothing to learn; sleep and check again
                    time.sleep(10)
                    continue

                for item in batch:
                    if not self._running:
                        break
                    try:
                        self._learn_one(item)
                    except Exception as e:
                        logger.error(f"Uncaught error learning '{item.topic}': {e}")
                        logger.debug(traceback.format_exc())
                        item.status = "failed" if item.attempts >= self.max_retries else "pending"
                        self._stats["total_failed"] += 1

                    # Checkpoint after EVERY item — crash safety
                    with self._lock:
                        self.checkpoint.save(self._queue, self._stats)

                    time.sleep(self.sleep_between)

                # Prune completed/failed items older than 24h
                self._prune_done()

            except Exception as e:
                logger.error(f"Learning loop error: {e}")
                logger.debug(traceback.format_exc())
                time.sleep(5)

        logger.info("Learning loop stopped")

    def _get_pending_batch(self) -> list[LearningItem]:
        with self._lock:
            pending = [i for i in self._queue if i.status == "pending"]
            pending.sort(key=lambda x: (-x.priority, x.attempts))
            return pending[:self.batch_size]

    def _prune_done(self):
        cutoff = time.time() - 86400  # 24h
        with self._lock:
            before = len(self._queue)
            self._queue = [
                i for i in self._queue
                if not (i.status in ("done", "failed") and i.last_attempted < cutoff)
            ]
            removed = before - len(self._queue)
            if removed:
                logger.debug(f"Pruned {removed} completed/failed items from queue")

    # ── Start / Stop ─────────────────────────────────────────────────────

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="velynx-learner"
        )
        self._thread.start()
        logger.info("VelynxLearner started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=15)
        with self._lock:
            self.checkpoint.save(self._queue, self._stats)
        logger.info("VelynxLearner stopped and checkpointed")

    def stats(self) -> dict:
        with self._lock:
            pending = sum(1 for i in self._queue if i.status == "pending")
            done    = sum(1 for i in self._queue if i.status == "done")
            failed  = sum(1 for i in self._queue if i.status == "failed")
        return {
            **self._stats,
            "queue_pending": pending,
            "queue_done":    done,
            "queue_failed":  failed,
            "is_running":    self._running,
            "uptime_seconds": round(time.time() - self._stats.get("start_time", time.time()))
        }