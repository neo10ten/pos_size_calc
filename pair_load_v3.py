#!/usr/bin/env python3
"""
pair_load_v3.py

Fetches FX rate for base→target via Frankfurter.app (primary),
then floatrates.com (fallback), then tries reverse‐invert (final fallback).

Saves raw JSON to frank_json.json and float_json.json.
"""

import sys
import json
import logging
import requests

# Endpoints
FRANK_URL = "https://api.frankfurter.app/latest"
FLOAT_URL = "https://www.floatrates.com/daily/{base}.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def get_frankfurter(base: str, target: str):
    """Primary source: Frankfurter.app"""
    resp = requests.get(FRANK_URL, params={"from": base, "to": target}, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    with open("frank_json.json", "w") as f:
        json.dump(data, f, indent=2)
    return data.get("rates", {}).get(target)


def get_floatrates(base: str, target: str):
    """Secondary source: floatrates.com"""
    url = FLOAT_URL.format(base=base.lower())
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    with open("float_json.json", "w") as f:
        json.dump(data, f, indent=2)
    entry = data.get(target.lower())
    return entry.get("rate") if entry else None


def test_pair(base: str, target: str):
    print(f"\n=== Testing rate {base} → {target} ===")
    rate = None

    # 1) Frankfurter.app primary
    try:
        rate = get_frankfurter(base, target)
        print(f"Frankfurter.app rate: {rate}")
    except Exception as e:
        logging.error(f"Frankfurter error: {e}")

    # 2) floatrates.com fallback
    if rate is None:
        try:
            rate = get_floatrates(base, target)
            print(f"floatrates.com rate: {rate}")
        except Exception as e:
            logging.error(f"floatrates.com error: {e}")

    # 3) Reverse‐invert final fallback
    if rate is None:
        try:
            inv = get_floatrates(target, base)
            if inv:
                rate = 1.0 / inv
                print(f"Inverted {target}→{base} rate: {rate}")
        except Exception:
            pass

    # Result
    if rate is None:
        print("❌ No rate found or could not invert.")
    else:
        print(f"✅ Final rate used: {rate}")


def main():
    if len(sys.argv) >= 3:
        b, t = sys.argv[1].upper(), sys.argv[2].upper()
    else:
        b = input("Base (e.g. GBP): ").strip().upper()
        t = input("Target (e.g. USD): ").strip().upper()
    test_pair(b, t)


if __name__ == "__main__":
    main()