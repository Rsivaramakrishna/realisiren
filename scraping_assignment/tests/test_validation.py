from processing.validation import validate_record


def good():
    return {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/a",
        "name_or_title": "A",
        "price": 10.0,
        "rating": 3,
    }


def test_valid_record():
    assert validate_record(good()) == []


def test_missing_fields_are_reported():
    rec = {**good(), "name_or_title": None, "source_url": "ftp://x", "source": "Other"}
    assert set(validate_record(rec)) == {"missing_name", "invalid_url", "unknown_source"}


def test_bad_price_and_rating():
    assert validate_record({**good(), "price": -1}) == ["invalid_price"]
    assert validate_record({**good(), "rating": 9}) == ["invalid_rating"]


def test_empty_price_and_rating_are_allowed():
    assert validate_record({**good(), "price": None, "rating": None}) == []
