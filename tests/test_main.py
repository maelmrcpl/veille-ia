import json

from veille_ia import dedup, main
from veille_ia.models import Article

NOW = 1_700_000_000  # 2023-11-14 UTC


def setup(monkeypatch, tmp_path, articles, replies):
    monkeypatch.setenv("LLM_MODELS_CLUSTER", "c:10")
    monkeypatch.setenv("LLM_MODELS_SUMMARY", "s:5")
    monkeypatch.setattr(main, "collect_all", lambda: articles)
    calls = []

    def fake_complete(prompt, models, system=None):
        calls.append(models)
        return replies[len(calls) - 1]

    monkeypatch.setattr(main.llm, "complete", fake_complete)
    monkeypatch.setattr(main.summary, "fetch_text", lambda url: "")
    return calls, str(tmp_path / "ia"), str(tmp_path / "seen.json")


CLUSTER = '{"topics": [{"title": "IPO", "ids": [0, 1]}], "off_topic": [2]}'
SELECT = '{"topics": [{"ids": [0]}]}'
WRITE = '{"topics": [{"id": 0, "title": "Bourse", "text": "Texte parlé."}]}'


def articles():
    return [
        Article("A", "http://a", "HN", NOW, score=50, text="a"),
        Article("B", "http://b", "Reddit", NOW, text="b"),
        Article("C", "http://c", "HN", NOW, text="c"),
    ]


def test_run_writes_report_and_marks_reported_urls_seen(monkeypatch, tmp_path):
    calls, report_dir, seen_path = setup(
        monkeypatch, tmp_path, articles(), [CLUSTER, SELECT, WRITE]
    )
    monkeypatch.setattr(main.summary, "TOPIC_COUNT", 1)
    path = main.run(now=NOW, report_dir=report_dir, seen_path=seen_path)

    assert calls == [[("c", 10)], [("c", 10)], [("s", 5)]]
    with open(path, encoding="utf-8") as file:
        report = json.load(file)
    assert path.endswith(report["date"] + ".json")
    assert report["category"] == "ia"
    assert report["topics"][0]["title"] == "Bourse"
    assert [s["url"] for s in report["topics"][0]["sources"]] == ["http://a", "http://b"]
    assert set(dedup.load_seen(seen_path)) == {"http://a", "http://b"}


def test_run_retries_clustering_when_too_few_topics(monkeypatch, tmp_path):
    many = [Article(f"A{i}", f"http://{i}", "HN", NOW, text="t") for i in range(6)]
    few = '{"topics": [{"title": "X", "ids": [0]}], "off_topic": [1, 2, 3, 4, 5]}'
    full = '{"topics": [], "off_topic": []}'
    calls, report_dir, seen_path = setup(monkeypatch, tmp_path, many, [few, full, SELECT, WRITE])
    main.run(now=NOW, report_dir=report_dir, seen_path=seen_path)
    assert calls == [[("c", 10)], [("c", 10)], [("c", 10)], [("s", 5)]]


def test_run_skips_already_seen_articles(monkeypatch, tmp_path):
    calls, report_dir, seen_path = setup(monkeypatch, tmp_path, articles(), [])
    dedup.mark_seen(articles(), NOW, seen_path)
    assert main.run(now=NOW, report_dir=report_dir, seen_path=seen_path) is None
    assert calls == []


def test_missing_models_variable_raises(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path, [], [])
    monkeypatch.delenv("LLM_MODELS_SUMMARY")
    try:
        main.run(now=NOW, report_dir=str(tmp_path), seen_path=str(tmp_path / "s.json"))
    except main.llm.LLMError as error:
        assert "LLM_MODELS_SUMMARY" in str(error)
    else:
        raise AssertionError("LLMError expected")
