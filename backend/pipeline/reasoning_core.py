"""Internal reasoning engine — produces meaningful answers from sources without any external API.

Uses TF-IDF scoring, extractive sentence selection, and structured synthesis
to build well-cited answers from retrieved source content.
"""
from __future__ import annotations

import math
import re
from collections import Counter

_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must", "about",
    "above", "after", "again", "all", "also", "and", "any", "because",
    "before", "between", "both", "but", "by", "each", "for", "from",
    "further", "get", "got", "here", "how", "into", "just", "like",
    "make", "many", "more", "most", "much", "new", "now", "only",
    "other", "our", "out", "over", "own", "part", "per", "said", "same",
    "see", "she", "so", "some", "still", "such", "take", "than", "that",
    "their", "them", "then", "there", "these", "they", "this", "those",
    "through", "together", "too", "under", "until", "upon", "very",
    "want", "was", "well", "what", "when", "where", "which", "while",
    "who", "whom", "why", "with", "within", "without", "would", "your",
    "one", "two", "first", "also", "not", "no", "nor", "as", "if",
    "its", "it", "it's", "or", "an", "at", "by", "from", "up",
    "into", "on", "in", "to", "of", "for", "with", "is", "are",
    "be", "was", "were", "has", "have", "had", "do", "does", "did",
    "will", "would", "can", "could", "shall", "should", "may", "might",
})


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alpha words, removing stopwords."""
    words = re.findall(r"[a-zA-Z]{2,}", text.lower())
    return [w for w in words if w not in _STOP_WORDS]


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries."""
    # Split on sentence-ending punctuation followed by space or end
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = []
    for s in raw:
        s = s.strip()
        if len(s) > 20:  # skip very short fragments
            sentences.append(s)
    return sentences


def _tfidf_score(query_tokens: list[str], sentence_tokens: list[str],
                 doc_freqs: Counter, num_docs: int) -> float:
    """Compute TF-IDF similarity between query and sentence."""
    if not sentence_tokens or not query_tokens:
        return 0.0

    # Build term frequency for sentence
    tf = Counter(sentence_tokens)
    max_tf = max(tf.values()) if tf else 1

    score = 0.0
    query_set = set(query_tokens)
    for token in query_set:
        if token in tf:
            # Normalized TF
            tf_val = tf[token] / max_tf
            # IDF with smoothing
            df = doc_freqs.get(token, 0)
            idf = math.log((num_docs + 1) / (df + 1)) + 1
            score += tf_val * idf

    # Normalize by query length to avoid bias toward long queries
    return score / len(query_set) if query_set else 0.0


def _score_snippets(query: str, sources: list[dict]) -> list[dict]:
    """Score each source snippet by TF-IDF relevance to query."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    # Build document frequency across all snippets
    all_snippets: list[str] = []
    doc_freqs: Counter = Counter()

    for src in sources:
        snippet = src.get("snippet") or ""
        if snippet:
            all_snippets.append(snippet)
            unique_tokens = set(_tokenize(snippet))
            for token in unique_tokens:
                doc_freqs[token] += 1

    num_docs = max(len(all_snippets), 1)

    # Score each source
    scored: list[dict] = []
    for i, src in enumerate(sources):
        snippet = src.get("snippet") or ""
        if not snippet:
            continue

        sentences = _split_sentences(snippet)
        for sentence in sentences:
            sent_tokens = _tokenize(sentence)
            tfidf = _tfidf_score(query_tokens, sent_tokens, doc_freqs, num_docs)
            # Boost by source score (truth filter)
            src_score = src.get("score", 0.5)
            combined = tfidf * (0.7 + 0.3 * src_score)

            if combined > 0:
                scored.append({
                    "sentence": sentence,
                    "score": combined,
                    "source_idx": i,
                    "source_title": src.get("title") or src.get("url") or f"Source {i + 1}",
                    "source_url": src.get("url", ""),
                })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def _extract_key_sentences(scored: list[dict], max_sentences: int = 8) -> list[dict]:
    """Extract top sentences, deduplicating near-identical ones."""
    if not scored:
        return []

    selected: list[dict] = []
    seen_fingerprints: set[str] = set()

    for item in scored:
        # Deduplicate: first 50 chars as fingerprint
        fp = item["sentence"][:50].lower()
        if fp in seen_fingerprints:
            continue
        seen_fingerprints.add(fp)
        selected.append(item)
        if len(selected) >= max_sentences:
            break

    return selected


def _is_on_topic(sentence: str, query: str) -> bool:
    """Check if sentence is relevant to the query topic."""
    stop = {"what", "is", "the", "a", "an", "how", "why", "when", "where",
            "who", "does", "do", "are", "was", "were", "of", "in", "on",
            "at", "to", "for", "with", "by", "and", "or", "but", "it"}
    q_words = set(re.sub(r"[^\w\s]", "", query.lower()).split()) - stop
    s_words = set(re.sub(r"[^\w\s]", "", sentence.lower()).split())
    if not q_words:
        return True
    overlap = len(q_words & s_words) / len(q_words)
    if overlap < 0.2:
        return False
    # Domain drift check
    drift_words = {"mars", "venus", "jupiter", "saturn", "nasa", "spacex", "tesla",
                   "google", "apple", "microsoft", "amazon", "facebook"}
    if any(w in sentence.lower() for w in drift_words) and not any(w in query.lower() for w in drift_words):
        return False
    return True


def _synthesize_answer(query: str, evidence: list[dict], sources: list[dict]) -> str:
    """Build a coherent answer paragraph from evidence sentences with citations."""
    if not evidence:
        # Fallback: use source snippets directly when TF-IDF found nothing
        snippets = []
        for i, src in enumerate(sources[:5]):
            snippet = src.get("snippet", "").strip()
            if snippet and len(snippet) > 30:
                snippets.append({
                    "sentence": snippet[:400],
                    "source_url": src.get("url", ""),
                })
        if snippets:
            evidence = snippets
        elif sources:
            titles = [s.get("title") or s.get("url") or "" for s in sources[:3] if s]
            if titles:
                return f"I found {len(sources)} source(s) on this topic ({', '.join(titles[:3])}), but could not extract specific evidence to answer your question."
            return "No relevant evidence was found in the retrieved sources."
        else:
            return "No relevant evidence was found in the retrieved sources."

    # Filter off-topic evidence before synthesis
    on_topic = [e for e in evidence if _is_on_topic(e["sentence"], query)]
    if on_topic:
        evidence = on_topic[:6]  # Max 6 on-topic pieces
    else:
        evidence = evidence[:4]  # If nothing matches, keep top 4 anyway

    parts: list[str] = []

    # Map source indices to citation numbers
    source_urls: dict[str, int] = {}
    citation_counter = 0
    for item in evidence:
        url = item["source_url"]
        if url and url not in source_urls:
            citation_counter += 1
            source_urls[url] = citation_counter

    # Lead with the strongest evidence
    lead = evidence[0]
    lead_citation = _format_citation(lead, source_urls)
    parts.append(f"{lead['sentence']} {lead_citation}")

    # Add supporting evidence
    transitions = ["Additionally", "Furthermore", "Moreover", "Also"]
    for i, item in enumerate(evidence[1:], 1):
        citation = _format_citation(item, source_urls)
        sent = item['sentence']
        # Don't lowercase sentences starting with proper nouns (capitalized multi-word)
        if i <= len(transitions):
            # Keep original case for proper nouns
            if sent[0].isupper() and len(sent) > 1 and not sent[0:2].isupper():
                parts.append(f"{transitions[i - 1]}, {sent[0].lower()}{sent[1:]} {citation}")
            else:
                parts.append(f"{transitions[i - 1]}, {sent} {citation}")
        else:
            parts.append(f"{sent} {citation}")

    return " ".join(parts)


def _format_citation(item: dict, source_urls: dict[str, int]) -> str:
    """Format a citation reference for a piece of evidence."""
    url = item.get("source_url", "")
    if url and url in source_urls:
        return f"[{source_urls[url]}]"
    return ""


def _compute_confidence(sources: list[dict], evidence: list[dict]) -> str:
    """Derive confidence from source quality and evidence coverage."""
    if not sources:
        return "UNKNOWN"

    source_count = len(sources)
    evidence_count = len(evidence)

    # Average source score
    scores = [s.get("score", 0) for s in sources if s.get("score")]
    avg_score = sum(scores) / max(len(scores), 1)

    # Composite confidence
    composite = 0.0
    # Source count factor (diminishing returns)
    composite += min(source_count / 5.0, 1.0) * 0.3
    # Evidence quality factor
    composite += min(evidence_count / 4.0, 1.0) * 0.3
    # Source relevance factor
    composite += avg_score * 0.4

    if composite >= 0.75:
        return "CERTAIN"
    if composite >= 0.55:
        return "PROBABLE"
    if composite >= 0.35:
        return "DEBATED"
    if evidence_count > 0:
        return "LOW"
    return "UNKNOWN"


def _identify_gaps(query: str, sources: list[dict], evidence: list[dict]) -> list[str]:
    """Identify query terms not covered by evidence."""
    gaps: list[str] = []

    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return gaps

    # Collect tokens from evidence
    evidence_text = " ".join(e["sentence"] for e in evidence)
    evidence_tokens = set(_tokenize(evidence_text))

    # Find uncovered query terms
    uncovered = query_tokens - evidence_tokens
    if uncovered and len(uncovered) > len(query_tokens) * 0.5:
        gaps.append(f"Key terms not addressed: {', '.join(sorted(uncovered)[:5])}")

    if len(sources) < 3:
        gaps.append("Limited sources retrieved; answer may be incomplete.")

    if not evidence:
        gaps.append("No specific evidence could be extracted from sources.")

    return gaps


# ── Main entry point ─────────────────────────────────────────────

def _confidence_from_scores(sources: list[dict]) -> str:
    if not sources:
        return "UNKNOWN"
    scores = [s.get("score") or 0 for s in sources]
    avg = sum(scores) / max(len(scores), 1)
    if avg >= 0.75:
        return "CERTAIN"
    if avg >= 0.55:
        return "PROBABLE"
    if avg >= 0.35:
        return "DEBATED"
    return "UNKNOWN"


def reason(
    sources: list[dict],
    query: str | None = None,
    constitution: str | None = None,
    cognitive_layer: str | None = None,
) -> dict:
    """Reason across sources to produce a well-cited answer using internal NLP.

    Uses TF-IDF scoring to find relevant sentences, then synthesizes
    a coherent answer with citations. No external API required.
    """
    if not sources:
        return {
            "draft": "No sources found for this query.",
            "confidence": "UNKNOWN",
            "citations": [],
            "gaps": ["No sources available to answer this query."],
        }

    if not query:
        # Fallback for legacy callers without query
        top_titles = [s.get("title") or s.get("url") for s in sources[:3]]
        summary = ", ".join([t for t in top_titles if t])
        return {
            "draft": f"Based on sources: {summary}.",
            "confidence": _confidence_from_scores(sources),
            "citations": [s.get("url") for s in sources if s.get("url")][:5],
            "gaps": [],
        }

    # Step 1: Score snippets by TF-IDF relevance to query
    scored = _score_snippets(query, sources)

    # Step 2: Extract top evidence sentences
    evidence = _extract_key_sentences(scored, max_sentences=8)

    # Step 2b: Fallback — if TF-IDF found nothing, use source snippets directly
    if not evidence:
        for i, src in enumerate(sources[:5]):
            snippet = src.get("snippet") or ""
            if snippet:
                sentences = _split_sentences(snippet)
                if sentences:
                    evidence.append({
                        "sentence": sentences[0],
                        "score": src.get("score", 0.5),
                        "source_idx": i,
                        "source_title": src.get("title") or src.get("url") or f"Source {i + 1}",
                        "source_url": src.get("url", ""),
                    })
        # If still no evidence, try raw snippets
        if not evidence:
            for i, src in enumerate(sources[:3]):
                snippet = src.get("snippet") or ""
                if snippet and len(snippet) > 20:
                    evidence.append({
                        "sentence": snippet[:300],
                        "score": src.get("score", 0.5),
                        "source_idx": i,
                        "source_title": src.get("title") or src.get("url") or f"Source {i + 1}",
                        "source_url": src.get("url", ""),
                    })

    # Step 3: Synthesize answer from evidence with citations
    draft = _synthesize_answer(query, evidence, sources)

    # Step 4: Clean HTML entities from draft
    import html as _html
    draft = _html.unescape(draft)

    # Step 5: Compute confidence
    confidence = _compute_confidence(sources, evidence)

    # Step 6: High-scrutiny topic downgrade
    if constitution and query and any(
        word in query.lower()
        for word in ["medical", "doctor", "health", "treatment", "law", "legal", "financial"]
    ):
        if confidence == "CERTAIN":
            confidence = "PROBABLE"

    # Step 7: Identify gaps
    gaps = _identify_gaps(query, sources, evidence)

    # Step 7b: High-scrutiny gap flag
    if constitution and query and any(
        word in query.lower()
        for word in ["medical", "doctor", "health", "treatment", "law", "legal", "financial"]
    ):
        gaps.append("Living constitution flagged this topic as high-scrutiny.")

    # Step 8: Build citation URLs
    citations = []
    seen_urls: set[str] = set()
    for e in evidence:
        url = e.get("source_url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            citations.append(url)

    return {
        "draft": draft,
        "confidence": confidence,
        "citations": citations,
        "gaps": gaps,
        "cognitive_layer": cognitive_layer,
    }
