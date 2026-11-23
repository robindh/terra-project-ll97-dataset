from terra_project_ll97_dataset.util.common import ENERGY_TYPES


def get_energy_consumption_in_billing_units(row):
    energy_consumption = {}
    for energy_type in ENERGY_TYPES:
        source_value = float(row.get(energy_type.source_column, 0.0))
        energy_consumption[energy_type.name] = source_value / float(energy_type.billing_unit_divisor)
    return energy_consumption


def sum_consumption_times_rate(row, rate_by_energy_type: dict[str, float]) -> float:
    energy_consumption = get_energy_consumption_in_billing_units(row)
    total = 0.0
    for energy_type in ENERGY_TYPES:
        total += energy_consumption[energy_type.name] * rate_by_energy_type[energy_type.name]
    return total
