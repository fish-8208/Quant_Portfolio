from __future__ import annotations
import pandas as pd

from ...portfolio import BuyOnlyPortfolio
from ..base import Strategy, StrategyResult

class PeakDrawdownBuy(Strategy):
    name = "strat3_peak_dd"

    def __init__(
        self,
        threshold: float = 0.05,     # 5% below peak
        mode: str = "fixed",         # "fixed" | "proportional"
        fixed_amount: float = 50.0,
        k: float = 1000.0,
    ):
        self.threshold = float(threshold)
        self.mode = mode
        self.fixed_amount = float(fixed_amount)
        self.k = float(k)

    def run(self, prices: pd.DataFrame, portfolio_weights: dict[str, float]):
        tickers = list(portfolio_weights.keys())
        pf = BuyOnlyPortfolio(tickers)

        # synthetic index
        asset_rets = prices.pct_change().fillna(0.0)
        w = pd.Series(portfolio_weights)
        port_ret = (asset_rets * w).sum(axis=1)
        index_level = (1.0 + port_ret).cumprod()

        peak = index_level.cummax()
        dd = index_level / peak - 1.0  # negative or 0
        trigger = dd <= -self.threshold

        for dt in prices.index:
            if not bool(trigger.loc[dt]):
                continue

            magnitude = float(-dd.loc[dt])  # positive
            if self.mode == "fixed":
                amount = self.fixed_amount
            elif self.mode == "proportional":
                amount = self.k * magnitude
            else:
                raise ValueError("mode must be 'fixed' or 'proportional'")

            for tkr, weight in portfolio_weights.items():
                px = float(prices.loc[dt, tkr])
                pf.buy(dt, tkr, cash=amount * weight, price=px)

        extra = {
            "peak_to_trough_drawdown": dd,
            "trigger": trigger.astype(int),
        }
        return pf, StrategyResult(extra_series=extra)