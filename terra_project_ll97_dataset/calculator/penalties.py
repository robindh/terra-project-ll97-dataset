from terra_project_ll97_dataset.util.common import PENALTY_DOLLARS_PER_TCO2E


def calculate_penalties(row, carbon_emmissions_column_name: str, carbon_emissions_threshold_column_name: str) -> float:
    if row[carbon_emmissions_column_name] <= row[carbon_emissions_threshold_column_name]:
        return 0.0

    return PENALTY_DOLLARS_PER_TCO2E * (
                row[carbon_emmissions_column_name] - row[carbon_emissions_threshold_column_name])
