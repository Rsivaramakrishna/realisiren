import logging
from urllib.parse import urljoin

from config import BOOKS_SOURCE, BOOKS_URL
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BooksScraper(BaseScraper):
    source = BOOKS_SOURCE
    start_url = BOOKS_URL
    item_selector = "article.product_pod"

    def __init__(self, fetch_details=True, **kwargs):
        super().__init__(**kwargs)
        self.fetch_details = fetch_details

    def parse_item(self, article, page_url):
        record = self.parse_book(article, page_url)
        if self.fetch_details and record["href"]:
            record.update(self.parse_details(record["href"]))
        return record

    def parse_book(self, article, page_url):
        link = article.select_one("h3 > a")
        price = article.select_one("p.price_color")
        rating = article.select_one("p.star-rating")
        return {
            "title": link.get("title") if link else None,
            "href": urljoin(page_url, link["href"]) if link and link.get("href") else None,
            "price_raw": price.get_text() if price else None,
            "rating_raw": " ".join(rating.get("class", [])) if rating else None,
            "category": None,
            "description": None,
        }

    def parse_details(self, url):
        soup = self.fetch(url)
        if soup is None:
            return {}
        crumbs = soup.select("ul.breadcrumb li a")
        description = soup.select_one("#product_description + p")
        return {
            "category": crumbs[2].get_text() if len(crumbs) >= 3 else None,
            "description": description.get_text() if description else None,
        }
