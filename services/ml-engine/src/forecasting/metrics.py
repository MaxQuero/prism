"""Forecast error metrics (floored MAPE, per-horizon errors)."""

import numpy as np
from numpy.typing import NDArray


def mean_absolute_percentage_error(
    y_true: NDArray[np.floating] | np.ndarray,
    y_pred: NDArray[np.floating] | np.ndarray,
    *,
    denominator_floor: float = 1.0,
) -> float:
    """MAPE in percent, with ``|y_true|`` floored at ``denominator_floor``.

    The floor bounds the ratio when y_true is near zero: such points are scored
    against the floor (error per floor unit), NOT a true percentage — it does not
    make them small, just finite and explicit. Pick a floor negligible for the
    series at hand (default 1.0 = 1 MW, vs ~30 000 MW off-peak national load).
    """
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)
    return float(np.mean(_percentage_errors(yt, yp, denominator_floor)))


def mean_absolute_error(
    y_true: NDArray[np.floating] | np.ndarray,
    y_pred: NDArray[np.floating] | np.ndarray,
) -> float:
    """MAE in the physical unit of the series (MW here); what operators actually reason in."""
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)
    return float(np.mean(np.abs(yt - yp)))


def per_horizon_percentage_error(
    y_true: NDArray[np.floating] | np.ndarray,
    y_pred: NDArray[np.floating] | np.ndarray,
    *,
    denominator_floor: float = 1.0,
) -> NDArray[np.float64]:
    """Absolute percentage error at each horizon step (vector, length = horizon).

    Same floored denominator as ``mean_absolute_percentage_error``.
    """
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)
    return _percentage_errors(yt, yp, denominator_floor)


def _percentage_errors(
    yt: NDArray[np.float64],
    yp: NDArray[np.float64],
    denominator_floor: float,
) -> NDArray[np.float64]:
    if denominator_floor <= 0:
        msg = f"denominator_floor must be > 0, got {denominator_floor}"
        raise ValueError(msg)
    denominator = np.maximum(np.abs(yt), denominator_floor)
    return np.abs(yt - yp) / denominator * 100.0
