from typing import Any

import httpx

from src.core.logger import logger


class HttpClientError(Exception):
    """Raised when an HTTP request returns a non-success status code."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class HttpClient:
    """Generic async HTTP client with logging and error handling."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        logger.debug(f"[HTTP] {method} {path}")
        response = await self._client.request(method, path, **kwargs)
        if not response.is_success:
            logger.error(f"[HTTP] {method} {path} → {response.status_code}")
            raise HttpClientError(response.status_code, response.text)
        return response.json()  # type: ignore[no-any-return]

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return await self.request("POST", path, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()
