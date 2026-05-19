"""Train-free evaluation window layouts (context, holdout, naive baseline)."""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnknownVariableType=false

from dataclasses import dataclass
from typing import cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class EvalWindowSpec:
    """Hourly layout for backtest-style slices (indices are relative to the end of the series).

    - ``context``: number of history hours fed to the forecaster (immediately before the holdout).
    - ``horizon``: holdout length in hours (last ``horizon`` points).
    - ``seasonal_lag_hours``: lag for the naive seasonal baseline
      (e.g. 168 for same hour last week).
    """

    name: str
    context: int
    horizon: int
    seasonal_lag_hours: int


EVAL_WINDOW_24H = EvalWindowSpec(
    name="context_168h_horizon_24h",
    horizon=24,
    context=168,
    seasonal_lag_hours=168,
)

EVAL_WINDOW_48H = EvalWindowSpec(
    name="context_336h_horizon_48h",
    horizon=48,
    context=336,
    seasonal_lag_hours=168,
)


@dataclass(frozen=True, slots=True)
class EvalWindows:
    """Numeric windows plus the holdout index (reporting or plots vs time)."""

    context: NDArray[np.float64]
    holdout: NDArray[np.float64]
    baseline: NDArray[np.float64]
    holdout_index: pd.Index


def extract_windows(y: pd.Series, spec: EvalWindowSpec) -> EvalWindows:
    """Slice ``y`` into context, holdout, and naive baseline; all values as float64 vectors."""
    context_start = spec.context + spec.horizon
    baseline_start = spec.seasonal_lag_hours + spec.horizon

    context_series = y.iloc[-context_start : -spec.horizon]
    holdout_series = y.iloc[-spec.horizon :]
    baseline_series = y.iloc[-baseline_start : -spec.seasonal_lag_hours]

    if baseline_series.shape[0] != holdout_series.shape[0]:
        msg = (
            f"baseline length {baseline_series.shape[0]} != "
            f"holdout length {holdout_series.shape[0]} for spec {spec.name!r}"
        )
        raise ValueError(msg)

    return EvalWindows(
        context=cast(
            NDArray[np.float64],
            context_series.to_numpy(dtype=np.float64, copy=True),
        ),
        holdout=cast(
            NDArray[np.float64],
            holdout_series.to_numpy(dtype=np.float64, copy=True),
        ),
        baseline=cast(
            NDArray[np.float64],
            baseline_series.to_numpy(dtype=np.float64, copy=True),
        ),
        holdout_index=cast(pd.Index, holdout_series.index),
    )
