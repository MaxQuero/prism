from datetime import datetime
from typing import Protocol

from src.energy.domain.models.consumption import ElectricityConsumptionModel, ForecastHorizon


class EnergyDataGatewayPort(Protocol):
    """Port defining the contract for any energy data provider (RTE, Enedis, etc.)."""

    async def get_realized_consumption(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ElectricityConsumptionModel]: ...

    async def get_forecast_consumption(
        self,
        forecast_horizon: ForecastHorizon,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ElectricityConsumptionModel]: ...
