from typing import Protocol


class EnergyDataGateway(Protocol):
    """Port defining the contract for any energy data provider (RTE, Enedis, etc.)."""

    async def request_token(self) -> str: ...
