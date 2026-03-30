from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.logger import logger, setup_logger
from src.energy.bootstrap import init_energy, shutdown_energy
from src.energy.entrypoints.http.router import consumption_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logger()
    logger.info("[APP] Starting the Prism ML Engine")

    await init_energy(app)

    yield

    await shutdown_energy(app)
    logger.info("[APP] Stopping the Prism ML Engine")


app = FastAPI(
    title="Prism ML Engine",
    description="Real-time RTE energy data analysis and forecasting",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(consumption_router, prefix="/api/v1/energy")


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {
        "status": "online",
        "service": "ml-engine",
        "version": "0.1.0",
    }
