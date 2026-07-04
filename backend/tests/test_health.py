import sys
from pathlib import Path
import asyncio

import httpx

sys.path.append(str(Path(__file__).resolve().parents[1]))
from backend.app.main import app  # noqa: E402


def test_health() -> None:
    async def _get_health() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/health")

    response = asyncio.run(_get_health())
    assert response.status_code == 200
    data = response.json()
    assert "overall_status" in data
    assert "subsystems" in data
