#!/usr/bin/env python3
"""
test_fx_pairs.py

Fetches the latest currency pairs from Yahoo Finance, saves to JSON,
and lets you test tickers interactively.
"""

import json
import logging
import sys
import time

import requests
from bs4 import BeautifulSoup

# List of common currencies for fallback
COMMON_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

YAHOO_CURRENCIES_URL = "https://finance.yahoo.com/currencies"
OUTPUT_JSON = "supported_pairs.json"


def load_supported_pairs():
    """
    Scrape Yahoo Finance currencies page for /quote/XXXYYY=X tickers.
    On HTTP 429 or any other failure, falls back to common-currency cross pairs.
    Returns a set of strings like 'EURUSD=X'.
    """
    logging.info("Starting load_supported_pairs()")
    pairs = set()

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        logging.info(f"GET {YAHOO_CURRENCIES_URL}")
        resp = requests.get(YAHOO_CURRENCIES_URL, headers=headers, timeout=5)
        resp.raise_for_status()
        logging.info("Page fetched successfully")

        soup = BeautifulSoup(resp.text, "html.parser")
        anchors = soup.find_all("a", href=True)
        for a in anchors:
            href = a["href"]
            if href.startswith("/quote/") and href.endswith("=X"):
                symbol = href.split("/quote/")[1]
                pairs.add(symbol)

        if pairs:
            logging.info(f"Scraped {len(pairs)} tickers from Yahoo.")
        else:
            # No matches found in HTML—treat as failed scrape
            raise RuntimeError("No tickers found in page HTML")

    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 429:
            logging.warning("Received HTTP 429 Too Many Requests — using fallback list.")
        else:
            logging.error(f"HTTP error {code} fetching currencies: {e}")
    except Exception as e:
        logging.error(f"Failed to fetch/parse page: {e}")

    # Fallback to common‐currency cross‐pair matrix if nothing scraped
    if not pairs:
        logging.info("Building fallback cross-pairs from COMMON_CURRENCIES")
        for b in COMMON_CURRENCIES:
            for t in COMMON_CURRENCIES:
                if b != t:
                    pairs.add(f"{b}{t}=X")
        logging.info(f"Loaded {len(pairs)} fallback cross-pairs.")

    return pairs


def save_to_json(pairs, filename=OUTPUT_JSON):
    """Save the set of pairs to a JSON file."""
    try:
        with open(filename, "w") as f:
            json.dump(sorted(pairs), f, indent=2)
        logging.info(f"Saved {len(pairs)} pairs to {filename}")
    except Exception as e:
        logging.error(f"Failed to save JSON: {e}")


def interactive_test(pairs):
    """
    Prompt loop: user can enter ticker symbols to test membership.
    Commands:
      - list  : show first 20 tickers
      - count : show total count
      - quit  : exit
    """
    logging.info("Entering interactive test loop")
    print("\nType a ticker (e.g. EURUSD=X) to check, 'list' to preview, 'count', or 'quit'.\n")

    while True:
        entry = input(">>> ").strip()
        if not entry:
            continue

        cmd = entry.lower()
        if cmd == "quit":
            break
        elif cmd == "list":
            print("\nSample tickers:")
            for s in sorted(pairs)[:20]:
                print(" ", s)
            print()
        elif cmd == "count":
            print(f"\nTotal pairs loaded: {len(pairs)}\n")
        else:
            status = "✔️ Present" if entry in pairs else "❌ Not found"
            print(f"{entry}: {status}\n")

    logging.info("Exiting interactive loop")


def main():
    pairs = load_supported_pairs()
    if not pairs:
        logging.warning("No pairs loaded — unexpected. Check fallback logic.")
    save_to_json(pairs)
    interactive_test(pairs)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Interrupted by user. Exiting.")
        sys.exit(0)