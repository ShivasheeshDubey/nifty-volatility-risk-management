"""
Block-bootstrap utilities for strategy comparisons.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import annualized_sharpe


def align_backtests(
    bt_a: pd.DataFrame,
    bt_b: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Align two backtests to a common set of dates.
    """

    common_index = (
        bt_a.index
        .intersection(
            bt_b.index
        )
    )

    if len(common_index) == 0:
        raise ValueError(
            "Backtests have no common dates."
        )

    a = (
        bt_a
        .loc[common_index]
        .copy()
    )

    b = (
        bt_b
        .loc[common_index]
        .copy()
    )

    return a, b


def circular_block_indices(
    n: int,
    block_length: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Generate bootstrap indices using circular blocks.

    Consecutive observations are sampled together so that
    short-range time dependence is partially preserved.
    """

    if n <= 0:
        raise ValueError(
            "n must be positive."
        )

    if block_length <= 0:
        raise ValueError(
            "block_length must be positive."
        )

    indices = []

    while len(indices) < n:

        start = int(
            rng.integers(
                0,
                n,
            )
        )

        block = (
            start
            + np.arange(
                block_length
            )
        ) % n

        indices.extend(
            block.tolist()
        )

    return np.asarray(
        indices[:n],
        dtype=int,
    )


def paired_sharpe_bootstrap(
    bt_a: pd.DataFrame,
    bt_b: pd.DataFrame,
    block_length: int = 15,
    n_bootstrap: int = 5000,
    seed: int = 42,
) -> dict:
    """
    Paired circular block bootstrap for a Sharpe difference.

    Computes:

        Sharpe(A) - Sharpe(B)

    The same bootstrap indices are applied to both strategies
    and the risk-free series so that the comparison remains paired.
    """

    if n_bootstrap <= 0:
        raise ValueError(
            "n_bootstrap must be positive."
        )

    a, b = align_backtests(
        bt_a,
        bt_b,
    )

    required = [
        "Portfolio_Return",
        "RF_Return",
    ]

    for name, bt in [
        ("bt_a", a),
        ("bt_b", b),
    ]:
        missing = [
            col
            for col in required
            if col not in bt.columns
        ]

        if missing:
            raise ValueError(
                f"{name} missing columns: {missing}"
            )

    rf_a = (
        a["RF_Return"]
        .to_numpy(
            dtype=float
        )
    )

    rf_b = (
        b["RF_Return"]
        .to_numpy(
            dtype=float
        )
    )

    if not np.allclose(
        rf_a,
        rf_b,
    ):
        raise ValueError(
            "Risk-free return series differ between backtests."
        )

    ra = (
        a["Portfolio_Return"]
        .to_numpy(
            dtype=float
        )
    )

    rb = (
        b["Portfolio_Return"]
        .to_numpy(
            dtype=float
        )
    )

    rf = rf_a

    n = len(ra)

    sharpe_a = (
        annualized_sharpe(
            ra,
            rf,
        )
    )

    sharpe_b = (
        annualized_sharpe(
            rb,
            rf,
        )
    )

    observed_difference = (
        sharpe_a - sharpe_b
    )

    rng = np.random.default_rng(
        seed
    )

    bootstrap_differences = (
        np.empty(
            n_bootstrap,
            dtype=float,
        )
    )

    bootstrap_sharpe_a = (
        np.empty(
            n_bootstrap,
            dtype=float,
        )
    )

    bootstrap_sharpe_b = (
        np.empty(
            n_bootstrap,
            dtype=float,
        )
    )

    for i in range(
        n_bootstrap
    ):
        idx = (
            circular_block_indices(
                n=n,
                block_length=block_length,
                rng=rng,
            )
        )

        sr_a = (
            annualized_sharpe(
                ra[idx],
                rf[idx],
            )
        )

        sr_b = (
            annualized_sharpe(
                rb[idx],
                rf[idx],
            )
        )

        bootstrap_sharpe_a[i] = (
            sr_a
        )

        bootstrap_sharpe_b[i] = (
            sr_b
        )

        bootstrap_differences[i] = (
            sr_a - sr_b
        )

    ci_lower = float(
        np.percentile(
            bootstrap_differences,
            2.5,
        )
    )

    ci_upper = float(
        np.percentile(
            bootstrap_differences,
            97.5,
        )
    )

    probability_a_better = float(
        np.mean(
            bootstrap_differences
            > 0
        )
    )

    return {
        "Sharpe_A": sharpe_a,
        "Sharpe_B": sharpe_b,
        "Observed_Difference": observed_difference,
        "CI_2.5%": ci_lower,
        "CI_97.5%": ci_upper,
        "Bootstrap_P_A_gt_B": probability_a_better,
        "Bootstrap_Differences": bootstrap_differences,
        "Bootstrap_Sharpe_A": bootstrap_sharpe_a,
        "Bootstrap_Sharpe_B": bootstrap_sharpe_b,
    }
