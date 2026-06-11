"""
VELYNX Voice Engine — Symbolic NLG compiler.
Translates graph paths (soul → bridge → domain) into direct natural speech.
No LLM. No external API. Pure template compilation.
"""
from __future__ import annotations

import random
from typing import Any

DISSONANCE_TEMPLATES: list[str] = [
    "Cognitive dissonance detected. You are holding {concept_a} and {concept_b} simultaneously. These are structurally opposed.",
    "Graph collision: {concept_a} actively starves {concept_b}. Your current state is contradictory.",
    "Dissonance alert: {concept_a} and {concept_b} cannot both be true in the same system. The graph registers a structural conflict.",
    "The mind holds {concept_a} and {concept_b} at once. These states pull in opposite directions — one negates the other.",
    "Internal contradiction: {concept_a} requires the absence of {concept_b}. You are running incompatible patterns.",
]

EDGE_TEMPLATES: dict[str, list[str]] = {
    "requires": [
        "{source} demands {target}.",
        "{source} forces the extraction of {target}.",
        "{source} cannot exist without {target}.",
        "{target} is a prerequisite for {source}.",
        "{source} pulls {target} into existence.",
    ],
    "produces": [
        "{source} yields {target}.",
        "The direct output of {source} is {target}.",
        "{source} generates {target}.",
        "{target} crystallizes from {source}.",
        "{source} resolves into {target}.",
    ],
    "contrasts": [
        "{source} stands against {target}.",
        "Where {source} rules, {target} cannot exist.",
        "{source} and {target} pull in opposite directions.",
        "{source} negates {target}.",
        "The presence of {source} undermines {target}.",
    ],
    "catalyzes": [
        "{source} accelerates {target}.",
        "{source} ignites {target}.",
        "{source} speeds the arrival of {target}.",
        "Under {source}, {target} intensifies.",
        "{source} drives rapid change in {target}.",
    ],
    "enables": [
        "{source} unlocks {target}.",
        "{source} makes {target} possible.",
        "{target} depends on {source}.",
        "{source} clears the path for {target}.",
    ],
    "opposes": [
        "{source} fights {target}.",
        "{source} blocks {target}.",
        "{target} erodes under {source}.",
        "{source} is the inverse of {target}.",
    ],
    "reduces": [
        "{source} diminishes {target}.",
        "{source} erodes {target} over time.",
        "{target} decays under {source}.",
        "{source} drains {target}.",
        "{source} subtracts from {target}.",
    ],
}

BRIDGE_TEMPLATES: dict[str, list[str]] = {
    "shame": [
        "The experience of {soul} maps directly onto {domain} in systems.",
        "In code, {soul} manifests as {domain}.",
        "{soul} in the mind is {domain} in the machine.",
    ],
    "resilience": [
        "What the mind calls {soul}, the system implements as {domain}.",
        "{soul} translates to {domain} at the infrastructure level.",
        "The pattern of {soul} is mirrored in {domain}.",
    ],
    "grief": [
        "Systems carry {soul} as {domain} — accumulated weight.",
        "{soul} in engineering terms is {domain}.",
        "{domain} is the structural echo of {soul}.",
    ],
    "loss": [
        "{soul} in a living system becomes {domain} in a codebase.",
        "The {soul} pattern is {domain} when viewed through infrastructure.",
    ],
    "depression": [
        "A system in {soul} state exhibits {domain}.",
        "{soul} at the cognitive level is {domain} at the architectural level.",
    ],
    "stagnation": [
        "{soul} in a system maps to {domain} — nothing moves.",
        "The {soul} pattern in cognition becomes {domain} in economics or physics.",
        "{soul} manifests as {domain}: the absence of flow.",
    ],
    "resistance": [
        "{soul} in a person is {domain} in a system — opposition to change.",
        "What feels like {soul} translates directly to {domain}.",
        "{domain} is the physical name for the emotional experience of {soul}.",
    ],
    "pain": [
        "What registers as {soul} in feeling registers as {domain} in operations.",
        "{domain} is the technical name for {soul}.",
    ],
    "trust": [
        "{soul} in a team looks like {domain} in a codebase.",
        "{domain} is {soul} formalized into process.",
    ],
    "identity": [
        "{soul} crisis in a person is {domain} crisis in a system.",
        "{domain} asks the same questions as {soul}: what stays true?",
    ],
    "anger": [
        "{soul} in the developer produces {domain} in the code.",
        "Unresolved {soul} accumulates as {domain}.",
    ],
    "hope": [
        "The mechanism of {soul} in operations is {domain}.",
        "{domain} is what {soul} looks like when it works.",
    ],
    "curiosity": [
        "{soul} drives the same cycle as {domain}.",
        "Inquiry is {soul}; its loop is {domain}.",
    ],
    "patience": [
        "What the mind experiences as {soul}, the process enforces as {domain}.",
        "{domain} is {soul} compiled into a workflow.",
    ],
    "forgiveness": [
        "{soul} in a codebase is {domain} — letting go of the past shape.",
        "The emotional act of {soul} has a technical equivalent: {domain}.",
    ],
    "regret": [
        "{soul} in architecture is {domain} — the cost of what was chosen.",
        "Every {domain} carries the signature of {soul}.",
    ],
    "understanding": [
        "Deep {soul} in a domain resolves to {domain}.",
        "{domain} is the formal version of {soul}.",
    ],
    "courage": [
        "{soul} in software engineering means {domain}.",
        "The emotional muscle of {soul} becomes the technical act of {domain}.",
    ],
    "planning": [
        "{soul} is the cognitive form of {domain}.",
        "What the mind plans, the system expresses as {domain}.",
    ],
}

DEFAULT_BRIDGE_TEMPLATE = "{soul} bridges to {domain}."


def _pick(templates: list[str]) -> str:
    return random.choice(templates)


def _capitalize_first(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def _render_edge(source: str, relation: str, target: str) -> str:
    key = relation.lower()
    if key not in EDGE_TEMPLATES:
        return f"{source} {relation} {target}."
    template = _pick(EDGE_TEMPLATES[key])
    return template.format(source=source.capitalize(), target=target)


def _render_bridge(soul: str, domain: str) -> str:
    key = soul.lower()
    templates = BRIDGE_TEMPLATES.get(key, [DEFAULT_BRIDGE_TEMPLATE])
    template = _pick(templates)
    return template.format(soul=soul.capitalize(), domain=domain)


def _build_soul_path_text(soul_result: dict) -> list[str]:
    lines: list[str] = []
    concepts = soul_result.get("concepts", [])
    if not concepts:
        return ["No emotional pattern detected."]
    arc = soul_result.get("arc", "")
    if arc:
        lines.append(_capitalize_first(arc) + ".")
    else:
        chain = " then ".join(c.capitalize() for c in concepts)
        lines.append(f"The path runs through {chain}.")
    return lines


def _build_bridge_text(bridge_connections: list[dict]) -> list[str]:
    if not bridge_connections:
        return []
    lines: list[str] = []
    seen = set()
    for bc in bridge_connections:
        key = (bc["soul"], bc["domain"])
        if key not in seen:
            seen.add(key)
            lines.append(_render_bridge(bc["soul"], bc["domain"]))
    return lines


def _build_domain_path_text(
    domain_concepts: list[str],
    domain_arc: str,
    kg: Any,
) -> list[str]:
    lines: list[str] = []
    if not domain_concepts:
        return lines
    if domain_arc:
        for segment in domain_arc.split("; "):
            segment = segment.strip()
            if not segment:
                continue
            parts = segment.split()
            if len(parts) >= 3:
                src = parts[0]
                rel = parts[1]
                tgt = " ".join(parts[2:])
                lines.append(_render_edge(src, rel, tgt))
            else:
                lines.append(_capitalize_first(segment) + ".")
    return lines


def _build_modifier(meta_packet: dict) -> str | None:
    meta = meta_packet.get("meta", {})
    confidence = meta.get("confidence", 0.0)
    gaps = meta_packet.get("gaps", [])
    if confidence < 0.6 or gaps:
        return "Systemic data thin. Hypothesizing:"
    if confidence < 0.75:
        return "Based on available patterns:"
    return None


def _build_dissonance_text(dissonance_list: list[dict]) -> list[str]:
    """Generate dissonance warning lines from detected dissonance pairs."""
    if not dissonance_list:
        return []
    lines: list[str] = []
    for d in dissonance_list:
        a = d["concept_a"].title()
        b = d["concept_b"].title()
        template = random.choice(DISSONANCE_TEMPLATES)
        lines.append(template.format(concept_a=a, concept_b=b))
    return lines


def compile_path_to_speech(
    cognitive_packet: dict,
    meta_packet: dict,
) -> str:
    soul_result = cognitive_packet.get("soul_result", {})
    bridge_connections = cognitive_packet.get("bridge_connections", [])
    domain_concepts = cognitive_packet.get("domain_concepts", [])
    domain_arc = cognitive_packet.get("domain_arc", "")
    dissonance = cognitive_packet.get("dissonance_detected")

    from knowledge.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()

    modifier = _build_modifier(meta_packet)

    soul_lines = _build_soul_path_text(soul_result)
    bridge_lines = _build_bridge_text(bridge_connections)
    domain_lines = _build_domain_path_text(domain_concepts, domain_arc, kg)
    dissonance_payload = dissonance if isinstance(dissonance, list) else ([dissonance] if dissonance else [])
    dissonance_lines = _build_dissonance_text(dissonance_payload)

    all_lines: list[str] = []
    all_lines.extend(dissonance_lines)
    if modifier:
        all_lines.append(modifier)
    all_lines.extend(soul_lines)
    all_lines.extend(bridge_lines)
    all_lines.extend(domain_lines)

    return " ".join(all_lines)
