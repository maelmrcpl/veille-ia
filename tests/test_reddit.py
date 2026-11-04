from veille_ia.categories import CATEGORIES
from veille_ia.collectors import reddit, rss

NOW = 1_700_000_000

ATOM = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>r/x</title>
<entry><title>Post</title><link href="http://post"/>
<updated>2023-11-14T21:00:00+00:00</updated>
<content type="html">&lt;p&gt;Body &amp;amp; more&lt;/p&gt;</content></entry>
</feed>"""


class FakeResponse:
    def __init__(self, status=200):
        self.status = status
        self.content = ATOM.encode()

    def raise_for_status(self):
        if self.status != 200:
            raise rss.requests.HTTPError(str(self.status))


def test_collect_reads_atom_and_skips_blocked_subreddit(monkeypatch):
    def fake_get(url, headers, timeout):
        return FakeResponse(429 if "LocalLLaMA" in url else 200)

    monkeypatch.setattr(rss.requests, "get", fake_get)
    articles = reddit.collect(CATEGORIES["ia"].reddit_feeds, now=NOW)
    assert len(articles) == 1
    assert articles[0].source == "Reddit r/MachineLearning"
    assert articles[0].url == "http://post"
    assert articles[0].text == "Body & more"
