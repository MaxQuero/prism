from src.energy.domain.ports.energy_data_gateway import EnergyDataGateway


class FetchProviderToken:
    """Use case: authenticate with an energy data provider and retrieve a token."""

    def __init__(self, gateway: EnergyDataGateway) -> None:
        self._gateway = gateway

    async def execute(self) -> str:
        return await self._gateway.request_token()
