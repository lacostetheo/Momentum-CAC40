# Momentum on the CAC 40

A backtest of a momentum strategy on CAC 40 stocks between 2005 and 2026, written in Python. I wanted to see whether the effect described by Jegadeesh and Titman (1993) shows up on a small universe of French stocks once transaction costs are taken into account.

## How it works

At the end of each month I rank the stocks by their return between t-12 and t-1 (the most recent month is skipped to avoid the short-term reversal effect). I buy the top 20% and short the bottom 20%, with equal weights, and hold the portfolio for one month. Costs are set at 10 basis points per unit of turnover.

Weights chosen at the end of month t are only used for the return of month t+1. A unit test checks that changing future prices does not change past returns.

To judge the strategy I look at return, volatility, Sharpe ratio and maximum drawdown. I also regress its returns on an equal-weighted portfolio of the same stocks to get an alpha and a beta.

## Running the code

```bash
pip install -r requirements.txt
pytest
jupyter notebook notebooks/01_momentum_cac40.ipynb
```

Prices are downloaded the first time and stored in `data/prices.csv`. The file `notebooks/momentum_cac40_colab.ipynb` contains all the code and can be opened directly in Google Colab.

## Files

```
src/data.py        price download and ticker list
src/strategy.py    signal, long/short weights and backtest
src/metrics.py     Sharpe, drawdown, alpha and beta
tests/             unit tests
notebooks/         full analysis
```

## Results

Universe: 39 stocks (URW.AS could not be found on Yahoo), January 2005 to September 2026, monthly rebalancing. Average turnover is about 1.0 per month.

| | Momentum gross | Momentum net | Equal-weighted |
|---|---|---|---|
| Annualized return | 5.3% | 4.0% | 10.0% |
| Annualized volatility | 19.5% | 19.5% | 17.2% |
| Sharpe | 0.37 | 0.31 | 0.64 |
| Max drawdown | -54% | -57% | -51% |

Against the equal-weighted portfolio, the net alpha is 11.3% per year (t = 3.0) but the beta is -0.48. The strategy is partly short the market, and over a period where the market rose a lot this produces a statistical alpha without the strategy being profitable on its own.

By formation window (net of costs):

| Window | Return | Sharpe | Max DD |
|---|---|---|---|
| 3 months | -6.9% | -0.25 | -88% |
| 6 months | -5.6% | -0.19 | -89% |
| 9 months | -3.5% | -0.07 | -81% |
| 12 months | 4.0% | 0.31 | -57% |

By cost level (12-month window):

| Costs | Return | Sharpe |
|---|---|---|
| 0 bps | 5.3% | 0.37 |
| 10 bps | 4.0% | 0.31 |
| 20 bps | 2.8% | 0.24 |
| 50 bps | -0.8% | 0.06 |

For the out-of-sample test I split the period in January 2018 and pick the window on the first part. It selects the 12-month window, with a Sharpe of -0.03 in training and 0.77 in the test period. The better test score comes mostly from 2024-2026: the curve was flat from 2009 to 2024, so I don't read it as proof that the strategy works.

The worst months are April 2009 (-30%), November 2020 (-27%), January 2011 (-15%), July 2010 (-13%) and April 2014 (-12%). They are sharp rebounds in stocks that were sold short (Renault, Stellantis and Michelin in 2009, Renault and the banks after the vaccine announcements in 2020). This is not a data error, it is the momentum crash described in the literature.

In short, on these 39 stocks, 12-1 momentum does worse than a simple equal-weighted portfolio and does not hold up when the window changes. I did not look into where the -81% to -89% drawdowns of the shorter windows come from.

## Limitations

- The tickers are the current CAC 40 members (worth checking, the list changes). Companies that left the index are missing, which cuts both ways for the strategy but mostly inflates the equal-weighted portfolio.
- With about 40 stocks, each quintile holds only 8 names, so the results are noisy. Momentum is usually studied on hundreds of stocks.
- Costs are proportional to turnover. The borrowing cost of short positions is not included.
- The risk-free rate is assumed to be zero in the Sharpe ratio.
- Possible next steps: Fama-French Europe factors, a wider universe with historical index membership, volatility-scaled momentum.

## Reference

Jegadeesh, N. and Titman, S. (1993), Returns to Buying Winners and Selling Losers, Journal of Finance.
