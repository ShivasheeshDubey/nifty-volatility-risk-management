"""
Volatility forecasting models used in the project.

All return inputs are expected in decimal form, e.g.

    0.01 = 1% daily return

Forecasts are stored on the date on which they are created.

Therefore:

    forecast[t]

represents the variance forecast for the next trading day,
using information available through date t.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from arch import arch_model


TRADING_DAYS = 252


def rolling_variance_forecast(
    returns: pd.Series,
    window: int = 20,
) -> pd.Series:
    """
    Compute a rolling zero-mean variance forecast.

    For date t:

        h_(t+1|t) = mean(r_t^2, ..., r_(t-window+1)^2)

    Parameters
    ----------
    returns
        Daily returns in decimal units.

    window
        Number of observations in the rolling window.

    Returns
    -------
    pd.Series
        One-step-ahead variance forecasts stored on
        their forecast-creation dates.
    """

    if window <= 0:
        raise ValueError("window must be positive.")

    r = returns.astype(float)

    squared_returns = r**2

    forecast = squared_returns.rolling(
        window=window,
        min_periods=window,
    ).mean()

    return forecast


def ewma_variance_forecast(
    returns: pd.Series,
    lam: float = 0.94,
    initial_window: int = 20,
) -> pd.Series:
    """
    Compute an EWMA one-day-ahead variance forecast.

    Recursion:

        h_(t+1|t)
            = lam * h_(t|t-1)
            + (1 - lam) * r_t^2

    The initial variance is seeded using the mean
    squared return over `initial_window` observations.

    Parameters
    ----------
    returns
        Daily returns in decimal units.

    lam
        EWMA decay parameter.

    initial_window
        Number of observations used to initialize variance.

    Returns
    -------
    pd.Series
        One-step-ahead variance forecasts stored on
        their forecast-creation dates.
    """

    if not 0 < lam < 1:
        raise ValueError(
            "lam must lie strictly between 0 and 1."
        )

    if initial_window <= 0:
        raise ValueError(
            "initial_window must be positive."
        )

    original_index = returns.index

    r = (
        returns
        .dropna()
        .astype(float)
        .copy()
    )

    if len(r) < initial_window:
        raise ValueError(
            "Not enough return observations to initialize EWMA."
        )

    squared_returns = r**2

    forecasts = pd.Series(
        np.nan,
        index=r.index,
        dtype=float,
    )

    seed_position = initial_window - 1

    initial_variance = (
        squared_returns
        .iloc[:initial_window]
        .mean()
    )

    # The seed uses information through this date,
    # so it is interpreted as a forecast for the next day.
    forecasts.iloc[seed_position] = (
        initial_variance
    )

    for i in range(
        initial_window,
        len(r),
    ):
        forecasts.iloc[i] = (
            lam
            * forecasts.iloc[i - 1]
            +
            (1 - lam)
            * squared_returns.iloc[i]
        )

    return forecasts.reindex(
        original_index
    )


def variance_to_annualized_volatility(
    variance: pd.Series,
    trading_days: int = TRADING_DAYS,
) -> pd.Series:
    """
    Convert daily variance forecasts into annualized volatility.

    Parameters
    ----------
    variance
        Daily variance series.

    trading_days
        Number of trading days used for annualization.

    Returns
    -------
    pd.Series
        Annualized volatility in decimal units.
    """

    valid_variance = variance.dropna()

    if (valid_variance < 0).any():
        raise ValueError(
            "Variance cannot be negative."
        )

    return (
        np.sqrt(variance)
        * np.sqrt(trading_days)
    )


def _fit_garch11(
    returns_pct: pd.Series,
):
    """
    Fit zero-mean Normal GARCH(1,1).

    Returns are expected in percentage units.
    """

    model = arch_model(
        returns_pct,
        mean="Zero",
        vol="GARCH",
        p=1,
        q=1,
        dist="normal",
        rescale=False,
    )

    result = model.fit(
        disp="off",
        update_freq=0,
    )

    return result


def garch11_monthly_walkforward(
    returns: pd.Series,
    oos_start: str = "2015-01-01",
) -> tuple[pd.Series, pd.DataFrame]:
    """
    Expanding-window GARCH(1,1) forecasting.

    Model:

        h_(t+1)
            = omega
            + alpha * r_t^2
            + beta * h_t

    Parameters are re-estimated once per calendar month.

    Between monthly refits, conditional variance is updated
    daily using fixed parameters.

    The GARCH model is fitted on returns multiplied by 100
    for numerical stability.

    Parameters
    ----------
    returns
        Daily returns in decimal units.

    oos_start
        Beginning of the intended out-of-sample period.

    Returns
    -------
    forecast_var_decimal : pd.Series
        One-day-ahead variance forecasts in decimal-return
        variance units.

    parameter_history : pd.DataFrame
        GARCH parameters recorded at every monthly refit.
    """

    r = (
        returns
        .dropna()
        .astype(float)
        .sort_index()
        .copy()
    )

    if not isinstance(
        r.index,
        pd.DatetimeIndex,
    ):
        raise TypeError(
            "returns must have a DatetimeIndex."
        )

    if not r.index.is_monotonic_increasing:
        raise ValueError(
            "returns index must be sorted by date."
        )

    # Percentage-return units make GARCH optimization
    # numerically more stable.
    r_pct = 100 * r

    dates = r_pct.index

    oos_start = pd.Timestamp(
        oos_start
    )

    first_oos_pos = dates.searchsorted(
        oos_start
    )

    if first_oos_pos <= 0:
        raise ValueError(
            "OOS start must occur after the beginning of the sample."
        )

    if first_oos_pos < 500:
        raise ValueError(
            "At least 500 observations are required before OOS forecasting."
        )

    forecast_var_pct2 = pd.Series(
        np.nan,
        index=dates,
        dtype=float,
    )

    parameter_records = []

    # --------------------------------------------------
    # Initial fit:
    # all data through the final observation before OOS
    # --------------------------------------------------

    initial_end_pos = (
        first_oos_pos - 1
    )

    initial_train = (
        r_pct.iloc[
            :initial_end_pos + 1
        ]
    )

    result = _fit_garch11(
        initial_train
    )

    omega = float(
        result.params["omega"]
    )

    alpha = float(
        result.params["alpha[1]"]
    )

    beta = float(
        result.params["beta[1]"]
    )

    # Conditional variance corresponding to
    # the final fitted observation.
    h_t = float(
        result
        .conditional_volatility
        .iloc[-1] ** 2
    )

    initial_date = (
        dates[initial_end_pos]
    )

    current_refit_month = (
        initial_date.year,
        initial_date.month,
    )

    persistence = (
        alpha + beta
    )

    if persistence < 1:
        long_run_var_pct2 = (
            omega
            /
            (1 - persistence)
        )

        long_run_ann_vol = (
            np.sqrt(
                long_run_var_pct2
            )
            * np.sqrt(TRADING_DAYS)
            / 100
        )
    else:
        long_run_ann_vol = np.nan

    parameter_records.append({
        "Refit_Date":
            initial_date,

        "omega":
            omega,

        "alpha":
            alpha,

        "beta":
            beta,

        "alpha_plus_beta":
            persistence,

        "Long_Run_Ann_Vol":
            long_run_ann_vol,

        "Convergence_Flag":
            result.convergence_flag,

        "Estimation_Observations":
            len(initial_train),
    })

    # --------------------------------------------------
    # Walk forward through time
    # --------------------------------------------------

    for i in range(
        initial_end_pos,
        len(r_pct) - 1,
    ):
        current_date = dates[i]

        month_key = (
            current_date.year,
            current_date.month,
        )

        # Re-estimate parameters when entering
        # a new calendar month.
        if (
            i > initial_end_pos
            and
            month_key
            != current_refit_month
        ):
            train = (
                r_pct.iloc[
                    :i + 1
                ]
            )

            result = _fit_garch11(
                train
            )

            omega = float(
                result.params["omega"]
            )

            alpha = float(
                result.params["alpha[1]"]
            )

            beta = float(
                result.params["beta[1]"]
            )

            h_t = float(
                result
                .conditional_volatility
                .iloc[-1] ** 2
            )

            current_refit_month = (
                month_key
            )

            persistence = (
                alpha + beta
            )

            if persistence < 1:
                long_run_var_pct2 = (
                    omega
                    /
                    (1 - persistence)
                )

                long_run_ann_vol = (
                    np.sqrt(
                        long_run_var_pct2
                    )
                    * np.sqrt(
                        TRADING_DAYS
                    )
                    / 100
                )
            else:
                long_run_ann_vol = (
                    np.nan
                )

            parameter_records.append({
                "Refit_Date":
                    current_date,

                "omega":
                    omega,

                "alpha":
                    alpha,

                "beta":
                    beta,

                "alpha_plus_beta":
                    persistence,

                "Long_Run_Ann_Vol":
                    long_run_ann_vol,

                "Convergence_Flag":
                    result.convergence_flag,

                "Estimation_Observations":
                    len(train),
            })

        # ----------------------------------------------
        # One-day-ahead forecast made at current_date
        # ----------------------------------------------

        r_t_pct = float(
            r_pct.iloc[i]
        )

        h_next = (
            omega
            +
            alpha * (
                r_t_pct**2
            )
            +
            beta * h_t
        )

        forecast_var_pct2.loc[
            current_date
        ] = h_next

        # Today's forecast becomes tomorrow's
        # conditional variance state.
        h_t = h_next

    # Variance of percentage returns is 10,000 times
    # variance of decimal returns.
    forecast_var_decimal = (
        forecast_var_pct2
        / 10_000
    )

    parameter_history = (
        pd.DataFrame(
            parameter_records
        )
        .set_index(
            "Refit_Date"
        )
    )

    return (
        forecast_var_decimal,
        parameter_history,
    )
