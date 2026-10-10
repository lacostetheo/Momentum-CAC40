"""Loading CAC 40 prices from Yahoo Finance."""
from pathlib import Path

import numpy as np
import pandas as pd

CAC40_TICKERS = [
    "AI.PA", "AIR.PA", "ALO.PA", "MT.AS", "CS.PA", "BNP.PA", "EN.PA",
    "CAP.PA", "CA.PA", "ACA.PA", "BN.PA", "DSY.PA", "ENGI.PA", "EL.PA",
    "ERF.PA", "RMS.PA", "KER.PA", "OR.PA", "LR.PA", "MC.PA", "ML.PA",
    "ORA.PA", "RI.PA", "PUB.PA", "RNO.PA", "SAF.PA", "SGO.PA", "SAN.PA",
    "SU.PA", "GLE.PA", "STLAP.PA", "STMPA.PA", "TEP.PA", "HO.PA", "TTE.PA",
    "URW.AS", "VIE.PA", "DG.PA", "WLN.PA", "VIV.PA",
]
BENCHMARK = "^FCHI"


def download_prices(tickers, start="2005-01-01", end=None, cache="data/prices.csv"):
    """Download adjusted prices and keep them in a CSV file."""
    cache = Path(cache)
    if cache.exists():
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    import yfinance as yf

    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    prices = raw["Close"].dropna(axis=1, how="all")
    missing = sorted(set(tickers) - set(prices.columns))
    if missing:
        print(f"No data for {missing}")
    cache.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(cache)
    return prices


def to_monthly(prices):
    """Last price of each month, leaving out the current month if it is not over."""
    monthly = prices.resample("ME").last()
    if prices.index[-1] < monthly.index[-1] - pd.Timedelta(days=3):
        monthly = monthly.iloc[:-1]
    return monthly


def synthetic_prices(n_assets=40, years=15, seed=0):
    """Random prices to test the code offline. Not meant to say anything about markets."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2008-01-01", periods=years * 252)
    market = rng.normal(0.0003, 0.01, len(idx))
    rets = market[:, None] + rng.normal(0.0001, 0.015, (len(idx), n_assets))
    cols = [f"S{i:02d}" for i in range(n_assets)]
    return pd.DataFrame(100 * np.exp(np.cumsum(rets, axis=0)), index=idx, columns=cols)
