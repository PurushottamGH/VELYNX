"""Tests for browser retrieval module."""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.retrieval import browser  # noqa: E402


def test_fetch_page_returns_none_on_failure(monkeypatch) -> None:
    """Timeout or navigation error returns None gracefully."""

    async def _fail(*args, **kwargs):
        raise TimeoutError("simulated timeout")

    # Patch at the playwright level: make the async context manager raise
    class _BrokenPlaywright:
        async def __aenter__(self):
            raise TimeoutError("simulated timeout")

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(browser, "async_playwright", lambda: _BrokenPlaywright())

    result = asyncio.run(browser.fetch_page("https://example.com"))
    assert result is None


def test_fetch_page_returns_structured_content(monkeypatch) -> None:
    """Successful fetch returns dict with expected keys."""

    class _FakePage:
        async def goto(self, *a, **kw):
            pass

        async def evaluate(self, *a, **kw):
            return {
                "title": "Example Domain",
                "canonicalUrl": "https://example.com/",
                "fullText": "Example Domain This domain is for use in examples.",
                "h1": ["Example Domain"],
                "h2": [],
                "h3": [],
            }

    class _FakeContext:
        async def new_page(self):
            return _FakePage()

        async def close(self):
            pass

    class _FakeBrowser:
        async def new_context(self, **kw):
            return _FakeContext()

        async def close(self):
            pass

    class _FakeChromium:
        async def launch(self, **kw):
            return _FakeBrowser()

    class _FakePW:
        chromium = _FakeChromium()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(browser, "async_playwright", lambda: _FakePW())

    result = asyncio.run(browser.fetch_page("https://example.com"))
    assert result is not None
    assert result["title"] == "Example Domain"
    assert result["source"] == "browser"
    assert "full_text" in result
    assert "snippet" in result
    assert result["score"] == 0.75


def test_fetch_page_handles_empty_body(monkeypatch) -> None:
    """Page with no body text still returns a result."""

    class _FakePage:
        async def goto(self, *a, **kw):
            pass

        async def evaluate(self, *a, **kw):
            return {
                "title": "Empty Page",
                "canonicalUrl": "",
                "fullText": "",
                "h1": [],
                "h2": [],
                "h3": [],
            }

    class _FakeContext:
        async def new_page(self):
            return _FakePage()

        async def close(self):
            pass

    class _FakeBrowser:
        async def new_context(self, **kw):
            return _FakeContext()

        async def close(self):
            pass

    class _FakeChromium:
        async def launch(self, **kw):
            return _FakeBrowser()

    class _FakePW:
        chromium = _FakeChromium()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(browser, "async_playwright", lambda: _FakePW())

    result = asyncio.run(browser.fetch_page("https://empty.example.com"))
    assert result is not None
    assert result["snippet"] is None


def test_fetch_sources_returns_list(monkeypatch) -> None:
    """fetch_sources processes multiple URLs and filters None results."""

    async def _fake_fetch(url, timeout_ms=20000):
        if "fail" in url:
            return None
        return {"url": url, "title": "Test", "source": "browser", "score": 0.75,
                "snippet": "s", "full_text": "full", "canonical_url": url, "headers": {}}

    monkeypatch.setattr(browser, "fetch_page", _fake_fetch)

    sources = [
        {"url": "https://good.example.com"},
        {"url": "https://fail.example.com"},
        {"url": "https://also-good.example.com"},
    ]
    results = asyncio.run(browser.fetch_sources(sources))
    assert len(results) == 2
    assert all(r["source"] == "browser" for r in results)


def test_fetch_sources_handles_empty_list() -> None:
    """Empty source list returns empty result."""
    results = asyncio.run(browser.fetch_sources([]))
    assert results == []


def test_fetch_sources_deduplicates_urls(monkeypatch) -> None:
    """Duplicate URLs are only fetched once."""

    fetched_urls: list[str] = []

    async def _fake_fetch(url, timeout_ms=20000):
        fetched_urls.append(url)
        return {"url": url, "title": "T", "source": "browser", "score": 0.75,
                "snippet": "s", "full_text": "f", "canonical_url": url, "headers": {}}

    monkeypatch.setattr(browser, "fetch_page", _fake_fetch)

    sources = [
        {"url": "https://example.com"},
        {"url": "https://example.com"},
        {"url": "https://other.com"},
    ]
    asyncio.run(browser.fetch_sources(sources))
    assert len(fetched_urls) == 2
