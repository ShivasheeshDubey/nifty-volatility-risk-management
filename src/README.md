# Source Modules

Reusable project functionality is separated from the end-to-end research notebook.

## `volatility.py`

Implements:

- 20-day rolling variance forecasts
- EWMA volatility forecasts
- expanding-window GARCH(1,1) forecasts
- annualized volatility conversion

## `backtest.py`

Implements:

- trading-week identification
- execution-lag handling
- transaction costs
- natural portfolio-weight drift
- long-only equity/cash portfolio backtesting

## `metrics.py`

Implements:

- annualized Sharpe ratio
- CAGR and volatility metrics
- maximum drawdown
- turnover and exposure statistics
- Kupiec unconditional VaR coverage test
- calendar-year performance summaries

## `bootstrap.py`

Implements:

- paired backtest alignment
- circular block resampling
- paired Sharpe-ratio bootstrap confidence intervals

The notebook in `notebooks/` contains the complete empirical workflow,
while the modules in this directory contain reusable modelling and
evaluation logic.
