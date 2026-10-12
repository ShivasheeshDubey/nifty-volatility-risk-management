"""
Portfolio backtesting utilities.

The engine is designed for long-only equity/cash strategies.

Important timing convention
---------------------------
A target weight calculated at the close of day t cannot earn
day-t returns.

With execution_lag=1, a decision created on day t is first
applied to the next trading day's return.

Portfolio weights are allowed to drift naturally between
scheduled rebalance dates.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def get_week_end_mask(
    index: pd.DatetimeIndex,
) -> pd.Series:
    """
    Identify the final observed trading day of each week.

    This works correctly around exchange holidays because it
    selects the final available observation within each W-FRI
    weekly period rather than assuming every Friday is traded.

    Parameters
    ----------
    index
        Trading-date DatetimeIndex.

    Returns
    -------
    pd.Series
        Boolean series indexed by date.
    """

    if not isinstance(
        index,
        pd.DatetimeIndex,
    ):
        raise TypeError(
            "index must be a pandas DatetimeIndex."
        )

    weeks = pd.Series(
        index.to_period("W-FRI"),
        index=index,
    )

    return (
        weeks != weeks.shift(-1)
    )


def run_backtest_drift_aware(
    equity_return: pd.Series,
    rf_return: pd.Series,
    target_weight: pd.Series,
    rebalance_mask: pd.Series,
    cost_bps: float = 5.0,
    execution_lag: int = 1,
) -> pd.DataFrame:
    """
    Backtest a long-only equity/cash allocation.

    Parameters
    ----------
    equity_return
        Daily simple equity returns in decimal units.

    rf_return
        Daily simple cash/risk-free returns in decimal units.

    target_weight
        Desired equity weight determined using information
        available through each date.

        Values must lie between 0 and 1.

    rebalance_mask
        Boolean series indicating dates on which a new target
        allocation is selected.

    cost_bps
        One-way transaction cost in basis points per unit of
        portfolio turnover.

        Example:
            5 bps -> 0.0005 * turnover

    execution_lag
        Number of trading days between signal creation and
        portfolio implementation.

        Primary project setting: 1.

    Returns
    -------
    pd.DataFrame
        Daily backtest containing exposure, turnover, costs,
        portfolio returns, wealth, and drawdown.
    """

    if execution_lag < 0:
        raise ValueError(
            "execution_lag cannot be negative."
        )

    if cost_bps < 0:
        raise ValueError(
            "cost_bps cannot be negative."
        )

    df = pd.concat(
        [
            equity_return.rename(
                "Equity_Return"
            ),
            rf_return.rename(
                "RF_Return"
            ),
            target_weight.rename(
                "Decision_Target"
            ),
            rebalance_mask.rename(
                "Decision_Rebalance"
            ),
        ],
        axis=1,
    ).sort_index()

    df["Decision_Rebalance"] = (
        df["Decision_Rebalance"]
        .fillna(False)
        .astype(bool)
    )

    # --------------------------------------------------
    # Timing:
    # decision at t becomes executable after the lag.
    # --------------------------------------------------

    df["Execution_Target"] = (
        df["Decision_Target"]
        .shift(execution_lag)
    )

    df["Execution_Rebalance"] = (
        df["Decision_Rebalance"]
        .shift(execution_lag)
        .fillna(False)
        .astype(bool)
    )

    df = df.dropna(
        subset=[
            "Equity_Return",
            "RF_Return",
        ]
    )

    # First date on which the strategy can actually trade.
    valid_start = (
        df["Execution_Rebalance"]
        &
        df["Execution_Target"].notna()
    )

    if not valid_start.any():
        raise ValueError(
            "Strategy never reaches a valid rebalance date."
        )

    first_date = (
        valid_start[
            valid_start
        ]
        .index[0]
    )

    df = df.loc[
        first_date:
    ].copy()

    cost_rate = (
        cost_bps / 10_000
    )

    current_weight = 0.0
    wealth = 1.0

    records = []

    # --------------------------------------------------
    # Daily walk-forward backtest
    # --------------------------------------------------

    for date, row in df.iterrows():

        equity_r = float(
            row["Equity_Return"]
        )

        rf_r = float(
            row["RF_Return"]
        )

        pre_trade_weight = (
            current_weight
        )

        # ----------------------------------------------
        # Rebalance only when scheduled.
        # ----------------------------------------------

        should_rebalance = (
            bool(
                row[
                    "Execution_Rebalance"
                ]
            )
            and
            pd.notna(
                row[
                    "Execution_Target"
                ]
            )
        )

        if should_rebalance:

            target = float(
                row[
                    "Execution_Target"
                ]
            )

            if not 0 <= target <= 1:
                raise ValueError(
                    f"Target weight outside [0, 1] on {date}: "
                    f"{target}"
                )

            weight_during_day = target

            turnover = abs(
                target
                -
                pre_trade_weight
            )

        else:

            # No trade:
            # yesterday's end-of-day weight becomes today's
            # starting exposure.
            weight_during_day = (
                pre_trade_weight
            )

            turnover = 0.0

        # ----------------------------------------------
        # Transaction cost
        # ----------------------------------------------

        transaction_cost = (
            cost_rate
            *
            turnover
        )

        # ----------------------------------------------
        # Gross portfolio return before trading cost
        # ----------------------------------------------

        gross_portfolio_return = (
            weight_during_day
            *
            equity_r
            +
            (
                1
                -
                weight_during_day
            )
            *
            rf_r
        )

        portfolio_return = (
            gross_portfolio_return
            -
            transaction_cost
        )

        wealth *= (
            1
            +
            portfolio_return
        )

        # ----------------------------------------------
        # Natural exposure drift after market returns
        # ----------------------------------------------

        equity_value = (
            weight_during_day
            *
            (1 + equity_r)
        )

        cash_value = (
            (
                1
                -
                weight_during_day
            )
            *
            (1 + rf_r)
        )

        gross_value = (
            equity_value
            +
            cash_value
        )

        if gross_value <= 0:
            raise ValueError(
                "Gross portfolio value became non-positive."
            )

        end_weight = (
            equity_value
            /
            gross_value
        )

        records.append({
            "Date":
                date,

            "Target_Weight":
                row[
                    "Execution_Target"
                ],

            "Rebalanced":
                should_rebalance,

            "Pre_Trade_Weight":
                pre_trade_weight,

            "Weight":
                weight_during_day,

            "End_Weight":
                end_weight,

            "Turnover":
                turnover,

            "Transaction_Cost":
                transaction_cost,

            "Equity_Return":
                equity_r,

            "RF_Return":
                rf_r,

            "Portfolio_Return":
                portfolio_return,

            "Excess_Return":
                portfolio_return
                -
                rf_r,

            "Wealth":
                wealth,
        })

        current_weight = (
            end_weight
        )

    result = (
        pd.DataFrame(
            records
        )
        .set_index(
            "Date"
        )
    )

    # --------------------------------------------------
    # Drawdown
    # --------------------------------------------------

    result[
        "Peak_Wealth"
    ] = (
        result[
            "Wealth"
        ].cummax()
    )

    result[
        "Drawdown"
    ] = (
        result[
            "Wealth"
        ]
        /
        result[
            "Peak_Wealth"
        ]
        -
        1
    )

    return result


def constant_target(
    index: pd.Index,
    weight: float,
) -> pd.Series:
    """
    Create a constant target-weight series.
    """

    if not 0 <= weight <= 1:
        raise ValueError(
            "weight must lie between 0 and 1."
        )

    return pd.Series(
        float(weight),
        index=index,
        dtype=float,
    )


def first_date_only_mask(
    index: pd.Index,
) -> pd.Series:
    """
    Rebalance only once, on the first date.

    Useful for buy-and-hold strategies.
    """

    if len(index) == 0:
        raise ValueError(
            "index cannot be empty."
        )

    mask = pd.Series(
        False,
        index=index,
    )

    mask.iloc[0] = True

    return mask
