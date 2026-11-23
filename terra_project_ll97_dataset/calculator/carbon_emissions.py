from terra_project_ll97_dataset.calculator.energy_unit_conversion import sum_consumption_times_rate
from terra_project_ll97_dataset.util.common import (
    EMISSION_FACTOR_CHANGE_YEAR,
    EMISSION_FACTORS_TCO2E_PER_BILLING_UNIT,
    ENERGY_TYPES,
)


def _tco2e_per_billing_unit(energy_name: str, year: int) -> float:
    before_change, from_change = EMISSION_FACTORS_TCO2E_PER_BILLING_UNIT[energy_name]
    if year >= EMISSION_FACTOR_CHANGE_YEAR:
        return from_change
    return before_change


def get_carbon_emissions_by_year_and_energy_type(
        start_year: int,
        end_year_inclusive: int) -> dict[int, dict[str, float]]:
    carbon_emissions: dict[int, dict[str, float]] = {}

    for year in range(start_year, end_year_inclusive + 1):
        carbon_emissions[year] = {
            energy_type.name: _tco2e_per_billing_unit(energy_type.name, year)
            for energy_type in ENERGY_TYPES
        }

    return carbon_emissions


def get_carbon_emissions(
        carbon_emissions_lookup_table: dict[int, dict[str, float]],
        year: int,
        row) -> float:
    return sum_consumption_times_rate(row, carbon_emissions_lookup_table[year])
