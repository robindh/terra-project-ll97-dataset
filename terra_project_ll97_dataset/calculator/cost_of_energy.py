from terra_project_ll97_dataset.calculator.energy_unit_conversion import sum_consumption_times_rate
from terra_project_ll97_dataset.util.common import ENERGY_PRICES_DOLLARS_PER_BILLING_UNIT, ENERGY_TYPES


def get_cost_of_energy_by_year_and_energy_type(
        start_year: int,
        end_year_inclusive: int) -> dict[int, dict[str, float]]:
    cost_of_energy_lookup_table: dict[int, dict[str, float]] = {}

    for year in range(start_year, end_year_inclusive + 1):
        cost_of_energy_lookup_table[year] = {
            energy_type.name: ENERGY_PRICES_DOLLARS_PER_BILLING_UNIT[energy_type.name]
            for energy_type in ENERGY_TYPES
        }

    return cost_of_energy_lookup_table


def get_cost_of_energy(
        cost_of_energy_lookup_table: dict[int, dict[str, float]],
        year: int,
        row) -> float:
    return sum_consumption_times_rate(row, cost_of_energy_lookup_table[year])
