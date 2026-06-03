from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


_PERSISTENCE_PATH = Path('data/permanence.json')


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> dict:
    if _PERSISTENCE_PATH.exists():
        return json.loads(_PERSISTENCE_PATH.read_text(encoding='utf-8'))
    return {'beliefs': {}, 'strategy_scores': {}, 'fact_history': {}}


def _save_state(state: dict) -> None:
    _PERSISTENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _PERSISTENCE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding='utf-8')


class PermanenceLayer:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _PERSISTENCE_PATH
        self._state = _load_state() if self.path == _PERSISTENCE_PATH else self._load_custom_state()

    def _load_custom_state(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding='utf-8'))
        return {'beliefs': {}, 'strategy_scores': {}, 'fact_history': {}}

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._state, indent=2, sort_keys=True), encoding='utf-8')

    @staticmethod
    def _hash_fact(fact: str) -> str:
        return hashlib.sha1(fact.strip().lower().encode('utf-8')).hexdigest()

    def confidence(self, fact: str, layer: str | None = None) -> float:
        key = self._hash_fact(_layer_key(layer, fact))
        entry = self._state['beliefs'].get(key)
        if not entry:
            return 0.5
        return float(entry.get('score', 0.5))

    def reinforce(self, fact: str, source: str | None = None, delta: float = 0.05, layer: str | None = None) -> float:
        return self._adjust_fact(fact, source=source, delta=abs(delta), layer=layer)

    def weaken(self, fact: str, source: str | None = None, delta: float = 0.1, layer: str | None = None) -> float:
        return self._adjust_fact(fact, source=source, delta=-abs(delta), layer=layer)

    def record_strategy(self, query_type: str, strategy: str, delta: float, layer: str | None = None) -> float:
        query_key = _layer_key(layer, query_type or 'general')
        query_bucket = self._state['strategy_scores'].setdefault(query_key, {})
        current = float(query_bucket.get(strategy, 0.0))
        query_bucket[strategy] = round(max(0.0, min(1.0, current + delta)), 3)
        self._persist()
        return query_bucket[strategy]

    def best_strategy(self, query_type: str, layer: str | None = None) -> str | None:
        query_key = _layer_key(layer, query_type or 'general')
        query_bucket = self._state['strategy_scores'].get(query_key, {})
        if not query_bucket:
            return None
        return max(query_bucket.items(), key=lambda item: item[1])[0]

    def _adjust_fact(self, fact: str, source: str | None, delta: float, layer: str | None = None) -> float:
        key = self._hash_fact(_layer_key(layer, fact))
        current = float(self._state['beliefs'].get(key, {}).get('score', 0.5))
        score = round(max(0.0, min(1.0, current + delta)), 3)
        self._state['beliefs'][key] = {
            'fact': fact,
            'layer': layer,
            'score': score,
            'source': source,
            'updated_at': _now(),
        }
        history = self._state['fact_history'].setdefault(key, [])
        history.append({'fact': fact, 'layer': layer, 'score': score, 'source': source, 'updated_at': _now()})
        self._persist()
        return score


def _layer_key(layer: str | None, key: str) -> str:
    if not layer:
        return key
    return f"{layer}::{key}"


_DEFAULT_PERMANENCE = PermanenceLayer()


def reinforce_fact(fact: str, source: str | None = None, delta: float = 0.05, layer: str | None = None) -> float:
    return _DEFAULT_PERMANENCE.reinforce(fact, source=source, delta=delta, layer=layer)


def weaken_fact(fact: str, source: str | None = None, delta: float = 0.1, layer: str | None = None) -> float:
    return _DEFAULT_PERMANENCE.weaken(fact, source=source, delta=delta, layer=layer)


def record_strategy(query_type: str, strategy: str, delta: float, layer: str | None = None) -> float:
    return _DEFAULT_PERMANENCE.record_strategy(query_type, strategy, delta, layer=layer)


def best_strategy(query_type: str, layer: str | None = None) -> str | None:
    return _DEFAULT_PERMANENCE.best_strategy(query_type, layer=layer)


def confidence(fact: str, layer: str | None = None) -> float:
    return _DEFAULT_PERMANENCE.confidence(fact, layer=layer)
