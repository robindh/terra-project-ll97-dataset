from terra_project_ll97_dataset.util.common import EnergyTypes

# Conversions based on https://portfoliomanager.energystar.gov/pdf/reference/Thermal%20Conversions.pdf
energy_units_conversion_dictionary = {
    "Electricity": {
        "source_column": "Electricity Use - Grid Purchase (kWh)",
        "conversion_factor": 1.0
    },
    "Natural Gas": {
        "source_column": "Natural Gas Use (kBtu)",
        "conversion_factor": 100.0
    },
    "Steam": {
        "source_column": "District Steam Use (kBtu)",
        "conversion_factor": 1194.00
    },
    "Fuel Oil 2": {
        "source_column": "Fuel Oil #2 Use (kBtu)",
        "conversion_factor": 138.00
    },
    "Fuel Oil 4": {
        "source_column": "Fuel Oil #4 Use (kBtu)",
        "conversion_factor": 146.00
    },
}


def _convert_energy_units(energy_type: str, row) -> float:
    source_column = energy_units_conversion_dictionary[energy_type]["source_column"]
    conversion_factor = float(energy_units_conversion_dictionary[energy_type]["conversion_factor"])

    return float(row.get(source_column, 0.0)) / conversion_factor


def get_energy_consumption_in_billing_units(row):
    energy_consumption = {}
    for energy_type in EnergyTypes:
        energy_consumption[energy_type] = _convert_energy_units(energy_type, row)
    return energy_consumption
