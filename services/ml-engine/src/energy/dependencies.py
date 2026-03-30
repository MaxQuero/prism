from typing import cast

from fastapi import Depends, Request

from src.energy.application.use_cases.get_realized_consumption import GetRealizedConsumptionUseCase
from src.energy.infrastructure.rte.adapter import RteApiClientAdapter


def get_rte_client_use_case(request: Request) -> RteApiClientAdapter:
    """FastAPI dependency — extracts the RTE client initialized during lifespan."""
    return cast(RteApiClientAdapter, request.app.state.rte_client)


def get_realized_consumption_use_case(
    client: RteApiClientAdapter = Depends(get_rte_client_use_case),
) -> GetRealizedConsumptionUseCase:
    """FastAPI dependency — builds the GetRealizedConsumption use case with its adapter."""
    return GetRealizedConsumptionUseCase(gateway=client)
