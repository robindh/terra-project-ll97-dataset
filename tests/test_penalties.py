import pandas as pd

from terra_project_ll97_dataset.calculator.penalties import calculate_penalties


def test_penalty_is_zero_at_the_limit():
    row = pd.Series({"emissions": 10.0, "threshold": 10.0})
    assert calculate_penalties(row, "emissions", "threshold") == 0.0


def test_penalty_is_zero_below_the_limit():
    row = pd.Series({"emissions": 9.5, "threshold": 10.0})
    assert calculate_penalties(row, "emissions", "threshold") == 0.0


def test_penalty_above_the_limit_is_268_dollars_per_tco2e():
    row = pd.Series({"emissions": 12.5, "threshold": 10.0})
    assert calculate_penalties(row, "emissions", "threshold") == 268 * (12.5 - 10.0)
