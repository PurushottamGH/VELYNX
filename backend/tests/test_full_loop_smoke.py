import asyncio
import sys
from pathlib import Path

import httpx

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.app.main import app  # noqa: E402
from backend.learning import feedback_loop, gap_tracker, permanence, source_trust  # noqa: E402
from backend.learning import living_constitution  # noqa: E402
from backend.pipeline import retrieval_mesh  # noqa: E402


def test_query_to_feedback_smoke(tmp_path, monkeypatch) -> None:
    async def fake_retrieve_all(_query: str) -> list[dict]:
        return [
            {
                'source': 'wikipedia',
                'title': 'Test Page',
                'snippet': 'Test snippet',
                'url': 'https://example.com/test',
            }
        ]

    monkeypatch.setattr(retrieval_mesh, 'retrieve_all', fake_retrieve_all)
    monkeypatch.setattr(source_trust, '_TRUST_PATH', tmp_path / 'trust.json', raising=False)
    monkeypatch.setattr(feedback_loop, '_DATA_PATH', tmp_path / 'feedback.jsonl', raising=False)
    monkeypatch.setattr(gap_tracker, '_GAPS_PATH', tmp_path / 'gaps.jsonl', raising=False)
    monkeypatch.setattr(living_constitution, '_RULES_PATH', tmp_path / 'living_constitution.json', raising=False)
    permanence._DEFAULT_PERMANENCE = permanence.PermanenceLayer(path=tmp_path / 'permanence.json')

    async def _exercise_loop() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url='http://testserver') as client:
            query_response = await client.post('/query', json={'text': 'Why is the sky blue?'})
            feedback_payload = {
                'query': 'Why is the sky blue?',
                'rating': -1,
                'meta': {
                    'answer': query_response.json()['answer'],
                    'confidence': query_response.json()['confidence'],
                    'source_count': len(query_response.json()['sources']),
                    'source_domains': ['wikipedia'],
                    'contradiction_count': len(query_response.json()['contradictions']),
                    'gap_count': len(query_response.json()['gaps']),
                    'sources': [
                        {
                            'source': item['source'],
                            'url': item['url'],
                            'score': item.get('score'),
                        }
                        for item in query_response.json()['sources']
                    ],
                },
            }
            feedback_response = await client.post('/feedback', json=feedback_payload)
            return query_response, feedback_response

    query_response, feedback_response = asyncio.run(_exercise_loop())

    assert query_response.status_code == 200
    assert query_response.json()['answer']
    assert feedback_response.status_code == 200
    learning = feedback_response.json()['learning']
    assert learning['failure']['mode'] in {'low_confidence', 'missing_evidence', 'unclear_failure', 'stale_source'}
    assert learning['rule']['title']
    assert learning['learning_context']['answer']
    assert (tmp_path / 'living_constitution.json').exists()