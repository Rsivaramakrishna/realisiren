import re
from datetime import datetime, timezone
from urllib.parse import urljoin

from config import BOOKS_SOURCE, QUOTES_SOURCE

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean_text(value):
    if value is None:
        return None
    text = " ".join(value.replace("\xa0", " ").split())
    return text or None


def strip_quotes(value):
    text = clean_text(value)
    if text is None:
        return None
    return clean_text(text.strip("\u201c\u201d\""))


def clean_price(raw):
    if not raw:
        return None
    match = re.search(r"\d+(?:\.\d+)?", raw.replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(raw):
    for word in (raw or "").lower().split():
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(tags):
    cleaned = set()
    for tag in tags or []:
        text = clean_text(tag)
        if text:
            cleaned.add(text.lower())
    return ";".join(sorted(cleaned)) or None


def normalize_url(url, base=None):
    url = clean_text(url)
    if url is None:
        return None
    return urljoin(base, url) if base else url


def clean_book(raw, scraped_at=None):
    return {
        "source": BOOKS_SOURCE,
        "source_url": normalize_url(raw.get("href")),
        "name_or_title": clean_text(raw.get("title")),
        "category": clean_text(raw.get("category")),
        "price": clean_price(raw.get("price_raw")),
        "rating": clean_rating(raw.get("rating_raw")),
        "author": None,
        "tags": None,
        "description": clean_text(raw.get("description")),
        "scraped_at": scraped_at or utc_now(),
    }


def clean_quote(raw, scraped_at=None):
    return {
        "source": QUOTES_SOURCE,
        "source_url": normalize_url(raw.get("page_url")),
        "name_or_title": strip_quotes(raw.get("text")),
        "category": None,
        "price": None,
        "rating": None,
        "author": clean_text(raw.get("author")),
        "tags": clean_tags(raw.get("tags")),
        "description": None,
        "scraped_at": scraped_at or utc_now(),
    }
