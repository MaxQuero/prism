# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnknownVariableType=false

import numpy as np
import pandas as pd
import pytest

from src.forecasting.windows import EvalWindowSpec, extract_windows

SPEC = EvalWindowSpec(name="test", context=6, horizon=3, seasonal_lag_hours=4)


def hourly_series(n: int) -> pd.Series:
    """Values equal their position so slice boundaries are readable in assertions."""
    index = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.Series(np.arange(n, dtype=np.float64), index=index)


def test_min_series_length_is_horizon_plus_longest_lookback() -> None:
    assert SPEC.min_series_length() == 3 + 6
    assert SPEC.min_series_length(offset=10) == 10 + 3 + 6


def test_windows_line_up_at_series_end() -> None:
    windows = extract_windows(hourly_series(20), SPEC)

    assert windows.holdout.tolist() == [17.0, 18.0, 19.0]
    assert windows.context.tolist() == [11.0, 12.0, 13.0, 14.0, 15.0, 16.0]
    assert windows.baseline.tolist() == [13.0, 14.0, 15.0]


def test_holdout_index_matches_holdout_timestamps() -> None:
    y = hourly_series(20)
    windows = extract_windows(y, SPEC)

    assert windows.holdout_index.equals(y.index[-3:])


def test_offset_shifts_every_window_back() -> None:
    windows = extract_windows(hourly_series(30), SPEC, offset=5)

    assert windows.holdout.tolist() == [22.0, 23.0, 24.0]
    assert windows.context.tolist() == [16.0, 17.0, 18.0, 19.0, 20.0, 21.0]
    assert windows.baseline.tolist() == [18.0, 19.0, 20.0]


def test_exact_minimum_length_is_accepted() -> None:
    windows = extract_windows(hourly_series(SPEC.min_series_length()), SPEC)

    assert windows.context.shape[0] == SPEC.context
    assert windows.holdout.shape[0] == SPEC.horizon
    assert windows.baseline.shape[0] == SPEC.horizon


def test_short_series_raises_instead_of_truncating() -> None:
    with pytest.raises(ValueError, match="needs at least 9"):
        extract_windows(hourly_series(SPEC.min_series_length() - 1), SPEC)


def test_offset_beyond_series_raises() -> None:
    y = hourly_series(SPEC.min_series_length())

    with pytest.raises(ValueError, match="offset=1"):
        extract_windows(y, SPEC, offset=1)


def test_negative_offset_rejected() -> None:
    with pytest.raises(ValueError, match="offset must be >= 0"):
        extract_windows(hourly_series(20), SPEC, offset=-1)


def test_returned_arrays_are_copies() -> None:
    y = hourly_series(20)
    windows = extract_windows(y, SPEC)
    windows.holdout[0] = -1.0

    assert y.iloc[-3] == 17.0
