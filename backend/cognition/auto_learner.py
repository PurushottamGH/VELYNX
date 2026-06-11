"""
VELYNX Self-Healing Auto-Learner
================================

A completely local, offline script that allows VELYNX to teach itself new
concepts based on its own ``gap_log.jsonl``.

It uses NLTK's WordNet corpus to look up definitions and synonyms for the
words the system keeps failing on, then proposes a graph patch that links the
newly discovered concept to nodes that already exist in VELYNX's Soul /
Knowledge graph.  All proposals are written to ``data/proposed_nodes.json`` so
a human (or a higher-level governance routine) can review them before they
are structurally appended to the SQLite knowledge base.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import nltk
from nltk.corpus import wordnet


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
GAP_LOG_PATH = DATA_DIR / "gap_log.jsonl"
CONCEPTS_PATH = DATA_DIR / "concepts.json"
SOUL_CONCEPTS_PATH = DATA_DIR / "soul_concepts.json"
PROPOSED_NODES_PATH = DATA_DIR / "proposed_nodes.json"

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "while", "with", "without",
    "of", "in", "on", "at", "to", "for", "from", "by", "as", "is", "are",
    "was", "were", "be", "been", "being", "i", "you", "he", "she", "it",
    "we", "they", "me", "him", "her", "us", "them", "my", "your", "his",
    "its", "our", "their", "this", "that", "these", "those", "do", "does",
    "did", "have", "has", "had", "not", "no", "so", "up", "down", "out",
    "about", "into", "over", "after", "before", "between", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "than", "too", "very", "s", "t", "can", "will", "just",
    "don", "should", "now", "feel", "felt", "feeling", "feelings", "query",
    "triggered", "zero", "concept", "concepts", "match", "matches", "marker",
    "markers", "present", "weak", "covered", "possible", "unknown", "know",
    "knows", "knew", "go", "goes", "going", "gone", "keep", "keeps", "kept",
    "thing", "things", "even", "still", "anything", "everything", "nothing",
    "something", "dont", "im", "i'm", "ive", "i've", "cant", "can't",
    "wont", "won't", "anyone", "everyone", "no one", "nobody",
}


def setup_wordnet() -> None:
    """Ensure the local WordNet corpus is available.

    NLTK ships its data separately from the package itself, so the first
    invocation of the auto-learner has to make sure the ``wordnet`` resource
    is on disk.  Subsequent runs are a no-op because NLTK caches the lookup
    in ``~/nltk_data``.
    """

    try:
        wordnet.ensure_loaded()
    except LookupError:
        nltk.download("wordnet", quiet=True)
        wordnet.ensure_loaded()


def _normalise_token(token: str) -> str:
    token = token.lower().strip()
    token = re.sub(r"^['\"]|['\"]$", "", token)
    token = re.sub(r"[^a-z0-9\-']", "", token)
    return token


def extract_candidate_concepts(gap_log_path: Path) -> Counter:
    """Read ``gap_log.jsonl`` and tally candidate missing concepts.

    Two complementary signals are mined from each entry:

    * the ``gaps`` field — free-text explanations the system already produced
      when it noticed it was missing something;
    * the ``query`` field — the original user utterance, which often contains
      the literal word the user is reaching for.
    """

    if not gap_log_path.exists():
        return Counter()

    counts: Counter = Counter()

    with gap_log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            for gap in entry.get("gaps", []):
                if not isinstance(gap, str):
                    continue
                quoted = re.findall(r"'([^']+)'|\"([^\"]+)\"", gap)
                for a, b in quoted:
                    word = a or b
                    normalised = _normalise_token(word)
                    if normalised and normalised not in STOPWORDS and len(normalised) > 2:
                        counts[normalised] += 1

                for token in re.findall(r"[A-Za-z][A-Za-z\-']+", gap):
                    normalised = _normalise_token(token)
                    if (
                        normalised
                        and normalised not in STOPWORDS
                        and len(normalised) > 3
                    ):
                        counts[normalised] += 0.5

            query = entry.get("query", "")
            if isinstance(query, str):
                for token in re.findall(r"[A-Za-z][A-Za-z\-']+", query):
                    normalised = _normalise_token(token)
                    if (
                        normalised
                        and normalised not in STOPWORDS
                        and len(normalised) > 3
                    ):
                        counts[normalised] += 0.25

    return counts


def _synonyms_for(lemma_name: str) -> list[str]:
    synonyms: list[str] = []
    for lemma in wordnet.synonyms(lemma_name):
        for synonym in lemma:
            cleaned = synonym.replace("_", " ").lower().strip()
            if cleaned and cleaned != lemma_name.lower():
                synonyms.append(cleaned)
    return synonyms


def _definition_for(word: str) -> str:
    synsets = wordnet.synsets(word)
    if not synsets:
        return ""
    return synsets[0].definition()


def _top_synonyms(word: str, limit: int = 3) -> list[str]:
    """Return up to ``limit`` distinct synonyms for ``word`` from WordNet."""

    synsets = wordnet.synsets(word)
    if not synsets:
        return []

    seen: set[str] = set()
    ordered: list[str] = []
    for synset in synsets:
        for lemma in synset.lemmas():
            name = lemma.name().replace("_", " ").lower().strip()
            if not name or name == word.lower():
                continue
            if name in seen:
                continue
            seen.add(name)
            ordered.append(name)
            if len(ordered) >= limit:
                return ordered
    return ordered


class AutoLearner:
    """Mine ``gap_log.jsonl`` and propose new nodes / edges for the graph."""

    def __init__(
        self,
        gap_log_path: Path = GAP_LOG_PATH,
        concepts_path: Path = CONCEPTS_PATH,
        soul_concepts_path: Path = SOUL_CONCEPTS_PATH,
        proposed_nodes_path: Path = PROPOSED_NODES_PATH,
    ) -> None:
        self.gap_log_path = gap_log_path
        self.concepts_path = concepts_path
        self.soul_concepts_path = soul_concepts_path
        self.proposed_nodes_path = proposed_nodes_path
        self.existing_concepts: set[str] = set()
        self.proposals: list[dict[str, Any]] = []

    def load_existing_concepts(self) -> None:
        """Read every concept name already known to VELYNX."""

        self.existing_concepts = set()

        if self.concepts_path.exists():
            try:
                with self.concepts_path.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                for name in (data.get("nodes") or {}).keys():
                    self.existing_concepts.add(name.lower())
            except (json.JSONDecodeError, OSError):
                pass

        if self.soul_concepts_path.exists():
            try:
                with self.soul_concepts_path.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                for name in (data.get("concepts") or {}).keys():
                    self.existing_concepts.add(name.lower())
                for name in (data.get("edges") or {}):
                    if isinstance(name, str):
                        self.existing_concepts.add(name.lower())
            except (json.JSONDecodeError, OSError):
                pass

    def process_gap_log(self, top_n: int = 5) -> list[dict[str, Any]]:
        """Read the gap log, find the most frequent missing concepts, and
        use WordNet to gather a definition + synonyms for each.

        Returns the list of proposals (also stored on ``self.proposals``).
        """

        setup_wordnet()
        self.load_existing_concepts()

        candidates = extract_candidate_concepts(self.gap_log_path)
        if not candidates:
            self.proposals = []
            return self.proposals

        ranked = [
            word
            for word, _ in candidates.most_common(top_n * 3)
            if word not in self.existing_concepts
        ][:top_n]

        self.proposals = []
        for concept in ranked:
            definition = _definition_for(concept)
            synonyms = _top_synonyms(concept, limit=3)

            if not definition and not synonyms:
                continue

            proposal = self.propose_graph_patch(
                concept=concept,
                synonyms=synonyms,
                definition=definition,
            )
            self.proposals.append(proposal)

        return self.proposals

    def propose_graph_patch(
        self,
        concept: str,
        synonyms: list[str],
        definition: str,
    ) -> dict[str, Any]:
        """Compare ``synonyms`` against VELYNX's existing concept set.

        For every synonym that already lives in the graph, a relational edge
        is proposed of the form::

            <concept> -> relates_to -> <synonym>

        The function also returns a self-contained proposal dictionary
        describing the new node, its definition, its source and the list of
        proposed edges.
        """

        normalised_concept = concept.lower()
        proposed_edges: list[dict[str, str]] = []
        matched_synonyms: list[str] = []

        for synonym in synonyms:
            synonym_norm = synonym.lower().strip()
            if not synonym_norm or synonym_norm == normalised_concept:
                continue
            if synonym_norm in self.existing_concepts:
                proposed_edges.append(
                    {
                        "source": normalised_concept,
                        "relationship": "relates_to",
                        "target": synonym_norm,
                    }
                )
                matched_synonyms.append(synonym_norm)

        proposal: dict[str, Any] = {
            "concept": normalised_concept,
            "definition": definition,
            "synonyms": synonyms,
            "matched_existing_concepts": matched_synonyms,
            "proposed_edges": proposed_edges,
            "origin": "auto_learner",
            "source": "nltk.wordnet",
            "status": "pending_review",
        }
        return proposal

    def write_proposals(self) -> Path:
        """Persist the current proposals to ``proposed_nodes.json``."""

        self.proposed_nodes_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_by": "backend.cognition.auto_learner.AutoLearner",
            "version": 1,
            "existing_concept_count": len(self.existing_concepts),
            "proposals": self.proposals,
        }
        with self.proposed_nodes_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        return self.proposed_nodes_path


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    top_n = 5
    if argv and argv[0].isdigit():
        top_n = max(1, int(argv[0]))

    learner = AutoLearner()
    proposals = learner.process_gap_log(top_n=top_n)
    output_path = learner.write_proposals()

    print(f"[auto_learner] Wrote {len(proposals)} proposal(s) to {output_path}")
    for proposal in proposals:
        print(
            f"  - {proposal['concept']}: "
            f"{len(proposal['matched_existing_concepts'])} existing-link(s) | "
            f"{len(proposal['synonyms'])} synonym(s) from WordNet"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
