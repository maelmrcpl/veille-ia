import json
import os
import sys
import time

from dotenv import load_dotenv

from veille_ia import cluster, dedup, llm, summary
from veille_ia.categories import CATEGORIES
from veille_ia.collectors import blogs, hn, reddit

DATA_DIR = "data"


def models_from_env(name):
    value = os.environ.get(name)
    if not value:
        raise llm.LLMError(f"Missing environment variable {name}")
    return llm.parse_models(value)


def collect_all(category):
    return (
        hn.enrich(hn.collect(category.hn_keywords))
        + blogs.collect(category.blog_feeds)
        + reddit.collect(category.reddit_feeds)
    )


def run(category, now=None, report_dir=None, seen_path=dedup.SEEN_PATH):
    now = now if now is not None else int(time.time())
    report_dir = report_dir or os.path.join(DATA_DIR, category.id)
    models_cluster = models_from_env("LLM_MODELS_CLUSTER")
    models_summary = models_from_env("LLM_MODELS_SUMMARY")

    articles = dedup.filter_new(collect_all(category), seen_path)
    candidates = []
    for _ in range(2):
        candidates = summary.select_candidates(
            cluster.cluster(articles, models_cluster, category), category
        )
        if len(candidates) >= category.topic_count:
            break
    topics = summary.summarize(candidates, category, models_cluster, models_summary)
    if not topics:
        return None

    date = time.strftime("%Y-%m-%d", time.localtime(now))
    report = {"date": date, "category": category.id, "topics": topics}
    os.makedirs(report_dir, exist_ok=True)
    path = os.path.join(report_dir, f"{date}.json")
    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    reported_urls = {s["url"] for t in topics for s in t["sources"]}
    dedup.mark_seen([a for a in articles if a.url in reported_urls], now, seen_path)
    return path


def main(ids=None):
    load_dotenv()
    failed = []
    for category in [CATEGORIES[i] for i in ids] if ids else CATEGORIES.values():
        try:
            path = run(category)
        except Exception as error:
            print(f"{category.id} : échec : {error}")
            failed.append(category.id)
            continue
        if path is None:
            print(f"{category.id} : aucun nouvel article, aucun fichier écrit.")
            continue
        with open(path, encoding="utf-8") as file:
            topics = json.load(file)["topics"]
        words = sum(len(t["text"].split()) for t in topics)
        print(f"{path} : {len(topics)} sujets, {words} mots")
    if failed:
        sys.exit(1)
