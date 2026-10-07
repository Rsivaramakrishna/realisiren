import logging
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "ScrapingAssignment/1.0 (learning project)"})
    retries = Retry(total=3, backoff_factor=1.0, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class BaseScraper:
    source = ""
    start_url = ""
    item_selector = ""

    def __init__(self, session=None, delay=0.5, timeout=10):
        self.session = session or create_session()
        self.delay = delay
        self.timeout = timeout
        self.pages_scraped = 0
        self.parse_errors = 0

    def fetch(self, url):
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None
        response.encoding = "utf-8"
        time.sleep(self.delay)
        return BeautifulSoup(response.text, "lxml")

    def parse_item(self, item, page_url):
        raise NotImplementedError

    def parse_page(self, soup, page_url):
        records = []
        for item in soup.select(self.item_selector):
            try:
                records.append(self.parse_item(item, page_url))
            except Exception:
                self.parse_errors += 1
                logger.exception("Could not parse a record on %s", page_url)
        return records

    def scrape(self):
        records = []
        visited = set()
        url = self.start_url
        while url and url not in visited:
            visited.add(url)
            logger.info("%s page %d: %s", self.source, len(visited), url)
            soup = self.fetch(url)
            if soup is None:
                break
            self.pages_scraped += 1
            records.extend(self.parse_page(soup, url))
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
        logger.info("%s done: %d records from %d pages", self.source, len(records), self.pages_scraped)
        return records
