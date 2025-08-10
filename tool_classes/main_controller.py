# tool_classes/main_controller.py

from functools import partial
import time
from kivy.clock import Clock

from .asset_controller import AssetController
from .position_sizer import PositionSizer
from ..services.prompts import show_error,prompt_manual_rate
from ..utils.network import online_status,fetch_rate
from ..utils.threads import run_in_executor,run_in_thread

class Controller:
    def __init__(self, view=None):
        self.view = view    # a reference to PrimaryUI instance
        self._stop_rate_loop = False
        self.online = self.is_online()
        self.asset_controller = AssetController()
        self._populate_asset_spinners()
    
    # Function to hold online status
    def is_online(self):
        return online_status()
    
    # Function to start the rate updater
    def start_rate_updates(self):
        if self.online:
            pass
        else:
            self.view.rate_input.hint_text = "OFFLINE - Enter rate manually."
    
    # Function to run a loop
    def _rate_loop(self):
        while not self._stop_rate_loop:
            self._fethc_and_push()
            time.sleep(300) # CACHE_TTL in seconds
    
    # Function to collect new rate
    def _fetch_and_push(self):
        base = self.view.acc_curr.text
        quote = self.view.stock_curr.text
        try:
            rate = fetch_rate(base,quote)
        except:
            return
        Clock.schedule_once(lambda dt, r=rate: self.view.update_rate(r))
    
    # Function to collect one off rate
    def fetch_rate_once(self):
        if self.online:
            run_in_thread(fn=self._fetch_and_push)
        else:
            return
    
    # Function to stop updates
    def stop_rate_updates(self):
        self._stop_rate_loop = True
    
    # Function to add assets to spinners for selections
    def _populate_asset_spinners(self):
        self.view.set_currency_options(self.asset_controller.currencies.keys())
        self.view.set_pair_options(self.asset_controller.standard_pairs)
        self.view.set_other_instruments(self.asset_controller.other_instruments)
        
    # Function to refresh assets and UI
    def refresh_assets_and_ui(self):
        """Clear asset caches and reload UI dropdowns."""
        self.asset_controller.refresh()
        self._populate_asset_spinners()

    def start_calculation(self, raw, asset_controller):
        # Check online status and parse for calculation
        
        fn = partial(
        self._do_calculation,
        raw["account"],
        raw["price"],
        raw["pct"],
        raw["base"],
        raw["quote"],
        raw["leverage"],
        raw["manual_rate"],
        asset_controller
        )
        if self.online:
            run_in_executor(fn, self._on_result)
        else:
            if raw["manual_rate"] is None:
                prompt_manual_rate(self)
            else:
                run_in_executor(fn, self._on_result)
    
    def _on_error(self,error=None):
        if error is None:
            show_error(self,"Error raised - Check inputs and try again.")
        else:
            show_error(self,error)

    def _do_calculation(self, account, pct, price, base, quote, leverage, asset_controller, manual_rate=None):
        """Runs off main thread—compute qty & rate."""
        sizer = PositionSizer(account, pct, price, base, quote, leverage, asset_controller, manual_rate=manual_rate)
        return sizer.calculate()

    def _on_result(self, result):
        """Back on main thread — push to view."""
        if result:
            qty, rate = result
            self.view.update_result(qty, rate)
        else:
            show_error(self,"Calculation failed - Check connection and values, then try again.")

############################################################################################

# tool_classes/main_controller.py

from tool_classes.asset_controller import AssetController
from tool_classes.position_sizer import PositionSizer

class MainController:
    def __init__(self):
        self.asset_controller = AssetController(main_controller=self)
        self.position_sizer = PositionSizer(self.asset_controller)
        # immediately check for updates on launch
        self.asset_controller.start_update_check()

    def calculate_positions(self, user_inputs: dict):
        """
        Perform sizing logic, then on success update the UI.
        If inputs are invalid, we raise or return an error instead.
        """
        try:
            results = self.position_sizer.calculate(user_inputs)
            # only on successful sizing do we refresh UI
            self.on_calculation_complete(results)
        except Exception:
            # surface error to user; do not refresh assets/UI
            return

    def on_calculation_complete(self, results):
        """
        Hook for when sizing finishes successfully.
        Your UI-view should bind to this to draw the new positions.
        """
        
        # example:
        # self.view.update_positions(results)

    def on_assets_refreshed(self):
        """
        Called after asset JSONs are downloaded & reloaded.
        You might e.g. rebuild dropdowns or rebind data sources here.
        """
        
        # example:
        # self.view.refresh_asset_dropdowns(self.asset_controller.currencies)