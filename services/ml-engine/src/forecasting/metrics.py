"""Forecast error metrics (stable MAPE, per-horizon errors)."""

import numpy as np
from numpy.typing import NDArray


def mean_absolute_percentage_error(
    y_true: NDArray[np.floating] | np.ndarray,
    y_pred: NDArray[np.floating] | np.ndarray,
    *,
    epsilon: float = 1e-6,
) -> float:
    """MAPE in percent; epsilon avoids blow-ups when y_true is near zero."""
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)
    return float(np.mean(np.abs((yt - yp) / (yt + epsilon))) * 100.0)


def per_horizon_percentage_error(
    y_true: NDArray[np.floating] | np.ndarray,
    y_pred: NDArray[np.floating] | np.ndarray,
    *,
    epsilon: float = 1e-6,
) -> NDArray[np.float64]:
    """Absolute percentage error at each horizon step (vector, length = horizon)."""
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_pred, dtype=np.float64)
    return np.abs((yt - yp) / (yt + epsilon)) * 100.0
