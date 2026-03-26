from typing import cast

from fastapi import Depends, Request

from src.energy.application.use_cases.fetch_provider_token import FetchProviderToken
from src.energy.infrastructure.rte.adapter import RteApiClient


def get_rte_client(request: Request) -> RteApiClient:
    """FastAPI dependency — extracts the RTE client initialized during lifespan."""
    return cast(RteApiClient, request.app.state.rte_client)


def get_fetch_provider_token(
    client: RteApiClient = Depends(get_rte_client),
) -> FetchProviderToken:
    """FastAPI dependency — builds the FetchProviderToken use case with its adapter."""
    return FetchProviderToken(gateway=client)
