# assets/__init__.py

from .paths import ASSETS_JSONS

from .loader import (
    load_currencies,
    load_pairs_split,
    load_other_instruments
    )

from .updater import (
    REMOTE_VERSION_URL,
    download_assets
)

from .previous_prices import (
    load_previous_prices,
    save_previous_prices,
    update_previous_price
)

CURRENCIES = load_currencies()
STANDARD_SET, OTHER_PAIRS = load_pairs_split()
OTHER_INSTRUMENTS = load_other_instruments()