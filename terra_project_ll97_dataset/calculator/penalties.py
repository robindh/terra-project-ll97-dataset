penalty_per_tCO2_over_threshold = 268


def calculate_penalties(row, carbon_emmissions_column_name: str, carbon_emissions_threshold_column_name: str) -> float:
    if row[carbon_emmissions_column_name] <= row[carbon_emissions_threshold_column_name]:
        return 0.0

    return penalty_per_tCO2_over_threshold * (
                row[carbon_emmissions_column_name] - row[carbon_emissions_threshold_column_name])
