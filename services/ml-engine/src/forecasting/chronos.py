"""Chronos zero-shot inference and evaluation helpers."""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd
import torch
from chronos import ChronosPipeline
from numpy.typing import NDArray

from src.forecasting.windows import EvalWindowSpec, extract_windows

_QUANTILE_LEVELS: Final[tuple[float, ...]] = (0.1, 0.5, 0.9)

_MAX_REASONABLE_PEAK_MULTIPLIER: Final[float] = 1.5

_PIPELINE_CACHE: dict[tuple[str, str], ChronosPipeline] = {}


def get_chronos_pipeline(model_id: str, device_map: str = "cpu") -> ChronosPipeline:
    """Return a cached Chronos pipeline for (model_id, device_map)."""
    key = (model_id, device_map)
    if key not in _PIPELINE_CACHE:
        _PIPELINE_CACHE[key] = ChronosPipeline.from_pretrained(model_id, device_map=device_map)
    return _PIPELINE_CACHE[key]


def clear_chronos_pipeline_cache() -> None:
    """Drop cached pipelines (e.g. after OOM or in tests)."""
    _PIPELINE_CACHE.clear()


@dataclass(frozen=True, slots=True)
class ChronosEvalResult:
    """Outputs of a single zero-shot Chronos evaluation on a holdout window."""

    window_name: str
    model_id: str
    prediction_length: int
    ground_truth: NDArray[np.float64]
    baseline: NDArray[np.float64]
    median: NDArray[np.float64]
    low: NDArray[np.float64]
    high: NDArray[np.float64]
    sanity_messages: tuple[str, ...]
    holdout_index: pd.Index


def _physical_sanity_messages(
    y_full: pd.Series,
    low: NDArray[np.float64],
    high: NDArray[np.float64],
) -> tuple[str, ...]:
    messages: list[str] = []
    if float(np.min(low)) < 0.0:
        messages.append("Negative P10 values — check physical plausibility.")
    y_max = float(np.max(np.asarray(y_full.values, dtype=np.float64)))
    if float(np.max(high)) > y_max * _MAX_REASONABLE_PEAK_MULTIPLIER:
        messages.append(
            "P90 max exceeds "
            f"{_MAX_REASONABLE_PEAK_MULTIPLIER:g}x historical max — check plausibility."
        )
    return tuple(messages)


def run_chronos_eval(
    y: pd.Series,
    spec: EvalWindowSpec,
    *,
    model_id: str,
    device_map: str = "cpu",
    num_samples: int = 100,
) -> ChronosEvalResult:
    """Slice windows, run Chronos.predict, aggregate sample quantiles, run sanity checks."""
    windows = extract_windows(y, spec)
    prediction_length = int(windows.holdout.shape[0])
    if prediction_length < 1:
        msg = "Holdout window is empty."
        raise ValueError(msg)

    pipeline = get_chronos_pipeline(model_id, device_map=device_map)
    context_tensor = torch.tensor(windows.context, dtype=torch.float32)
    forecasts = pipeline.predict(
        context_tensor,
        prediction_length=prediction_length,
        num_samples=num_samples,
    )
    # forecasts: (batch, samples, horizon)
    sample_paths = forecasts[0].detach().float().cpu().numpy()
    low, median, high = np.quantile(sample_paths, _QUANTILE_LEVELS, axis=0).astype(np.float64)

    sanity_messages = _physical_sanity_messages(y, low, high)

    return ChronosEvalResult(
        window_name=spec.name,
        model_id=model_id,
        prediction_length=prediction_length,
        ground_truth=windows.holdout,
        baseline=windows.baseline,
        median=median,
        low=low,
        high=high,
        sanity_messages=sanity_messages,
        holdout_index=windows.holdout_index,
    )
