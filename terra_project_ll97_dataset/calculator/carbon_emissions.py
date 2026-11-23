"""Estimate building greenhouse-gas emissions in tCO2e.

Electricity and steam use a lower factor from 2030 onward. Natural gas
and both fuel oils keep one factor for every year.
"""

import pandas as pd

from terra_project_ll97_dataset.calculator import energy_unit_conversion
from terra_project_ll97_dataset.util import common


def _tco2e_per_billing_unit(energy_name: str, year: int) -> float:
    """Return one energy type's emission factor for a calendar year.

    Args:
        energy_name: Energy-type name, such as "Electricity".
        year: Calendar year.

    Returns:
        Tonnes of CO2 equivalent per billing unit.
    """
    factors = common.EMISSION_FACTORS_TCO2E_PER_BILLING_UNIT[energy_name]
    before_change, from_change = factors
    if year >= common.EMISSION_FACTOR_CHANGE_YEAR:
        return from_change
    return before_change


def get_carbon_emissions_by_year_and_energy_type(
    start_year: int,
    end_year_inclusive: int,
) -> dict[int, dict[str, float]]:
    """Build the emission-factor table for an inclusive year span.

    Args:
        start_year: First calendar year in the table.
        end_year_inclusive: Last calendar year in the table.

    Returns:
        A mapping of year to energy-type name to tCO2e per billing unit.
    """
    carbon_emissions: dict[int, dict[str, float]] = {}

    for year in range(start_year, end_year_inclusive + 1):
        carbon_emissions[year] = {
            energy_type.name: _tco2e_per_billing_unit(energy_type.name, year)
            for energy_type in common.ENERGY_TYPES
        }

    return carbon_emissions


def get_carbon_emissions(
    carbon_emissions_lookup_table: dict[int, dict[str, float]],
    year: int,
    row: pd.Series,
) -> float:
    """Return one building's emissions for one year.

    Args:
        carbon_emissions_lookup_table: Factor table from
            get_carbon_emissions_by_year_and_energy_type.
        year: Calendar year. Must be a key in the lookup table.
        row: One LL84 building row.

    Returns:
        Emissions in tCO2e.
    """
    return energy_unit_conversion.sum_consumption_times_rate(
        row,
        carbon_emissions_lookup_table[year],
    )
