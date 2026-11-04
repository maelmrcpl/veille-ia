from veille_ia.collectors import hn
from veille_ia.models import Article


class FakeResponse:
    def __init__(self, hits):
        self._hits = hits

    def raise_for_status(self):
        pass

    def json(self):
        return {"hits": self._hits}


def hit(story_id, title="Title", url="http://a", points=50, created=1000):
    return {
        "objectID": story_id,
        "title": title,
        "url": url,
        "points": points,
        "created_at_i": created,
    }


def test_search_sends_24h_and_points_filter(monkeypatch):
    seen = {}

    def fake_get(url, params, timeout):
        seen.update(params)
        return FakeResponse([])

    monkeypatch.setattr(hn.requests, "get", fake_get)
    hn.search_stories("AI", now=200000)
    assert seen["query"] == "AI"
    assert seen["tags"] == "story"
    assert seen["numericFilters"] == f"created_at_i>{200000 - 86400},points>={hn.MIN_POINTS}"


def test_collect_deduplicates_across_keywords(monkeypatch):
    monkeypatch.setattr(
        hn.requests, "get", lambda *a, **k: FakeResponse([hit("1"), hit("2", points=90)])
    )
    articles = hn.collect(["AI", "LLM"], now=2000)
    assert [a.title for a in articles] == ["Title", "Title"]
    assert len(articles) == 2


def test_collect_sorts_by_score_and_maps_fields(monkeypatch):
    monkeypatch.setattr(
        hn.requests,
        "get",
        lambda *a, **k: FakeResponse([hit("1", points=30), hit("2", points=90)]),
    )
    articles = hn.collect(["AI"], now=2000)
    assert [a.score for a in articles] == [90, 30]
    assert articles[0].source == "Hacker News"
    assert articles[0].url == "http://a"
    assert articles[0].published == 1000


def test_collect_falls_back_to_hn_item_url(monkeypatch):
    monkeypatch.setattr(
        hn.requests, "get", lambda *a, **k: FakeResponse([hit("42", url=None)])
    )
    articles = hn.collect(["AI"], now=2000)
    assert articles[0].url == "https://news.ycombinator.com/item?id=42"


def test_enrich_fills_text_and_skips_hn_items(monkeypatch):
    monkeypatch.setattr(hn, "fetch_text", lambda url: f"text of {url}")
    external = Article("A", "http://a", "Hacker News", 1)
    internal = Article("B", "https://news.ycombinator.com/item?id=1", "Hacker News", 1)
    hn.enrich([external, internal])
    assert external.text == "text of http://a"
    assert internal.text == ""
