"""Matplotlib helpers for Chronos zero-shot notebooks."""

# pyright: reportUnknownMemberType=false

from __future__ import annotations

import numpy as np
from matplotlib import pyplot as plt
from numpy.typing import NDArray


def plot_forecast_comparison(
    ground_truth: NDArray[np.floating] | np.ndarray,
    baseline: NDArray[np.floating] | np.ndarray,
    median: NDArray[np.floating] | np.ndarray,
    low: NDArray[np.floating] | np.ndarray,
    high: NDArray[np.floating] | np.ndarray,
    *,
    horizon: int,
    title: str = "Chronos vs realized consumption",
) -> None:
    """Overlay holdout, naive baseline, median forecast, and P10–P90 band."""
    ground_truth = np.asarray(ground_truth, dtype=np.float64)
    baseline = np.asarray(baseline, dtype=np.float64)
    median = np.asarray(median, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    high = np.asarray(high, dtype=np.float64)
    hours = np.arange(horizon, dtype=np.int64)
    plt.figure(figsize=(12, 6))
    plt.plot(hours, ground_truth, label="Realized (holdout)", color="black", lw=2)
    plt.plot(
        hours,
        baseline,
        label="Naive baseline (week ago)",
        linestyle="--",
        color="gray",
        lw=2,
        alpha=0.8,
    )
    plt.plot(hours, median, label="Chronos (median)", color="blue")
    plt.fill_between(hours, low, high, color="blue", alpha=0.2, label="P10–P90")
    plt.title(title)
    plt.xlabel("Horizon (h)")
    plt.ylabel("MW")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_horizon_errors(
    errors_percent: NDArray[np.floating] | np.ndarray,
    *,
    horizon: int,
    title: str | None = None,
) -> None:
    """Line plot of absolute percentage error across forecast horizons."""
    err = np.asarray(errors_percent, dtype=np.float64)
    if err.shape[0] != horizon:
        msg = f"errors length {err.shape[0]} != horizon {horizon}"
        raise ValueError(msg)
    hours = np.arange(horizon, dtype=np.int64)
    if title is None:
        title = f"Absolute percentage error by horizon ({horizon} h)"
    plt.figure(figsize=(10, 4))
    plt.plot(hours, err)
    plt.title(title)
    plt.ylabel("Absolute error (%)")
    plt.xlabel("Horizon (h)")
    plt.tight_layout()
    plt.show()
