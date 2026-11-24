from pathlib import Path

import pandas as pd
import pytest

from terra_project_ll97_dataset.calculator.carbon_emissions_thresholds import (
    get_carbon_emissions_threshold_amounts,
    get_carbon_emissions_threshold_by_building_type_and_start_year,
    get_carbon_emissions_thresholds,
)

THRESHOLD_CSV = (
    Path(__file__).resolve().parents[1]
    / "terra_project_ll97_dataset"
    / "data"
    / "carbon_thresholds_by_building_type.csv"
)

# Office factors from the shipped threshold table, tCO2e per ft².
OFFICE_FACTOR_BY_PERIOD_START = {
    2024: 0.0076,
    2030: 0.0027,
    2035: 0.0017,
    2040: 0.0006,
    2050: 0.0,
}


def _office_row() -> pd.Series:
    return pd.Series(
        {
            "Largest Property Use Type": "Office",
            "Largest Property Use Type - Gross Floor Area (ft²)": 1000.0,
            # Present so a future change that consults the 2nd or 3rd use would fail.
            "2nd Largest Property Use Type": "Hospital (General Medical & Surgical)",
            "2nd Largest Property Use Type - Gross Floor Area (ft²)": 1_000_000.0,
            "3rd Largest Property Use Type": "Data Center",
            "3rd Largest Property Use Type - Gross Floor Area (ft²)": 1_000_000.0,
        }
    )


@pytest.fixture(scope="module")
def threshold_table():
    return get_carbon_emissions_threshold_by_building_type_and_start_year(str(THRESHOLD_CSV))


@pytest.mark.parametrize(
    ("year", "period_start"),
    [
        (2024, 2024),
        (2029, 2024),
        (2030, 2030),
        (2034, 2030),
        (2035, 2035),
        (2039, 2035),
        (2040, 2040),
        (2049, 2040),
        (2050, 2050),
    ],
)
def test_threshold_uses_largest_property_use_and_period_start(threshold_table, year, period_start):
    threshold = get_carbon_emissions_thresholds(threshold_table, year, _office_row())
    assert threshold == 1000.0 * OFFICE_FACTOR_BY_PERIOD_START[period_start]


def test_unknown_property_use_type_has_zero_threshold(threshold_table):
    row = _office_row()
    row["Largest Property Use Type"] = "Not A Real Type"
    assert get_carbon_emissions_thresholds(threshold_table, 2024, row) == 0.0


def test_threshold_amounts_match_the_row_calculation(threshold_table):
    office = _office_row()
    unknown = _office_row()
    unknown["Largest Property Use Type"] = "Not A Real Type"
    buildings = pd.DataFrame([office, unknown])
    amounts = get_carbon_emissions_threshold_amounts(
        threshold_table,
        2034,
        buildings,
    )
    expected = [
        get_carbon_emissions_thresholds(threshold_table, 2034, office),
        get_carbon_emissions_thresholds(threshold_table, 2034, unknown),
    ]
    assert amounts.tolist() == expected
