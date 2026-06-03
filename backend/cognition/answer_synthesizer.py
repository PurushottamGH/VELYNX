"""
VELYNX Answer Synthesizer v2
=============================
Takes multiple evidence sources (KG triples, vector results, reasoning chain)
and synthesizes ONE high-quality answer with an honest confidence score.
"""

import json
import os
from dataclasses import dataclass, field
from groq import Groq as _Groq

_groq = _Groq(api_key=os.environ.get("GROQ_API_KEY", ""))


@dataclass
class SynthesisResult:
    text: str
    confidence: float
    sources: list[str] = field(default_factory=list)
    reasoning_used: bool = False
    why: str = ""
    how: str = ""


class AnswerSynthesizer:

    def __init__(self, kg):
        self.kg = kg

    async def synthesize(self, query: str, reasoning_chain, vec_results: list) -> SynthesisResult:
        """
        Build the best possible answer from:
        - reasoning chain steps
        - vector search hits
        - KG understanding nodes
        """

        # Gather all evidence
        evidence_parts = []

        if reasoning_chain and reasoning_chain.steps:
            chain_text = "\n".join(f"  [{i+1}] {s}" for i, s in enumerate(reasoning_chain.steps))
            evidence_parts.append(f"REASONING CHAIN:\n{chain_text}")

        if vec_results:
            vec_text = "\n".join(
                f"  [{r.get('source','unknown')}] {r.get('text','')[:200]}"
                for r in vec_results[:4]
            )
            evidence_parts.append(f"VECTOR MEMORY:\n{vec_text}")

        # Get any stored understanding
        understanding = await self.kg.get_understanding(query)
        if understanding:
            evidence_parts.append(f"STORED UNDERSTANDING:\n{understanding[:500]}")

        if not evidence_parts:
            return SynthesisResult(
                text="I don't have enough information to answer this confidently.",
                confidence=0.2,
            )

        evidence_block = "\n\n".join(evidence_parts)

        prompt = f"""You are VELYNX's answer synthesizer. Produce the best answer to this query.

QUERY: {query}

EVIDENCE:
{evidence_block}

Rules:
1. Answer the query directly and precisely.
2. Use only facts supported by the evidence.
3. If the evidence is incomplete, say so honestly.
4. Include a WHY and HOW if the query asks for explanation.
5. At the end, on a new line, write: CONFIDENCE: <number 0.0 to 1.0>

Format your response:
<answer text>

CONFIDENCE: 0.XX"""

        try:
            resp = _groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800,
            )
            raw = resp.choices[0].message.content.strip()

            # Parse confidence
            confidence = 0.5
            text = raw
            if "CONFIDENCE:" in raw:
                parts = raw.rsplit("CONFIDENCE:", 1)
                text = parts[0].strip()
                try:
                    confidence = float(parts[1].strip())
                    confidence = max(0.0, min(1.0, confidence))
                except ValueError:
                    pass

            sources = [r.get("source", "") for r in vec_results if r.get("source")]

            return SynthesisResult(
                text=text,
                confidence=confidence,
                sources=sources,
                reasoning_used=bool(reasoning_chain and reasoning_chain.steps),
            )

        except Exception as e:
            return SynthesisResult(
                text=f"Synthesis error: {e}",
                confidence=0.1,
            )