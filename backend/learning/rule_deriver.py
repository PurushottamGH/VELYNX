from __future__ import annotations

from hashlib import sha1


def _rule_id(failure: dict, query: str) -> str:
    seed = f"{failure.get('mode', 'unknown')}::{query.lower().strip()}"
    return sha1(seed.encode('utf-8')).hexdigest()[:12]


def derive_rule_from_failure(failure: dict, query: str, meta: dict | None = None) -> dict:
    meta = meta or {}
    mode = failure.get('mode', 'unclear_failure')
    domain = failure.get('domain', 'general')
    risk = failure.get('risk', 'low')
    cognitive_layer = meta.get('cognitive_layer') or meta.get('layer')
    signals = failure.get('signals') or {}
    reason = failure.get('reason') or ''
    source_count = int(signals.get('source_count') or 0)
    gap_count = int(signals.get('gap_count') or 0)
    contradiction_count = int(signals.get('contradiction_count') or 0)

    templates = {
        'stale_source': (
            'Prefer recent corroboration',
            'If a likely stale source is used for a recency-sensitive query, require newer corroboration before answering confidently.',
        ),
        'medical_claim': (
            'Medical claims require higher scrutiny',
            'Treat medical answers as high-risk and prefer peer-reviewed or consensus-backed sources before asserting certainty.',
        ),
        'legal_claim': (
            'Legal claims require expert sources',
            'Treat legal answers as high-risk and prefer primary or expert legal sources before asserting certainty.',
        ),
        'contradiction_heavy': (
            'Resolve contradictions before confidence',
            'When multiple contradictions appear, slow down, summarize both sides, and avoid a confident answer until evidence converges.',
        ),
        'missing_evidence': (
            'Insufficient evidence stays tentative',
            'When evidence is sparse, surface uncertainty explicitly and ask for more context or better sources.',
        ),
        'low_confidence': (
            'Low confidence should stay bounded',
            'Do not escalate a tentative answer to certainty without supporting evidence.',
        ),
    }

    title, body = templates.get(mode, templates['low_confidence'])
    if source_count:
        body = f'{body} This correction was based on {source_count} source(s).'
    if gap_count:
        body = f'{body} The answer had {gap_count} gap(s) in evidence coverage.'
    if contradiction_count:
        body = f'{body} The answer surfaced {contradiction_count} contradiction(s).'
    if reason:
        body = f'{body} Reason: {reason}'

    return {
        'id': _rule_id(failure, query),
        'title': title,
        'body': body,
        'domains': [domain],
        'risk': risk,
        'failure_mode': mode,
        'source': 'feedback',
        'query': query,
        'signals': signals,
        'metadata': meta,
        'cognitive_layer': cognitive_layer or 'general',
    }
