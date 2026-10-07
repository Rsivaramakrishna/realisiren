from main import process_source
from processing.cleaning import clean_book
from scrapers.books_scraper import BooksScraper
from tests.conftest import book_html, page_html

ROOT = "https://books.toscrape.com/"


def test_counts_add_up(make_session):
    items = [
        book_html("Alpha"),
        book_html("ALPHA "),
        book_html(""),
        book_html("Beta", price="\u00a35.00"),
    ]
    scraper = BooksScraper(session=make_session({ROOT: page_html(items)}), fetch_details=False, delay=0)
    records, stats = process_source(scraper, clean_book)
    assert stats["raw_collected"] == 4
    assert stats["rejected_total"] == 1
    assert stats["rejected_by_reason"] == {"missing_name": 1}
    assert stats["duplicates"] == 1
    assert stats["final"] == len(records) == 2
    assert stats["raw_collected"] - stats["rejected_total"] - stats["duplicates"] == stats["final"]
