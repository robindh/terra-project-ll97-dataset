import pandas as pd

from terra_project_ll97_dataset.calculator.energy_unit_conversion import (
    get_energy_consumption_in_billing_units,
)


def _row(**overrides) -> pd.Series:
    values = {
        "Electricity Use - Grid Purchase (kWh)": 0.0,
        "Natural Gas Use (kBtu)": 0.0,
        "District Steam Use (kBtu)": 0.0,
        "Fuel Oil #2 Use (kBtu)": 0.0,
        "Fuel Oil #4 Use (kBtu)": 0.0,
    }
    values.update(overrides)
    return pd.Series(values)


def test_electricity_stays_in_kwh_and_other_fuels_use_billing_divisors():
    consumption = get_energy_consumption_in_billing_units(
        _row(
            **{
                "Electricity Use - Grid Purchase (kWh)": 250.0,
                "Natural Gas Use (kBtu)": 1000.0,
                "District Steam Use (kBtu)": 2388.0,
                "Fuel Oil #2 Use (kBtu)": 276.0,
                "Fuel Oil #4 Use (kBtu)": 292.0,
            }
        )
    )

    assert consumption["Electricity"] == 250.0
    assert consumption["Natural Gas"] == 1000.0 / 100.0
    assert consumption["Steam"] == 2388.0 / 1194.00
    assert consumption["Fuel Oil 2"] == 276.0 / 138.00
    assert consumption["Fuel Oil 4"] == 292.0 / 146.00


def test_missing_source_column_contributes_zero():
    consumption = get_energy_consumption_in_billing_units(pd.Series(dtype="float64"))

    assert consumption == {
        "Electricity": 0.0,
        "Natural Gas": 0.0,
        "Steam": 0.0,
        "Fuel Oil 2": 0.0,
        "Fuel Oil 4": 0.0,
    }
