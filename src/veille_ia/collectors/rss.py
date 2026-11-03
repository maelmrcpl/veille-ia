import calendar
import html
import logging
import re
import time

import feedparser
import requests

from veille_ia.models import Article

WINDOW_SECONDS = 24 * 3600
TIMEOUT = 30
HEADERS = {"User-Agent": "veille-ia/0.1"}
MAX_TEXT = 2000

logger = logging.getLogger(__name__)


def clean_text(raw):
    text = re.sub(r"<[^>]+>", " ", raw or "")
    return " ".join(html.unescape(text).split())[:MAX_TEXT]


def entry_timestamp(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    return calendar.timegm(parsed) if parsed else None


def collect_feed(url, source, now=None):
    now = now if now is not None else int(time.time())
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as error:
        logger.warning("Feed %s skipped: %s", source, error)
        return []
    articles = []
    for entry in feedparser.parse(response.content).entries:
        published = entry_timestamp(entry)
        if published is None or published <= now - WINDOW_SECONDS:
            continue
        articles.append(
            Article(
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                source=source,
                published=published,
                text=clean_text(entry.get("summary", "")),
            )
        )
    return articles
