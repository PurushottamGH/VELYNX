from __future__ import annotations

import re
from typing import Any


class _PersonalContextBackend:
    def query(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "Personal Context backend is not configured for this VELYNX node."
        )


class ContextRecon:
    _DEPLOYMENT_QUERY = (
        "engineering OR repository OR platform OR deployment OR build OR ci "
        "vercel OR render OR railway OR github-actions OR github actions"
    )

    _BOILERPLATE_PATTERNS: tuple[re.Pattern[str], ...] = (
        re.compile(r"^\s*[-*•·]+\s*"),
        re.compile(r"\bunsubscribe\b.*$", re.IGNORECASE),
        re.compile(r"\bview (?:in|on) (?:browser|app)\b.*$", re.IGNORECASE),
        re.compile(r"\bmanage (?:notifications|settings|preferences)\b.*$", re.IGNORECASE),
        re.compile(r"\bprivacy policy\b.*$", re.IGNORECASE),
        re.compile(r"\bterms of service\b.*$", re.IGNORECASE),
        re.compile(r"^https?://\S+$", re.IGNORECASE),
        re.compile(r"^(?:dear|hi|hello)\s+\w+[,:]?\s*", re.IGNORECASE),
        re.compile(r"^\s*from:\s.*$", re.IGNORECASE),
        re.compile(r"^\s*to:\s.*$", re.IGNORECASE),
        re.compile(r"^\s*date:\s.*$", re.IGNORECASE),
        re.compile(r"^\s*subject:\s.*$", re.IGNORECASE),
        re.compile(r"\[image\s*:\s*[^\]]+\]", re.IGNORECASE),
        re.compile(r"\[link\s*:\s*[^\]]+\]", re.IGNORECASE),
    )

    _FALLBACK_MESSAGE = (
        "[VELYNX CONTEXT] No active external deployment logs detected in personal data."
    )

    def __init__(self, backend: _PersonalContextBackend | None = None) -> None:
        self._backend: _PersonalContextBackend = backend or _PersonalContextBackend()

    def scan_deployment_updates(self, max_results: int = 15) -> list[dict[str, Any]]:
        try:
            results = self._backend.query(
                self._DEPLOYMENT_QUERY, max_results=max_results
            )
        except Exception as exc:
            print(f"[ContextRecon] Backend query failed: {type(exc).__name__}: {exc}")
            return []
        return self._normalize_results(results)

    def summarize_active_projects(self, max_results: int = 15) -> str:
        try:
            raw_results = self.scan_deployment_updates(max_results=max_results)
        except Exception as exc:
            print(f"[ContextRecon] Scan failed: {type(exc).__name__}: {exc}")
            return self._FALLBACK_MESSAGE

        if not raw_results:
            return self._FALLBACK_MESSAGE

        signals: list[str] = []
        for entry in raw_results:
            text = entry.get("text", "")
            if not text:
                continue
            cleaned = self._clean_text(text)
            if not cleaned:
                continue
            signals.append(f"- {cleaned}")

        if not signals:
            return self._FALLBACK_MESSAGE

        header = (
            f"[VELYNX CONTEXT] {len(signals)} active deployment signal(s) detected:"
        )
        return f"{header}\n" + "\n".join(signals)

    def _normalize_results(
        self, results: list[dict[str, Any]] | None
    ) -> list[dict[str, Any]]:
        if not results:
            return []
        normalized: list[dict[str, Any]] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            text = item.get("text") or item.get("body") or item.get("content") or ""
            source = (
                item.get("source")
                or item.get("provider")
                or item.get("sender")
                or "unknown"
            )
            if not isinstance(text, str) or not text.strip():
                continue
            normalized.append({"text": text, "source": str(source)})
        return normalized

    def _clean_text(self, text: str) -> str:
        lines = text.splitlines()
        cleaned_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            for pattern in self._BOILERPLATE_PATTERNS:
                stripped = pattern.sub("", stripped).strip()
            if not stripped:
                continue
            if len(stripped) < 4:
                continue
            cleaned_lines.append(stripped)
        return " ".join(cleaned_lines)
