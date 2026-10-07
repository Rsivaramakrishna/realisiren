from processing.cleaning import (
    clean_book,
    clean_price,
    clean_quote,
    clean_rating,
    clean_tags,
    clean_text,
    normalize_url,
    strip_quotes,
)


def test_clean_text_collapses_whitespace():
    assert clean_text("  Hello \n\xa0 World ") == "Hello World"


def test_clean_text_empty_becomes_none():
    assert clean_text("   ") is None
    assert clean_text(None) is None


def test_strip_quotes_removes_curly_quotes():
    assert strip_quotes("\u201c The world is big. \u201d") == "The world is big."


def test_clean_price():
    assert clean_price("\u00a351.77") == 51.77
    assert clean_price("\u00c2\u00a31,051.00") == 1051.0
    assert clean_price("free") is None
    assert clean_price(None) is None


def test_clean_rating():
    assert clean_rating("star-rating Three") == 3
    assert clean_rating("star-rating") is None
    assert clean_rating(None) is None


def test_clean_tags_sorted_lowercase_unique():
    assert clean_tags(["Love", " books", "love"]) == "books;love"
    assert clean_tags([]) is None


def test_normalize_url():
    assert normalize_url("page-2.html", "https://a.com/x/") == "https://a.com/x/page-2.html"
    assert normalize_url("  https://a.com ") == "https://a.com"
    assert normalize_url(None) is None


def test_clean_book_record():
    raw = {
        "title": " A  Book ",
        "href": "https://books.toscrape.com/a/index.html",
        "price_raw": "\u00a351.77",
        "rating_raw": "star-rating Four",
        "category": "Travel",
        "description": None,
    }
    rec = clean_book(raw, scraped_at="t")
    assert rec["name_or_title"] == "A Book"
    assert rec["price"] == 51.77
    assert rec["rating"] == 4
    assert rec["author"] is None


def test_clean_quote_record():
    raw = {"text": "\u201cHi\u201d", "author": " Ann ", "tags": ["B", "a"], "page_url": "https://quotes.toscrape.com/"}
    rec = clean_quote(raw, scraped_at="t")
    assert rec["name_or_title"] == "Hi"
    assert rec["author"] == "Ann"
    assert rec["tags"] == "a;b"
    assert rec["price"] is None
