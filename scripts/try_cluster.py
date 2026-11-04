import os
import sys

sys.path.insert(0, "src")

from dotenv import load_dotenv

from veille_ia import cluster
from veille_ia.categories import CATEGORIES
from veille_ia.collectors import blogs, hn, reddit
from veille_ia.llm import parse_models

load_dotenv()
models = parse_models(os.environ["LLM_MODELS_CLUSTER"])

category = CATEGORIES["ia"]
articles = (
    hn.enrich(hn.collect(category.hn_keywords))
    + blogs.collect(category.blog_feeds)
    + reddit.collect(category.reddit_feeds)
)
print(f"{len(articles)} articles collectés")

topics = cluster.cluster(articles, models, category)
kept = sum(len(t.articles) for t in topics)
print(f"{len(topics)} sujets, {kept} articles gardés, {len(articles) - kept} écartés")
for topic in topics:
    print(f"\n- {topic.title} ({len(topic.articles)} article(s))")
    for a in topic.articles:
        print(f"    [{a.source}] {a.title}")

kept_ids = {id(a) for t in topics for a in t.articles}
print("\nÉcartés :")
for a in articles:
    if id(a) not in kept_ids:
        print(f"    [{a.source}] {a.title}")
