from veille_ia.collectors.rss import collect_feed


def collect(feeds, now=None):
    articles = []
    for source, url in feeds.items():
        articles.extend(collect_feed(url, source, now))
    return articles
