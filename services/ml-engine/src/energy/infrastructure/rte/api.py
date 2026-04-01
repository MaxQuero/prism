from datetime import datetime

from pydantic import ValidationError

from src.core.http_client import HttpClient, HttpClientError
from src.core.logger import logger
from src.energy.domain.exceptions import EnergyProviderError
from src.energy.infrastructure.rte.dto import (
    RteForecastType,
    RteShortTermConsumptionResponse,
    RteTokenResponse,
)


class RteApi:
    """RTE-specific HTTP layer: knows the endpoints, auth headers, and error mapping."""

    def __init__(self, http: HttpClient, credentials: str) -> None:
        self._http = http
        self._credentials = credentials

    async def fetch_token(self) -> RteTokenResponse:
        logger.info("[RTE] Requesting OAuth2 token")
        try:
            raw_data = await self._http.post(
                "/token/oauth",
                headers={
                    "Authorization": f"Basic {self._credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

            return RteTokenResponse.model_validate(raw_data)

        except HttpClientError as exc:
            raise EnergyProviderError(exc.status_code, exc.detail) from exc

        except ValidationError as exc:
            logger.error(f"[RTE] Invalid payload format received: {exc}")
            raise EnergyProviderError(502, "Invalid response format from provider") from exc

    async def get_short_term_consumption(
        self,
        forecast_type: RteForecastType,
        token: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> RteShortTermConsumptionResponse:
        logger.info(f"[RTE] Fetching energy consumption for {start_date} to {end_date}")
        try:
            params = {"type": forecast_type.value}

            if start_date:
                params["start_date"] = start_date.replace(microsecond=0).isoformat()
            if end_date:
                params["end_date"] = end_date.replace(microsecond=0).isoformat()

            raw_data = await self._http.get(
                "/open_api/consumption/v1/short_term",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )
            return RteShortTermConsumptionResponse.model_validate(raw_data)
        except HttpClientError as exc:
            raise EnergyProviderError(exc.status_code, exc.detail) from exc
        except ValidationError as exc:
            logger.error(f"[RTE] Invalid payload format received: {exc}")
            raise EnergyProviderError(502, "Invalid response format from provider") from exc
