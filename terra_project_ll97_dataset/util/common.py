# Common enums and constants
from typing import List

EnergyTypes: List[str] = [
    "Electricity",
    "Natural Gas",
    "Steam",
    "Fuel Oil 2",
    "Fuel Oil 4",
]

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
