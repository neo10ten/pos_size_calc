# tool_classes/controller.py

from functools import partial
import time

from kivy.clock import Clock
from ..utils.network import online_status,fetch_rate
from ..utils.threads import run_in_executor,run_in_thread
from .position_sizer import PositionSizer

class Controller:
    def __init__(self, view=None):
        self.view = view    # a reference to PrimaryUI instance
        self._stop_rate_loop = False
        self.online = self.is_online()
    
    # Function too hold online status
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
        run_in_thread(fn=self._fetch_and_push)
    
    # Function to stop updates
    def stop_rate_updates(self):
        self._stop_rate_loop = True
    
    # Function to prommpt manual input for FX rate
    def prompt_manual_rate(self):
        self.view.show_error("Offline - Please enter FX rate manually.")
    
    
    def start_calculation(self, raw):
        if not self.online and raw.get("manual_rate") is None:
            return self.prompt_manual_rate()

        fn = partial(
            self._do_calculation,
            raw["account"],
            raw["price"],
            raw["pct"],
            raw["base"],
            raw["quote"],
            raw.get("manual_rate")
        )
        run_in_executor(fn, self._on_result)

    def _do_calculation(self, account, price, pct, base, quote, manual_rate=None):
        """Runs off main thread—compute qty & rate."""
        sizer = PositionSizer(account, pct, price, base, quote, manual_rate=manual_rate)
        return sizer.calculate()

    def _on_result(self, result):
        """Back on main thread—push to view."""
        if result:
            qty, rate = result
            self.view.update_result(qty, rate)
        else:
            self.view.show_error("Calculation failed.")
