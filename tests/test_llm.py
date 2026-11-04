import pytest

from veille_ia import llm


class FakeResponse:
    def __init__(self, status_code=200, content="ok", text=""):
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = text
        self._content = content

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setattr(llm, "load_dotenv", lambda: None)
    monkeypatch.setenv("LLM_API_URL", "http://fake")
    monkeypatch.setenv("LLM_API_KEY", "secret")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    llm._last_call.clear()
    llm._exhausted.clear()


def test_parse_models():
    assert llm.parse_models("a:15, b:5") == [("a", 15), ("b", 5)]


def test_parse_models_invalid():
    with pytest.raises(llm.LLMError):
        llm.parse_models("a")


def test_complete_builds_request_and_returns_content(monkeypatch):
    calls = []

    def fake_post(url, headers, json, timeout):
        calls.append((url, headers, json))
        return FakeResponse(content="bonjour")

    monkeypatch.setattr(llm.requests, "post", fake_post)
    result = llm.complete("salut", [("m1", 10)], system="sys")
    assert result == "bonjour"
    url, headers, body = calls[0]
    assert url == "http://fake"
    assert headers["Authorization"] == "Bearer secret"
    assert body["model"] == "m1"
    assert body["messages"][0] == {"role": "system", "content": "sys"}
    assert body["messages"][1] == {"role": "user", "content": "salut"}


def test_fallback_on_429(monkeypatch):
    def fake_post(url, headers, json, timeout):
        if json["model"] == "m1":
            return FakeResponse(status_code=429, text="quota")
        return FakeResponse(content="from m2")

    monkeypatch.setattr(llm.requests, "post", fake_post)
    assert llm.complete("x", [("m1", 5), ("m2", 5)]) == "from m2"
    assert "m1" in llm._exhausted


def test_fallback_on_503_without_marking_model_exhausted(monkeypatch):
    def fake_post(url, headers, json, timeout):
        if json["model"] == "m1":
            return FakeResponse(status_code=503, text="overloaded")
        return FakeResponse(content="from m2")

    monkeypatch.setattr(llm.requests, "post", fake_post)
    assert llm.complete("x", [("m1", 5), ("m2", 5)]) == "from m2"
    assert "m1" not in llm._exhausted


def test_fallback_on_404_marks_model_exhausted(monkeypatch):
    def fake_post(url, headers, json, timeout):
        if json["model"] == "m1":
            return FakeResponse(status_code=404, text="gone")
        return FakeResponse(content="from m2")

    monkeypatch.setattr(llm.requests, "post", fake_post)
    assert llm.complete("x", [("m1", 5), ("m2", 5)]) == "from m2"
    assert "m1" in llm._exhausted


def test_exhausted_model_is_not_retried(monkeypatch):
    seen = []

    def fake_post(url, headers, json, timeout):
        seen.append(json["model"])
        if json["model"] == "m1":
            return FakeResponse(status_code=429, text="quota")
        return FakeResponse()

    monkeypatch.setattr(llm.requests, "post", fake_post)
    llm.complete("x", [("m1", 5), ("m2", 5)])
    llm.complete("x", [("m1", 5), ("m2", 5)])
    assert seen == ["m1", "m2", "m2"]


def test_all_models_exhausted(monkeypatch):
    monkeypatch.setattr(
        llm.requests, "post", lambda *a, **k: FakeResponse(status_code=429, text="quota")
    )
    with pytest.raises(llm.LLMError, match="All models exhausted"):
        llm.complete("x", [("m1", 5), ("m2", 5)])


def test_other_http_error_raises(monkeypatch):
    monkeypatch.setattr(
        llm.requests, "post", lambda *a, **k: FakeResponse(status_code=500, text="boom")
    )
    with pytest.raises(llm.LLMError, match="HTTP 500"):
        llm.complete("x", [("m1", 5), ("m2", 5)])


def test_missing_env_variable(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY")
    with pytest.raises(llm.LLMError, match="LLM_API_KEY"):
        llm.complete("x", [("m1", 5)])


def test_rate_limiter_sleeps_between_calls(monkeypatch):
    sleeps = []
    monkeypatch.setattr(llm.time, "sleep", sleeps.append)
    monkeypatch.setattr(llm.requests, "post", lambda *a, **k: FakeResponse())
    llm.complete("x", [("m1", 3)])
    llm.complete("x", [("m1", 3)])
    assert len(sleeps) == 1
    assert 0 < sleeps[0] <= 20


def test_all_models_overloaded_then_retry_after_wait_succeeds(monkeypatch):
    sleeps = []
    monkeypatch.setattr(llm, "OVERLOAD_WAITS", (7, 9))
    monkeypatch.setattr(llm.time, "sleep", sleeps.append)
    answers = [FakeResponse(status_code=503), FakeResponse(status_code=503), FakeResponse(content="late")]
    monkeypatch.setattr(llm.requests, "post", lambda *a, **k: answers.pop(0))
    assert llm.complete("x", [("m1", 6000), ("m2", 6000)]) == "late"
    assert [s for s in sleeps if s in (7, 9)] == [7]


def test_overload_gives_up_after_all_waits(monkeypatch):
    calls = []
    monkeypatch.setattr(llm, "OVERLOAD_WAITS", (7, 9))
    monkeypatch.setattr(
        llm.requests, "post", lambda *a, **k: calls.append(1) or FakeResponse(status_code=503, text="busy")
    )
    with pytest.raises(llm.LLMError, match="All models exhausted"):
        llm.complete("x", [("m1", 6000), ("m2", 6000)])
    assert len(calls) == 6


def test_quota_exhaustion_is_not_retried(monkeypatch):
    calls = []
    monkeypatch.setattr(
        llm.requests, "post", lambda *a, **k: calls.append(1) or FakeResponse(status_code=429, text="quota")
    )
    with pytest.raises(llm.LLMError):
        llm.complete("x", [("m1", 6000), ("m2", 6000)])
    assert len(calls) == 2


def test_used_model_and_unavailable_models_are_logged(monkeypatch, capsys):
    def fake_post(url, headers, json, timeout):
        if json["model"] == "m1":
            return FakeResponse(status_code=503, text="busy")
        return FakeResponse(content="ok")

    monkeypatch.setattr(llm.requests, "post", fake_post)
    llm.complete("x", [("m1", 6000), ("m2", 6000)])
    out = capsys.readouterr().out
    assert "LLM : m1 indisponible (HTTP 503)" in out
    assert "LLM : m2" in out
