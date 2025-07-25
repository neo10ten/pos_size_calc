#!/usr/bin/env python3
"""
main_v7.py – adds:
  4) FX-pair spinner & validation
  6) Parallel rate pre-warming
  7) Non-currency instrument spinner
 10) Full “Browse All Pairs” browser popup
"""

import os
import json
import socket
import time
import math
import logging
import threading
from functools import partial
from concurrent.futures import ThreadPoolExecutor  # for parallel pre‐warm

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from packaging.version import Version

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ─── HTTP session with retries ─────────────────────────────────────────────────
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504])
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

def is_online(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False

_rate_cache = {}
CACHE_TTL = 300

def fetch_rate(base, quote):
    key = (base, quote)
    now = time.time()
    if key in _rate_cache:
        ts, r = _rate_cache[key]
        if now - ts < CACHE_TTL:
            return r
    resp = session.get("https://api.frankfurter.app/latest",
                       params={"from": base, "to": quote}, timeout=5)
    resp.raise_for_status()
    rate = resp.json().get("rates", {}).get(quote)
    if rate is None:
        raise ValueError(f"No rate for {base}/{quote}")
    _rate_cache[key] = (now, rate)
    return float(rate)

REMOTE_VERSION_URL = "https://my.server.com/asset_version.json"

def download_assets(remote_ver):
    logging.info(f"Would download new assets v{remote_ver}")

class ScrollableSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_dropdown_height = Window.height * 0.6

    def _create_dropdown(self):
        dropdown = super()._create_dropdown()
        orig = dropdown.container
        scroll = ScrollView(
            size_hint=(1, None),
            height=self.max_dropdown_height,
            scroll_type=['bars','content'],
            bar_width='10dp'
        )
        scroll.add_widget(orig)
        dropdown.container = scroll
        return dropdown

# ─── Load assets ────────────────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
with open(os.path.join(ASSETS, "currencies.json")) as f:
    CURRENCIES = json.load(f)
with open(os.path.join(ASSETS, "pairs_split.json")) as f:
    ps = json.load(f)
    STANDARD_SET = set(ps["standard"])
    OTHER_PAIRS  = ps["other"]

class ForexConverter:
    @staticmethod
    def get_rate(b, q):
        return fetch_rate(b, q)

class PositionSizer:
    def __init__(self, account_size, allocation_pct, stock_price,
                 acct_curr, stock_curr, manual_rate=None):
        self.account_size = account_size
        self.allocation_pct = allocation_pct / 100.0
        self.stock_price = stock_price
        self.acct_curr = acct_curr
        self.stock_curr = stock_curr
        self.manual_rate = manual_rate

    def calculate(self):
        allocated = self.account_size * (self.allocation_pct / 100.0)

        rate = 1.0
        if self.acct_curr != self.stock_curr:
            # 2) Check both directions against STANDARD_SET
            direct = (self.acct_curr, self.stock_curr)
            inverse = (self.stock_curr, self.acc_curr)

            if direct in STANDARD_SET:
                raw = self.manual_rate if self.manual_rate is not None else fetch_rate(*direct)
                rate = raw
            elif inverse in STANDARD_SET:
                raw = self.manual_rate if self.manual_rate is not None else fetch_rate(*inverse)
                rate = 1.0 / raw
            else:
                # last-ditch: try the direct quote anyway
                rate = self.manual_rate if self.manual_rate is not None else fetch_rate(*direct)

            allocated *= rate

        qty = math.floor(allocated / self.stock_price)
        return qty, rate


class SizerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=10, **kwargs)
        form = GridLayout(cols=2, row_force_default=True,
                          row_default_height=40, spacing=5)

        # Account
        form.add_widget(Label(text="Account Balance:"))
        self.acc_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(self.acc_input)

        form.add_widget(Label(text="Account Currency:"))
        self.acc_curr = ScrollableSpinner(text=CURRENCIES[0], values=CURRENCIES)
        form.add_widget(self.acc_curr)
        
        # Allocation % of account
        form.add_widget(Label(text="Allocate % of Account:"))
        self.pct_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(self.pct_input)

        # Margin ratio (leverage), default 1.0
        form.add_widget(Label(text="Margin Ratio (e.g. 1.0 for 1:1):"))
        self.margin_input = TextInput(text="1.0", multiline=False, input_filter="float")
        form.add_widget(self.margin_input)

        # Stock
        form.add_widget(Label(text="Stock Price:"))
        self.price_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(self.price_input)

        form.add_widget(Label(text="Stock Currency:"))
        self.stock_curr = ScrollableSpinner(text=CURRENCIES[0], values=CURRENCIES)
        form.add_widget(self.stock_curr)

        # (4) FX-Pair Spinner
        form.add_widget(Label(text="Or pick a predefined pair:"))
        self.pair_spinner = ScrollableSpinner(
            text="Select Pair", values=sorted(STANDARD_SET)
        )
        self.pair_spinner.bind(text=self.on_pair_select)
        form.add_widget(self.pair_spinner)

        # (7) Non-currency Instruments
        form.add_widget(Label(text="Other Instruments:"))
        # load from oanda_inst.json
        insts = []
        try:
            with open(os.path.join(ASSETS, "oanda_inst.json")) as f:
                data = json.load(f)["instruments"]
            insts = [i["displayName"] for i in data if i.get("type") != "CURRENCY"]
        except Exception as e:
            logging.error(f"Loading other instruments failed: {e}")
        self.inst_spinner = ScrollableSpinner(
            text="Select Instrument", values=sorted(insts)
        )
        form.add_widget(self.inst_spinner)

        # Inline error + spacer
        self.error_label = Label(text="", color=(1,0,0,1))
        form.add_widget(self.error_label)
        form.add_widget(Label())

        self.calc_btn = Button(text="Calculate Position Size", size_hint_y=None, height=50)
        self.calc_btn.bind(on_release=self.on_calculate)
        self.result_label = Label(text="", font_size=18, size_hint_y=None, height=60)

        # (10) Browse all pairs
        self.browse_btn = Button(text="Browse All Pairs", size_hint_y=None, height=40)
        self.browse_btn.bind(on_release=self.open_pair_browser)

        self.add_widget(form)
        self.add_widget(self.calc_btn)
        self.add_widget(self.result_label)
        self.add_widget(self.browse_btn)

    def on_pair_select(self, spinner, text):
        # set base/quote from selected pair
        if len(text) == 6:
            self.acc_curr.text = text[:3]
            self.stock_curr.text = text[3:]

    def on_calculate(self, _):
        if not is_online():
            self.prompt_manual_rate()
            return

        try:
            account = float(self.acc_input.text)
            price   = float(self.price_input.text)
        except ValueError:
            self.error_label.text = "Enter valid numbers."
            return

        threading.Thread(
            target=partial(self.run_calc, account, price),
            daemon=True
        ).start()

    def run_calc(self, account, price):
        try:
            pct = float(self.acc_input.text)  # reuse field or prompt separately
            sizer = PositionSizer(
                account, pct, price,
                self.acc_curr.text, self.stock_curr.text
            )
            qty, rate = sizer.calculate()
            Clock.schedule_once(lambda dt: self.update_result(qty, rate))
        except Exception as e:
            Clock.schedule_once(lambda dt, exc=e: self.show_error(str(e)))

    def update_result(self, qty, rate):
        base = self.acc_curr.text
        quote = self.stock_curr.text
        direction = ""
        if (base, quote) not in STANDARD_SET and (quote, base) in STANDARD_SET:
            direction = "(Inverted) "
        self.result_label.text = (
            f"{direction}1 {base} = {rate:.4f} {quote}\n"
            f"Quantity to Buy: {qty}"
        )

    def prompt_manual_rate(self):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        layout.add_widget(Label(text="Offline. Enter manual FX rate:"))
        rate_input = TextInput(input_filter="float", multiline=False)
        layout.add_widget(rate_input)
        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        ok = Button(text="Use Rate"); cancel = Button(text="Cancel")
        btns.add_widget(ok); btns.add_widget(cancel)
        layout.add_widget(btns)
        popup = Popup(title="Manual FX Override", content=layout, size_hint=(0.8,0.5))
        ok.bind(on_release=lambda *_: self.on_manual(rate_input.text, popup))
        cancel.bind(on_release=popup.dismiss)
        popup.open()

    def on_manual(self, rate_text, popup):
        try:
            rate = float(rate_text)
            popup.dismiss()
            account = float(self.acc_input.text)
            price   = float(self.price_input.text)
            threading.Thread(
                target=partial(self.run_calc_manual, account, price, rate),
                daemon=True
            ).start()
        except ValueError:
            pass

    def run_calc_manual(self, account, price, manual_rate):
        try:
            sizer = PositionSizer(
                account, float(self.acc_input.text), price,
                self.acc_curr.text, self.stock_curr.text,
                manual_rate=manual_rate
            )
            qty, rate = sizer.calculate()
            Clock.schedule_once(lambda dt: self.update_result(qty, rate))
        except Exception as e:
            Clock.schedule_once(lambda dt, exc=e: self.show_error(str(e)))

    # (10) Popup to browse OTHER_PAIRS
    def open_pair_browser(self, _=None):
        content = GridLayout(cols=1, size_hint_y=None, spacing=2, padding=5)
        content.bind(minimum_height=content.setter('height'))
        for p in OTHER_PAIRS:
            btn = Button(text=p, size_hint_y=None, height=30)
            btn.bind(on_release=lambda btn, pair=p: (
                self.pair_spinner.text == pair, popup.dismiss()
            ))
            content.add_widget(btn)
        scroll = ScrollView(size_hint=(1,1))
        scroll.add_widget(content)
        popup = Popup(title="All Pairs", content=scroll, size_hint=(0.9,0.9))
        popup.open()

    def show_error(self, msg):
        Popup(title="Error", content=Label(text=msg), size_hint=(0.8,0.4)).open()

class PositionSizerApp(App):
    def build(self):
        return SizerUI()

    def on_start(self):
        # pre-warm standard-pair rates in parallel (6)
        with ThreadPoolExecutor(max_workers=10) as executor:
            for pair in STANDARD_SET:
                b, q = pair[:3], pair[3:]
                executor.submit(fetch_rate, b, q)
        # asset-version check (from v6)
        try:
            local = json.load(open(os.path.join(ASSETS, "asset_version.json")))["asset_version"]
            resp = session.get(REMOTE_VERSION_URL, timeout=5); resp.raise_for_status()
            remote = resp.json().get("asset_version")
            if Version(remote) > Version(local):
                self.prompt_update(local, remote)
        except Exception as e:
            logging.info(f"Version check skipped: {e}")

    def prompt_update(self, local, remote):
        txt = f"Assets v{remote} available (you have v{local}). Download?"
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        layout.add_widget(Label(text=txt))
        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        yes = Button(text="Yes"); no = Button(text="No")
        btns.add_widget(yes); btns.add_widget(no)
        layout.add_widget(btns)
        popup = Popup(title="Update Assets", content=layout, size_hint=(0.8,0.4))
        yes.bind(on_release=lambda *_: (popup.dismiss(), download_assets(remote)))
        no.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == "__main__":
    PositionSizerApp().run()