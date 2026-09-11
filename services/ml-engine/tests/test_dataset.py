# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnknownVariableType=false

from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd
import pytest

from src.forecasting.dataset import (
    enforce_hourly_continuity,
    find_hourly_gaps,
    load_consumption_series,
)


def hourly_index(n: int) -> pd.DatetimeIndex:
    # Starts just before the 2024-03-31 Paris DST switch: UTC storage must not care.
    return pd.date_range("2024-03-30 22:00", periods=n, freq="1h", tz="UTC")


def write_csv(path: Path, frame: pd.DataFrame) -> str:
    frame.index.name = "timestamp"
    frame.to_csv(path, index=True)
    return str(path)


def test_csv_round_trip_keeps_utc_index_and_float_values(tmp_path: Path) -> None:
    index = hourly_index(48)
    frame = pd.DataFrame({"megawatts": np.arange(48), "hour_of_day": 0}, index=index)

    series = load_consumption_series(write_csv(tmp_path / "consumption.csv", frame))

    assert series.index.equals(index)
    assert series.dtype == np.float64
    assert series.tolist() == [float(v) for v in range(48)]


def test_load_sorts_rows_by_timestamp(tmp_path: Path) -> None:
    index = hourly_index(6)
    frame = cast(pd.DataFrame, pd.DataFrame({"megawatts": np.arange(6)}, index=index).iloc[::-1])

    series = load_consumption_series(write_csv(tmp_path / "shuffled.csv", frame))

    assert series.index.equals(index)
    assert series.tolist() == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]


def test_continuous_index_has_no_gaps() -> None:
    assert find_hourly_gaps(hourly_index(48)).empty


def test_missing_hours_are_reported() -> None:
    index = hourly_index(48)

    gaps = find_hourly_gaps(index.delete([5, 6, 20]))

    assert gaps.equals(index[[5, 6, 20]])


def test_small_gaps_are_interpolated_in_place() -> None:
    index = hourly_index(48)
    y = pd.Series(np.arange(48, dtype=np.float64), index=index)
    y.iloc[10:13] = np.nan  # 3h hole in a linear ramp

    cleaned = enforce_hourly_continuity(y, max_gap_hours=6)

    assert cleaned.index.equals(index)  # timestamps untouched: filled in place
    assert cleaned.tolist() == [float(v) for v in range(48)]  # ramp restored exactly


def test_gaps_longer_than_limit_are_refused() -> None:
    y = pd.Series(np.arange(48, dtype=np.float64), index=hourly_index(48))
    y.iloc[10:18] = np.nan  # 8h hole > 6h limit

    with pytest.raises(ValueError, match="hours missing"):
        enforce_hourly_continuity(y, max_gap_hours=6)


def test_missing_rows_are_refused_like_nan_gaps() -> None:
    y = pd.Series(np.arange(48, dtype=np.float64), index=hourly_index(48))
    y = y.drop(y.index[10:18])  # rows absent entirely, not NaN

    with pytest.raises(ValueError, match="hours missing"):
        enforce_hourly_continuity(y, max_gap_hours=6)
