# Quant Backtest Research Framework

A modular, reproducible Python framework for researching systematic investment and accumulation strategies.  
Built as a **personal quantitative research project** to develop and demonstrate skills relevant to quantitative finance, trading, and research roles.

This repository is intended as a **research and learning framework**, not a production trading system.

## Overview

This project provides a backtesting framework for evaluating long-term, systematic investment strategies, with a focus on disciplined accumulation rules and drawdown-aware allocation logic.

Implemented strategies include:
- Regular dollar-cost averaging (DCA)
- Rolling drawdown-based accumulation strategies
- Peak-to-trough drawdown buying rules

The framework is designed to be **extensible**, allowing future additions such as momentum, mean-reversion, or volatility-targeting strategies without modifying the core engine.

Key design goals:
- **Reproducibility** — environment snapshots and YAML-based experiment configs  
- **Traceability** — timestamped outputs with archived parameter files  
- **Separation of concerns** — strategy logic, execution, portfolio accounting, and metrics are decoupled  
- **Clean analysis** — structured CSV outputs and comparison notebooks  

## Repository Structure

    Quant_Research/
    │
    ├── pyproject.toml          # Python package metadata & dependencies
    ├── environment.yml         # Reproducible conda environment
    ├── README.md
    │
    ├── src/
    │   └── quant_backtest/
    │       ├── data.py         # Data loading & preprocessing
    │       ├── engine.py       # Backtest orchestration
    │       ├── portfolio.py    # Portfolio accounting
    │       ├── metrics.py      # Performance metrics
    │       │
    │       ├── strategies/
    │       │   ├── dca/        # DCA-style strategies
    │       │   ├── momentum/   # (future extension)
    │       │   └── ...
    │       │
    │       └── cli/
    │           └── run_strategy.py   # Command-line interface
    │
    ├── runs/                   # YAML experiment configurations
    ├── outputs/                # Backtest outputs (CSV / JSON)
    ├── notebooks/              # Analysis & comparison notebooks
    └── tests/                  # Unit tests (optional)

## Installation & Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd Quant_Research

conda env create -f environment.yml
conda activate quant_research

pip install -e .

pip install ipykernel
python -m ipykernel install --user --name quant_research --display-name "Python (quant_research)"


---

### 5️⃣ Running Backtests

```md
## Running Backtests

All strategies are executed via a command-line interface.

### Recommended: run using a configuration file
```bash
python -m quant_backtest.cli.run_strategy \
  --config runs/strat3_peakdd_10pct_fixed_50.yml

Each run:

- executes the strategy,
- generates timestamped outputs,
- copies the exact configuration file into `outputs/` for full reproducibility.

---

### 6️⃣ Example Strategy Configuration

```md
## Example Strategy Configuration

```yaml
run_name: strat3_peakdd_10pct_fixed_50
strategy: strat3

start: "2005-01-01"
source: stooq
tickers: ["SPY", "ACWI"]
weights: [0.7, 0.3]

threshold: 0.10
mode: fixed
fixed: 50


---

### 7️⃣ Outputs

```md
## Outputs

Each run produces the following artifacts:

outputs/
├── <run_name>__<timestamp>.timeseries.csv
├── <run_name>__<timestamp>.trades.csv
├── <run_name>__<timestamp>.metrics.json
└── <run_name>__<timestamp>.config.yml

### Timeseries CSV
Daily portfolio state including:
- portfolio value
- contributions and cumulative contributions
- drawdown
- asset units
- strategy-specific diagnostic series

### Trades CSV
Every executed trade:
- date
- ticker
- cash amount
- units
- execution price

### Metrics JSON
Summary statistics such as:
- total contributions
- terminal portfolio value
- simple return
- IRR (money-weighted)
- TWR / CAGR (time-weighted)
- maximum drawdown
- number of trades

### Config Archive
A copy of the exact YAML configuration used to generate the run.

## Analysis & Visualisation

A comparison notebook is provided:

This notebook enables:
- selection of specific runs,
- side-by-side strategy comparison,
- visualisation of portfolio value, drawdowns, and trade timing,
- inspection of performance metrics in a clean comparison table.

## Reproducibility

To reproduce any result in this repository:

1. Clone the repository  
2. Create the conda environment using `environment.yml`  
3. Install the package with `pip install -e .`  
4. Re-run the corresponding YAML configuration under `runs/`  

All runs are timestamped and self-documenting.

## Extending the Framework

To add a new strategy:

1. Create a new module under `src/quant_backtest/strategies/<family>/`
2. Implement the strategy interface
3. Register the strategy in the CLI
4. Add a YAML configuration under `runs/`

The core engine and portfolio logic do **not** need to be modified to add new strategies.

## Data Sources

- **Stooq** (via `pandas-datareader`)  
- **Yahoo Finance** (via `yfinance`, optional)

Data caching is supported to reduce repeated downloads.

## Disclaimer

This project is for **research and educational purposes only**.  
It does not constitute financial advice and does not account for transaction costs, taxes, or slippage unless explicitly modeled.

## License

This project is licensed under the **MIT License**.