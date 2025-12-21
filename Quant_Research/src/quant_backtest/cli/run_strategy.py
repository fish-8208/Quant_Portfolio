from __future__ import annotations
import argparse
import os
import shutil
import hashlib
from pathlib import Path
import pandas as pd
try:
    import yaml
except ImportError:
    yaml = None

from ..data import load_prices
from ..engine import run_backtest
from ..strategies.dca.simple_dca import MonthlyFixedBuy
from ..strategies.dca.rolling_drawdown import RollingDrawdownBuy
from ..strategies.dca.peak_drawdown import PeakDrawdownBuy

def load_yaml_config(path: str) -> dict:
    if yaml is None:
        raise RuntimeError("pyyaml is not installed. Run: pip install pyyaml")
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def basename_no_ext(path: str) -> str:
    return Path(path).stem

def main():
    # 1) Minimal parser to grab --config early
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", default=None, help="Path to YAML run config")
    pre_args, remaining = pre.parse_known_args()

    cfg = {}
    if pre_args.config:
        cfg = load_yaml_config(pre_args.config)

    # 2) Full parser, using config values as defaults
    p = argparse.ArgumentParser(parents=[pre])
    p.add_argument(
        "strategy",
        choices=["strat1", "strat2", "strat3"],
        default=cfg.get("strategy", None),
        nargs="?",
        help="Strategy to run (or set in config file).",
    )

    p.add_argument("--start", default=cfg.get("start", "2005-01-01"))
    p.add_argument("--end", default=cfg.get("end", None))
    p.add_argument("--source", default=cfg.get("source", "auto"), choices=["auto", "yahoo", "stooq"])
    p.add_argument("--cache", default=cfg.get("cache", "price_cache.parquet"))
    p.add_argument("--out", default=cfg.get("out", "outputs"))
    p.add_argument("--run-name", default=cfg.get("run_name", None))

    # universe/weights
    p.add_argument("--tickers", nargs="+", default=cfg.get("tickers", ["SPY", "ACWI"]))
    p.add_argument("--weights", nargs="+", type=float, default=cfg.get("weights", [0.7, 0.3]))

    # strat1 params
    p.add_argument("--amount", type=float, default=cfg.get("amount", 100.0))

    # strat2/3 params
    p.add_argument("--window", type=int, default=cfg.get("window", 5))
    p.add_argument("--threshold", type=float, default=cfg.get("threshold", 0.05))
    p.add_argument("--mode", choices=["fixed", "proportional"], default=cfg.get("mode", "fixed"))
    p.add_argument("--fixed", type=float, default=cfg.get("fixed", 50.0))
    p.add_argument("--k", type=float, default=cfg.get("k", 1000.0))

    args = p.parse_args(remaining)

    # If strategy omitted on CLI, require it from config
    if not args.strategy:
        raise SystemExit("Missing strategy. Provide positional strategy or set 'strategy:' in the config file.")

    # Build weights dict (and sanity-check)
    if len(args.tickers) != len(args.weights):
        raise SystemExit("--tickers and --weights must have the same length.")
    weights = dict(zip(args.tickers, args.weights))

    # Build a timestamp once
    ts = pd.Timestamp.today().strftime("%Y%m%d_%H%M%S")

    # run_name: CLI overrides config; else derive from config filename; always append timestamp
    if args.run_name:
        run_name = f"{args.run_name}__{ts}"
    elif pre_args.config:
        run_name = f"{basename_no_ext(pre_args.config)}__{ts}"
    else:
        run_name = f"{args.strategy}__{ts}"

    # Load prices
    prices = load_prices(args.tickers, start=args.start, end=args.end, source=args.source, cache_path=args.cache)

    # Instantiate strategy
    if args.strategy == "strat1":
        strat = MonthlyFixedBuy(amount_per_month=args.amount)
    elif args.strategy == "strat2":
        strat = RollingDrawdownBuy(
            window_days=args.window,
            threshold=args.threshold,
            mode=args.mode,
            fixed_amount=args.fixed,
            k=args.k,
        )
    else:
        strat = PeakDrawdownBuy(
            threshold=args.threshold,
            mode=args.mode,
            fixed_amount=args.fixed,
            k=args.k,
        )

    # Run
    csv_path, trades_path, metrics_path = run_backtest(
        prices=prices,
        weights=weights,
        strategy=strat,
        out_dir=args.out,
        run_name=run_name,
    )

    # If config was used, copy it next to outputs with matching prefix
    if pre_args.config:
        config_copy_path = os.path.join(args.out, f"{run_name}.config.yml")
        shutil.copyfile(pre_args.config, config_copy_path)
        print("Config saved:", config_copy_path)

    print("Wrote:")
    print(" ", csv_path)
    print(" ", trades_path)
    print(" ", metrics_path)

if __name__ == "__main__":
    main()