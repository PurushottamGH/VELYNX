"""Self-model — VELYNX knows itself in real time."""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

logger = logging.getLogger("uvicorn")

BACKEND_ROOT = Path(__file__).parent.parent
SOUL_PATH = BACKEND_ROOT / "soul" / "concepts.json"
LEARNING_PATH = BACKEND_ROOT / "velynx_data" / "learning" / "learning_stats.json"


class SelfModel:

    async def snapshot(self) -> dict:
        kg = self._kg_stats()
        return {
            "knowledge": {
                "total_learned": kg["total"],
                "triples": kg["triples"],
                "top_domains": kg["top"][:8],
                "weak_topics": kg["weak"],
            },
            "learning": self._learning(),
            "soul": self.soul_concepts(),
            "health": await self._health(),
            "uptime_sec": self._uptime(),
        }

    def what_i_know(self) -> list[str]:
        return [t for t, _ in self._ranked(0.7, True)]

    def what_i_dont_know(self) -> list[str]:
        return [t for t, _ in self._ranked(0.5)]

    def last_learned(self) -> str | None:
        rows = self._ranked(0.0, True)
        return rows[0][0] if rows else None

    def soul_concepts(self) -> list[str]:
        d = self._read(SOUL_PATH)
        return sorted(d.keys()) if d else []

    # ── internal ─────────────────────────────────────────────

    def _kg_stats(self) -> dict:
        try:
            import sqlite3
            from memory.knowledge_graph import KnowledgeGraph
            db = sqlite3.connect(str(KnowledgeGraph().db_path))
            total = db.execute("SELECT COUNT(*) FROM understandings").fetchone()[0]
            triples = db.execute("SELECT COUNT(*) FROM triples").fetchone()[0]
            weak = [r[0] for r in db.execute(
                "SELECT topic FROM understandings WHERE confidence<0.5 ORDER BY confidence LIMIT 20"
            ).fetchall()]
            doms: dict[str, int] = {}
            for t, _ in db.execute("SELECT topic,confidence FROM understandings ORDER BY confidence DESC"):
                k = t.split()[0].rstrip(",:;") if t.split() else "general"
                doms[k] = doms.get(k, 0) + 1
            db.close()
            return {"total": total, "triples": triples, "weak": weak, "top": sorted(doms.items(), key=lambda x: -x[1])[:10]}
        except Exception:
            return {"total": 0, "triples": 0, "weak": [], "top": []}

    def _ranked(self, threshold: float, desc: bool = False) -> list[tuple[str, float]]:
        try:
            import sqlite3
            from memory.knowledge_graph import KnowledgeGraph
            db = sqlite3.connect(str(KnowledgeGraph().db_path))
            op, order = (">=", "DESC") if desc else ("<", "ASC")
            rows = db.execute(
                f"SELECT topic,confidence FROM understandings WHERE confidence{op}? ORDER BY confidence {order}",
                (threshold,)
            ).fetchall()
            db.close()
            return [(r[0], r[1]) for r in rows]
        except Exception:
            return []

    def _learning(self) -> dict:
        s = self._read(LEARNING_PATH)
        return {
            "total_queries": s.get("total_queries", 0),
            "concepts": s.get("total_concepts_learned", 0),
            "avg_confidence": s.get("avg_confidence", 0),
            "domains": s.get("domains_covered", {}),
        }

    async def _health(self) -> str:
        try:
            from ops.health_monitor import health_monitor
            if health_monitor.is_alive() and health_monitor.is_ready():
                return "healthy"
            return "degraded"
        except Exception:
            return "unknown"

    def _uptime(self) -> float:
        try:
            from ops.health_monitor import health_monitor
            return round(time.time() - health_monitor._start_time, 1)
        except Exception:
            return 0

    def _read(self, path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}


self_model = SelfModel()


def get_snapshot() -> dict:
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(self_model.snapshot())
    if loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(lambda: asyncio.run(self_model.snapshot()))
            return future.result(timeout=5)
    return loop.run_until_complete(self_model.snapshot())
