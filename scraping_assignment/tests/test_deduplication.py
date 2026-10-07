from processing.deduplication import find_duplicates


def test_duplicates_ignore_case_and_spaces():
    base = {"source": "Books to Scrape", "author": None}
    records = [
        {**base, "name_or_title": "Example Book Title"},
        {**base, "name_or_title": "  Example Book Title "},
        {**base, "name_or_title": "EXAMPLE BOOK TITLE"},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 1 and len(dupes) == 2


def test_quotes_use_author_and_first_50_characters():
    base = {"source": "Quotes to Scrape"}
    text = "x" * 60
    records = [
        {**base, "author": "Ann", "name_or_title": text + "a"},
        {**base, "author": "ann", "name_or_title": text + "b"},
        {**base, "author": "Bob", "name_or_title": text + "a"},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 2 and len(dupes) == 1


def test_same_title_in_different_sources_is_not_duplicate():
    records = [
        {"source": "Books to Scrape", "author": None, "name_or_title": "Hi"},
        {"source": "Quotes to Scrape", "author": None, "name_or_title": "Hi"},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 2 and not dupes
