from fastapi import APIRouter, Depends, HTTPException

from src.core.logger import logger
from src.energy.application.use_cases.fetch_provider_token import FetchProviderToken
from src.energy.dependencies import get_fetch_provider_token
from src.energy.domain.exceptions import EnergyProviderError

router = APIRouter(tags=["Energy"])


@router.post("/provider/token")
async def fetch_provider_token(
    use_case: FetchProviderToken = Depends(get_fetch_provider_token),
) -> dict[str, str]:
    try:
        token = await use_case.execute()
    except EnergyProviderError as exc:
        logger.error(f"[ENERGY] Provider error: {exc}")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"access_token": token}
