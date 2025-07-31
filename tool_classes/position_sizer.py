# tool_classes/position_sizer.py

from math import floor
from ..utils.network import fetch_rate
from ..assets import STANDARD_SET

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
            inverse = (self.stock_curr, self.acct_curr)

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

        qty = floor(allocated / self.stock_price)
        return qty, rate