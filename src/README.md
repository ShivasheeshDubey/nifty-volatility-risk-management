# Source Modules

Reusable project functionality is separated from the research notebook.

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
- equity/cash portfolio backtesting

## Remaining Modules

The repository also separates:

- statistical and performance metrics
- VaR coverage tests
- paired block-bootstrap inference

into dedicated modules.
