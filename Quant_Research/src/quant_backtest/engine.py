from __future__ import annotations
import os
import json
import pandas as pd

from .portfolio import BuyOnlyPortfolio
from .metrics import (
    drawdown_series, max_drawdown, simple_return_pct, twr_annualized, irr_annualized
)
from quant_backtest.strategies.base import Strategy

def run_backtest(
    prices: pd.DataFrame,
    weights: dict[str, float],
    strategy: Strategy,
    out_dir: str,
    run_name: str,
):
    os.makedirs(out_dir, exist_ok=True)

    pf, result = strategy.run(prices=prices, portfolio_weights=weights)

    # Core series
    value = pf.daily_value(prices)
    cashflows = pf.daily_cashflows(prices.index)          # negative on buy days
    contrib = (-cashflows).clip(lower=0.0)                # positive contributions
    cum_contrib = contrib.cumsum()

    # Positions (units per ticker)
    units = pf.daily_units(prices.index)
    total_units = units.sum(axis=1)  # not super meaningful across tickers, but useful; keep per-ticker too

    # Performance series
    dd_portfolio = drawdown_series(value)

    # Build output frame
    out = pd.DataFrame({
        "portfolio_value": value,
        "contribution": contrib,
        "cumulative_contributions": cum_contrib,
        "portfolio_drawdown": dd_portfolio,
    }, index=prices.index)

    # Add units columns
    for tkr in units.columns:
        out[f"units_{tkr}"] = units[tkr]
    out["units_total"] = total_units

    # Add any extra diagnostic series from strategy
    for k, s in result.extra_series.items():
        out[k] = s.reindex(out.index).astype(float)

    # Metrics (end-of-period)
    total_contrib = float(contrib.sum())
    final_value = float(value.iloc[-1])
    md, md_peak, md_trough = max_drawdown(value)

    metrics = {
        "strategy": strategy.name,
        "start": str(out.index.min().date()),
        "end": str(out.index.max().date()),
        "total_contributions": total_contrib,
        "terminal_value": final_value,
        "simple_return_pct": simple_return_pct(final_value, total_contrib),
        "twr_annualized": twr_annualized(value),
        "irr_annualized": irr_annualized(cashflows, terminal_value=final_value),
        "max_drawdown_pct": md * 100.0,
        "max_dd_peak": str(md_peak.date()),
        "max_dd_trough": str(md_trough.date()),
        "num_trades": int(len(pf.trades)),
    }

    # Write outputs
    csv_path = os.path.join(out_dir, f"{run_name}.timeseries.csv")
    out.to_csv(csv_path, index=True)

    trades_path = os.path.join(out_dir, f"{run_name}.trades.csv")
    pf.trades_df().to_csv(trades_path, index=False)

    metrics_path = os.path.join(out_dir, f"{run_name}.metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    return csv_path, trades_path, metrics_path