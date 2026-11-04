from veille_ia.categories import CATEGORIES


def test_each_category_is_complete_and_keyed_by_its_id():
    for key, category in CATEGORIES.items():
        assert category.id == key
        assert category.label
        assert category.topic_count > 0
        assert category.hn_keywords
        assert category.blog_feeds
        assert category.reddit_feeds
