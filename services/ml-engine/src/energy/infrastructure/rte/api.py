from pydantic import BaseModel, ValidationError

from src.core.http_client import HttpClient, HttpClientError
from src.core.logger import logger
from src.energy.domain.exceptions import EnergyProviderError


class RteTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


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
