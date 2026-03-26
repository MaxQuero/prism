from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RteSettings(BaseSettings):
    """RTE API configuration loaded from environment variables."""

    client_id: str = Field(default="")
    client_secret: str = Field(default="")

    base_url: str = "https://digital.iservices.rte-france.com"

    model_config = SettingsConfigDict(
        env_prefix="RTE_",
        extra="ignore",
    )
