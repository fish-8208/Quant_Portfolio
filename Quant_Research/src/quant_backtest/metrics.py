from __future__ import annotations
import numpy as np
import pandas as pd

def simple_return_pct(final_value: float, total_contrib: float) -> float:
    if total_contrib == 0:
        return np.nan
    return (final_value - total_contrib) / total_contrib * 100.0

def max_drawdown(series: pd.Series):
    peak = series.cummax()
    dd = series / peak - 1.0
    trough = dd.idxmin()
    peak_date = series.loc[:trough].idxmax()
    return float(dd.min()), peak_date, trough

def drawdown_series(series: pd.Series) -> pd.Series:
    peak = series.cummax()
    return series / peak - 1.0

def twr_annualized(portfolio_value: pd.Series, periods_per_year: int = 252) -> float:
    r = portfolio_value.pct_change().fillna(0.0)
    n = len(r)
    if n <= 1:
        return np.nan
    return float((1.0 + r).prod() ** (periods_per_year / n) - 1.0)

def cagr(portfolio_value: pd.Series, periods_per_year: int = 252) -> float:
    n = len(portfolio_value)
    if n <= 1:
        return np.nan
    total = portfolio_value.iloc[-1] / portfolio_value.iloc[0]
    years = n / periods_per_year
    return float(total ** (1.0 / years) - 1.0)

def try_irr(cashflows: np.ndarray) -> float:
    """
    Equally spaced IRR; returns per-period rate.
    """
    try:
        import numpy_financial as npf
        r = npf.irr(cashflows)
        return float(r) if np.isfinite(r) else np.nan
    except Exception:
        return np.nan

def irr_annualized(cashflows: pd.Series, terminal_value: float, periods_per_year: int = 252) -> float:
    cf = cashflows.copy()
    cf.iloc[-1] += float(terminal_value)
    r = try_irr(cf.values.astype(float))
    if not np.isfinite(r):
        return np.nan
    return float((1.0 + r) ** periods_per_year - 1.0)