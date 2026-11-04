from dataclasses import replace

import pytest

from veille_ia import llm, summary
from veille_ia.categories import CATEGORIES
from veille_ia.models import Article, Topic

MODELS = [("m", 10)]
CATEGORY = replace(CATEGORIES["ia"], topic_count=6)


def topic(title, *articles):
    return Topic(title, list(articles))


def art(source, url="http://x", score=0, text="body", title=None):
    return Article(title or f"T {url}", url, source, 1, score=score, text=text)


def fake_llm(monkeypatch, *replies):
    prompts = []

    def fake_complete(prompt, models, system=None):
        prompts.append(prompt)
        return replies[len(prompts) - 1]

    monkeypatch.setattr(summary.llm, "complete", fake_complete)
    return prompts


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(summary, "fetch_text", lambda url: "")


def test_ranking_puts_multi_source_then_official_blogs_then_score_and_discussions_last():
    discussion = topic("d", art("Reddit", "1", title="Question [D]"))
    multi = topic("multi", art("Hacker News", "2"), art("Reddit", "3"))
    blog = topic("blog", art("OpenAI", "4"))
    high = topic("high", art("Hacker News", "5", score=500))
    ranked = summary.select_candidates([discussion, high, blog, multi], CATEGORY)
    assert [t.title for t in ranked] == ["multi", "blog", "high", "d"]


def test_candidates_are_capped():
    topics = [topic(str(i), art("A", str(i))) for i in range(30)]
    assert len(summary.select_candidates(topics, CATEGORY)) == summary.MAX_CANDIDATES


def test_choose_keeps_llm_order_and_merges(monkeypatch):
    cands = [topic(str(i), art("S", str(i))) for i in range(8)]
    fake_llm(monkeypatch, '{"topics": [{"ids": [3, 1]}, {"ids": [0]}, {"ids": [2]},'
             ' {"ids": [4]}, {"ids": [5]}, {"ids": [6]}, {"ids": [7]}]}')
    assert summary.choose(cands, MODELS, CATEGORY) == [[3, 1], [0], [2], [4], [5], [6]]


def test_choose_fills_up_to_topic_count_in_candidate_order(monkeypatch):
    cands = [topic(str(i), art("S", str(i))) for i in range(8)]
    fake_llm(monkeypatch, '{"topics": [{"ids": [5]}, {"ids": [9, "x"]}, {"ids": [5]}]}')
    assert summary.choose(cands, MODELS, CATEGORY) == [[5], [0], [1], [2], [3], [4]]


def test_choose_with_few_candidates_keeps_them_all(monkeypatch):
    cands = [topic(str(i), art("S", str(i))) for i in range(3)]
    fake_llm(monkeypatch, '{"topics": []}')
    assert summary.choose(cands, MODELS, CATEGORY) == [[0], [1], [2]]


def test_fetch_full_texts_keeps_longer_text_and_skips_hn_items(monkeypatch):
    monkeypatch.setattr(summary, "fetch_text", lambda url: "full text" if "long" in url else "")
    longer = art("S", "http://long", text="short")
    blocked = art("S", "http://blocked", text="extract")
    hn_item = art("HN", "https://news.ycombinator.com/item?id=1", text="")
    summary.fetch_full_texts([longer, blocked, hn_item])
    assert (longer.text, blocked.text, hn_item.text) == ("full text", "extract", "")


def test_summarize_writes_chosen_topics_with_full_texts_and_all_sources(monkeypatch):
    monkeypatch.setattr(summary, "fetch_text", lambda url: f"full {url} " * 5)
    category = replace(CATEGORY, topic_count=2)
    cands = [
        topic("A", art("S1", "http://1")),
        topic("B", art("S2", "http://2")),
        topic("C", art("S3", "http://3")),
    ]
    prompts = fake_llm(
        monkeypatch,
        '{"topics": [{"ids": [2, 0]}, {"ids": [1]}]}',
        '{"topics": [{"id": 1, "title": "Titre B", "text": "Texte B."},'
        ' {"id": 0, "title": "Titre CA", "text": "Texte CA."}]}',
    )
    result = summary.summarize(cands, category, MODELS, MODELS)
    assert "full http://3" in prompts[1]
    assert [t["title"] for t in result] == ["Titre CA", "Titre B"]
    assert [t["rank"] for t in result] == [1, 2]
    assert [s["url"] for s in result[0]["sources"]] == ["http://3", "http://1"]
    assert set(result[0]["sources"][0]) == {"name", "title", "url"}


def test_write_prompt_limits_articles_and_text():
    group = [art("S", str(i), text="x" * 9000) for i in range(5)]
    prompt = summary.build_write_prompt([group], CATEGORY)
    assert prompt.count("(S)") == summary.ARTICLES_PER_TOPIC
    assert "x" * (summary.TEXT_CHARS + 1) not in prompt


def test_spoken_text_has_no_links_or_markdown(monkeypatch):
    fake_llm(monkeypatch, '{"topics": [{"id": 0, "title": "T", "text": "**Voir** https://a.com/x [ici]\\nsuite"}]}')
    result = summary.write([[art("S")]], MODELS, CATEGORY)
    assert result[0]["text"] == "Voir ici suite"


def test_write_ignores_invalid_duplicate_and_empty_items(monkeypatch):
    fake_llm(
        monkeypatch,
        '{"topics": [{"id": 9, "text": "x"}, {"id": 0, "text": ""}, {"id": 0, "text": "ok"},'
        ' {"id": 0, "text": "again"}]}',
    )
    result = summary.write([[art("S", title="Original")]], MODELS, CATEGORY)
    assert len(result) == 1
    assert result[0]["text"] == "ok"
    assert result[0]["title"] == "Original"


def test_invalid_json_or_no_usable_topic_raises(monkeypatch):
    fake_llm(monkeypatch, "nope")
    with pytest.raises(llm.LLMError):
        summary.write([[art("S")]], MODELS, CATEGORY)
    fake_llm(monkeypatch, '{"topics": []}')
    with pytest.raises(llm.LLMError):
        summary.write([[art("S")]], MODELS, CATEGORY)


def test_no_candidates_makes_no_llm_call(monkeypatch):
    prompts = fake_llm(monkeypatch)
    assert summary.summarize([], CATEGORY, MODELS, MODELS) == []
    assert prompts == []
