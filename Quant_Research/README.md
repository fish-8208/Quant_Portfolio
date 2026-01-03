# Quant Research → Live Decision Framework

A modular Python framework for **quantitative research, strategy validation, and live decision-making** for systematic investment strategies.

Originally built as a **backtesting and research framework**, this project has evolved into a **research → paper-trading → live execution pipeline**, designed to mirror how real quantitative trading systems are structured.

> ⚠️ **Disclaimer**  
> This repository is a personal research and learning project.  
> Live trading components are implemented cautiously, with strong safety guards, and are not intended as a turnkey production trading system.

## High-Level Architecture
'''
┌──────────────────────────────┐
│ Research & Backtesting       │
│ (quant_backtest)             │
│                              │
│ - Historical data            │
│ - Strategy logic             │
│ - Portfolio accounting       │
│ - Performance metrics        │
└──────────────┬───────────────┘
               │
               │ validated strategy logic
               ▼
┌──────────────────────────────┐
│ Live Decision Engine         │
│ (quant_live)                 │
│                              │
│ - Market data (EOD)          │
│ - Drawdown / indicators      │
│ - FX-aware sizing            │
│ - Risk constraints           │
│ - OrderIntent generation     │
└──────────────┬───────────────┘
               │
               │ order intents (what to do)
               ▼
┌──────────────────────────────┐
│ Broker Execution Layer       │
│ (Trading212 API)             │
│                              │
│ - Account snapshot           │
│ - Positions & orders         │
│ - Market orders (demo/live)  │
└──────────────────────────────┘
'''

**Key idea:**  
Strategies never place trades directly. They generate **order intents**, which are validated, risk-checked, and optionally executed by a broker adapter.

## Project Goals

- **Reproducible research** — YAML-configured backtests with archived parameters  
- **Separation of concerns** — research logic, decision logic, and execution are isolated  
- **Traceability** — every decision is logged with inputs, diagnostics, and reasoning  
- **Safety-first live trading** — paper mode, idempotency, and validation by default  
- **Extensibility** — new strategies, brokers, and risk rules can be added without refactoring core logic  

## Repository Structure
'''
Quant_Research/
│
├── pyproject.toml            # Python package metadata
├── environment.yml           # Reproducible conda environment
├── README.md
│
├── config/
│   └── symbols.yml           # Internal symbol → broker instrument mapping
│
├── runs/                     # Backtest experiment configs
├── live_runs/                # Live / paper-trading configs
│
├── outputs/                  # Backtest outputs
├── live_outputs/             # Live decision artifacts
│
├── notebooks/                # Analysis & comparison notebooks
│
├── src/
│   ├── quant_backtest/       # Research & backtesting engine
│   │   ├── data.py
│   │   ├── engine.py
│   │   ├── portfolio.py
│   │   ├── metrics.py
│   │   ├── strategies/
│   │   └── cli/
│   │       └── run_strategy.py
│   │
│   └── quant_live/           # Live decision & execution framework
│       ├── cli/
│       │   └── run_live.py
│       ├── broker/
│       │   ├── trading212.py
│       │   └── snapshot.py
│       ├── strategies/
│       │   ├── indicators.py
│       │   └── adapter.py
│       ├── execution/
│       │   ├── orders.py
│       │   └── risk.py
│       └── data/
│           └── fx.py
│
└── tests/
'''

## Backtesting Framework (`quant_backtest`)

The backtesting engine provides a **vectorised, reproducible research environment** for systematic strategies.

### Implemented strategy families

- Dollar-cost averaging (DCA)
- Rolling drawdown accumulation
- Peak-to-trough drawdown strategies

### Design principles

- Strategy logic is **stateless and deterministic**
- Portfolio accounting is **fully explicit**
- Metrics are calculated post-run
- All experiments are driven by YAML configs

### Running Backtests

'''bash
python -m quant_backtest.cli.run_strategy \
  --config runs/strat3_peakdd_10pct_fixed_50.yml
'''

## Live Decision Framework (`quant_live`)

The live framework **reuses research logic**, but runs it in a **state-aware, broker-integrated environment**.

### What “live” means here

- Pulls real broker state (cash, positions, pending orders)
- Uses historical market data for signals
- Generates **OrderIntents**, not trades
- Can run in **paper mode** or **demo execution mode**

### OrderIntent Abstraction

'''python
OrderIntent(
    broker_ticker="VUSAl_EQ",
    side="BUY",
    quantity=0.0278,
    reason="PeakDD trigger (ccy=GBP)",
    est_price=683.17,
    est_value_gbp=18.99
    )
'''

## Currency & FX Handling

The system supports:

- GBP instruments (no FX conversion)
- USD instruments (GBPUSD FX conversion)
- GBX instruments (pence → GBP normalization)

Currency identification is sourced from:

- Trading212 instrument metadata (authoritative)
- Explicit symbol mapping (`symbols.yml`)
- Defensive validation before execution

## Live Run Outputs

Each live run creates a fully auditable artifact:

live_outputs/
└── 20260103_131346_peakdd_demo/
    └── decisions.json


### `decisions.json` contains:

- run configuration
- broker snapshot (cash, positions, orders)
- FX rates used
- drawdown diagnostics
- generated order intents
- risk filters applied

This makes every decision **explainable and reproducible**.

## Safety & Risk Controls

By design:

- **Paper mode is default**
- Stale market data aborts runs
- Unknown instruments abort runs
- FX conversion must be explicit
- Minimum order size enforced
- Daily spend caps enforced

Live execution is opt-in and guarded.

## Extending the System

### Add a new strategy
- Implement it in `quant_backtest/strategies/`
- Reuse logic in `quant_live/strategies/adapter.py`

### Add a new broker
- Implement a new adapter in `quant_live/broker/`
- Keep strategy logic unchanged

### Add risk rules
- Extend `quant_live/execution/risk.py`
- No changes required to strategy code

## Data Sources

- **Stooq** — historical market data  
- **Yahoo Finance** — equities & FX (via `yfinance`)  
- **Trading212 API** — account state and execution  

## Disclaimer

This project is for **research and educational purposes only**.  
It does not constitute financial advice and does not guarantee profitability.

Live trading components are implemented conservatively and should not be used without full understanding and independent verification.

## License

MIT License