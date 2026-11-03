import requests

from veille_ia.collectors import blogs, rss

NOW = 1_700_000_000
RECENT = "Tue, 14 Nov 2023 21:00:00 GMT"  # 1_699_995_600, about 1 h before NOW
OLD = "Mon, 01 Jan 2023 00:00:00 GMT"


def feed_xml(*items):
    body = "".join(
        f"<item><title>{t}</title><link>{u}</link><pubDate>{d}</pubDate>"
        f"<description>{s}</description></item>"
        for t, u, d, s in items
    )
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>{body}</channel></rss>'


class FakeResponse:
    def __init__(self, xml, status=200):
        self.content = xml.encode()
        self.status = status

    def raise_for_status(self):
        if self.status != 200:
            raise requests.HTTPError(str(self.status))


def test_collect_feed_keeps_only_last_24h_and_maps_fields(monkeypatch):
    xml = feed_xml(
        ("New", "http://new", RECENT, "<p>Hello &amp; <b>world</b></p>"),
        ("Old", "http://old", OLD, "old"),
    )
    monkeypatch.setattr(rss.requests, "get", lambda *a, **k: FakeResponse(xml))
    articles = rss.collect_feed("http://feed", "Blog", now=NOW)
    assert len(articles) == 1
    article = articles[0]
    assert (article.title, article.url, article.source) == ("New", "http://new", "Blog")
    assert article.published == 1_699_995_600
    assert article.text == "Hello & world"


def test_collect_feed_skips_failing_feed(monkeypatch):
    monkeypatch.setattr(rss.requests, "get", lambda *a, **k: FakeResponse("", status=429))
    assert rss.collect_feed("http://feed", "Blog", now=NOW) == []


def test_collect_feed_sends_user_agent(monkeypatch):
    seen = {}

    def fake_get(url, headers, timeout):
        seen.update(headers)
        return FakeResponse(feed_xml())

    monkeypatch.setattr(rss.requests, "get", fake_get)
    rss.collect_feed("http://feed", "Blog", now=NOW)
    assert "User-Agent" in seen


def test_blogs_collect_gathers_all_feeds(monkeypatch):
    monkeypatch.setattr(blogs, "FEEDS", {"A": "http://a", "B": "http://b"})
    xml = feed_xml(("T", "http://t", RECENT, "s"))
    monkeypatch.setattr(rss.requests, "get", lambda *a, **k: FakeResponse(xml))
    articles = blogs.collect(now=NOW)
    assert [a.source for a in articles] == ["A", "B"]
