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
    "cyber": Category(
        id="cyber",
        label="cybersécurité",
        topic_count=4,
        hn_keywords=[
            "security",
            "cybersecurity",
            "vulnerability",
            "ransomware",
            "breach",
            "malware",
            "exploit",
            "zero-day",
            "phishing",
            "hackers",
        ],
        blog_feeds={
            "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
            "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
            "SecurityWeek": "https://feeds.feedburner.com/securityweek",
            "Dark Reading": "https://www.darkreading.com/rss.xml",
            "Krebs on Security": "https://krebsonsecurity.com/feed/",
            "Schneier on Security": "https://www.schneier.com/feed/atom/",
        },
        reddit_feeds={
            "Reddit r/netsec": "https://www.reddit.com/r/netsec/.rss",
            "Reddit r/cybersecurity": "https://www.reddit.com/r/cybersecurity/.rss",
        },
    ),
    "cloud": Category(
        id="cloud",
        label="cloud, DevOps et infrastructure informatique",
        topic_count=2,
        hn_keywords=[
            "kubernetes",
            "devops",
            "cloud",
            "Docker",
            "Terraform",
            "outage",
            "infrastructure",
            "Cloudflare",
            "Azure",
            "serverless",
        ],
        blog_feeds={
            "AWS News Blog": "https://aws.amazon.com/blogs/aws/feed/",
            "Google Cloud": "https://cloudblog.withgoogle.com/rss/",
            "Azure": "https://azure.microsoft.com/en-us/blog/feed/",
            "Kubernetes": "https://kubernetes.io/feed.xml",
            "CNCF": "https://www.cncf.io/feed/",
            "Cloudflare": "https://blog.cloudflare.com/rss/",
            "Docker": "https://www.docker.com/blog/feed/",
            "GitHub": "https://github.blog/feed/",
            "The New Stack": "https://thenewstack.io/feed/",
            "InfoQ": "https://feed.infoq.com/",
        },
        reddit_feeds={
            "Reddit r/devops": "https://www.reddit.com/r/devops/.rss",
            "Reddit r/kubernetes": "https://www.reddit.com/r/kubernetes/.rss",
        },
    ),
}
