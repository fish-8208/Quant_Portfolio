# Quant Portfolio

Research projects in quantitative finance.

## Projects

### [Simulating_Data_GBM](./Simulating_Data_GBM)
Simulating synthetic stock price paths using Geometric Brownian Motion and Monte Carlo methods.
**Demonstrates:** stochastic process simulation, Monte Carlo methods.

### [Quant_Research](./Quant_Research)
A modular backtesting and live-decision framework for systematic investment strategies, structured to mirror how real quantitative trading systems are built: a research/backtesting layer, a broker-agnostic live decision engine that emits order intents rather than trading directly, and a Trading212 execution adapter. Implements dollar-cost-averaging and drawdown-based strategy families, with FX-aware position sizing and a safety-first design (paper-mode default, risk checks, spend caps). See its own [README](./Quant_Research/README.md) for the full architecture.
**Demonstrates:** software architecture and separation of concerns, reproducible research practice (YAML-configured, archived experiment parameters), risk management design, broker/market-data API integration, rigorous validation methodology.

## Requirements

Python 3 with the standard scientific/data stack (`numpy`, `pandas`, `matplotlib`); `Quant_Research` has its own `environment.yml` for its full dependency set including `yfinance` and Trading212 API access.
