from dataclasses import dataclass


@dataclass
class Category:
    id: str
    label: str
    topic_count: int
    hn_keywords: list[str]
    blog_feeds: dict[str, str]
    reddit_feeds: dict[str, str]


CATEGORIES = {
    "ia": Category(
        id="ia",
        label="intelligence artificielle",
        topic_count=5,
        hn_keywords=[
            "AI",
            "LLM",
            "GPT",
            "OpenAI",
            "Anthropic",
            "Claude",
            "Gemini",
            "machine learning",
        ],
        blog_feeds={
            "OpenAI": "https://openai.com/news/rss.xml",
            "Hugging Face": "https://huggingface.co/blog/feed.xml",
            "Google AI": "https://blog.google/technology/ai/rss/",
            "Anthropic": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
        },
        reddit_feeds={
            "Reddit r/MachineLearning": "https://www.reddit.com/r/MachineLearning/.rss",
            "Reddit r/LocalLLaMA": "https://www.reddit.com/r/LocalLLaMA/.rss",
        },
    ),
}
