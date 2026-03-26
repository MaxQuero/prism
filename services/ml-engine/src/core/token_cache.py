from datetime import UTC, datetime, timedelta


class TokenCache:
    """Handles in-memory temporal caching for authentication tokens."""

    def __init__(self) -> None:
        self._token: str | None = None
        self._expires_at: datetime | None = None

    def get_valid_token(self) -> str | None:
        """Returns the token if it exists and is still valid, else None."""
        if not self._token or not self._expires_at:
            return None

        now = datetime.now(UTC)
        if now < (self._expires_at - timedelta(seconds=60)):
            return self._token

        return None

    def save(self, token: str, expires_in_seconds: int) -> None:
        """Saves the token and calculates its exact expiration date."""
        self._token = token
        self._expires_at = datetime.now(UTC) + timedelta(seconds=expires_in_seconds)
