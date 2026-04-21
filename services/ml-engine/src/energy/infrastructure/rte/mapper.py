# src/energy/infrastructure/rte/mappers.py

from src.energy.domain.models.consumption import ElectricityConsumptionModel, ForecastHorizon
from src.energy.infrastructure.rte.dto import RteForecastType, RteShortTermConsumptionResponse


def map_horizon_to_rte_type(horizon: ForecastHorizon) -> RteForecastType:
    """Translates Domain horizon to RTE specific infrastructure type."""
    match horizon:
        case ForecastHorizon.INTRADAY:
            return RteForecastType.ID
        case ForecastHorizon.DAY_AHEAD:
            return RteForecastType.D_1
        case ForecastHorizon.TWO_DAYS_AHEAD:
            return RteForecastType.D_2
        case _:
            raise ValueError(f"Unsupported forecast horizon: {horizon}")


def map_rte_consumption_to_domain_models(
    rte_dto: RteShortTermConsumptionResponse,
) -> list[ElectricityConsumptionModel]:
    return [
        ElectricityConsumptionModel(
            timestamp=point.start_date,
            megawatts=0 if point.value is None else point.value,
        )
        for block in rte_dto.short_term
        for point in block.values
    ]
