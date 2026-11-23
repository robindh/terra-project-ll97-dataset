"""Convert LL84 energy use into the billing units used by the rates.

Electricity stays in kWh. Natural gas becomes therms, district steam
becomes Mlb, and fuel oil becomes gallons.
"""

import pandas as pd

from terra_project_ll97_dataset.util import common


def get_energy_consumption_in_billing_units(
    row: pd.Series,
) -> dict[str, float]:
    """Convert one building row into billing-unit consumption.

    Args:
        row: One LL84 building row. A missing source column contributes 0.0.

    Returns:
        Consumption keyed by energy-type name.
    """
    energy_consumption = {}
    for energy_type in common.ENERGY_TYPES:
        source_value = float(row.get(energy_type.source_column, 0.0))
        energy_consumption[energy_type.name] = (
            source_value / float(energy_type.billing_unit_divisor)
        )
    return energy_consumption


def billing_unit_consumption_by_energy_type(
    buildings: pd.DataFrame,
) -> dict[str, pd.Series]:
    """Convert each building's LL84 use into billing-unit consumption.

    Args:
        buildings: Building rows. Each energy type's source column must
            be present. Values are already numeric.

    Returns:
        Consumption keyed by energy-type name. Electricity stays in kWh.
        Natural gas is therms, steam is Mlb, and fuel oil is gallons.
    """
    consumption: dict[str, pd.Series] = {}
    for energy_type in common.ENERGY_TYPES:
        source = buildings[energy_type.source_column].astype("float64")
        consumption[energy_type.name] = source / float(
            energy_type.billing_unit_divisor
        )
    return consumption


def sum_billing_unit_consumption_times_rate(
    consumption_by_energy_type: dict[str, pd.Series],
    rate_by_energy_type: dict[str, float],
) -> pd.Series:
    """Sum billing-unit consumption times a rate for each building.

    The running total starts at 0.0 and adds energy types in ENERGY_TYPES
    order, matching sum_consumption_times_rate.

    Args:
        consumption_by_energy_type: Billing-unit consumption for every
            energy type. Each series is one building per row, and every
            series shares an index.
        rate_by_energy_type: tCO2e or dollars per billing unit, keyed by
            energy-type name. The mapping must contain every energy type.

    Returns:
        The total for each building. Emissions callers get tCO2e. Cost
        callers get dollars.
    """
    index = next(iter(consumption_by_energy_type.values())).index
    total = pd.Series(0.0, index=index, dtype="float64")
    for energy_type in common.ENERGY_TYPES:
        total = total + (
            consumption_by_energy_type[energy_type.name]
            * rate_by_energy_type[energy_type.name]
        )
    return total


def sum_consumption_times_rate(
    row: pd.Series,
    rate_by_energy_type: dict[str, float],
) -> float:
    """Sum billing-unit consumption times a rate for each energy type.

    Args:
        row: One LL84 building row.
        rate_by_energy_type: tCO2e or dollars per billing unit, keyed by
            energy-type name. The mapping must contain every energy type.

    Returns:
        The total for this row. Emissions callers get tCO2e. Cost callers
        get dollars.
    """
    energy_consumption = get_energy_consumption_in_billing_units(row)
    total = 0.0
    for energy_type in common.ENERGY_TYPES:
        total += (
            energy_consumption[energy_type.name]
            * rate_by_energy_type[energy_type.name]
        )
    return total
