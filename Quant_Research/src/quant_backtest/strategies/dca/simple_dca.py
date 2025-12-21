from __future__ import annotations
import pandas as pd

from ...portfolio import BuyOnlyPortfolio
from ..base import Strategy, StrategyResult

def first_trading_day_each_month(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    s = pd.Series(index=index, data=1)
    firsts = s.groupby([index.year, index.month]).head(1).index
    return pd.DatetimeIndex(firsts).sort_values()

class MonthlyFixedBuy(Strategy):
    name = "strat1_monthly"

    def __init__(self, amount_per_month: float = 100.0):
        self.amount = float(amount_per_month)

    def run(self, prices: pd.DataFrame, portfolio_weights: dict[str, float]):
        tickers = list(portfolio_weights.keys())
        pf = BuyOnlyPortfolio(tickers)

        dca_dates = first_trading_day_each_month(prices.index)

        for dt in dca_dates:
            for tkr, w in portfolio_weights.items():
                cash = self.amount * w
                px = float(prices.loc[dt, tkr])
                pf.buy(dt, tkr, cash=cash, price=px)

        return pf, StrategyResult(extra_series={})