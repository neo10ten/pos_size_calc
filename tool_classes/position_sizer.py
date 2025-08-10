# tool_classes/position_sizer.py

from math import floor
from ..utils.network import fetch_rate

class PositionSizer:
    def __init__(self, account_size, allocation_pct, stock_price,
                 acct_curr, stock_curr, leverage, manual_rate=None,asset_controller=None):
        self.account_size = account_size
        self.allocation_pct = allocation_pct
        self.stock_price = stock_price
        self.acct_curr = acct_curr
        self.stock_curr = stock_curr
        self.leverage = leverage
        self.manual_rate = manual_rate
        
        # Reference asset controller to access prices
        if asset_controller == None:
            raise ValueError("AssetController must be provided.")
        self.assets = asset_controller

    def calculate(self):
        allocated = self.account_size * (self.allocation_pct / 100.0)

        rate = 1.0
        if self.acct_curr != self.stock_curr:
            # 2) Check both directions against standard pairs
            direct = (self.acct_curr, self.stock_curr)
            inverse = (self.stock_curr, self.acct_curr)

            if direct in self.assets.standard_pairs:
                raw = self.manual_rate if self.manual_rate is not None else fetch_rate(*direct)
                rate = raw
            elif inverse in self.assets.standard_pairs:
                raw = self.manual_rate if self.manual_rate is not None else fetch_rate(*inverse)
                rate = 1.0 / raw
            else:
                # last-ditch: try the direct quote anyway
                rate = self.manual_rate if self.manual_rate is not None else fetch_rate(*direct)

        # Calculate asset currency allocated capital
        allocated *= rate
        # Calculate amount with leverage
        allocated *= self.leverage
            
        try:
            qty = floor(allocated / self.stock_price)
            return qty, rate
        except:
            return
        
        
###############################################################################

# tool_classes/position_sizer.py


class PositionSizer:
    def __init__(self, asset_controller):
        self.assets = asset_controller

    def calculate(self, inputs: dict) -> dict:
        """
        Example signature—read spot, pair selections, etc., from inputs,
        fetch live rates from self.assets, compute lot sizes.
        """
        pair = inputs["pair"]
        balance = float(inputs["balance"])
        risk_pct = float(inputs["risk_pct"]) / 100.0

        
        prev_price = self.assets.get_previous_price(pair)
        if prev_price is None:
            raise ValueError(f"No previous price found for {pair}")

        # simplistic example: risk $ => units
        risk_amount = balance * risk_pct
        units = risk_amount / prev_price
        
        return {
            "pair": pair,
            "units": units,
            "risk_amount": risk_amount,
        }