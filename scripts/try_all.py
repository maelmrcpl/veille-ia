import sys

sys.path.insert(0, "src")

from veille_ia.categories import CATEGORIES
from veille_ia.collectors import blogs, hn, reddit

category = CATEGORIES["ia"]
sources = [
    ("Hacker News", lambda: hn.collect(category.hn_keywords)),
    ("Blogs", lambda: blogs.collect(category.blog_feeds)),
    ("Reddit", lambda: reddit.collect(category.reddit_feeds)),
]
for name, collect in sources:
    articles = collect()
    print(f"{name}: {len(articles)} articles")
    for a in articles:
        print(f"  [{a.source}] {a.title} ({len(a.text)} chars) {a.url}")
