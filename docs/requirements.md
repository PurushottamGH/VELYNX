# VELYNX Requirements Summary

Source: extracted from VELYNX Project document.

## Vision

VELYNX is a raised synthetic mind that finds truth live from sources, reasons across contradictions, and communicates confidence honestly.

## Founding Principles

- Every answer must be traceable to sources.
- Uncertainty is a feature, not a weakness.
- The system learns from being wrong without retraining.
- Knowledge has no cutoff date.
- The builder owns the system completely.

## Seven-Layer Architecture

1. Constitution Layer: rules for reasoning, uncertainty, communication.
2. Intent Engine: decomposes queries into dimensions.
3. Retrieval Mesh: parallel search across many sources.
4. Truth Filter: credibility scoring and deduplication.
5. Contradiction Engine: surfaces disagreements.
6. Reasoning Core: reasons across filtered sources.
7. Human Synthesis: outputs in tone profiles with confidence.

## Core Pipelines (MVP Focus)

- Query decomposition -> retrieval -> truth filtering -> synthesis.
- All answers include confidence tier and source list.
- Contradictions should be reported, not hidden.

## Tech Stack (per document)

- Backend: Python 3.11+, FastAPI, aiohttp, Playwright, BeautifulSoup4, Pydantic.
- Retrieval: SearXNG, Brave, Tavily, arXiv, Wikipedia, Semantic Scholar.
- Memory: Redis, ChromaDB, SQLite FTS5.
- Frontend: React, Vite, TailwindCSS, Framer Motion, Zustand, React Query.
- Deployment: HuggingFace Spaces, Vercel, Railway, GitHub Actions.

## Project Structure (Target)

The document specifies a multi-module layout with backend pipeline layers, retrieval clients, memory, learning, and frontend visualization components. This repository now mirrors that structure with placeholders.

## Roadmap Phases (Condensed)

1. Foundation: structure, constitution, first API endpoint.
2. Retrieval Layer: parallel search, source dedupe, time targets.
3. Truth Filter: credibility scoring, MinHash dedupe.
4. Contradiction Engine: detect and explain conflicts.
5. Reasoning + Synthesis: full pipeline, confidence tiers.
6. Browser + Video: Playwright + Whisper + OpenCV.
7. Learning Loop: feedback, trust updates, gap tracking.
8. Frontend + Deployment: live UI and hosted stack.

## Acceptance Criteria (MVP)

- FastAPI endpoint responds and returns a structured answer object.
- Retrieval mesh executes multiple sources in parallel.
- Truth filter scores sources and returns a filtered list.
- Contradictions are identified and reported.
- Response includes confidence tier and citations.

## Immediate Next Steps

1. Implement intent decomposition and retrieval mesh async pipeline.
2. Wire first real source (Wikipedia or SearXNG).
3. Add simple truth scoring and a confidence tier enum.
4. Return structured response from the API for frontend rendering.
