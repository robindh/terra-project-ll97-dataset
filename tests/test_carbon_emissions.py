import pandas as pd

from terra_project_ll97_dataset.calculator.carbon_emissions import (
    get_carbon_emissions,
    get_carbon_emissions_by_year_and_energy_type,
)

ENERGY_TYPES = ["Electricity", "Natural Gas", "Steam", "Fuel Oil 2", "Fuel Oil 4"]


def test_emission_factors_by_year_and_energy_type():
    factors = get_carbon_emissions_by_year_and_energy_type(2024, 2050)

    assert list(factors) == list(range(2024, 2051))
    for year in factors:
        assert set(factors[year]) == set(ENERGY_TYPES)

    assert factors[2024]["Electricity"] == 0.29 / 1000.00
    assert factors[2029]["Electricity"] == 0.29 / 1000.00
    assert factors[2030]["Electricity"] == 0.15 / 1000.00
    assert factors[2050]["Electricity"] == 0.15 / 1000.00

    assert factors[2024]["Natural Gas"] == 5.0 / 1000.00
    assert factors[2050]["Natural Gas"] == 5.0 / 1000.00

    assert factors[2024]["Steam"] == 53.6 / 1000.00
    assert factors[2029]["Steam"] == 53.6 / 1000.00
    assert factors[2030]["Steam"] == 51.6 / 1000.00
    assert factors[2050]["Steam"] == 51.6 / 1000.00

    assert factors[2024]["Fuel Oil 2"] == 10.24 / 1000.00
    assert factors[2050]["Fuel Oil 2"] == 10.24 / 1000.00
    assert factors[2024]["Fuel Oil 4"] == 10.99 / 1000.00
    assert factors[2050]["Fuel Oil 4"] == 10.99 / 1000.00


def test_emissions_are_consumption_times_year_specific_factor():
    factors = get_carbon_emissions_by_year_and_energy_type(2024, 2050)
    row = pd.Series(
        {
            "Electricity Use - Grid Purchase (kWh)": 1000.0,
            "Natural Gas Use (kBtu)": 1000.0,
            "District Steam Use (kBtu)": 1194.0,
            "Fuel Oil #2 Use (kBtu)": 138.0,
            "Fuel Oil #4 Use (kBtu)": 146.0,
        }
    )

    # 1000 kWh, 10 therms, 1 Mlb steam, 1 gal of each fuel oil.
    emissions_2024 = (
        1000.0 * (0.29 / 1000.00)
        + 10.0 * (5.0 / 1000.00)
        + 1.0 * (53.6 / 1000.00)
        + 1.0 * (10.24 / 1000.00)
        + 1.0 * (10.99 / 1000.00)
    )
    emissions_2030 = (
        1000.0 * (0.15 / 1000.00)
        + 10.0 * (5.0 / 1000.00)
        + 1.0 * (51.6 / 1000.00)
        + 1.0 * (10.24 / 1000.00)
        + 1.0 * (10.99 / 1000.00)
    )

    assert get_carbon_emissions(factors, 2024, row) == emissions_2024
    assert get_carbon_emissions(factors, 2029, row) == emissions_2024
    assert get_carbon_emissions(factors, 2030, row) == emissions_2030
    assert get_carbon_emissions(factors, 2050, row) == emissions_2030
