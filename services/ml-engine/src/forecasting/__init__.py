"""Time-series forecasting utilities (Chronos zero-shot, backtest, dataset, metrics, plots)."""

from src.forecasting.backtest import BACKTEST_METRIC_COLUMNS, run_chronos_backtest
from src.forecasting.chronos import (
    ChronosEvalResult,
    clear_chronos_pipeline_cache,
    get_chronos_pipeline,
    run_chronos_eval,
)
from src.forecasting.dataset import (
    enforce_hourly_continuity,
    fetch_realized_history,
    find_hourly_gaps,
    load_consumption_series,
)
from src.forecasting.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    per_horizon_percentage_error,
)
from src.forecasting.plots import plot_forecast_comparison, plot_horizon_errors
from src.forecasting.windows import (
    EVAL_WINDOW_24H,
    EVAL_WINDOW_48H,
    EvalWindowSpec,
    ExtractedWindows,
    extract_windows,
)

__all__ = [
    "BACKTEST_METRIC_COLUMNS",
    "EVAL_WINDOW_24H",
    "EVAL_WINDOW_48H",
    "ChronosEvalResult",
    "EvalWindowSpec",
    "ExtractedWindows",
    "clear_chronos_pipeline_cache",
    "enforce_hourly_continuity",
    "extract_windows",
    "fetch_realized_history",
    "find_hourly_gaps",
    "get_chronos_pipeline",
    "load_consumption_series",
    "mean_absolute_error",
    "mean_absolute_percentage_error",
    "per_horizon_percentage_error",
    "plot_forecast_comparison",
    "plot_horizon_errors",
    "run_chronos_backtest",
    "run_chronos_eval",
]
