"""Consumption dataset helpers: chunked history fetch, CSV loading, continuity checks."""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import cast

import httpx
import pandas as pd

REALIZED_CONSUMPTION_PATH = "/api/v1/energy/consumption/realized"


def fetch_realized_history(
    base_url: str,
    start: datetime,
    end: datetime,
    *,
    chunk_days: int = 14,
    pause_seconds: float = 0.5,
    timeout: float = 30.0,
) -> pd.DataFrame:
    """Fetch realized consumption from the ml-engine API over [start, end) in date chunks.

    The RTE API caps the range of a single call, so the span is requested
    ``chunk_days`` at a time. Returns a DataFrame indexed by UTC timestamp,
    sorted and de-duplicated (chunk boundaries may overlap).
    """
    if start >= end:
        msg = f"start ({start}) must be before end ({end})"
        raise ValueError(msg)

    chunk = timedelta(days=chunk_days)
    frames: list[pd.DataFrame] = []
    with httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout) as client:
        cursor = start
        while cursor < end:
            chunk_end = min(cursor + chunk, end)
            response = client.get(
                REALIZED_CONSUMPTION_PATH,
                params={"start": cursor.isoformat(), "end": chunk_end.isoformat()},
            )
            if not response.is_success:
                msg = (
                    f"fetch failed for {cursor:%Y-%m-%d} -> {chunk_end:%Y-%m-%d}: "
                    f"HTTP {response.status_code}: {response.text[:300]}"
                )
                raise RuntimeError(msg)
            payload = response.json()
            if payload:
                frames.append(pd.DataFrame(payload))
            cursor = chunk_end
            if pause_seconds and cursor < end:
                time.sleep(pause_seconds)

    if not frames:
        msg = f"no data returned between {start} and {end}"
        raise RuntimeError(msg)

    df = pd.concat(frames, ignore_index=True)
    df["timestamp"] = pd.to_datetime(cast(pd.Series, df["timestamp"]), utc=True)
    return df.drop_duplicates(subset="timestamp").sort_values("timestamp").set_index("timestamp")


def load_consumption_series(path: str, *, column: str = "megawatts") -> pd.Series:
    """Load a processed CSV as a float64 series indexed by UTC timestamp, sorted."""
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(cast(pd.Series, df["timestamp"]), utc=True)
    df = df.set_index("timestamp").sort_index()
    return cast(pd.Series, df[column].astype("float64"))


def find_hourly_gaps(observed: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Hours missing from an hourly index; empty means the series is continuous.

    Seasonal lags (e.g. 168h = one week) are only meaningful on a gap-free series.
    """
    expected = pd.date_range(observed.min(), observed.max(), freq="1h", tz=observed.tz)
    return cast(pd.DatetimeIndex, expected.difference(observed))


def enforce_hourly_continuity(y: pd.Series, *, max_gap_hours: int = 6) -> pd.Series:
    """Fill gaps of up to ``max_gap_hours`` in place; raise on anything longer.

    Downstream slicing (eval windows, seasonal lags) is positional and assumes one
    row per hour. Small holes are linearly interpolated so timestamps never shift;
    a hole the interpolation cannot cover raises instead of silently breaking that
    "1 row = 1 hour" contract.
    """
    if max_gap_hours < 1:
        msg = f"max_gap_hours must be >= 1, got {max_gap_hours}"
        raise ValueError(msg)

    filled = y.interpolate(method="linear", limit=max_gap_hours).dropna()
    if filled.empty:
        msg = "series is empty once missing values are dropped"
        raise ValueError(msg)

    gaps = find_hourly_gaps(cast(pd.DatetimeIndex, filled.index))
    if not gaps.empty:
        msg = (
            f"{len(gaps)} hours missing after interpolating gaps <= {max_gap_hours}h "
            f"(first: {gaps[:5].tolist()}); a gapped series silently shifts positional "
            "windows and seasonal lags — fetch more history or narrow the period"
        )
        raise ValueError(msg)
    return filled
