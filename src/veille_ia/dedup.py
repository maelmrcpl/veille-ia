import json
import os
import time

SEEN_PATH = os.path.join("data", "seen_urls.json")
RETENTION_SECONDS = 14 * 24 * 3600


def load_seen(path=SEEN_PATH):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def filter_new(articles, path=SEEN_PATH):
    seen = load_seen(path)
    new = []
    batch = set()
    for article in articles:
        if article.url in seen or article.url in batch:
            continue
        batch.add(article.url)
        new.append(article)
    return new


def mark_seen(articles, now=None, path=SEEN_PATH):
    now = now if now is not None else int(time.time())
    seen = {
        url: seen_at
        for url, seen_at in load_seen(path).items()
        if seen_at > now - RETENTION_SECONDS
    }
    for article in articles:
        seen[article.url] = now
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(seen, file, indent=2)
