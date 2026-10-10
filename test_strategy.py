import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data import synthetic_prices, to_monthly
from src.strategy import backtest, long_short_weights, momentum_signal


def monthly():
    return to_monthly(synthetic_prices(n_assets=20, years=10))


def test_weights_sum_to_zero():
    w = long_short_weights(momentum_signal(monthly())).dropna(how="all")
    active = w[(w != 0).any(axis=1)]
    assert np.allclose(active.sum(axis=1), 0)
    assert np.allclose(active.abs().sum(axis=1), 2)


def test_future_prices_do_not_change_past_returns():
    p = monthly()
    base = backtest(p)
    cut = p.index[80]
    p2 = p.copy()
    p2.loc[p2.index > cut] *= 1.5
    alt = backtest(p2)
    before = base.index[base.index <= cut]
    pd.testing.assert_frame_equal(base.loc[before], alt.loc[before])


def test_costs_reduce_returns():
    res = backtest(monthly(), cost_bps=20)
    assert (res["net"] <= res["gross"] + 1e-12).all()


def test_incomplete_last_month_is_dropped():
    idx = pd.bdate_range("2023-01-02", "2023-10-10")
    prices = pd.DataFrame({"A": np.arange(len(idx), dtype=float) + 100}, index=idx)
    assert to_monthly(prices).index[-1] == pd.Timestamp("2023-09-30")
