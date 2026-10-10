"""Performance measures for monthly returns."""
import numpy as np
import pandas as pd
import statsmodels.api as sm

PERIODS = 12


def annual_return(r):
    return (1 + r).prod() ** (PERIODS / len(r)) - 1


def annual_vol(r):
    return r.std() * np.sqrt(PERIODS)


def sharpe(r, rf=0.0):
    """Annualized Sharpe ratio, with a zero risk-free rate by default."""
    ex = r - rf / PERIODS
    return ex.mean() / ex.std() * np.sqrt(PERIODS)


def max_drawdown(r):
    wealth = (1 + r).cumprod()
    return (wealth / wealth.cummax() - 1).min()


def alpha_beta(r, benchmark):
    """Regress r on the benchmark (Newey-West errors). Alpha is annualized."""
    df = pd.concat([r, benchmark], axis=1).dropna()
    X = sm.add_constant(df.iloc[:, 1])
    res = sm.OLS(df.iloc[:, 0], X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    return {
        "alpha_annual": res.params.iloc[0] * PERIODS,
        "alpha_tstat": res.tvalues.iloc[0],
        "beta": res.params.iloc[1],
    }


def summary(r, name="strategy"):
    return pd.Series(
        {
            "Annualized return": annual_return(r),
            "Annualized volatility": annual_vol(r),
            "Sharpe": sharpe(r),
            "Max drawdown": max_drawdown(r),
        },
        name=name,
    )
