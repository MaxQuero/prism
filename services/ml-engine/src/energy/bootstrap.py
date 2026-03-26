from fastapi import FastAPI

from src.core.logger import logger
from src.energy.infrastructure.rte.adapter import RteApiClient
from src.energy.infrastructure.rte.settings import RteSettings


async def init_energy(app: FastAPI) -> None:
    """Bootstrap the energy module: create and store the provider client."""
    rte_settings = RteSettings()
    app.state.rte_client = RteApiClient(
        base_url=rte_settings.base_url,
        client_id=rte_settings.client_id,
        client_secret=rte_settings.client_secret,
    )
    logger.info("[ENERGY] Module initialized (provider: RTE)")


async def shutdown_energy(app: FastAPI) -> None:
    """Gracefully close the provider client."""
    await app.state.rte_client.close()
    logger.info("[ENERGY] Module shut down")
