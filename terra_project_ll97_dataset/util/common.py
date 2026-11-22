# Common enums and constants
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class EnergyType:
    name: str
    source_column: str
    # Divisor that converts the LL84 source column into the billing unit
    # (kWh, therm, Mlb, or gallon).
    # Conversions based on https://portfoliomanager.energystar.gov/pdf/reference/Thermal%20Conversions.pdf
    billing_unit_divisor: float


ENERGY_TYPES: tuple[EnergyType, ...] = (
    EnergyType("Electricity", "Electricity Use - Grid Purchase (kWh)", 1.0),
    EnergyType("Natural Gas", "Natural Gas Use (kBtu)", 100.0),
    EnergyType("Steam", "District Steam Use (kBtu)", 1194.00),
    EnergyType("Fuel Oil 2", "Fuel Oil #2 Use (kBtu)", 138.00),
    EnergyType("Fuel Oil 4", "Fuel Oil #4 Use (kBtu)", 146.00),
)

# years when the carbon emissions threshold change
StartYears: List[int] = [2024, 2030, 2035, 2040, 2050]


def get_year_ranges():
    year_ranges = []

    for index, year in enumerate(StartYears):
        if index + 1 < len(StartYears):
            year_ranges.append((year, StartYears[index + 1] - 1))
        else:
            year_ranges.append((year, -1))

    return year_ranges
