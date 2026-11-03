from veille_ia.collectors.rss import collect_feed

FEEDS = {
    "Reddit r/MachineLearning": "https://www.reddit.com/r/MachineLearning/.rss",
    "Reddit r/LocalLLaMA": "https://www.reddit.com/r/LocalLLaMA/.rss",
}


def collect(now=None):
    articles = []
    for source, url in FEEDS.items():
        articles.extend(collect_feed(url, source, now))
    return articles
