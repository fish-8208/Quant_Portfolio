from __future__ import annotations
import time
from typing import List, Optional, Dict

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except Exception:
    yf = None

try:
    from pandas_datareader import data as pdr
except Exception:
    pdr = None


def _download_yahoo(ticker: str, start: str, end: Optional[str], session=None, tries=4, sleep_base=3) -> pd.Series:
    if yf is None:
        raise RuntimeError("yfinance not installed/available.")
    last_err = None
    for attempt in range(tries):
        try:
            df = yf.download(
                ticker, start=start, end=end,
                auto_adjust=True, progress=False,
                threads=False, session=session
            )
            if df is None or df.empty:
                raise RuntimeError(f"Empty Yahoo frame for {ticker}")
            return df["Close"].rename(ticker)
        except Exception as e:
            last_err = e
            msg = str(e)
            if "Too Many Requests" in msg and attempt < tries - 1:
                time.sleep(sleep_base * (attempt + 1))
                continue
            raise RuntimeError(f"Yahoo failed for {ticker}: {e}") from e
    raise RuntimeError(f"Yahoo failed for {ticker}: {last_err}")


def _download_stooq(ticker: str, start: str, end: Optional[str]) -> pd.Series:
    if pdr is None:
        raise RuntimeError("pandas-datareader not installed/available.")
    sym = f"{ticker}.US"
    df = pdr.DataReader(sym, "stooq", start=start, end=end)
    if df is None or df.empty:
        raise RuntimeError(f"Empty Stooq frame for {ticker}")
    df = df.sort_index()
    return df["Close"].rename(ticker)


def load_prices(
    tickers: List[str],
    start: str,
    end: Optional[str],
    source: str = "auto",
    cache_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    Returns a DataFrame of close prices (columns=tickers, index=trading dates).
    Uses optional parquet cache.
    """
    if cache_path:
        try:
            cached = pd.read_parquet(cache_path)
            if set(tickers).issubset(set(cached.columns)):
                return cached.loc[:, tickers].dropna(how="all")
        except Exception:
            pass

    chosen = source.lower()
    session = None
    if yf is not None:
        try:
            session = yf.utils.get_yf_session()
        except Exception:
            session = None

    out = []
    used: Dict[str, str] = {}

    for t in tickers:
        if chosen in ("yahoo", "auto"):
            try:
                out.append(_download_yahoo(t, start, end, session=session))
                used[t] = "yahoo"
                continue
            except Exception:
                if chosen == "yahoo":
                    raise

        if chosen in ("stooq", "auto"):
            out.append(_download_stooq(t, start, end))
            used[t] = "stooq"
            continue

        raise RuntimeError(f"Failed all sources for {t}")

    prices = pd.concat(out, axis=1).dropna(how="all")

    if cache_path:
        try:
            prices.to_parquet(cache_path)
        except Exception:
            pass

    return prices


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Daily simple returns."""
    return prices.pct_change().fillna(0.0)


def weighted_portfolio_return(asset_rets: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    w = pd.Series(weights)
    return (asset_rets * w).sum(axis=1)