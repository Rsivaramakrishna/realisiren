from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from tests.conftest import book_html, page_html, quote_html

ROOT = "https://books.toscrape.com/"


def test_books_follow_next_links(make_session):
    pages = {
        ROOT: page_html([book_html("One"), book_html("Two")], "catalogue/page-2.html"),
        ROOT + "catalogue/page-2.html": page_html([book_html("Three")]),
    }
    scraper = BooksScraper(session=make_session(pages), fetch_details=False, delay=0)
    records = scraper.scrape()
    assert [r["title"] for r in records] == ["One", "Two", "Three"]
    assert scraper.pages_scraped == 2


def test_failed_page_keeps_earlier_records(make_session):
    pages = {ROOT: page_html([book_html("One")], "page-2.html")}
    scraper = BooksScraper(session=make_session(pages), fetch_details=False, delay=0)
    records = scraper.scrape()
    assert len(records) == 1
    assert scraper.pages_scraped == 1


def test_book_details_are_read(make_session):
    detail = (
        '<ul class="breadcrumb"><li><a>Home</a></li><li><a>Books</a></li>'
        '<li><a>Travel</a></li><li class="active">One</li></ul>'
        '<div id="product_description"></div><p>A short story.</p>'
    )
    pages = {
        ROOT: page_html([book_html("One", href="one/index.html")]),
        ROOT + "one/index.html": detail,
    }
    scraper = BooksScraper(session=make_session(pages), delay=0)
    record = scraper.scrape()[0]
    assert record["category"] == "Travel"
    assert record["description"] == "A short story."


def test_quotes_scraper_reads_tags(make_session):
    url = "https://quotes.toscrape.com/"
    pages = {url: page_html([quote_html("Hi", "Ann", ["a", "b"])])}
    scraper = QuotesScraper(session=make_session(pages), delay=0)
    record = scraper.scrape()[0]
    assert record["author"] == "Ann"
    assert record["tags"] == ["a", "b"]
