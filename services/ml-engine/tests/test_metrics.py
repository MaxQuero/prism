import numpy as np
import pytest

from src.forecasting.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    per_horizon_percentage_error,
)

Y_TRUE = np.array([100.0, 200.0, 400.0])
Y_PRED = np.array([110.0, 180.0, 400.0])


def test_perfect_forecast_has_zero_error() -> None:
    assert mean_absolute_percentage_error(Y_TRUE, Y_TRUE) == 0.0
    assert mean_absolute_error(Y_TRUE, Y_TRUE) == 0.0


def test_mape_is_mean_of_percentage_errors() -> None:
    # 10%, 10%, 0% -> 6.67%
    assert mean_absolute_percentage_error(Y_TRUE, Y_PRED) == pytest.approx(20.0 / 3, rel=1e-6)


def test_mape_is_symmetric_in_sign_of_error() -> None:
    over = mean_absolute_percentage_error(Y_TRUE, Y_TRUE + 10.0)
    under = mean_absolute_percentage_error(Y_TRUE, Y_TRUE - 10.0)

    assert over == pytest.approx(under, rel=1e-6)


def test_mape_denominator_is_floored_near_zero() -> None:
    # y_true=0: scored against the explicit floor, bounded instead of exploding
    result = mean_absolute_percentage_error(
        np.array([0.0]), np.array([100.0]), denominator_floor=50.0
    )

    assert result == pytest.approx(200.0)


def test_mape_uses_absolute_value_for_negative_series() -> None:
    # e.g. a balance of exchanges: a negative denominator must not flip the sign
    result = mean_absolute_percentage_error(np.array([-100.0]), np.array([-110.0]))

    assert result == pytest.approx(10.0)


def test_mae_is_in_physical_units() -> None:
    # |10| + |20| + 0 -> 10 MW on average
    assert mean_absolute_error(Y_TRUE, Y_PRED) == pytest.approx(10.0)


def test_per_horizon_errors_keep_one_value_per_step() -> None:
    errors = per_horizon_percentage_error(Y_TRUE, Y_PRED)

    assert errors.shape == (3,)
    assert errors == pytest.approx([10.0, 10.0, 0.0], rel=1e-6)
