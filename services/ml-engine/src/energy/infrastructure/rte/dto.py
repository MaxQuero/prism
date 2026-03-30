from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class RteForecastType(StrEnum):
    REALIZED = "REALISED"  # UK spelling in RTE API
    ID = "ID"
    D_1 = "D-1"
    D_2 = "D-2"


class RteTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class RteShortTermConsumptionValueDto(BaseModel):
    start_date: datetime
    end_date: datetime
    updated_date: datetime | None = None
    value: int | None = None


class RteShortTermConsumptionDto(BaseModel):
    start_date: datetime
    end_date: datetime
    type: RteForecastType
    values: list[RteShortTermConsumptionValueDto]


class RteShortTermConsumptionResponse(BaseModel):
    short_term: list[RteShortTermConsumptionDto]
