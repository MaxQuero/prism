from typing import cast

from fastapi import Depends, Request

from src.energy.application.use_cases.get_forecast_consumption import GetForecastConsumptionUseCase
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


def get_forecast_consumption_use_case(
    client: RteApiClientAdapter = Depends(get_rte_client_use_case),
) -> GetForecastConsumptionUseCase:
    """FastAPI dependency — builds the GetForecastConsumption use case with its adapter."""
    return GetForecastConsumptionUseCase(gateway=client)
