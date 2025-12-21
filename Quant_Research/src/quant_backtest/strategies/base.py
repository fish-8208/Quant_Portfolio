from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd

@dataclass(frozen=True)
class StrategyResult:
    extra_series: Dict[str, pd.Series]   # any additional columns to export

class Strategy:
    name: str = "base"

    def run(
        self,
        prices: pd.DataFrame,
        portfolio_weights: dict[str, float],
    ) -> tuple["BuyOnlyPortfolio", StrategyResult]:
        raise NotImplementedError