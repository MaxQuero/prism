import base64

from src.core.http_client import HttpClient
from src.core.logger import logger
from src.core.token_cache import TokenCache
from src.energy.infrastructure.rte.api import RteApi


class RteApiClient:
    """Adapter implementing the EnergyDataGateway port for RTE."""

    def __init__(self, base_url: str, client_id: str, client_secret: str) -> None:
        logger.info("[RTE] Initializing the RTE API client")
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        self._http = HttpClient(base_url=base_url)
        self._api = RteApi(http=self._http, credentials=credentials)
        self._token_cache = TokenCache()

    async def request_token(self) -> str:
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

    async def close(self) -> None:
        await self._http.close()
