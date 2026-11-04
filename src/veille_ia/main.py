import json
import os
import time

from dotenv import load_dotenv

from veille_ia import cluster, dedup, llm, summary
from veille_ia.collectors import blogs, hn, reddit

REPORT_DIR = os.path.join("data", "ia")


def models_from_env(name):
    value = os.environ.get(name)
    if not value:
        raise llm.LLMError(f"Missing environment variable {name}")
    return llm.parse_models(value)


def collect_all():
    return hn.enrich(hn.collect()) + blogs.collect() + reddit.collect()


def run(now=None, report_dir=REPORT_DIR, seen_path=dedup.SEEN_PATH):
    now = now if now is not None else int(time.time())
    models_cluster = models_from_env("LLM_MODELS_CLUSTER")
    models_summary = models_from_env("LLM_MODELS_SUMMARY")

    articles = dedup.filter_new(collect_all(), seen_path)
    candidates = []
    for _ in range(2):
        candidates = summary.select_candidates(cluster.cluster(articles, models_cluster))
        if len(candidates) >= summary.TOPIC_COUNT:
            break
    topics = summary.summarize(candidates, models_cluster, models_summary)
    if not topics:
        return None

    date = time.strftime("%Y-%m-%d", time.localtime(now))
    report = {"date": date, "category": "ia", "topics": topics}
    os.makedirs(report_dir, exist_ok=True)
    path = os.path.join(report_dir, f"{date}.json")
    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    reported_urls = {s["url"] for t in topics for s in t["sources"]}
    dedup.mark_seen([a for a in articles if a.url in reported_urls], now, seen_path)
    return path


def main():
    load_dotenv()
    path = run()
    if path is None:
        print("Aucun nouvel article : aucun fichier écrit.")
        return
    with open(path, encoding="utf-8") as file:
        topics = json.load(file)["topics"]
    words = sum(len(t["text"].split()) for t in topics)
    print(f"{path} : {len(topics)} sujets, {words} mots")
