# Web Scraping ETL Pipeline

Scrapes Books to Scrape and Quotes to Scrape, cleans and validates the data, removes duplicates, and writes one CSV plus a JSON summary and a log.

## Setup

Tested with Python 3.9 and 3.12 (works on 3.9 to 3.12).

```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```
python main.py
```

Optional: `python main.py --skip-details` skips the 1,000 book detail pages. It is much faster, but `category` and `description` stay empty for books.

Tests (no internet needed):

```
pytest
```

Outputs:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

A full run with book detail pages makes about 1,060 requests with a 0.5 second pause each, so expect roughly 10 minutes.

## How it works

```
Scrape -> Clean -> Validate -> Deduplicate -> Consolidate -> Save
```

- `scrapers/` talks to the websites. `base_scraper.py` holds the session, retries, timeout, pause, and the pagination loop. The two scrapers hold only their own selectors.
- `processing/` only transforms data: `cleaning.py`, `validation.py`, `deduplication.py`.
- `main.py` connects the stages and writes the files.
- `config.py` holds source names, URLs, paths, and the column order.

## Website observations

| Item | Books to Scrape | Quotes to Scrape |
| --- | --- | --- |
| One record | `article.product_pod` | `div.quote` |
| Main text | `h3 > a`, full title in the `title` attribute | `span.text` |
| Price | `p.price_color` | none |
| Rating | class on `p.star-rating` | none |
| Author | none | `small.author` |
| Tags | none | `a.tag` |
| Category | breadcrumb on the detail page | none |
| Description | `#product_description + p` on the detail page | none |
| Next page | `li.next > a` | `li.next > a` |

## Pagination

Each scraper starts at the home page, parses the records, then reads `li.next > a` and joins its relative link with `urljoin`. It stops when there is no next link. Page numbers are never hard-coded. A set of visited URLs prevents an endless loop.

## Data model

| Column | Books | Quotes |
| --- | --- | --- |
| `source` | Books to Scrape | Quotes to Scrape |
| `source_url` | Book detail page URL | Page URL where the quote appeared |
| `name_or_title` | Title | Quote text without curly quotes |
| `category` | From detail page | Empty |
| `price` | Number | Empty |
| `rating` | 1 to 5 | Empty |
| `author` | Empty | Author name |
| `tags` | Empty | `tag1;tag2` (lowercase, sorted) |
| `description` | From detail page | Empty |
| `scraped_at` | UTC timestamp | UTC timestamp |

Fields that do not apply are left empty. No fake values are used.

## Cleaning

Small functions in `cleaning.py`: `clean_text` (extra spaces, newlines, `\xa0`), `strip_quotes`, `clean_price`, `clean_rating`, `clean_tags`, `normalize_url`. Page encoding is set to UTF-8 so the `£` sign is read correctly.

## Validation

`validate_record` returns a list of problems. An empty list means valid. Rules: known source, non-empty name, URL starts with http or https, price is a number of 0 or more if present, rating is 1 to 5 if present. Rejected records are logged as warnings and counted by reason. A record with two problems is counted once in `rejected_total` and once for each reason in `rejected_by_reason`.

## Duplicate detection

A fingerprint is a SHA-256 hash of the normalized key (lowercase, punctuation removed, spaces collapsed).

- Books: source + title
- Quotes: source + author + first 50 characters of the quote text

Duplicates are removed, not flagged, because the final file should have one row per real item. They are counted in the summary and logged. The real sites have no duplicates, so `tests/test_deduplication.py` proves the logic with sample data.

## Error handling

- Requests use a 10 second timeout and 3 retries with backoff for HTTP 429, 500, 502, 503, 504.
- A failed page is logged and that source stops. Records collected before the failure are kept.
- One bad record is logged and skipped. It is counted in `parse_errors`.
- A failed book detail page is logged and the book keeps empty category and description.
- Each source runs in its own `try/except`, so one source failing does not stop the other.

## Summary report

Per source: pages scraped, raw collected, parse errors, cleaned, rejected (total and by reason), duplicates, final. Plus totals, start time, end time, and duration. The numbers add up: raw collected - rejected - duplicates = final. `main.py` logs a warning if they do not.

## Assumptions and limitations

- `source_url` for quotes is the listing page, not the author page.
- A price that cannot be parsed becomes empty and is not rejected.
- Book detail pages roughly double the run time.
- The selectors match the current practice sites. If their layout changes, only the scraper files need to change.
