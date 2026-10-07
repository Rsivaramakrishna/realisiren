import argparse
import csv
import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone

from config import COLUMNS, DATASET_PATH, LOG_DIR, LOG_PATH, OUTPUT_DIR, SUMMARY_PATH
from processing.cleaning import clean_book, clean_quote
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

logger = logging.getLogger("main")


def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
    )


def process_source(scraper, cleaner):
    try:
        raw = scraper.scrape()
    except Exception:
        logger.exception("Scraping failed for %s", scraper.source)
        raw = []

    reasons = Counter()
    rejected_total = 0
    cleaned_count = 0
    valid = []
    for item in raw:
        try:
            record = cleaner(item)
        except Exception:
            logger.exception("Cleaning failed for %s", item)
            reasons["clean_error"] += 1
            rejected_total += 1
            continue
        cleaned_count += 1
        problems = validate_record(record)
        if problems:
            rejected_total += 1
            reasons.update(problems)
            logger.warning("Rejected %s record %r: %s", scraper.source, record.get("name_or_title"), problems)
            continue
        valid.append(record)

    unique, dupes = find_duplicates(valid)
    for rec in dupes:
        logger.warning("Duplicate removed: %r", rec["name_or_title"])

    stats = {
        "pages_scraped": scraper.pages_scraped,
        "raw_collected": len(raw),
        "parse_errors": scraper.parse_errors,
        "cleaned": cleaned_count,
        "rejected_total": rejected_total,
        "rejected_by_reason": dict(reasons),
        "duplicates": len(dupes),
        "final": len(unique),
    }
    return unique, stats


def write_csv(records):
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(DATASET_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def write_summary(summary):
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-details", action="store_true", help="skip book detail pages (faster, category and description stay empty)")
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()
    started = datetime.now(timezone.utc)
    timer = time.perf_counter()

    sources = [
        (BooksScraper(fetch_details=not args.skip_details), clean_book),
        (QuotesScraper(), clean_quote),
    ]
    final, per_source = [], {}
    for scraper, cleaner in sources:
        try:
            records, stats = process_source(scraper, cleaner)
        except Exception:
            logger.exception("Source %s failed", scraper.source)
            continue
        final.extend(records)
        per_source[scraper.source] = stats

    raw_total = sum(s["raw_collected"] for s in per_source.values())
    rejected_total = sum(s["rejected_total"] for s in per_source.values())
    duplicate_total = sum(s["duplicates"] for s in per_source.values())
    if raw_total - rejected_total - duplicate_total != len(final):
        logger.warning("Summary counts do not add up")

    write_csv(final)
    write_summary({
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duration_seconds": round(time.perf_counter() - timer, 2),
        "sources": per_source,
        "totals": {
            "raw_collected": raw_total,
            "rejected": rejected_total,
            "duplicates": duplicate_total,
            "final_record_count": len(final),
        },
    })
    logger.info("Finished: %d records written to %s", len(final), DATASET_PATH)


if __name__ == "__main__":
    main()
