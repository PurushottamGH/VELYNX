from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


_RULES_PATH = Path('data/living_constitution.json')

_RISKY_DOMAINS = {'medical', 'legal', 'safety'}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> dict:
    if _RULES_PATH.exists():
        return json.loads(_RULES_PATH.read_text(encoding='utf-8'))
    return {'active': [], 'pending': []}


def _save_state(state: dict) -> None:
    _RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    _RULES_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding='utf-8')


def list_rules(include_pending: bool = True) -> list[dict]:
    state = _load_state()
    rules = list(state.get('active', []))
    if include_pending:
        rules.extend(state.get('pending', []))
    return rules


def should_auto_apply(rule: dict) -> bool:
    if rule.get('risk') == 'high':
        return False
    domains = {domain.lower() for domain in rule.get('domains', [])}
    if domains & _RISKY_DOMAINS:
        return False
    return True


def record_rule(rule: dict) -> dict:
    state = _load_state()
    requested_status = str(rule.get('status') or '').lower()
    status = requested_status if requested_status in {'draft', 'pending', 'active', 'archived'} else None
    if status is None:
        status = 'active' if should_auto_apply(rule) else 'pending'
    rule = {
        'id': rule.get('id') or f"rule-{len(state.get('active', [])) + len(state.get('pending', [])) + 1}",
        'title': rule.get('title', 'Unnamed rule'),
        'body': rule.get('body', ''),
        'domains': rule.get('domains', []),
        'risk': rule.get('risk', 'low'),
        'source': rule.get('source', 'feedback'),
        'status': status,
        'created_at': rule.get('created_at', _now()),
        'failure_mode': rule.get('failure_mode'),
        'cognitive_layer': rule.get('cognitive_layer', 'general'),
    }
    bucket = 'active' if rule['status'] == 'active' else 'pending'
    existing = state.get(bucket, [])
    existing = [item for item in existing if item.get('id') != rule['id']]
    existing.append(rule)
    state[bucket] = existing
    _save_state(state)
    return rule


def promote_rule(rule_id: str) -> dict | None:
    state = _load_state()
    pending = state.get('pending', [])
    for index, rule in enumerate(pending):
        if rule.get('id') == rule_id:
            promoted = {**rule, 'status': 'active', 'promoted_at': _now()}
            state['pending'] = pending[:index] + pending[index + 1 :]
            state.setdefault('active', []).append(promoted)
            _save_state(state)
            return promoted
    return None


def render_rules(include_pending: bool = True, cognitive_layer: str | None = None, statuses: set[str] | None = None) -> str:
    rules = list_rules(include_pending=include_pending)
    if cognitive_layer:
        rules = [rule for rule in rules if str(rule.get('cognitive_layer', 'general')) == cognitive_layer]
    if statuses:
        rules = [rule for rule in rules if str(rule.get('status', 'active')).lower() in statuses]
    if not rules:
        return ''
    lines: list[str] = []
    for rule in rules:
        lines.append(f"- [{rule.get('status', 'active').upper()}] {rule.get('title', 'Unnamed rule')}: {rule.get('body', '')}")
    return '\n'.join(lines)
