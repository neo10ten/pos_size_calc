# tool_classes/asset_controller.py

from ..config.core.constants import REMOTE_VERSION_URL
from ..config.core.paths import ASSETS_DIR
from ..services.loader import load_currencies, load_pairs_split, load_other_instruments

class AssetController:
    
    ''''
    Controlls all aspects for assets - includes loading, updating, saving.
    '''
    
    def __init__(self):
        self.assets_dir = ASSETS_DIR
        self.version_url = REMOTE_VERSION_URL
        self._currencies = None
        self._standard_pairs = None
        self._other_pairs = None
        self._other_instruments = None

    @property
    def currencies(self) -> dict:
        if self._currencies is None:
            self._currencies = load_currencies(self.assets_dir)
        return self._currencies

    @property
    def standard_pairs(self) -> set:
        if self._standard_pairs is None:
            std, oth = load_pairs_split(self.assets_dir)
            self._standard_pairs, self._other_pairs = std, oth
        return self._standard_pairs

    @property
    def other_pairs(self) -> set:
        if self._other_pairs is None:
            _ = self.standard_pairs
        return self._other_pairs

    @property
    def other_instruments(self) -> set:
        if self._other_instruments is None:
            self._other_instruments = load_other_instruments(self.assets_dir)
        return self._other_instruments

    def refresh(self):
        self._currencies = None
        self._standard_pairs = None
        self._other_pairs = None
        self._other_instruments = None

#############################################################################################

# tool_classes/asset_controller.py

import json

from services.previous_prices import load_previous_prices, update_previous_price
import services.updater as updater
from config.core.paths import ASSETS_JSONS


class AssetController:
    def __init__(self, main_controller=None):
        self.main_controller = main_controller
        self.asset_version = None
        self.currencies = {}
        self.pairs = {}
        self.inst2 = {}
        self.previous_prices = {}
        self.load_all_assets()

    def load_all_assets(self):
        """
        Read every JSON into memory.
        """
        try:
            base = ASSETS_JSONS
            self.asset_version = json.loads((base / "asset_version.json").read_text())
            self.currencies = json.loads((base / "currencies.json").read_text())
            self.pairs = json.loads((base / "pairs_split.json").read_text())
            self.inst2 = json.loads((base / "oanda_inst2.json").read_text())
            self.previous_prices = load_previous_prices()
        except Exception:
            pass

    def refresh_assets_and_ui(self):
        """
        Re-load disk JSONs and notify the main controller to update its view.
        """
        self.load_all_assets()
        if self.main_controller:
            self.main_controller.on_assets_refreshed()

    def start_update_check(self):
        """
        Called by the UI or MainController startup to kick off version checking.
        """
        updater.check_for_version_update(self)

    def update_assets(self, remote_version: str):
        """
        Called by the updater prompt to download and then refresh.
        """
        updater._start_download(self, remote_version)

    def get_previous_price(self, pair: str) -> float:
        return self.previous_prices.get(pair)

    def record_price(self, pair: str, price: float):
        update_previous_price(pair, price)
        self.previous_prices[pair] = price