from dataclasses import dataclass
from typing import List, Optional
import hashlib
import json

@dataclass
class CandidateBelief:
    belief_text: str
    belief_hash: str
    support_count: int
    belief_confidence: float
    mean_effect: float
    promotion_score: float
    promoted: bool
    reason: str = ""

    @staticmethod
    def from_row(row: tuple) -> 'CandidateBelief':
        return CandidateBelief(
            belief_text=row[0],
            belief_hash=row[1],
            support_count=row[2],
            belief_confidence=row[3],
            mean_effect=row[4],
            promotion_score=row[5],
            promoted=bool(row[6]),
            reason=row[7] if len(row) > 7 else ""
        )

@dataclass
class CoreBelief:
    concept: str
    belief_text: str
    belief_hash: str
    confidence: float
    created_turn: int
    updated_turn: int