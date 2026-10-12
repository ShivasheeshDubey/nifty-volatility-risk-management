# Data

The primary dataset used in this project is daily NIFTY 50 market data.

## Primary Asset

- Index: NIFTY 50
- Yahoo Finance ticker: `^NSEI`
- Frequency: Daily
- Sample start: September 2007
- Source: Yahoo Finance via `yfinance`

The analysis downloads market data programmatically, so raw market-data
files are not committed to the repository.

## Returns

Both simple and logarithmic daily returns are constructed from the index
price series.

Log returns are used for volatility modelling.

Simple returns are used for portfolio backtesting.

## Risk-Free Rate

A flat 6% annual risk-free rate was used as an initial fallback during
development. The final repository will document either a historical Indian
short-rate series or a sensitivity analysis around the cash-rate assumption.

## NIFTYBEES Data Quality Check

NIFTYBEES was initially investigated as a tradeable ETF proxy.

The Yahoo Finance history contained severe price discontinuities that were
not corrected by the adjusted-price field. Because these discontinuities
would contaminate returns and volatility estimates, NIFTYBEES was not used
as the primary return series.
