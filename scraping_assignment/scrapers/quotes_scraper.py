from config import QUOTES_SOURCE, QUOTES_URL
from scrapers.base_scraper import BaseScraper


class QuotesScraper(BaseScraper):
    source = QUOTES_SOURCE
    start_url = QUOTES_URL
    item_selector = "div.quote"

    def parse_item(self, block, page_url):
        text = block.select_one("span.text")
        author = block.select_one("small.author")
        return {
            "text": text.get_text() if text else None,
            "author": author.get_text() if author else None,
            "tags": [tag.get_text() for tag in block.select("a.tag")],
            "page_url": page_url,
        }
