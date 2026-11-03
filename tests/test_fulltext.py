import requests

from veille_ia import fulltext


class FakeResponse:
    def __init__(self, text="<html></html>", fail=False):
        self.text = text
        self._fail = fail

    def raise_for_status(self):
        if self._fail:
            raise requests.HTTPError("boom")


def test_fetch_text_extracts_and_truncates(monkeypatch):
    monkeypatch.setattr(fulltext.requests, "get", lambda *a, **k: FakeResponse())
    monkeypatch.setattr(fulltext.trafilatura, "extract", lambda html: "x" * 10000)
    assert len(fulltext.fetch_text("http://a")) == fulltext.MAX_CHARS


def test_fetch_text_returns_empty_on_http_error(monkeypatch):
    monkeypatch.setattr(
        fulltext.requests, "get", lambda *a, **k: FakeResponse(fail=True)
    )
    assert fulltext.fetch_text("http://a") == ""


def test_fetch_text_returns_empty_when_nothing_extracted(monkeypatch):
    monkeypatch.setattr(fulltext.requests, "get", lambda *a, **k: FakeResponse())
    monkeypatch.setattr(fulltext.trafilatura, "extract", lambda html: None)
    assert fulltext.fetch_text("http://a") == ""
