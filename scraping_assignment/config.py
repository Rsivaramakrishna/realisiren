from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
DATASET_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"

BOOKS_SOURCE = "Books to Scrape"
QUOTES_SOURCE = "Quotes to Scrape"
VALID_SOURCES = {BOOKS_SOURCE, QUOTES_SOURCE}

BOOKS_URL = "https://books.toscrape.com/"
QUOTES_URL = "https://quotes.toscrape.com/"

COLUMNS = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at",
]
