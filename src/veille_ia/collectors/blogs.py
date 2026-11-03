from veille_ia.collectors.rss import collect_feed

FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
    "Anthropic": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
}


def collect(now=None):
    articles = []
    for source, url in FEEDS.items():
        articles.extend(collect_feed(url, source, now))
    return articles
