from __future__ import annotations

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ARXIV_ENDPOINT = "http://export.arxiv.org/api/query"


def search(query: str, limit: int = 5, timeout: int = 3) -> list[dict]:
    """Query arXiv API and return normalized results."""
    if not query.strip():
        return []

    params = {
        "search_query": f"all:{query}",
        "start": "0",
        "max_results": str(limit),
    }
    url = f"{ARXIV_ENDPOINT}?{urllib.parse.urlencode(params)}"

    with urllib.request.urlopen(url, timeout=timeout) as response:
        xml_bytes = response.read()

    root = ET.fromstring(xml_bytes)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results: list[dict] = []
    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        url_val = link_el.attrib.get("href") if link_el is not None else None
        results.append(
            {
                "source": "arxiv",
                "title": title,
                "snippet": summary,
                "url": url_val,
            }
        )
    return results
