"""Async LLM client for Gitlawb OpenGateway (OpenAI-compatible)."""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx
from backend.ops.circuit_breakers import CircuitOpenError, llm_circuit
from pydantic import BaseModel, Field

logger = logging.getLogger("uvicorn")

OPENGATEWAY_BASE_URL = os.getenv("OPENGATEWAY_BASE_URL", "https://opengateway.gitlawb.com/v1")
OPENGATEWAY_API_KEY = os.getenv("OPENGATEWAY_API_KEY", "")
OPENGATEWAY_MODEL = os.getenv("OPENGATEWAY_MODEL", "mimo-v2.5-pro")

_TIMEOUT = httpx.Timeout(None)  # No timeout — allow unlimited processing time
_MAX_RETRIES = 2


# ── Pydantic models ─────────────────────────────────────────────

class LLMMessage(BaseModel):
    role: str
    content: str


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class LLMResponse(BaseModel):
    content: str = ""
    reasoning_content: str = ""
    usage: TokenUsage = Field(default_factory=TokenUsage)
    model: str = ""
    finish_reason: str = ""


# ── Client ───────────────────────────────────────────────────────

class LLMClient:
    """Async OpenAI-compatible LLM client with retries."""

    def __init__(
        self,
        base_url: str = OPENGATEWAY_BASE_URL,
        api_key: str = OPENGATEWAY_API_KEY,
        model: str = OPENGATEWAY_MODEL,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        if not self.api_key:
            raise ValueError(
                "API Key missing! Cannot initialize LLMClient.\n"
                "Set OPENGATEWAY_API_KEY environment variable."
            )

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def chat(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int | None = None,
        response_format: dict[str, str] | None = None,
    ) -> LLMResponse:
        """Send a chat completion request with circuit breaker and retries."""
        try:
            return await llm_circuit.call(
                self._raw_chat, messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
            )
        except CircuitOpenError:
            logger.warning("LLM circuit breaker open — falling back to internal reasoning")
            raise RuntimeError("LLM unavailable (circuit breaker open)")

    async def _raw_chat(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int | None = None,
        response_format: dict[str, str] | None = None,
    ) -> LLMResponse:
        """Raw HTTP chat request with retries."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "temperature": temperature,
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if response_format:
            body["response_format"] = response_format

        last_error: Exception | None = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                    resp = await client.post(url, headers=headers, json=body)
                    resp.raise_for_status()
                    return self._parse_response(resp.json())
            except (httpx.HTTPStatusError, httpx.TransportError) as exc:
                last_error = exc
                logger.warning("LLM request attempt %d failed: %s", attempt + 1, exc)
                if attempt < _MAX_RETRIES and isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code >= 500:
                    continue
                break

        raise RuntimeError(f"LLM request failed after {_MAX_RETRIES + 1} attempts: {last_error}")

    def _parse_response(self, data: dict[str, Any]) -> LLMResponse:
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage_raw = data.get("usage") or {}
        return LLMResponse(
            content=message.get("content") or "",
            reasoning_content=message.get("reasoning_content") or "",
            usage=TokenUsage(
                prompt_tokens=usage_raw.get("prompt_tokens", 0),
                completion_tokens=usage_raw.get("completion_tokens", 0),
                total_tokens=usage_raw.get("total_tokens", 0),
            ),
            model=data.get("model", ""),
            finish_reason=choice.get("finish_reason", ""),
        )

    def parse_json_content(self, response: LLMResponse) -> dict[str, Any] | None:
        """Extract JSON from LLM response content."""
        text = response.content.strip()
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Try extracting from markdown code block
        if "```" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
        return None


# Module-level singleton
llm_client = LLMClient()
