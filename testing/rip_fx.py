"""
rip_fx.py

1. Fetch Frankfurter.app currency list → assets/currencies.json
2. Build cross-pairs → assets/pairs.json
3. Load assets/oanda_inst.json → filter type CURRENCY → commonly_tradeable list
4. Split pairs.json into:
     - standard (in commonly_tradeable)
     - other    (all others)
   → assets/pairs_split.json
"""

import os
import json
import logging
import requests
from .assets import *
# Frankfurter endpoint
CURRENCIES_URL = "https://api.frankfurter.app/currencies"

# Asset paths
ASSETS_DIR      = "assets"
CURRENCIES_FILE = "currencies.json"
PAIRS_FILE      = "pairs.json"
PAIRS_SPLIT     = "pairs_split.json"
OANDA_FILE      = os.path.join(ASSETS_DIR, "oanda_inst.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # 1) Fetch Frankfurter currencies
    logging.info("Fetching currencies from Frankfurter.app")
    resp = requests.get(CURRENCIES_URL, timeout=5)
    resp.raise_for_status()
    currencies_map = resp.json()  # e.g. {"USD":"US Dollar", ...}
    currencies = sorted(currencies_map.keys())
    with open(os.path.join(ASSETS_DIR, CURRENCIES_FILE), "w") as f:
        json.dump(currencies, f, indent=2)
    logging.info(f"Wrote {len(currencies)} currencies to {CURRENCIES_FILE}")

    # 2) Build full cross-pair list
    pairs = [b + q for b in currencies for q in currencies if b != q]
    with open(os.path.join(ASSETS_DIR, PAIRS_FILE), "w") as f:
        json.dump(sorted(pairs), f, indent=2)
    logging.info(f"Wrote {len(pairs)} pairs to {PAIRS_FILE}")

    # 3) Load OANDA instruments and filter CURRENCY types
    logging.info(f"Loading OANDA instruments from {OANDA_FILE}")
    try:
        with open(OANDA_FILE, "r") as f:
            oanda = json.load(f).get("instruments", [])
    except Exception as e:
        logging.error(f"Failed to load {OANDA_FILE}: {e}")
        oanda = []

    commonly_tradeable = []
    for inst in oanda:
        if inst.get("type", "").upper() == "CURRENCY":
            disp = inst.get("displayName", "")
            # e.g. "USD/THB" → "USDTHB"
            code = disp.replace("/", "").upper()
            commonly_tradeable.append(code)

    commonly_tradeable = sorted(set(commonly_tradeable))
    logging.info(f"Found {len(commonly_tradeable)} commonly tradeable currencies")

    # 4) Split pairs into standard vs other
    standard = [p for p in pairs if p in commonly_tradeable]
    other    = [p for p in pairs if p not in commonly_tradeable]
    split = {"standard": sorted(standard), "other": sorted(other)}

    with open(os.path.join(ASSETS_DIR, PAIRS_SPLIT), "w") as f:
        json.dump(split, f, indent=2)
    logging.info(
        f"Wrote pairs_split.json: {len(standard)} standard, {len(other)} other"
    )


if __name__ == "__main__":
    main()