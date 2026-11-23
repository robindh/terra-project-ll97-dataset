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
