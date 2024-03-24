from typing import Dict

from terra_project_ll97_dataset.calculator.energy_unit_conversion import get_energy_consumption_in_billing_units
from terra_project_ll97_dataset.util.common import EnergyTypes

'''
Cost of energy per energy type per year

Electricity -> "$/kWh"

Natural Gas -> "$/therm"

Steam -> $/Mlb

Fuel Oil #2 $/gal

Fuel Oil #4 $/gal
'''


def get_cost_of_energy_by_year_and_energy_type(
        start_year: int,
        end_year_inclusive: int) -> Dict[int, Dict[str, float]]:
    cost_of_energy_lookup_table: Dict[int, Dict[str, float]] = {}

    for year in range(start_year, end_year_inclusive + 1):
        cost_of_energy_lookup_table[year]: Dict[str, float] = {}
        cost_of_energy_per_unit_energy = 0.0
        for energy_type in EnergyTypes:
            match energy_type:
                case "Electricity":
                    cost_of_energy_per_unit_energy = 0.22
                case "Natural Gas":
                    cost_of_energy_per_unit_energy = 0.997
                case "Steam":
                    cost_of_energy_per_unit_energy = 35.0
                case "Fuel Oil 2":
                    cost_of_energy_per_unit_energy = 1.65
                case "Fuel Oil 4":
                    cost_of_energy_per_unit_energy = 1.65
            cost_of_energy_lookup_table[year][energy_type] = cost_of_energy_per_unit_energy

    return cost_of_energy_lookup_table


def get_cost_of_energy(
        cost_of_energy_lookup_table: Dict[int, Dict[str, float]],
        year: int,
        row) -> float:
    energy_consumption = get_energy_consumption_in_billing_units(row)

    cost_of_energy_in_year = 0.0
    cost_of_energy_by_energy_type = cost_of_energy_lookup_table[year]

    for energy_type in EnergyTypes:
        cost_of_energy_in_year += energy_consumption[energy_type] * cost_of_energy_by_energy_type[energy_type]
    return cost_of_energy_in_year
