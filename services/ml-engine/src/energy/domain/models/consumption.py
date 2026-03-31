from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ForecastHorizon(StrEnum):
    """Business representation of forecast horizons."""

    INTRADAY = "intraday"
    DAY_AHEAD = "day_ahead"
    TWO_DAYS_AHEAD = "two_days_ahead"


@dataclass(frozen=True, slots=True)
class ElectricityConsumptionModel:
    """Represents the electricity consumption (real or forecasted) at a given time."""

    timestamp: datetime
    megawatts: int
