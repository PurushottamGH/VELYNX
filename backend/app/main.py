"""VELYNX API — FastAPI application entry point."""
from __future__ import annotations

import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from backend.app.lifespan import lifespan
from backend.app.routes_ops import router as ops_router
from backend.app.routes_query import router as query_router
from backend.app.routes_eval import router as eval_router

load_dotenv()

logger = logging.getLogger("uvicorn")

app = FastAPI(title="VELYNX API", lifespan=lifespan)

# Register route modules
app.include_router(ops_router)
app.include_router(query_router)
app.include_router(eval_router)
