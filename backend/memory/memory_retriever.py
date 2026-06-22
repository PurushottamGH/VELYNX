import sqlite3
import json
from contextlib import contextmanager
from typing import List, Dict, Any, Union, Iterable

from backend.memory import _sqlite
from backend.memory.retrieval_engine import (
    _state_query_to_vector,
    _cosine_similarity_state,
)

class MemoryRetriever:
    # Phase 52.9A: size of the pre-cutoff observability pool we capture for
    # diversity analysis (proving diverse candidates exist before top_k slicing).
    RAW_CANDIDATE_POOL_SIZE = 20

    # Phase 52.9B: blend weights for the semantic relevance score and the
    # assumed maximum theoretical memory strength used for normalization.
    COSINE_WEIGHT = 0.8
    STRENGTH_WEIGHT = 0.2
    MAX_THEORETICAL_STRENGTH = 10.0

    # Phase 52.9D: Hybrid multi-representation blend. The semantic base mixes the
    # pure trigger (activated_concepts) with the broader cognitive state
    # (dominant_concepts). Trigger is weighted higher to stay associative and
    # avoid the "gray mush" state-collapse seen with state-only retrieval.
    TRIGGER_WEIGHT = 0.7
    STATE_WEIGHT = 0.3

    def __init__(self, db_path: str = "velynx_state.db"):
        self.db_path = db_path
        # Phase 52.9A: holds the most recent retrieve_by_context raw pool
        # (top-N candidates BEFORE the top_k cutoff). This is pure observability
        # state — it never feeds back into retrieval. Each entry:
        #   {"memory_id": int, "score": float}
        self.last_raw_candidates: List[Dict[str, Any]] = []

    @contextmanager
    def _conn(self):
        conn = _sqlite.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _safe_json(raw: Any) -> Dict[str, float]:
        """
        Parse a JSON concept-map column into a dict. Missing/null/blank columns
        (e.g. a legacy row with no activated_concepts_json) become an empty dict,
        which yields a cosine of 0.0 rather than an error.
        """
        if not raw:
            return {}
        if isinstance(raw, dict):
            return raw
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def _memory_log_columns(self, conn) -> set:
        """Returns the set of column names present on memory_log (schema-aware)."""
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(memory_log)")
        return {row[1] for row in cur.fetchall()}

    def retrieve_by_context(
        self,
        active_concepts: Union[Dict[str, float], Iterable[str]],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Phase 52.9D: Hybrid Multi-Representation Retrieval.

        Candidates are pre-filtered cheaply via SQL LIKE clauses against BOTH
        the pure trigger (activated_concepts_json) and the broader cognitive
        state (dominant_concepts_json), then scored in Python with a two-stage
        blend:

            trigger_cosine = cos(query, activated_concepts)
            state_cosine   = cos(query, dominant_concepts)
            hybrid_semantic = trigger_cosine * 0.7 + state_cosine * 0.3
            final_score     = hybrid_semantic * 0.8 + normalized_strength * 0.2

        Mixing both representations avoids the "gray mush" state-collapse of
        state-only retrieval while keeping the system associative.

        ``active_concepts`` is a {concept: thermodynamic_weight} mapping (a bare
        list of concept names is still accepted for backward compatibility).
        """
        query_vec = _state_query_to_vector(active_concepts)

        if not query_vec:
            # Reset observability state so a stale pool is never re-logged.
            self.last_raw_candidates = []
            return []

        with self._conn() as conn:
            columns = self._memory_log_columns(conn)
            # activated_concepts_json may be absent on legacy databases.
            has_activated = "activated_concepts_json" in columns

            # Build LIKE clauses against every representation column available so
            # candidates are never prematurely filtered out.
            search_cols = ["dominant_concepts_json"]
            if has_activated:
                search_cols.append("activated_concepts_json")

            like_parts = []
            params: List[str] = []
            for concept in query_vec:
                token = f'%"{concept}"%'
                for col in search_cols:
                    like_parts.append(f"{col} LIKE ?")
                    params.append(token)
            like_clauses = " OR ".join(like_parts)

            activated_select = "activated_concepts_json" if has_activated else "NULL AS activated_concepts_json"
            query = f"""
                SELECT turn_index, memory_type, priority, user_input,
                       dominant_concepts_json, {activated_select}, memory_strength
                FROM memory_log
                WHERE priority IN ('high', 'medium')
                  AND ({like_clauses})
            """

            cursor = conn.cursor()
            cursor.execute(query, params)

            memories = []
            for row in cursor.fetchall():
                memories.append({
                    "turn_index": row[0],
                    "type": row[1],
                    "priority": row[2],
                    "trigger": row[3],
                    "dominant_states": self._safe_json(row[4]),
                    "activated_states": self._safe_json(row[5]),
                    "strength": row[6],
                })

        if not memories:
            self.last_raw_candidates = []
            return []

        # Python-side two-stage hybrid scoring.
        for mem in memories:
            trigger_cosine = _cosine_similarity_state(query_vec, mem["activated_states"])
            state_cosine = _cosine_similarity_state(query_vec, mem["dominant_states"])
            hybrid_semantic = (trigger_cosine * self.TRIGGER_WEIGHT) + (state_cosine * self.STATE_WEIGHT)

            raw_strength = float(mem.get("strength") or 0.0)
            # Normalize against the assumed max theoretical strength, clamped to
            # [0, 1] so an unusually strong memory can't blow past the blend.
            normalized_strength = max(0.0, min(1.0, raw_strength / self.MAX_THEORETICAL_STRENGTH))

            mem["trigger_cosine"] = trigger_cosine
            mem["state_cosine"] = state_cosine
            mem["hybrid_semantic_score"] = hybrid_semantic
            mem["normalized_strength"] = normalized_strength
            mem["final_score"] = (hybrid_semantic * self.COSINE_WEIGHT) + (normalized_strength * self.STRENGTH_WEIGHT)

        # Sort descending by relevance. Tie-break on raw strength for stability.
        memories.sort(key=lambda m: (m["final_score"], float(m.get("strength") or 0.0)), reverse=True)

        # Phase 52.9A telemetry: capture the top-N raw pool BEFORE the top_k cut.
        # We record the blended final_score as the canonical score, plus the
        # trigger/state split so the hybrid blend stays debuggable downstream.
        self.last_raw_candidates = [
            {
                "memory_id": m["turn_index"],
                "score": float(m["final_score"]),
                "trigger_cosine": float(m["trigger_cosine"]),
                "state_cosine": float(m["state_cosine"]),
            }
            for m in memories[:self.RAW_CANDIDATE_POOL_SIZE]
        ]

        return memories[:top_k]

    def retrieve_latest_episodic(self, limit: int = 1) -> List[Dict[str, Any]]:
        """Pulls the most recent major shocks or shifts, regardless of current context."""
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT turn_index, user_input, dominant_concepts_json, memory_strength
                FROM memory_log
                WHERE memory_type = 'episodic'
                ORDER BY turn_index DESC
                LIMIT ?
            """, (limit,))
            
            return [{
                "turn": row[0],
                "trigger": row[1],
                "states": json.loads(row[2]),
                "strength": row[3]
            } for row in cursor.fetchall()]