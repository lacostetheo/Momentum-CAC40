"""Cross-sectional long/short momentum, after Jegadeesh and Titman (1993)."""
import numpy as np
import pandas as pd


def momentum_signal(monthly_prices, lookback=12, skip=1):
    """Return between t-lookback and t-skip, using only prices known at the end of month t."""
    return monthly_prices.shift(skip) / monthly_prices.shift(lookback) - 1


def long_short_weights(signal, quantile=0.2):
    """Buy the top quantile and short the bottom one, equal weights, summing to zero."""
    w = pd.DataFrame(0.0, index=signal.index, columns=signal.columns)
    for date, row in signal.iterrows():
        row = row.dropna()
        n = int(len(row) * quantile)
        if n < 1:
            continue
        ranked = row.sort_values()
        w.loc[date, ranked.index[-n:]] = 1.0 / n
        w.loc[date, ranked.index[:n]] = -1.0 / n
    return w


def backtest(monthly_prices, lookback=12, skip=1, quantile=0.2, cost_bps=10.0):
    """Monthly strategy returns, before and after costs.

    Weights chosen at the end of month t are applied to the return of month t+1.
    Costs are proportional to turnover. The borrowing cost of short positions
    is not included.
    """
    rets = monthly_prices.pct_change()
    w = long_short_weights(momentum_signal(monthly_prices, lookback, skip), quantile)
    w_held = w.shift(1)
    gross = (w_held * rets).sum(axis=1, min_count=1)
    turnover = w_held.diff().abs().sum(axis=1)
    net = gross - turnover * cost_bps / 1e4
    out = pd.DataFrame({"gross": gross, "net": net, "turnover": turnover})
    return out.dropna(subset=["gross"]).loc[lambda d: d.index >= w_held.dropna(how="all").index[1]]
