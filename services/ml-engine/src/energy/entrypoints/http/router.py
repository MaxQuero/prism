from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from src.core.logger import logger
from src.energy.application.use_cases.get_realized_consumption import GetRealizedConsumptionUseCase
from src.energy.dependencies import get_realized_consumption_use_case
from src.energy.domain.exceptions import EnergyProviderError
from src.energy.domain.models.consumption import ElectricityConsumptionModel

consumption_router = APIRouter(prefix="/consumption", tags=["Consumption"])


@consumption_router.get(
    "/realized",
    summary="Get realized consumption",
    description=(
        "Get realized consumption. Optional start/end filter the window; "
        "omit both to rely on the data provider default (e.g. RTE short_term)."
    ),
)
async def get_realized_consumption_endpoint(
    start: datetime | None = Query(
        None, description="Start of period (inclusive); omit to use provider default"
    ),
    end: datetime | None = Query(
        None, description="End of period (inclusive); omit to use provider default"
    ),
    use_case: GetRealizedConsumptionUseCase = Depends(get_realized_consumption_use_case),
) -> list[ElectricityConsumptionModel]:
    try:
        return await use_case.execute(start=start, end=end)
    except EnergyProviderError as exc:
        logger.error(f"[ENERGY] Provider error: {exc}")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
