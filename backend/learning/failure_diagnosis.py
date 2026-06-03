from __future__ import annotations


MEDICAL_KEYWORDS = {'medical', 'doctor', 'diagnosis', 'treatment', 'drug', 'health', 'symptom'}
LEGAL_KEYWORDS = {'legal', 'law', 'court', 'attorney', 'contract', 'compliance'}
RECENCY_KEYWORDS = {'recent', 'latest', 'current', 'updated', 'today', 'year'}
COMPLEXITY_KEYWORDS = {'math', 'maths', 'algebra', 'calculus', 'proof', 'code', 'coding', 'algorithm'}


def _domain_from_query(query: str) -> str:
    text = query.lower()
    if any(word in text for word in MEDICAL_KEYWORDS):
        return 'medical'
    if any(word in text for word in LEGAL_KEYWORDS):
        return 'legal'
    if any(word in text for word in COMPLEXITY_KEYWORDS):
        return 'technical'
    return 'general'


def _source_names(meta: dict) -> list[str]:
    names: list[str] = []
    for item in meta.get('sources') or []:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            source = item.get('source') or item.get('domain')
            if source:
                names.append(str(source))
    return names


def diagnose_failure(query: str, rating: int, meta: dict | None = None) -> dict:
    meta = meta or {}
    sources = meta.get('sources') or []
    source_names = _source_names(meta)
    confidence = str(meta.get('confidence', '')).upper()
    contradictions = meta.get('contradictions') or []
    gaps = meta.get('gaps') or []
    answer = str(meta.get('answer') or '').strip()
    source_count = int(meta.get('source_count') or len(sources))
    gap_count = int(meta.get('gap_count') or len(gaps))
    contradiction_count = int(meta.get('contradiction_count') or len(contradictions))
    domains = meta.get('source_domains') or []
    domains = [str(domain) for domain in domains if domain]
    domain = _domain_from_query(query)

    if any(source == 'wikipedia' for source in source_names) and any(word in query.lower() for word in RECENCY_KEYWORDS):
        return {
            'mode': 'stale_source',
            'domain': domain,
            'risk': 'low',
            'reason': 'A likely stale source was used for a recency-sensitive query.',
            'signals': {'source_count': source_count, 'domains': domains, 'answer_present': bool(answer)},
        }

    if domain == 'medical':
        return {
            'mode': 'medical_claim',
            'domain': 'medical',
            'risk': 'high',
            'reason': 'Medical answers need higher-confidence sourcing and explicit caution.',
            'signals': {'source_count': source_count, 'domains': domains, 'answer_present': bool(answer)},
        }

    if domain == 'legal':
        return {
            'mode': 'legal_claim',
            'domain': 'legal',
            'risk': 'high',
            'reason': 'Legal answers need expert-grade sourcing and careful phrasing.',
            'signals': {'source_count': source_count, 'domains': domains, 'answer_present': bool(answer)},
        }

    if contradiction_count >= 2:
        return {
            'mode': 'contradiction_heavy',
            'domain': domain,
            'risk': 'medium',
            'reason': 'Multiple contradictions were surfaced and should be resolved before confidence increases.',
            'signals': {'source_count': source_count, 'domains': domains, 'contradiction_count': contradiction_count},
        }

    if gap_count >= 2 or (gap_count and source_count < 3):
        return {
            'mode': 'missing_evidence',
            'domain': domain,
            'risk': 'low',
            'reason': 'Evidence coverage was thin, so the answer should stay tentative.',
            'signals': {'source_count': source_count, 'domains': domains, 'gap_count': gap_count},
        }

    if confidence in {'UNKNOWN', 'DEBATED'} or rating < 0:
        return {
            'mode': 'low_confidence',
            'domain': domain,
            'risk': 'low',
            'reason': 'The system lacked enough confidence to treat the answer as stable.',
            'signals': {'source_count': source_count, 'domains': domains, 'confidence': confidence},
        }

    return {
        'mode': 'unclear_failure',
        'domain': domain,
        'risk': 'low',
        'reason': 'A correction arrived without a strong failure signature, so the lesson is kept broad.',
        'signals': {'source_count': source_count, 'domains': domains, 'confidence': confidence},
    }
