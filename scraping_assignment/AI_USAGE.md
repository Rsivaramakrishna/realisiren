# AI Usage

Fill in the parts marked FILL before submitting. This file must be honest and in your own words.

## Tools used

- Claude (Anthropic), used to draft the project structure, the scrapers, the processing modules, the tests, and the README.

## What AI was used for

- Drafting the first version of all modules in `scrapers/` and `processing/`
- Writing the unit tests
- Writing the README

## Real prompts

FILL: paste 2 or 3 prompts you actually sent.

## What I changed after reviewing the output

FILL: list what you changed or decided yourself (for example: kept the pagination loop in `base_scraper.py`, chose to remove duplicates instead of flagging them, chose to fetch book detail pages).

## Mistakes found in AI suggestions

FILL: write any mistakes you found while reading and running the code.

## How I tested the final code

- Ran `pytest` (unit tests for cleaning, validation, deduplication, scrapers with fake pages, and the count reconciliation)
- FILL: write that you ran `python main.py` from a fresh virtual environment, and the row count you got in the CSV compared with `summary_report.json`
