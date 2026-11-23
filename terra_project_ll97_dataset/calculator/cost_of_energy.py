"""Estimate annual energy cost in dollars.

Prices are constant across years. They use the same billing units as the
emission factors: kWh, therm, Mlb, and gallon.
"""

import pandas as pd

from terra_project_ll97_dataset.calculator import energy_unit_conversion
from terra_project_ll97_dataset.util import common


def get_cost_of_energy_by_year_and_energy_type(
    start_year: int,
    end_year_inclusive: int,
) -> dict[int, dict[str, float]]:
    """Build the energy-price table for an inclusive year span.

    Args:
        start_year: First calendar year in the table.
        end_year_inclusive: Last calendar year in the table.

    Returns:
        A mapping of year to energy-type name to dollars per billing unit.
        Every year carries the same prices.
    """
    cost_of_energy_lookup_table: dict[int, dict[str, float]] = {}

    for year in range(start_year, end_year_inclusive + 1):
        cost_of_energy_lookup_table[year] = {
            energy_type.name: (
                common.ENERGY_PRICES_DOLLARS_PER_BILLING_UNIT[energy_type.name]
            )
            for energy_type in common.ENERGY_TYPES
        }

    return cost_of_energy_lookup_table


def get_cost_of_energy(
    cost_of_energy_lookup_table: dict[int, dict[str, float]],
    year: int,
    row: pd.Series,
) -> float:
    """Return one building's energy cost for one year.

    Args:
        cost_of_energy_lookup_table: Price table from
            get_cost_of_energy_by_year_and_energy_type.
        year: Calendar year. Must be a key in the lookup table.
        row: One LL84 building row.

    Returns:
        Energy cost in dollars.
    """
    return energy_unit_conversion.sum_consumption_times_rate(
        row,
        cost_of_energy_lookup_table[year],
    )
