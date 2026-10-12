# Experimental Protocol

This document records the primary modelling and backtesting decisions used
in the project before interpreting the final strategy results.

## Research Questions

1. Which simple volatility model best forecasts next-day NIFTY 50 variance?
2. Are volatility-based Normal VaR forecasts appropriately calibrated?
3. Can volatility forecasts improve the risk characteristics of a long-only
   NIFTY equity allocation?
4. Are the conclusions robust to reasonable modelling and implementation
   assumptions?

## Data

- Primary asset: NIFTY 50
- Yahoo Finance ticker: `^NSEI`
- Frequency: Daily
- Sample begins in September 2007
- Market data downloaded programmatically using `yfinance`

Log returns are used for volatility modelling.

Simple returns are used for portfolio backtesting.

## Volatility Models

The primary models are:

- 20-day rolling variance
- EWMA variance with lambda = 0.94
- GARCH(1,1)

The primary out-of-sample forecast comparison begins in 2015.

GARCH parameters are estimated using an expanding window and refitted
monthly. Conditional variance is updated daily between parameter refits.

## Forecast Evaluation

Primary loss function:

- QLIKE

Secondary loss functions:

- MSE
- MAE

All models are evaluated over a common set of out-of-sample dates.

## Value-at-Risk

One-day Normal VaR is evaluated at:

- 95%
- 99%

VaR coverage is examined using:

- observed exception rates
- Kupiec unconditional coverage test

## Portfolio Rules

Strategies are long-only and unlevered.

Primary volatility target:

- 12% annualized volatility

Primary trend rule:

- 200-day moving average

Primary transaction cost:

- 5 basis points one-way

Primary execution lag:

- 1 trading day

Volatility-managed allocations rebalance weekly.

Portfolio weights are allowed to drift naturally between rebalance dates.

## Robustness

The following alternatives are reported without selecting the
best-performing configuration:

- Volatility target: 10%, 12%, 15%
- Moving-average window: 100, 200 trading days
- Transaction cost: 0, 5, 10, 20 bps
- Execution lag: 1, 2 trading days
- Bootstrap block length: 10, 15, 40 trading days

## Statistical Uncertainty

Sharpe-ratio differences are examined using a paired circular block
bootstrap.

Both strategies in each comparison are resampled using the same time
blocks so that they continue to experience the same market observations.

A confidence interval containing zero is interpreted as insufficient
evidence of a reliable Sharpe difference.

## Interpretation

A weak or negative strategy result is treated as a valid empirical result.

Headline specifications are not changed in response to final performance.
