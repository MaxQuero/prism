from datetime import UTC, datetime, timedelta

import pytest

from src.energy.domain.models.consumption import ForecastHorizon
from src.energy.infrastructure.rte.dto import (
    RteForecastType,
    RteShortTermConsumptionDto,
    RteShortTermConsumptionResponse,
    RteShortTermConsumptionValueDto,
)
from src.energy.infrastructure.rte.mapper import (
    map_horizon_to_rte_type,
    map_rte_consumption_to_domain_models,
)

T0 = datetime(2024, 1, 1, tzinfo=UTC)


def point(step: int, value: int | None) -> RteShortTermConsumptionValueDto:
    start = T0 + timedelta(minutes=15 * step)
    return RteShortTermConsumptionValueDto(
        start_date=start, end_date=start + timedelta(minutes=15), value=value
    )


def response(*blocks: list[RteShortTermConsumptionValueDto]) -> RteShortTermConsumptionResponse:
    return RteShortTermConsumptionResponse(
        short_term=[
            RteShortTermConsumptionDto(
                start_date=values[0].start_date,
                end_date=values[-1].end_date,
                type=RteForecastType.REALIZED,
                values=values,
            )
            for values in blocks
        ]
    )


@pytest.mark.parametrize(
    ("horizon", "expected"),
    [
        (ForecastHorizon.INTRADAY, RteForecastType.ID),
        (ForecastHorizon.DAY_AHEAD, RteForecastType.D_1),
        (ForecastHorizon.TWO_DAYS_AHEAD, RteForecastType.D_2),
    ],
)
def test_every_domain_horizon_maps_to_an_rte_type(
    horizon: ForecastHorizon, expected: RteForecastType
) -> None:
    assert map_horizon_to_rte_type(horizon) is expected


def test_blocks_are_flattened_in_order() -> None:
    models = map_rte_consumption_to_domain_models(
        response([point(0, 50_000), point(1, 51_000)], [point(2, 52_000)])
    )

    assert [m.megawatts for m in models] == [50_000, 51_000, 52_000]
    assert [m.timestamp for m in models] == [T0 + timedelta(minutes=15 * i) for i in range(3)]


def test_points_without_value_are_dropped_not_zeroed() -> None:
    models = map_rte_consumption_to_domain_models(
        response([point(0, 50_000), point(1, None), point(2, 52_000)])
    )

    assert [m.megawatts for m in models] == [50_000, 52_000]
    assert all(m.megawatts != 0 for m in models)


def test_empty_response_maps_to_empty_list() -> None:
    empty = RteShortTermConsumptionResponse(short_term=[])

    assert map_rte_consumption_to_domain_models(empty) == []
