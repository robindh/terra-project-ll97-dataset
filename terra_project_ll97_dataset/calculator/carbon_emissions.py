from typing import Dict

from terra_project_ll97_dataset.calculator.energy_unit_conversion import get_energy_consumption_in_billing_units
from terra_project_ll97_dataset.util.common import EnergyTypes

'''
Carbon Emissions per energy type per year

Electricity -> "tCO2e/kWh"

Natural Gas -> "tCO2e/therm"

Steam -> tCO2e/Mlb

Fuel Oil #2 tCO2e/gal

Fuel Oil #4 tCO2e/gal

'''


def get_carbon_emissions_by_year_and_energy_type(
        start_year: int,
        end_year_inclusive: int) -> Dict[int, Dict[str, float]]:
    carbon_emissions: Dict[int, Dict[str, float]] = {}

    for year in range(start_year, end_year_inclusive + 1):
        carbon_emissions[year]: Dict[str, float] = {}
        carbon_emission_per_unit_energy = 0.0
        for energy_type in EnergyTypes:
            match energy_type:
                case "Electricity":
                    if year >= 2030:
                        carbon_emission_per_unit_energy = 0.15 / 1000.00
                    else:
                        carbon_emission_per_unit_energy = 0.29 / 1000.00
                case "Natural Gas":
                    carbon_emission_per_unit_energy = 5.0 / 1000.00
                case "Steam":
                    if year >= 2030:
                        carbon_emission_per_unit_energy = 51.6 / 1000.00
                    else:
                        carbon_emission_per_unit_energy = 53.6 / 1000.00
                case "Fuel Oil 2":
                    carbon_emission_per_unit_energy = 10.24 / 1000.00
                case "Fuel Oil 4":
                    carbon_emission_per_unit_energy = 10.99 / 1000.00
            carbon_emissions[year][energy_type] = carbon_emission_per_unit_energy

    return carbon_emissions


def get_carbon_emissions(
        carbon_emissions_lookup_table: Dict[int, Dict[str, float]],
        year: int,
        row) -> float:
    energy_consumption = get_energy_consumption_in_billing_units(row)

    carbon_emissions_in_year = 0.0
    carbon_emissions_by_energy_type = carbon_emissions_lookup_table[year]

    for energy_type in EnergyTypes:
        carbon_emissions_in_year += energy_consumption[energy_type] * carbon_emissions_by_energy_type[energy_type]
    return carbon_emissions_in_year
