# Common enums and constants
from dataclasses import dataclass


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

LARGEST_PROPERTY_USE_TYPE = "Largest Property Use Type"
LARGEST_PROPERTY_USE_GFA_SQFT = "Largest Property Use Type - Gross Floor Area (ft²)"
SECOND_LARGEST_PROPERTY_USE_GFA_SQFT = "2nd Largest Property Use Type - Gross Floor Area (ft²)"
THIRD_LARGEST_PROPERTY_USE_GFA_SQFT = "3rd Largest Property Use Type - Gross Floor Area (ft²)"

# Years the dataset builder calculates. The last LL97 period is open-ended
# (2050+), but averages still stop at ANALYSIS_END_YEAR.
ANALYSIS_START_YEAR = 2024
ANALYSIS_END_YEAR = 2050

# Years when the carbon emissions threshold changes.
PERIOD_START_YEARS: list[int] = [2024, 2030, 2035, 2040, 2050]

# Electricity and steam emission factors change at this year.
EMISSION_FACTOR_CHANGE_YEAR = 2030

# Dollars charged for each tCO2e above the emissions limit.
PENALTY_DOLLARS_PER_TCO2E = 268

# tCO2e per billing unit, before EMISSION_FACTOR_CHANGE_YEAR and from that year on.
# Electricity is per kWh, natural gas per therm, steam per Mlb, fuel oil per gallon.
ELECTRICITY_TCO2E_PER_KWH_BEFORE_2030 = 0.29 / 1000.00
ELECTRICITY_TCO2E_PER_KWH_FROM_2030 = 0.15 / 1000.00
NATURAL_GAS_TCO2E_PER_THERM = 5.0 / 1000.00
STEAM_TCO2E_PER_MLB_BEFORE_2030 = 53.6 / 1000.00
STEAM_TCO2E_PER_MLB_FROM_2030 = 51.6 / 1000.00
FUEL_OIL_2_TCO2E_PER_GALLON = 10.24 / 1000.00
FUEL_OIL_4_TCO2E_PER_GALLON = 10.99 / 1000.00

EMISSION_FACTORS_TCO2E_PER_BILLING_UNIT: dict[str, tuple[float, float]] = {
    "Electricity": (ELECTRICITY_TCO2E_PER_KWH_BEFORE_2030, ELECTRICITY_TCO2E_PER_KWH_FROM_2030),
    "Natural Gas": (NATURAL_GAS_TCO2E_PER_THERM, NATURAL_GAS_TCO2E_PER_THERM),
    "Steam": (STEAM_TCO2E_PER_MLB_BEFORE_2030, STEAM_TCO2E_PER_MLB_FROM_2030),
    "Fuel Oil 2": (FUEL_OIL_2_TCO2E_PER_GALLON, FUEL_OIL_2_TCO2E_PER_GALLON),
    "Fuel Oil 4": (FUEL_OIL_4_TCO2E_PER_GALLON, FUEL_OIL_4_TCO2E_PER_GALLON),
}

# Dollars per billing unit. Prices do not change with the year.
ELECTRICITY_DOLLARS_PER_KWH = 0.22
NATURAL_GAS_DOLLARS_PER_THERM = 0.997
STEAM_DOLLARS_PER_MLB = 35.0
FUEL_OIL_2_DOLLARS_PER_GALLON = 1.65
FUEL_OIL_4_DOLLARS_PER_GALLON = 1.65

ENERGY_PRICES_DOLLARS_PER_BILLING_UNIT: dict[str, float] = {
    "Electricity": ELECTRICITY_DOLLARS_PER_KWH,
    "Natural Gas": NATURAL_GAS_DOLLARS_PER_THERM,
    "Steam": STEAM_DOLLARS_PER_MLB,
    "Fuel Oil 2": FUEL_OIL_2_DOLLARS_PER_GALLON,
    "Fuel Oil 4": FUEL_OIL_4_DOLLARS_PER_GALLON,
}


@dataclass(frozen=True)
class YearPeriod:
    """One LL97 compliance period.

    Labels look like ``2024-2029``. The final period is open-ended: its label
    is ``2050+`` and its range is only the start year (``range(2050, 2051)``),
    which is the average the builder uses today.
    """

    label: str
    years: range


def get_year_ranges() -> list[YearPeriod]:
    periods = []

    for index, start_year in enumerate(PERIOD_START_YEARS):
        if index + 1 < len(PERIOD_START_YEARS):
            end_year = PERIOD_START_YEARS[index + 1] - 1
            periods.append(YearPeriod(f"{start_year}-{end_year}", range(start_year, end_year + 1)))
        else:
            periods.append(YearPeriod(f"{start_year}+", range(start_year, start_year + 1)))

    return periods
