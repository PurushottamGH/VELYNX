from __future__ import annotations

from typing import Any

from playwright.async_api import async_playwright

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)


def _truncate(text: str, limit: int) -> str:
    trimmed = text.strip()
    return trimmed[:limit]


async def fetch_page(url: str, timeout_ms: int = 3000) -> dict[str, Any] | None:
    """Fetch page content via Playwright and extract key fields."""
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=_USER_AGENT)
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=timeout_ms)

            payload = await page.evaluate(
                """
                () => {
                  const canonical = document.querySelector('link[rel="canonical"]');
                  const headers = (selector) =>
                    Array.from(document.querySelectorAll(selector))
                      .map((el) => (el.innerText || '').trim())
                      .filter(Boolean)
                      .slice(0, 20);
                  return {
                    title: document.title || '',
                    canonicalUrl: canonical ? canonical.href : '',
                    fullText: document.body ? (document.body.innerText || '') : '',
                    h1: headers('h1'),
                    h2: headers('h2'),
                    h3: headers('h3'),
                  };
                }
                """
            )

            await context.close()
            await browser.close()

        full_text = _truncate(payload.get("fullText", ""), 5000)
        title = (payload.get("title") or "").strip() or None
        canonical_url = (payload.get("canonicalUrl") or "").strip() or url
        headers = {
            "h1": payload.get("h1") or [],
            "h2": payload.get("h2") or [],
            "h3": payload.get("h3") or [],
        }
        snippet = _truncate(full_text, 280) if full_text else None

        return {
            "url": url,
            "canonical_url": canonical_url,
            "title": title,
            "snippet": snippet,
            "full_text": full_text,
            "headers": headers,
            "source": "browser",
            "score": 0.75,
        }
    except Exception:  # noqa: BLE001 - fail gracefully for retrieval pipeline
        return None


async def fetch_sources(sources: list[dict], limit: int = 3) -> list[dict]:
    """Fetch content from the top sources, returning structured browser reads."""
    urls: list[str] = []
    for item in sources:
        url = (item.get("url") or "").strip()
        if url and url not in urls:
            urls.append(url)
        if len(urls) >= limit:
            break

    if not urls:
        return []

    results = [await fetch_page(url) for url in urls]
    return [item for item in results if item]
