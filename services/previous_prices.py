# services/previuos_prices.py

import json
from config.core.paths import ASSETS_JSONS

PREVIOUS_FILE = ASSETS_JSONS / "previous_prices.json"

def load_previous_prices():
    try:
        text = PREVIOUS_FILE.read_text(encoding="utf-8")
        return json.loads(text)
    except (FileNotFoundError, ValueError):
        return {}

def save_previous_prices(prices: dict):
    ASSETS_JSONS.mkdir(parents=True, exist_ok=True)
    tmp = PREVIOUS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(prices, indent=2), encoding="utf-8")
    tmp.replace(PREVIOUS_FILE)

def update_previous_price(pair: str, price: float):
    rates = load_previous_prices()
    rates[pair] = price
    save_previous_prices(rates)
