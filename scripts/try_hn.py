import sys

sys.path.insert(0, "src")

from veille_ia.collectors import hn

articles = hn.enrich(hn.collect())
print(f"{len(articles)} articles")
for a in articles:
    print(f"[{a.score:>4}] {a.title} ({len(a.text)} chars) {a.url}")
