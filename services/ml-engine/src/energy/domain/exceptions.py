class EnergyProviderError(Exception):
    """Raised when an energy data provider returns an unexpected response."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Energy provider error {status_code}: {detail}")
