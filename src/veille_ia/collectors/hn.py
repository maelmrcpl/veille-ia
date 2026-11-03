import time

import requests

from veille_ia.fulltext import fetch_text
from veille_ia.models import Article

SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"
KEYWORDS = [
    "AI",
    "LLM",
    "GPT",
    "OpenAI",
    "Anthropic",
    "Claude",
    "Gemini",
    "machine learning",
]
MIN_POINTS = 20
WINDOW_SECONDS = 24 * 3600
TIMEOUT = 30


def search_stories(keyword, now):
    response = requests.get(
        SEARCH_URL,
        params={
            "query": keyword,
            "tags": "story",
            "numericFilters": f"created_at_i>{now - WINDOW_SECONDS},points>={MIN_POINTS}",
            "hitsPerPage": 50,
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["hits"]


def collect(now=None):
    now = now if now is not None else int(time.time())
    articles = {}
    for keyword in KEYWORDS:
        for hit in search_stories(keyword, now):
            story_id = hit["objectID"]
            if story_id in articles:
                continue
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
            articles[story_id] = Article(
                title=hit["title"],
                url=url,
                source="Hacker News",
                published=hit["created_at_i"],
                score=hit.get("points") or 0,
            )
    return sorted(articles.values(), key=lambda a: a.score, reverse=True)


def enrich(articles):
    for article in articles:
        if "news.ycombinator.com/item" in article.url:
            continue
        article.text = fetch_text(article.url)
    return articles
