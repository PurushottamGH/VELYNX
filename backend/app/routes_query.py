"""Query, feedback, and streaming API routes."""
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel

from backend.models.answer import AnswerResponse
from backend.models.query import Query
from backend.app.pipeline import answer_question

logger = logging.getLogger("uvicorn")

router = APIRouter()


@router.post("/query", response_model=AnswerResponse)
async def query(payload: Query, request: Request) -> AnswerResponse:
    from ops.load_shedding import LoadShedError, load_shedder
    session_id = getattr(request.app.state, "session_id", None)
    try:
        async with load_shedder.acquire(priority="normal"):
            return await asyncio.wait_for(
                answer_question(payload.text, session_id=session_id),
                timeout=30.0,
            )
    except LoadShedError:
        return AnswerResponse(
            query=payload.text,
            answer="Server is at capacity. Please try again in a moment.",
            confidence="LOW",
            sources=[],
            contradictions=[],
            gaps=["load_shed"],
            citations=[],
            tone="error",
            debug={"error": "load_shed", "active": load_shedder.get_stats()},
        )
    except asyncio.TimeoutError:
        return AnswerResponse(
            query=payload.text,
            answer="Query processing timed out. Please try a simpler question.",
            confidence="LOW",
            sources=[],
            contradictions=[],
            gaps=["timeout"],
            citations=[],
            tone="error",
            debug={"error": "timeout", "timeout_seconds": 30},
        )


@router.get("/stream/query")
async def stream_query_endpoint(text: str, request: Request, session_id: str | None = None):
    """SSE streaming query endpoint."""
    from app.streaming import stream_query as sq
    sid = session_id or getattr(request.app.state, "session_id", None)
    return await sq(text, session_id=sid)


@router.post("/feedback")
async def feedback(payload: dict) -> dict:
    """Process user feedback for learning."""
    from learning.online_learner import learn_from_feedback
    from app.db_bridge import persist_feedback

    query_text = payload.get("query", "")
    rating = payload.get("rating", 0)
    meta = payload.get("meta", {})

    result = learn_from_feedback(query_text, rating, meta=meta)

    try:
        await persist_feedback(
            query=query_text,
            answer=str(meta.get("answer", "")),
            rating=rating,
            correction=meta.get("correction"),
        )
    except Exception as exc:
        logger.debug("Feedback persist skipped: %s", exc)

    try:
        from learning.online_learner import persist_learning_to_db
        await persist_learning_to_db(query_text, rating, meta, result)
    except Exception as exc:
        logger.debug("Learning persist skipped: %s", exc)

    return result


class VideoLearnRequest(BaseModel):
    url: str


@router.post("/learn/video")
async def learn_video(payload: VideoLearnRequest) -> dict:
    """Learn from a video URL."""
    from retrieval.video_learner import learn_from_url
    return await learn_from_url(payload.url)


@router.get("/proactive/status")
async def proactive_status() -> dict:
    """Proactive cognition status."""
    from learning.proactive_cognition import proactive_cognition
    return proactive_cognition.get_status()


@router.post("/proactive/run")
async def proactive_run() -> dict:
    """Trigger a proactive cognition cycle."""
    from learning.proactive_cognition import proactive_cognition
    return await proactive_cognition.run_cycle()
