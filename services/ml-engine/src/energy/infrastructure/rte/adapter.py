import base64
from datetime import datetime
from zoneinfo import ZoneInfo

from src.core.http_client import HttpClient
from src.core.logger import logger
from src.core.token_cache import TokenCache
from src.energy.domain.models.consumption import ElectricityConsumptionModel, ForecastHorizon
from src.energy.infrastructure.rte.api import RteApi
from src.energy.infrastructure.rte.dto import RteForecastType, RteShortTermConsumptionResponse
from src.energy.infrastructure.rte.mapper import (
    map_horizon_to_rte_type,
    map_rte_consumption_to_domain_models,
)


class RteApiClientAdapter:
    """Adapter implementing the EnergyDataGateway port for RTE."""

    def __init__(self, base_url: str, client_id: str, client_secret: str) -> None:
        logger.info("[RTE] Initializing the RTE API client")
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        self._http = HttpClient(base_url=base_url)
        self._api = RteApi(http=self._http, credentials=credentials)
        self._token_cache = TokenCache()

    def _secure_dates(
        self, start: datetime | None, end: datetime | None
    ) -> tuple[datetime | None, datetime | None]:
        """Attach Europe/Paris to naive datetimes; tz-aware inputs are returned untouched."""
        french_tz = ZoneInfo("Europe/Paris")

        if start and start.tzinfo is None:
            start = start.replace(tzinfo=french_tz)

        if end and end.tzinfo is None:
            end = end.replace(tzinfo=french_tz)

        return start, end

    async def _request_token(self) -> str:
        cached = self._token_cache.get_valid_token()
        if cached:
            logger.debug("[RTE] Using cached OAuth2 token")
            return cached

        data = await self._api.fetch_token()
        token: str = data.access_token
        expires_in: int = data.expires_in
        self._token_cache.save(token, expires_in)
        logger.info(f"[RTE] OAuth2 token obtained, valid for {expires_in}s")
        return token

    async def get_realized_consumption(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ElectricityConsumptionModel]:
        token = await self._request_token()
        start, end = self._secure_dates(start, end)
        rteDto: RteShortTermConsumptionResponse = await self._api.get_short_term_consumption(
            RteForecastType.REALIZED,
            token,
            start_date=start,
            end_date=end,
        )
        return map_rte_consumption_to_domain_models(rteDto)

    async def get_forecast_consumption(
        self,
        forecast_horizon: ForecastHorizon,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ElectricityConsumptionModel]:
        token = await self._request_token()
        start, end = self._secure_dates(start, end)
        forecast_rte_type: RteForecastType = map_horizon_to_rte_type(forecast_horizon)

        rteDto: RteShortTermConsumptionResponse = await self._api.get_short_term_consumption(
            forecast_type=forecast_rte_type,
            token=token,
            start_date=start,
            end_date=end,
        )
        return map_rte_consumption_to_domain_models(rteDto)

    async def close(self) -> None:
        await self._http.close()
