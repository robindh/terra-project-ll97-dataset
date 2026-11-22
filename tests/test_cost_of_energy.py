import pandas as pd

from terra_project_ll97_dataset.calculator.cost_of_energy import (
    get_cost_of_energy,
    get_cost_of_energy_by_year_and_energy_type,
)

ENERGY_TYPES = ["Electricity", "Natural Gas", "Steam", "Fuel Oil 2", "Fuel Oil 4"]


def test_energy_prices_are_constant_across_years():
    prices = get_cost_of_energy_by_year_and_energy_type(2024, 2050)

    assert list(prices) == list(range(2024, 2051))
    for year in prices:
        assert prices[year] == {
            "Electricity": 0.22,
            "Natural Gas": 0.997,
            "Steam": 35.0,
            "Fuel Oil 2": 1.65,
            "Fuel Oil 4": 1.65,
        }
        assert set(prices[year]) == set(ENERGY_TYPES)


def test_cost_is_consumption_times_price():
    prices = get_cost_of_energy_by_year_and_energy_type(2024, 2050)
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
    expected = 1000.0 * 0.22 + 10.0 * 0.997 + 1.0 * 35.0 + 1.0 * 1.65 + 1.0 * 1.65

    assert get_cost_of_energy(prices, 2024, row) == expected
    assert get_cost_of_energy(prices, 2050, row) == expected
