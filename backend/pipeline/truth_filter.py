from __future__ import annotations

import re

from backend.learning.source_trust import load_trust_scores

try:
    from datasketch import MinHash, MinHashLSH
except ImportError:  # pragma: no cover - optional dependency
    MinHash = None
    MinHashLSH = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def _dedupe_sources(sources: list[dict]) -> list[dict]:
    seen_urls: set[str] = set()
    deduped: list[dict] = []

    for item in sources:
        url = item.get("url") or ""
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
        deduped.append(item)

    if MinHash is None or MinHashLSH is None:
        return deduped

    lsh = MinHashLSH(threshold=0.85, num_perm=64)
    result: list[dict] = []
    for idx, item in enumerate(deduped):
        snippet = item.get("snippet") or ""
        tokens = _tokenize(snippet)[:200]
        if not tokens:
            result.append(item)
            continue

        mh = MinHash(num_perm=64)
        for token in tokens:
            mh.update(token.encode("utf-8"))

        matches = lsh.query(mh)
        if matches:
            continue

        lsh.insert(str(idx), mh)
        result.append(item)

    return result


def _score_item(item: dict, trust_scores: dict, query_tokens: set[str] | None = None) -> float:
    score = 0.2
    source_type = item.get("source")
    if source_type == "wikipedia":
        score += 0.35
    if source_type == "searxng":
        score += 0.15
    if source_type == "arxiv":
        score += 0.3
    if source_type == "brave":
        score += 0.1
    if source_type == "tavily":
        score += 0.12

    snippet = item.get("snippet") or ""
    if snippet:
        score += min(len(snippet) / 600, 0.25)

    title = item.get("title") or ""
    if title:
        score += 0.05

    url = item.get("url") or ""
    if url.startswith("https://"):
        score += 0.05

    trust_bonus = float(trust_scores.get(source_type or "", 0.0))
    score += trust_bonus

    # Query-aware relevance bonus
    if query_tokens:
        text_tokens = set(_tokenize(f"{title} {snippet}"))
        if text_tokens:
            overlap = len(query_tokens & text_tokens)
            overlap_ratio = overlap / len(query_tokens) if query_tokens else 0
            score += overlap_ratio * 0.35
            if overlap == 0:
                score -= 0.15  # penalty for irrelevant sources

    return round(min(max(score, 0.0), 1.0), 3)


def _consensus_from_scores(scored: list[dict]) -> float:
    if not scored:
        return 0.0
    scores = [item.get("score") or 0 for item in scored]
    avg = sum(scores) / len(scores)
    return round(avg * 100, 1)


def score_sources(sources: list[dict], query: str | None = None) -> dict:
    """Score and filter sources by credibility (heuristic rubric + dedupe)."""
    sources = _dedupe_sources(sources)
    trust_scores = load_trust_scores()
    query_tokens = set(_tokenize(query)) if query else None
    scored: list[dict] = []
    for item in sources:
        score = _score_item(item, trust_scores, query_tokens=query_tokens)
        scored.append({**item, "score": score})

    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    top = scored[:8]
    report = {
        "total_sources": len(sources),
        "kept_sources": len(top),
        "consensus": _consensus_from_scores(top),
        "trust_scores": trust_scores,
    }
    return {"sources": top, "report": report}
