"""
Reusable tools for volatility forecasting,
risk analysis, and portfolio backtesting.
"""

from .volatility import (
    rolling_variance_forecast,
    ewma_variance_forecast,
    variance_to_annualized_volatility,
    garch11_monthly_walkforward,
)

from .backtest import (
    get_week_end_mask,
    run_backtest_drift_aware,
    constant_target,
    first_date_only_mask,
)

from .metrics import (
    annualized_sharpe,
    performance_metrics,
    kupiec_test,
    yearly_performance,
)

from .bootstrap import (
    align_backtests,
    circular_block_indices,
    paired_sharpe_bootstrap,
)
