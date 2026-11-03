import pytest

from veille_ia import cluster, llm
from veille_ia.models import Article

MODELS = [("m", 10)]


def articles(n):
    return [Article(f"T{i}", f"http://{i}", "S", 1, text=f"text {i}") for i in range(n)]


def fake_llm(monkeypatch, content):
    seen = {}

    def fake_complete(prompt, models, system=None):
        seen["prompt"] = prompt
        seen["models"] = models
        return content

    monkeypatch.setattr(cluster.llm, "complete", fake_complete)
    return seen


def test_same_event_gives_one_topic_with_all_sources(monkeypatch):
    fake_llm(monkeypatch, '{"topics": [{"title": "IPO", "ids": [0, 1]}], "off_topic": []}')
    topics = cluster.cluster(articles(2), MODELS)
    assert len(topics) == 1
    assert topics[0].title == "IPO"
    assert [a.url for a in topics[0].articles] == ["http://0", "http://1"]


def test_off_topic_is_dropped(monkeypatch):
    fake_llm(monkeypatch, '{"topics": [{"title": "A", "ids": [0]}], "off_topic": [1]}')
    topics = cluster.cluster(articles(2), MODELS)
    assert [t.title for t in topics] == ["A"]


def test_unlisted_article_becomes_its_own_topic(monkeypatch):
    fake_llm(monkeypatch, '{"topics": [{"title": "A", "ids": [0]}], "off_topic": []}')
    topics = cluster.cluster(articles(2), MODELS)
    assert [t.title for t in topics] == ["A", "T1"]


def test_unknown_and_duplicate_ids_are_ignored(monkeypatch):
    fake_llm(
        monkeypatch,
        '{"topics": [{"title": "A", "ids": [0, 9, "x"]}, {"title": "B", "ids": [0]}], "off_topic": []}',
    )
    topics = cluster.cluster(articles(1), MODELS)
    assert [t.title for t in topics] == ["A"]
    assert len(topics[0].articles) == 1


def test_json_in_code_fence_is_accepted(monkeypatch):
    fake_llm(monkeypatch, '```json\n{"topics": [{"title": "A", "ids": [0]}]}\n```')
    assert len(cluster.cluster(articles(1), MODELS)) == 1


def test_invalid_json_raises(monkeypatch):
    fake_llm(monkeypatch, "not json")
    with pytest.raises(llm.LLMError):
        cluster.cluster(articles(1), MODELS)


def test_prompt_numbers_articles_and_models_are_passed(monkeypatch):
    seen = fake_llm(monkeypatch, '{"topics": []}')
    cluster.cluster(articles(2), MODELS)
    assert "[0] T0 (S) text 0" in seen["prompt"]
    assert "[1] T1 (S) text 1" in seen["prompt"]
    assert seen["models"] == MODELS


def test_no_articles_makes_no_llm_call(monkeypatch):
    seen = fake_llm(monkeypatch, "")
    assert cluster.cluster([], MODELS) == []
    assert "prompt" not in seen
