from veille_ia import dedup
from veille_ia.models import Article


def article(url):
    return Article("T", url, "S", 1)


def test_missing_file_means_nothing_seen(tmp_path):
    path = str(tmp_path / "seen.json")
    assert [a.url for a in dedup.filter_new([article("a")], path)] == ["a"]


def test_marked_urls_are_filtered_out(tmp_path):
    path = str(tmp_path / "seen.json")
    dedup.mark_seen([article("a")], now=1000, path=path)
    new = dedup.filter_new([article("a"), article("b")], path)
    assert [a.url for a in new] == ["b"]


def test_duplicates_in_same_batch_are_removed(tmp_path):
    path = str(tmp_path / "seen.json")
    assert len(dedup.filter_new([article("a"), article("a")], path)) == 1


def test_old_entries_are_purged_and_dirs_created(tmp_path):
    path = str(tmp_path / "data" / "seen.json")
    dedup.mark_seen([article("old")], now=1000, path=path)
    later = 1000 + dedup.RETENTION_SECONDS + 1
    dedup.mark_seen([article("new")], now=later, path=path)
    assert set(dedup.load_seen(path)) == {"new"}
