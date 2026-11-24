import pandas as pd

from terra_project_ll97_dataset.calculator.penalties import (
    calculate_penalties,
    calculate_penalty_amounts,
)


def test_penalty_is_zero_at_the_limit():
    row = pd.Series({"emissions": 10.0, "threshold": 10.0})
    assert calculate_penalties(row, "emissions", "threshold") == 0.0


def test_penalty_is_zero_below_the_limit():
    row = pd.Series({"emissions": 9.5, "threshold": 10.0})
    assert calculate_penalties(row, "emissions", "threshold") == 0.0


def test_penalty_above_the_limit_is_268_dollars_per_tco2e():
    row = pd.Series({"emissions": 12.5, "threshold": 10.0})
    assert calculate_penalties(row, "emissions", "threshold") == 268 * (12.5 - 10.0)


def test_series_penalties_match_the_row_calculation():
    emissions = pd.Series([10.0, 9.5, 12.5])
    limits = pd.Series([10.0, 10.0, 10.0])
    amounts = calculate_penalty_amounts(emissions, limits)
    expected = [
        calculate_penalties(
            pd.Series({"emissions": emissions_value, "threshold": limit}),
            "emissions",
            "threshold",
        )
        for emissions_value, limit in zip(emissions, limits, strict=True)
    ]
    assert amounts.tolist() == expected
