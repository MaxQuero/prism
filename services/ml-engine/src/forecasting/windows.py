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

    def min_series_length(self, offset: int = 0) -> int:
        """Smallest series length usable for a holdout ending ``offset`` hours before the end."""
        return offset + self.horizon + max(self.context, self.seasonal_lag_hours)


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
class ExtractedWindows:
    """Numeric windows plus the holdout index (reporting or plots vs time)."""

    context: NDArray[np.float64]
    holdout: NDArray[np.float64]
    baseline: NDArray[np.float64]
    holdout_index: pd.Index


def extract_windows(y: pd.Series, spec: EvalWindowSpec, *, offset: int = 0) -> ExtractedWindows:
    """Slice ``y`` into context, holdout, and naive baseline; all values as float64 vectors.

    ``offset`` shifts the holdout back from the series end by that many hours
    (0 = last ``horizon`` points, 24 = the day before, etc.), enabling
    rolling-origin backtests.
    """
    if offset < 0:
        msg = f"offset must be >= 0, got {offset}"
        raise ValueError(msg)

    required = spec.min_series_length(offset)
    if y.shape[0] < required:
        msg = (
            f"series has {y.shape[0]} points but spec {spec.name!r} needs at least {required} "
            f"(context={spec.context}, horizon={spec.horizon}, "
            f"seasonal_lag={spec.seasonal_lag_hours}, offset={offset}); "
            "pandas would otherwise silently return truncated windows"
        )
        raise ValueError(msg)

    end = y.shape[0] - offset
    holdout_start = end - spec.horizon
    context_series = y.iloc[holdout_start - spec.context : holdout_start]
    holdout_series = y.iloc[holdout_start:end]
    baseline_series = y.iloc[
        holdout_start - spec.seasonal_lag_hours : end - spec.seasonal_lag_hours
    ]

    return ExtractedWindows(
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
