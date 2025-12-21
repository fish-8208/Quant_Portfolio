from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

@dataclass
class Trade:
    date: pd.Timestamp
    ticker: str
    cash: float       # negative for buy
    units: float
    price: float

class BuyOnlyPortfolio:
    def __init__(self, tickers: list[str]):
        self.tickers = tickers
        self.trades: List[Trade] = []

    def buy(self, date: pd.Timestamp, ticker: str, cash: float, price: float):
        # cash is positive input (how much to spend); we record negative cashflow
        units = cash / price if price > 0 else 0.0
        self.trades.append(Trade(date=date, ticker=ticker, cash=-cash, units=units, price=price))

    def trades_df(self) -> pd.DataFrame:
        return pd.DataFrame([t.__dict__ for t in self.trades]).sort_values("date").reset_index(drop=True)

    def daily_units(self, index: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Returns DataFrame of cumulative units held by date per ticker.
        """
        df = pd.DataFrame(0.0, index=index, columns=self.tickers)
        if not self.trades:
            return df

        tdf = self.trades_df()
        for t in self.tickers:
            buys = pd.Series(0.0, index=index)
            sub = tdf[tdf["ticker"] == t]
            if not sub.empty:
                grouped = sub.groupby("date")["units"].sum()
                buys.loc[grouped.index] = grouped.values
            df[t] = buys.cumsum()
        return df

    def daily_value(self, prices: pd.DataFrame) -> pd.Series:
        units = self.daily_units(prices.index)
        return (units * prices[self.tickers]).sum(axis=1)

    def daily_cashflows(self, index: pd.DatetimeIndex) -> pd.Series:
        """
        Cashflows aligned to index: negative on buy dates, 0 otherwise.
        """
        cf = pd.Series(0.0, index=index)
        if not self.trades:
            return cf
        tdf = self.trades_df()
        grouped = tdf.groupby("date")["cash"].sum()
        cf.loc[grouped.index] = grouped.values
        return cf