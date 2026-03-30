from dataclasses import dataclass
from datetime import datetime


@dataclass
class ElectricityConsumptionModel:
    """Represents the electricity consumption (real or forecasted) at a given time."""

    timestamp: datetime
    megawatts: int
