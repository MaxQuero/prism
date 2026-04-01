from datetime import datetime

from src.energy.domain.models.consumption import ElectricityConsumptionModel, ForecastHorizon
from src.energy.domain.ports.energy_data_gateway import EnergyDataGatewayPort


class GetForecastConsumptionUseCase:
    """Use case: Fetch forecasted electricity consumption for a given period."""

    def __init__(self, gateway: EnergyDataGatewayPort) -> None:
        self._gateway = gateway

    async def execute(
        self,
        forecast_horizon: ForecastHorizon,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ElectricityConsumptionModel]:
        return await self._gateway.get_forecast_consumption(
            forecast_horizon=forecast_horizon, start=start, end=end
        )
