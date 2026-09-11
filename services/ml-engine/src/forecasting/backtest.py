"""Rolling-origin backtest: Chronos zero-shot vs naive baseline over many holdouts."""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd
import torch

from src.forecasting.chronos import get_chronos_pipeline
from src.forecasting.metrics import mean_absolute_error, mean_absolute_percentage_error
from src.forecasting.windows import EvalWindowSpec, ExtractedWindows, extract_windows

BACKTEST_METRIC_COLUMNS: Final[tuple[str, ...]] = (
    "mape_chronos",
    "mape_baseline",
    "mae_chronos",
    "mae_baseline",
)


def run_chronos_backtest(
    y: pd.Series,
    spec: EvalWindowSpec,
    *,
    model_id: str,
    num_windows: int = 10,
    stride_hours: int = 24,
    device_map: str = "cpu",
    num_samples: int = 20,
) -> pd.DataFrame:
    """Evaluate Chronos on ``num_windows`` holdouts, each shifted back by ``stride_hours``.

    One row per window with MAPE/MAE for the Chronos median and the naive seasonal
    baseline. A single window is too noisy to rank models: aggregate with
    ``df[list(BACKTEST_METRIC_COLUMNS)].agg(["mean", "std"])`` and only keep a model
    that beats the baseline on average and consistently.

    All contexts are predicted in one batched call, so the cost is roughly one
    forecast regardless of ``num_windows``.
    """
    if num_windows < 1:
        msg = f"num_windows must be >= 1, got {num_windows}"
        raise ValueError(msg)
    if stride_hours < 1:
        msg = f"stride_hours must be >= 1, got {stride_hours}"
        raise ValueError(msg)

    offsets = [i * stride_hours for i in range(num_windows)]
    required = spec.min_series_length(offsets[-1])
    if y.shape[0] < required:
        msg = (
            f"series has {y.shape[0]} points but {num_windows} windows of "
            f"{spec.name!r} with stride {stride_hours}h need {required}; "
            "reduce num_windows/stride_hours or fetch more history"
        )
        raise ValueError(msg)

    windows: list[ExtractedWindows] = [
        extract_windows(y, spec, offset=offset) for offset in offsets
    ]

    pipeline = get_chronos_pipeline(model_id, device_map=device_map)
    context_batch = torch.stack(
        [torch.tensor(window.context, dtype=torch.float32) for window in windows]
    )
    forecasts = pipeline.predict(
        context_batch,
        prediction_length=spec.horizon,
        num_samples=num_samples,
    )
    # forecasts: (num_windows, num_samples, horizon)
    medians = np.median(forecasts.detach().float().cpu().numpy(), axis=1).astype(np.float64)

    rows: list[dict[str, object]] = []
    for offset, window, median in zip(offsets, windows, medians, strict=True):
        rows.append(
            {
                "offset_hours": offset,
                "holdout_start": window.holdout_index[0],
                "mape_chronos": mean_absolute_percentage_error(window.holdout, median),
                "mape_baseline": mean_absolute_percentage_error(window.holdout, window.baseline),
                "mae_chronos": mean_absolute_error(window.holdout, median),
                "mae_baseline": mean_absolute_error(window.holdout, window.baseline),
            }
        )
    return pd.DataFrame(rows)
