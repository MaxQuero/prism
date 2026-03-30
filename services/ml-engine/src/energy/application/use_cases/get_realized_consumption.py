from datetime import datetime

from src.energy.domain.models.consumption import ElectricityConsumptionModel
from src.energy.domain.ports.energy_data_gateway import EnergyDataGatewayPort


class GetRealizedConsumptionUseCase:
    """Use case: Fetch actual electricity consumption for a given period."""

    def __init__(self, gateway: EnergyDataGatewayPort) -> None:
        self._gateway = gateway

    async def execute(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ElectricityConsumptionModel]:
        return await self._gateway.get_realized_consumption(start, end=end)
