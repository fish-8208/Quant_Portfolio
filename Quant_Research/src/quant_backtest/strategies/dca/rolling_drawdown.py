from __future__ import annotations
import pandas as pd
import numpy as np

from ...portfolio import BuyOnlyPortfolio
from ..base import Strategy, StrategyResult

class RollingDrawdownBuy(Strategy):
    name = "strat2_rolling_dd"

    def __init__(
        self,
        window_days: int = 5,
        threshold: float = 0.02,     # 2% drop over window
        mode: str = "fixed",         # "fixed" | "proportional"
        fixed_amount: float = 50.0,
        k: float = 1000.0,           # proportional multiplier in $ per 1.0 drawdown (e.g. 0.03 * 1000 = $30)
    ):
        self.window = int(window_days)
        self.threshold = float(threshold)
        self.mode = mode
        self.fixed_amount = float(fixed_amount)
        self.k = float(k)

    def run(self, prices: pd.DataFrame, portfolio_weights: dict[str, float]):
        tickers = list(portfolio_weights.keys())
        pf = BuyOnlyPortfolio(tickers)

        # Build synthetic index level from weighted returns
        asset_rets = prices.pct_change().fillna(0.0)
        w = pd.Series(portfolio_weights)
        port_ret = (asset_rets * w).sum(axis=1)
        index_level = (1.0 + port_ret).cumprod()

        # Rolling window return (drawdown over last N days)
        roll_ret = index_level / index_level.shift(self.window) - 1.0
        roll_ret = roll_ret.fillna(0.0)

        # Trigger when rolling return <= -threshold
        trigger = roll_ret <= -self.threshold

        for dt in prices.index:
            if not bool(trigger.loc[dt]):
                continue

            dd = float(-roll_ret.loc[dt])  # positive magnitude
            if self.mode == "fixed":
                amount = self.fixed_amount
            elif self.mode == "proportional":
                amount = self.k * dd
            else:
                raise ValueError("mode must be 'fixed' or 'proportional'")

            for tkr, weight in portfolio_weights.items():
                px = float(prices.loc[dt, tkr])
                pf.buy(dt, tkr, cash=amount * weight, price=px)

        extra = {
            f"rolling_return_{self.window}d": roll_ret,
            "trigger": trigger.astype(int),
        }
        return pf, StrategyResult(extra_series=extra)