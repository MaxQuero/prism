from datetime import datetime
from typing import Protocol

from src.energy.domain.models.consumption import ElectricityConsumptionModel


class EnergyDataGatewayPort(Protocol):
    """Port defining the contract for any energy data provider (RTE, Enedis, etc.)."""

    async def get_realized_consumption(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ElectricityConsumptionModel]: ...
