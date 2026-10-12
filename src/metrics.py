"""
Performance and risk-evaluation metrics used in the project.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import xlogy
from scipy.stats import chi2


TRADING_DAYS = 252


def annualized_sharpe(
    portfolio_returns,
    rf_returns,
    trading_days: int = TRADING_DAYS,
) -> float:
    """
    Annualized Sharpe ratio based on excess returns.
    """

    portfolio_returns = np.asarray(
        portfolio_returns,
        dtype=float,
    )

    rf_returns = np.asarray(
        rf_returns,
        dtype=float,
    )

    if len(portfolio_returns) != len(rf_returns):
        raise ValueError(
            "portfolio_returns and rf_returns must have equal length."
        )

    excess = (
        portfolio_returns
        - rf_returns
    )

    if len(excess) < 2:
        return np.nan

    std = np.std(
        excess,
        ddof=1,
    )

    if std == 0:
        return np.nan

    return (
        np.mean(excess)
        / std
        * np.sqrt(trading_days)
    )


def performance_metrics(
    backtest: pd.DataFrame,
    name: str,
    trading_days: int = TRADING_DAYS,
) -> dict:
    """
    Calculate core strategy-performance statistics.

    Expected backtest columns:
        Portfolio_Return
        Excess_Return
        Wealth
        Drawdown
        Turnover
        Weight
    """

    required_columns = [
        "Portfolio_Return",
        "Excess_Return",
        "Wealth",
        "Drawdown",
        "Turnover",
        "Weight",
    ]

    missing = [
        col
        for col in required_columns
        if col not in backtest.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    r = (
        backtest["Portfolio_Return"]
        .dropna()
    )

    excess = (
        backtest["Excess_Return"]
        .reindex(r.index)
    )

    if len(r) < 2:
        raise ValueError(
            "Not enough observations for performance analysis."
        )

    n = len(r)

    years = (
        n / trading_days
    )

    final_wealth = float(
        backtest["Wealth"]
        .loc[r.index]
        .iloc[-1]
    )

    cagr = (
        final_wealth
        ** (1 / years)
        - 1
    )

    annual_return = (
        r.mean()
        * trading_days
    )

    annual_vol = (
        r.std(ddof=1)
        * np.sqrt(trading_days)
    )

    sharpe = (
        excess.mean()
        / excess.std(ddof=1)
        * np.sqrt(trading_days)
    )

    max_drawdown = (
        backtest["Drawdown"]
        .loc[r.index]
        .min()
    )

    annual_turnover = (
        backtest["Turnover"]
        .loc[r.index]
        .sum()
        / years
    )

    average_exposure = (
        backtest["Weight"]
        .loc[r.index]
        .mean()
    )

    return {
        "Strategy": name,
        "CAGR": cagr,
        "Annual_Return": annual_return,
        "Annual_Vol": annual_vol,
        "Sharpe": sharpe,
        "Max_Drawdown": max_drawdown,
        "Final_Wealth": final_wealth,
        "Average_Exposure": average_exposure,
        "Annual_Turnover": annual_turnover,
    }


def kupiec_test(
    violations,
    expected_violation_rate: float,
) -> dict:
    """
    Kupiec unconditional-coverage test.

    Null hypothesis:
        observed VaR violation rate equals the expected rate.
    """

    if not 0 < expected_violation_rate < 1:
        raise ValueError(
            "expected_violation_rate must lie between 0 and 1."
        )

    violations = (
        pd.Series(violations)
        .dropna()
        .astype(int)
    )

    n = len(violations)

    if n == 0:
        raise ValueError(
            "No violation observations supplied."
        )

    x = int(
        violations.sum()
    )

    p0 = (
        expected_violation_rate
    )

    p_hat = (
        x / n
    )

    log_likelihood_null = (
        xlogy(
            x,
            p0,
        )
        +
        xlogy(
            n - x,
            1 - p0,
        )
    )

    log_likelihood_alt = (
        xlogy(
            x,
            p_hat,
        )
        +
        xlogy(
            n - x,
            1 - p_hat,
        )
    )

    lr_uc = (
        -2
        * (
            log_likelihood_null
            - log_likelihood_alt
        )
    )

    p_value = (
        1
        - chi2.cdf(
            lr_uc,
            df=1,
        )
    )

    return {
        "Observations": n,
        "Exceptions": x,
        "Expected_Rate": p0,
        "Observed_Rate": p_hat,
        "LR_UC": lr_uc,
        "p_value": p_value,
        "Reject_5pct": p_value < 0.05,
    }


def yearly_performance(
    backtest: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calendar-year return and maximum drawdown.
    """

    rows = []

    for year, group in backtest.groupby(
        backtest.index.year
    ):
        r = (
            group["Portfolio_Return"]
            .dropna()
        )

        if r.empty:
            continue

        wealth = (
            1 + r
        ).cumprod()

        annual_return = (
            wealth.iloc[-1] - 1
        )

        peak = (
            wealth.cummax()
        )

        drawdown = (
            wealth / peak - 1
        )

        rows.append({
            "Year": year,
            "Return": annual_return,
            "Max_Drawdown": drawdown.min(),
        })

    return (
        pd.DataFrame(rows)
        .set_index("Year")
    )
