import sys

sys.path.insert(0, "src")

from veille_ia.collectors import blogs, hn, reddit

for name, collect in [("Hacker News", hn.collect), ("Blogs", blogs.collect), ("Reddit", reddit.collect)]:
    articles = collect()
    print(f"{name}: {len(articles)} articles")
    for a in articles:
        print(f"  [{a.source}] {a.title} ({len(a.text)} chars) {a.url}")
