from retrieval import wiki_client


def test_parse_results_strips_html_and_builds_url() -> None:
    payload = {
        "query": {
            "search": [
                {
                    "title": "Test Page",
                    "snippet": "Hello <span class='searchmatch'>world</span>",
                }
            ]
        }
    }

    results = wiki_client.parse_results(payload)

    assert results == [
        {
            "source": "wikipedia",
            "title": "Test Page",
            "snippet": "Hello world",
            "url": "https://en.wikipedia.org/wiki/Test_Page",
        }
    ]
